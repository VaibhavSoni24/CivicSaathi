from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
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
    Department, SubAdminCategory, Worker, WorkerAttendance, DepartmentAttendance
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    ComplaintSerializer, ComplaintCreateSerializer, ComplaintUpdateSerializer,
    ComplaintLogSerializer, ComplaintVoteSerializer, DepartmentSerializer,
    SubAdminCategorySerializer, ComplaintCategorySerializer,
    WorkerSerializer, WorkerAttendanceSerializer, DepartmentAttendanceSerializer
)
from .filter_system import ComplaintFilterSystem, ComplaintSortingSystem, ComplaintAssignmentSystem
from .permissions import IsAdmin, IsSubAdmin, IsDepartmentAdmin, IsCitizen


# -------------------------
# Helper Functions
# -------------------------
def get_action_user(request):
    """Get the user for logging actions, handling admin mock users"""
    if hasattr(request.user, 'is_admin') and request.user.is_admin:
        # Admin user is a mock object, return None for logging
        return None
    return request.user


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
        
        queryset = Complaint.objects.filter(
            is_deleted=False,
            filter_passed=True
        )
        
        # If admin, return all complaints without filtering
        if is_admin:
            return queryset.order_by('-created_at')
        
        # For regular users, filter by location
        user = self.request.user if self.request.user.is_authenticated else None
        if user:
            city = self.request.query_params.get('city', user.city)
            state = self.request.query_params.get('state', user.state)
        else:
            city = self.request.query_params.get('city')
            state = self.request.query_params.get('state')
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        return queryset.annotate(
            vote_count=Count('votes')
        ).order_by('-priority', '-upvote_count', '-created_at')
    
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
@permission_classes([IsAuthenticated])
def assign_to_worker(request, pk):
    """Assign complaint to worker"""
    complaint = get_object_or_404(Complaint, pk=pk)
    worker_id = request.data.get('worker_id')
    
    if not worker_id:
        return Response({'error': 'Worker ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    worker = get_object_or_404(Worker, pk=worker_id)
    
    # Update complaint
    old_status = complaint.status
    complaint.current_worker = worker
    complaint.status = 'ASSIGNED'
    complaint.save()
    
    # Log the action
    ComplaintLog.objects.create(
        complaint=complaint,
        action_by=get_action_user(request),
        note=f"Assigned to worker {worker.user.username}",
        old_status=old_status,
        new_status='ASSIGNED',
        new_assignee=worker.user.username
    )
    
    return Response({'message': 'Complaint assigned successfully'})


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
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics based on user role"""
    user = request.user
    stats = {}
    
    if user.user_type == 'CITIZEN':
        stats = {
            'total_complaints': Complaint.objects.filter(user=user, is_deleted=False).count(),
            'pending': Complaint.objects.filter(user=user, status='PENDING', is_deleted=False).count(),
            'in_progress': Complaint.objects.filter(user=user, status__in=['ASSIGNED', 'IN_PROGRESS'], is_deleted=False).count(),
            'completed': Complaint.objects.filter(user=user, status='COMPLETED', is_deleted=False).count(),
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
