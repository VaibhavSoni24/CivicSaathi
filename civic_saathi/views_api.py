from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime

from .models import (
    CustomUser, Complaint, ComplaintLog, ComplaintVote, ComplaintCategory,
    Department, SubAdminCategory, Worker, WorkerAttendance, DepartmentAttendance, Office
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    ComplaintSerializer, ComplaintCreateSerializer, ComplaintUpdateSerializer,
    ComplaintLogSerializer, ComplaintVoteSerializer, DepartmentSerializer,
    SubAdminCategorySerializer, ComplaintCategorySerializer,
    WorkerSerializer, WorkerAttendanceSerializer, DepartmentAttendanceSerializer, OfficeSerializer
)
from .filter_system import ComplaintFilterSystem, ComplaintSortingSystem, ComplaintAssignmentSystem
from .permissions import IsAdmin, IsSubAdmin, IsDepartmentAdmin, IsCitizen
from .admin_auth import AdminTokenAuthentication


# -------------------------
# Helper Functions
# -------------------------
def get_action_user(request):
    """Get the user for logging actions, handling admin mock users"""
    if hasattr(request.user, 'is_admin') and request.user.is_admin:
        # Admin user is a mock object, return None for logging
        return None
    return request.user


def assign_office_to_complaint(complaint):
    """
    Auto-assign office to complaint based on location and status.
    Assigns if status is PENDING or complaint has passed filtering.
    """
    # Check if complaint should be assigned to office
    if complaint.status not in ['PENDING', 'FILTERING', 'SORTING'] and not complaint.filter_passed:
        return
    
    # Check if complaint has department and city
    if not complaint.department or not complaint.city:
        return
    
    # Try to find matching office
    try:
        office = Office.objects.get(
            department=complaint.department,
            city__iexact=complaint.city,
            is_active=True
        )
        complaint.office = office
        complaint.save()
    except Office.DoesNotExist:
        # No matching office found
        pass
    except Office.MultipleObjectsReturned:
        # Multiple offices found, take the first one
        office = Office.objects.filter(
            department=complaint.department,
            city__iexact=complaint.city,
            is_active=True
        ).first()
        if office:
            complaint.office = office
            complaint.save()


# -------------------------
# Authentication Views
# -------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration"""
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import traceback
        print("Registration Error:", str(e))
        traceback.print_exc()
        return Response({
            'error': str(e),
            'detail': 'An error occurred during registration'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def worker_login(request):
    """Worker login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user and user.user_type == 'WORKER':
        # Check if worker exists
        try:
            worker = Worker.objects.get(user=user, is_active=True)
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'user_type': user.user_type,
                },
                'worker': {
                    'id': worker.id,
                    'department': worker.department.name,
                    'department_id': worker.department.id,
                    'office': worker.office.name if worker.office else None,
                    'office_id': worker.office.id if worker.office else None,
                    'role': worker.role,
                    'city': worker.city,
                    'state': worker.state,
                },
                'token': token.key
            })
        except Worker.DoesNotExist:
            return Response({'error': 'Worker account not found or inactive'}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({'error': 'Invalid credentials or not a worker account'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout"""
    request.user.auth_token.delete()
    return Response({'message': 'Successfully logged out'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current user info"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# -------------------------
# Complaint Views for Citizens
# -------------------------
class ComplaintCreateView(generics.CreateAPIView):
    """Create new complaint"""
    serializer_class = ComplaintCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        complaint = serializer.save(user=self.request.user)
        
        # Run through filter system
        validation_result = ComplaintFilterSystem.validate_complaint(complaint)
        
        complaint.filter_checked = True
        complaint.filter_passed = validation_result['passed']
        complaint.filter_reason = validation_result['reason']
        complaint.is_spam = validation_result['is_spam']
        
        if validation_result['passed']:
            complaint.status = 'FILTERING'
            # Auto-sort the complaint
            ComplaintSortingSystem.sort_complaint(complaint)
            # Auto-assign based on location
            ComplaintAssignmentSystem.assign_complaint(
                complaint, 
                complaint.city, 
                complaint.state
            )
            # Auto-assign office based on location
            assign_office_to_complaint(complaint)
        else:
            complaint.status = 'DECLINED'
        
        complaint.save()
        
        # Log the action
        ComplaintLog.objects.create(
            complaint=complaint,
            action_by=self.request.user,
            note=f"Complaint created and filtered. Result: {validation_result['reason']}",
            new_status=complaint.status
        )


class MyComplaintsView(generics.ListAPIView):
    """Get all complaints by current user"""
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Complaint.objects.filter(
            user=self.request.user,
            is_deleted=False
        ).order_by('-created_at')


class AllComplaintsView(generics.ListAPIView):
    """Get all complaints in user's area (city/state) or all for admins"""
    serializer_class = ComplaintSerializer
    permission_classes = [AllowAny]  # Allow any access for both users and admins
    authentication_classes = []  # Disable authentication requirement

    def get_queryset(self):
        # Check if admin headers are present
        is_admin = self.request.headers.get('X-Admin-Token') or self.request.headers.get('X-Admin-User')
        
        # Show all non-deleted complaints (including demo complaints that haven't been filtered)
        queryset = Complaint.objects.filter(
            is_deleted=False
        )
        
        # If admin, return all complaints without filtering
        if is_admin:
            return queryset.order_by('-created_at')
        
        # For regular users, filter by location (optional - show all if no filters)
        user = self.request.user if self.request.user.is_authenticated else None
        if user:
            city = self.request.query_params.get('city', None)  # Don't auto-filter by user's city
            state = self.request.query_params.get('state', None)
        else:
            city = self.request.query_params.get('city')
            state = self.request.query_params.get('state')
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        # Always order by most recent first
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """Override to ensure proper response format"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ComplaintDetailView(generics.RetrieveAPIView):
    """Get complaint details"""
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [AllowAny]  # Allow any access for both users and admins
    authentication_classes = []  # Disable authentication requirement

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upvote_complaint(request, pk):
    """Upvote a complaint"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Check if user already voted
    vote, created = ComplaintVote.objects.get_or_create(
        complaint=complaint,
        user=request.user
    )
    
    if created:
        # Increment upvote count
        complaint.upvote_count += 1
        complaint.save()
        return Response({'message': 'Upvoted successfully', 'upvotes': complaint.upvote_count})
    else:
        # Remove vote
        vote.delete()
        complaint.upvote_count -= 1
        complaint.save()
        return Response({'message': 'Vote removed', 'upvotes': complaint.upvote_count})


# -------------------------
# Department Admin Views
# -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def department_complaints(request):
    """Get complaints for department admin's department and city"""
    user = request.user
    
    # Check if user is department admin
    if not hasattr(user, 'departmentadminprofile'):
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    profile = user.departmentadminprofile
    department = profile.department
    city = profile.city
    
    status_filter = request.query_params.get('status', None)
    
    queryset = Complaint.objects.filter(
        department=department,
        city__icontains=city,
        is_deleted=False,
        filter_passed=True
    )
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    queryset = queryset.order_by('-priority', '-created_at')
    serializer = ComplaintSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def assign_to_worker(request, pk):
    """Assign complaint to worker"""
    complaint = get_object_or_404(Complaint, pk=pk)
    worker_id = request.data.get('worker_id')
    notes = request.data.get('notes', '')
    
    if not worker_id:
        return Response({'error': 'Worker ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    worker = get_object_or_404(Worker, pk=worker_id)
    
    # Update complaint
    old_status = complaint.status
    complaint.current_worker = worker
    complaint.status = 'IN_PROGRESS'
    complaint.assigned = True
    
    # Assign office from worker if worker has an office
    if worker.office:
        complaint.office = worker.office
    
    complaint.save()
    
    # Log the action - handle anonymous users
    action_user = None
    if request.user and request.user.is_authenticated:
        action_user = request.user
    
    ComplaintLog.objects.create(
        complaint=complaint,
        action_by=action_user,
        note=f"Assigned to worker {worker.user.username}. {notes}",
        old_status=old_status,
        new_status='IN_PROGRESS',
        new_assignee=worker.user.username
    )
    
    serializer = ComplaintSerializer(complaint)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_complaint(request, pk):
    """Verify a complaint as genuine"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    old_status = complaint.status
    complaint.is_genuine = True
    complaint.filter_passed = True
    complaint.filter_checked = True
    complaint.status = 'PENDING'
    complaint.save()
    
    # Log the action - handle anonymous users
    action_user = None
    if request.user and request.user.is_authenticated:
        action_user = request.user
    
    ComplaintLog.objects.create(
        complaint=complaint,
        action_by=action_user,
        note="Complaint verified as genuine",
        old_status=old_status,
        new_status='PENDING'
    )
    
    return Response({'message': 'Complaint verified successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_complaint_status(request, pk):
    """Update complaint status"""
    complaint = get_object_or_404(Complaint, pk=pk)
    new_status = request.data.get('status')
    note = request.data.get('note', '')
    
    if not new_status:
        return Response({'error': 'Status required'}, status=status.HTTP_400_BAD_REQUEST)
    
    old_status = complaint.status
    complaint.status = new_status
    
    # If marking as genuine or rejected
    if 'is_genuine' in request.data:
        complaint.is_genuine = request.data['is_genuine']
    
    # If completed, require completion image
    if new_status == 'COMPLETED':
        if 'completion_image' in request.FILES:
            complaint.completion_image = request.FILES['completion_image']
        complaint.completion_note = request.data.get('completion_note', '')
        complaint.completed_at = timezone.now()
    
    # Auto-assign office if status is PENDING and no office assigned
    if new_status == 'PENDING' and not complaint.office:
        assign_office_to_complaint(complaint)
    
    complaint.save()
    
    # Log the action
    ComplaintLog.objects.create(
        complaint=complaint,
        action_by=get_action_user(request),
        note=note or f"Status updated to {new_status}",
        old_status=old_status,
        new_status=new_status
    )
    
    return Response({'message': 'Status updated successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_complaint(request, pk):
    """Reject a complaint"""
    complaint = get_object_or_404(Complaint, pk=pk)
    reason = request.data.get('reason', 'Not genuine')
    
    old_status = complaint.status
    complaint.status = 'REJECTED'
    complaint.is_genuine = False
    complaint.save()
    
    ComplaintLog.objects.create(
        complaint=complaint,
        action_by=get_action_user(request),
        note=f"Rejected: {reason}",
        old_status=old_status,
        new_status='REJECTED'
    )
    
    return Response({'message': 'Complaint rejected'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_complaint(request, pk):
    """Delete unnecessary/wrong complaint (Sub-Admin only)"""
    user = request.user
    
    # Check if user is sub-admin or admin (allow admin mock users)
    if hasattr(user, 'is_admin') and user.is_admin:
        # Admin mock user, allow access
        pass
    elif not hasattr(user, 'user_type') or user.user_type not in ['ADMIN', 'SUB_ADMIN']:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    complaint = get_object_or_404(Complaint, pk=pk)
    complaint.is_deleted = True
    complaint.save()
    
    ComplaintLog.objects.create(
        complaint=complaint,
        action_by=get_action_user(request),
        note="Complaint deleted by admin",
        old_status=complaint.status,
        new_status='DELETED'
    )
    
    return Response({'message': 'Complaint deleted successfully'})


# -------------------------
# Worker Views
# -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def worker_assignments(request):
    """Get complaints assigned to current worker"""
    user = request.user
    
    if not hasattr(user, 'worker'):
        return Response({'error': 'Not a worker'}, status=status.HTTP_403_FORBIDDEN)
    
    worker = user.worker
    complaints = Complaint.objects.filter(
        current_worker=worker,
        is_deleted=False
    ).order_by('-priority', '-created_at')
    
    serializer = ComplaintSerializer(complaints, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def worker_complaint_detail(request, pk):
    """Get complaint detail for worker"""
    user = request.user
    
    if not hasattr(user, 'worker'):
        return Response({'error': 'Not a worker'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        complaint = Complaint.objects.get(pk=pk, current_worker=user.worker, is_deleted=False)
        serializer = ComplaintSerializer(complaint, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Complaint.DoesNotExist:
        return Response(
            {'error': 'Complaint not found or not assigned to you'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def worker_complete_complaint(request, pk):
    """Mark complaint as completed by worker"""
    user = request.user
    
    if not hasattr(user, 'worker'):
        return Response({'error': 'Not a worker'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        complaint = Complaint.objects.get(pk=pk, current_worker=user.worker, is_deleted=False)
        
        # Update complaint status
        complaint.status = 'COMPLETED'
        complaint.completion_note = request.data.get('completion_note', '')
        
        # Handle completion image if provided
        if 'completion_image' in request.FILES:
            complaint.completion_image = request.FILES['completion_image']
        
        complaint.resolved_at = timezone.now()
        complaint.save()
        
        # Create log entry
        ComplaintLog.objects.create(
            complaint=complaint,
            note=f'Status changed to COMPLETED by worker {user.username}. Completion note: {complaint.completion_note}',
            old_status=complaint.status,
            new_status='COMPLETED',
            action_by=user
        )
        
        serializer = ComplaintSerializer(complaint, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Complaint.DoesNotExist:
        return Response(
            {'error': 'Complaint not found or not assigned to you'},
            status=status.HTTP_404_NOT_FOUND
        )


# -------------------------
# Worker Management Views
# -------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def get_workers(request):
    """Get all workers with optional filters"""
    queryset = Worker.objects.filter(is_active=True).select_related('user', 'department', 'office')
    
    # Filters
    department_id = request.query_params.get('department')
    office_id = request.query_params.get('office')
    city = request.query_params.get('city')
    
    if department_id:
        queryset = queryset.filter(department_id=department_id)
    if office_id:
        queryset = queryset.filter(office_id=office_id)
    if city:
        queryset = queryset.filter(user__city__iexact=city)
    
    serializer = WorkerSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_worker_detail(request, pk):
    """Get worker detail"""
    worker = get_object_or_404(Worker, pk=pk)
    serializer = WorkerSerializer(worker)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_worker(request):
    """Create a new worker"""
    from django.db import connection
    from datetime import date
    
    # Extract data
    username = request.data.get('username')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    phone = request.data.get('phone')
    department_id = request.data.get('department_id')
    office_id = request.data.get('office_id')
    role = request.data.get('role')
    city = request.data.get('city')
    state = request.data.get('state', 'Rajasthan')
    address = request.data.get('address', '')
    
    # Validation
    if not all([username, password, first_name, last_name, department_id, role, city]):
        return Response(
            {'error': 'Missing required fields: username, password, first_name, last_name, department_id, role, city'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if username already exists
    if CustomUser.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate phone number if provided
    if phone:
        import re
        if not re.match(r'^[6-9]\d{9}$', phone):
            return Response(
                {'error': 'Phone number must be exactly 10 digits and start with 6, 7, 8, or 9'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if phone number already exists
        if CustomUser.objects.filter(phone=phone).exists():
            return Response(
                {'error': 'This phone number is already registered. Please use a different number.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Check if department exists
    try:
        department = Department.objects.get(id=department_id)
    except Department.DoesNotExist:
        return Response(
            {'error': 'Department not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if office exists (optional)
    office = None
    if office_id:
        try:
            office = Office.objects.get(id=office_id)
        except Office.DoesNotExist:
            pass
    
    try:
        # Create user in custom_user table
        user = CustomUser.objects.create_user(
            username=username,
            email=email or f'{username}@municipal.gov.in',
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type='WORKER',
            city=city,
            state=state,
            phone=phone or ''
        )
        
        # Create worker (Worker model uses CustomUser directly, no need for auth_user)
        worker = Worker.objects.create(
            user=user,
            department=department,
            office=office,
            role=role,
            city=city,
            state=state,
            address=address or f'{city}, {state}',
            joining_date=date.today(),
            is_active=True
        )
        
        serializer = WorkerSerializer(worker)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        # If worker creation fails, delete the user
        if 'user' in locals():
            user.delete()
        return Response(
            {'error': f'Failed to create worker: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_all_workers(request):
    """Delete all workers and their associated users"""
    try:
        # Get all workers
        workers = Worker.objects.all()
        worker_count = workers.count()
        
        # Delete users associated with workers
        user_ids = list(workers.values_list('user_id', flat=True))
        CustomUser.objects.filter(id__in=user_ids, user_type='WORKER').delete()
        
        # Delete workers
        workers.delete()
        
        return Response({
            'message': f'Successfully deleted {worker_count} workers',
            'deleted_count': worker_count
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Failed to delete workers: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@authentication_classes([])
@permission_classes([AllowAny])
def update_worker(request, pk):
    """Update worker details"""
    try:
        worker = get_object_or_404(Worker, pk=pk)
        
        # Extract data
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        department_id = request.data.get('department_id')
        office_id = request.data.get('office_id')
        role = request.data.get('role')
        city = request.data.get('city')
        state = request.data.get('state')
        address = request.data.get('address')
        is_active = request.data.get('is_active')
        
        # Update user fields
        user = worker.user
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if email is not None:
            user.email = email
        if phone is not None:
            user.phone = phone
        if city is not None:
            user.city = city
        if state is not None:
            user.state = state
        user.save()
        
        # Update worker fields
        if department_id is not None:
            try:
                department = Department.objects.get(id=department_id)
                worker.department = department
            except Department.DoesNotExist:
                return Response(
                    {'error': 'Department not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if office_id is not None:
            if office_id == '':
                worker.office = None
            else:
                try:
                    office = Office.objects.get(id=office_id)
                    worker.office = office
                except Office.DoesNotExist:
                    return Response(
                        {'error': 'Office not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        if role is not None:
            worker.role = role
        if city is not None:
            worker.city = city
        if state is not None:
            worker.state = state
        if address is not None:
            worker.address = address
        if is_active is not None:
            worker.is_active = is_active
        
        worker.save()
        
        serializer = WorkerSerializer(worker)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Failed to update worker: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_worker_statistics(request, pk):
    """Get worker statistics including active and completed assignments"""
    try:
        worker = get_object_or_404(Worker, pk=pk)
        
        # Get active assignments (IN_PROGRESS or ASSIGNED status)
        active_count = Complaint.objects.filter(
            current_worker=worker,
            status__in=['ASSIGNED', 'IN_PROGRESS']
        ).count()
        
        # Get completed assignments
        completed_count = Complaint.objects.filter(
            current_worker=worker,
            status='COMPLETED'
        ).count()
        
        # Total assignments
        total_count = Complaint.objects.filter(current_worker=worker).count()
        
        return Response({
            'worker_id': worker.id,
            'active_assignments': active_count,
            'completed_assignments': completed_count,
            'total_assignments': total_count
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Failed to get worker statistics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_worker_complaints(request, pk):
    """Get all complaints assigned to a specific worker"""
    try:
        worker = get_object_or_404(Worker, pk=pk)
        
        # Get all complaints for this worker
        complaints = Complaint.objects.filter(
            current_worker=worker,
            is_deleted=False
        ).order_by('-created_at')
        
        serializer = ComplaintSerializer(complaints, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Failed to get worker complaints: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -------------------------
# Attendance Views
# -------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    """Mark worker attendance"""
    worker_id = request.data.get('worker_id')
    date_str = request.data.get('date', timezone.now().date())
    attendance_status = request.data.get('status', 'PRESENT')
    check_in = request.data.get('check_in_time')
    check_out = request.data.get('check_out_time')
    
    worker = get_object_or_404(Worker, pk=worker_id)
    
    if isinstance(date_str, str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date_obj = date_str
    
    attendance, created = WorkerAttendance.objects.update_or_create(
        worker=worker,
        date=date_obj,
        defaults={
            'status': attendance_status,
            'check_in_time': check_in,
            'check_out_time': check_out,
            'marked_by': request.user
        }
    )
    
    serializer = WorkerAttendanceSerializer(attendance)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attendance(request):
    """Get attendance records"""
    department_id = request.query_params.get('department')
    city = request.query_params.get('city')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    queryset = WorkerAttendance.objects.all()
    
    if department_id:
        queryset = queryset.filter(worker__department_id=department_id)
    if city:
        queryset = queryset.filter(worker__city__icontains=city)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    
    queryset = queryset.order_by('-date')
    serializer = WorkerAttendanceSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([AdminTokenAuthentication])
@permission_classes([AllowAny])
def get_attendance_register(request):
    """
    Get attendance register for all workers for a specific date.
    Returns all workers with their attendance status (present/absent).
    If no attendance record exists for a worker on that date, they are marked as absent.
    """
    from datetime import date as date_module
    
    # Get query parameters
    date_str = request.query_params.get('date')
    department_id = request.query_params.get('department_id')
    city = request.query_params.get('city')
    
    # Default to today if no date provided
    if date_str:
        try:
            target_date = date_module.fromisoformat(date_str)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    else:
        target_date = date_module.today()
    
    # Get all workers with filters
    workers_query = Worker.objects.select_related('user', 'department', 'office').filter(is_active=True)
    
    if department_id:
        workers_query = workers_query.filter(department_id=department_id)
    if city:
        workers_query = workers_query.filter(user__city__iexact=city)
    
    workers = workers_query.order_by('department__name', 'user__first_name')
    
    # Get attendance records for the target date
    attendance_records = WorkerAttendance.objects.filter(date=target_date).select_related('worker')
    attendance_dict = {att.worker_id: att for att in attendance_records}
    
    # Build register data
    register_data = []
    for worker in workers:
        attendance = attendance_dict.get(worker.id)
        
        register_entry = {
            'worker_id': worker.id,
            'worker_name': f"{worker.user.first_name} {worker.user.last_name}".strip() or worker.user.username,
            'username': worker.user.username,
            'role': worker.role,
            'department': worker.department.name if worker.department else 'N/A',
            'office': worker.office.name if worker.office else 'N/A',
            'city': worker.user.city,
            'date': target_date,
            'status': attendance.status if attendance else 'ABSENT',
            'check_in_time': attendance.check_in_time if attendance else None,
            'check_out_time': attendance.check_out_time if attendance else None,
            'marked_by': attendance.marked_by.username if attendance and attendance.marked_by else None,
        }
        register_data.append(register_entry)
    
    return Response({
        'date': target_date,
        'total_workers': len(register_data),
        'present_count': sum(1 for entry in register_data if entry['status'] == 'PRESENT'),
        'absent_count': sum(1 for entry in register_data if entry['status'] == 'ABSENT'),
        'register': register_data
    })


@api_view(['POST'])
@authentication_classes([AdminTokenAuthentication])
@permission_classes([AllowAny])
def bulk_mark_attendance(request):
    """
    Mark multiple workers as present for a specific date.
    Accepts a list of worker IDs and marks them all as present.
    """
    from datetime import date as date_module
    
    worker_ids = request.data.get('worker_ids', [])
    date_str = request.data.get('date')
    check_in_time = request.data.get('check_in_time')
    
    if not worker_ids:
        return Response({'error': 'worker_ids is required'}, status=400)
    
    # Default to today if no date provided
    if date_str:
        try:
            target_date = date_module.fromisoformat(date_str)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    else:
        target_date = date_module.today()
    
    # Get marked_by user
    marked_by_user = get_action_user(request)
    
    # Mark attendance for all workers
    marked_count = 0
    for worker_id in worker_ids:
        try:
            worker = Worker.objects.get(id=worker_id)
            WorkerAttendance.objects.update_or_create(
                worker=worker,
                date=target_date,
                defaults={
                    'status': 'PRESENT',
                    'check_in_time': check_in_time,
                    'marked_by': marked_by_user
                }
            )
            marked_count += 1
        except Worker.DoesNotExist:
            continue
    
    return Response({
        'success': True,
        'message': f'Marked {marked_count} workers as present',
        'date': target_date,
        'marked_count': marked_count
    })


# -------------------------
# Category & Department Views
# -------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    """Get all complaint categories"""
    categories = ComplaintCategory.objects.all()
    serializer = ComplaintCategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_departments(request):
    """Get all departments"""
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_offices(request):
    """Get all offices with optional filters"""
    city = request.query_params.get('city')
    department_id = request.query_params.get('department_id')
    
    queryset = Office.objects.filter(is_active=True)
    
    if city:
        queryset = queryset.filter(city__iexact=city)
    if department_id:
        queryset = queryset.filter(department_id=department_id)
    
    queryset = queryset.order_by('city', 'department__name')
    serializer = OfficeSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def create_office(request):
    """Create a new office"""
    # Extract data
    name = request.data.get('name')
    department_id = request.data.get('department_id')
    city = request.data.get('city')
    state = request.data.get('state', 'Rajasthan')
    address = request.data.get('address')
    pincode = request.data.get('pincode', '')
    phone = request.data.get('phone', '')
    email = request.data.get('email', '')
    office_hours = request.data.get('office_hours', '9:00 AM - 5:00 PM')
    
    # Validation
    if not all([name, department_id, city, address]):
        return Response(
            {'error': 'Missing required fields: name, department_id, city, address'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if department exists
    try:
        department = Department.objects.get(id=department_id)
    except Department.DoesNotExist:
        return Response(
            {'error': 'Department not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if office with same department and city already exists
    if Office.objects.filter(department=department, city__iexact=city).exists():
        return Response(
            {'error': f'An office for {department.name} in {city} already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create office
        office = Office.objects.create(
            name=name,
            department=department,
            city=city,
            state=state,
            address=address,
            pincode=pincode or '000000',
            phone=phone or '0000000000',
            email=email or f'{city.lower()}.{department.name.lower().replace(" ", "")}@municipal.gov.in',
            office_hours=office_hours,
            is_active=True
        )
        
        serializer = OfficeSerializer(office)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': f'Failed to create office: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics based on user role"""
    user = request.user
    stats = {}
    
    if user.user_type == 'CITIZEN':
        # Show all system complaints for citizens (not just their own)
        all_complaints = Complaint.objects.filter(is_deleted=False)
        user_complaints = Complaint.objects.filter(user=user, is_deleted=False)
        
        stats = {
            'total_complaints': all_complaints.count(),
            'pending': all_complaints.filter(status__in=['SUBMITTED', 'PENDING', 'FILTERING', 'SORTING']).count(),
            'in_progress': all_complaints.filter(status__in=['ASSIGNED', 'IN_PROGRESS']).count(),
            'completed': all_complaints.filter(status__in=['COMPLETED', 'RESOLVED']).count(),
            'declined': all_complaints.filter(status__in=['DECLINED', 'REJECTED']).count(),
            # Also include personal stats
            'my_complaints': user_complaints.count(),
            'my_pending': user_complaints.filter(status__in=['SUBMITTED', 'PENDING', 'FILTERING', 'SORTING']).count(),
            'my_in_progress': user_complaints.filter(status__in=['ASSIGNED', 'IN_PROGRESS']).count(),
            'my_completed': user_complaints.filter(status__in=['COMPLETED', 'RESOLVED']).count(),
        }
    
    elif user.user_type == 'DEPT_ADMIN' and hasattr(user, 'departmentadminprofile'):
        profile = user.departmentadminprofile
        dept_complaints = Complaint.objects.filter(
            department=profile.department,
            city__icontains=profile.city,
            is_deleted=False
        )
        stats = {
            'total_complaints': dept_complaints.count(),
            'new_complaints': dept_complaints.filter(status='PENDING').count(),
            'assigned': dept_complaints.filter(status='ASSIGNED').count(),
            'in_progress': dept_complaints.filter(status='IN_PROGRESS').count(),
            'completed': dept_complaints.filter(status='COMPLETED').count(),
            'rejected': dept_complaints.filter(status='REJECTED').count(),
        }
    
    elif user.user_type in ['ADMIN', 'SUB_ADMIN']:
        all_complaints = Complaint.objects.filter(is_deleted=False)
        stats = {
            'total_complaints': all_complaints.count(),
            'pending': all_complaints.filter(status='PENDING').count(),
            'assigned': all_complaints.filter(status='ASSIGNED').count(),
            'in_progress': all_complaints.filter(status='IN_PROGRESS').count(),
            'completed': all_complaints.filter(status='COMPLETED').count(),
            'rejected': all_complaints.filter(status='REJECTED').count(),
            'declined': all_complaints.filter(status='DECLINED').count(),
        }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def complaint_logs(request, pk):
    """Get complaint history logs"""
    complaint = get_object_or_404(Complaint, pk=pk)
    logs = ComplaintLog.objects.filter(complaint=complaint).order_by('-timestamp')
    serializer = ComplaintLogSerializer(logs, many=True)
    return Response(serializer.data)
