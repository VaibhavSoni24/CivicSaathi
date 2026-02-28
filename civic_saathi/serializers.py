from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    CustomUser, AdminProfile, SubAdminProfile, DepartmentAdminProfile,
    Department, SubAdminCategory, ComplaintCategory, Complaint, ComplaintLog,
    ComplaintVote, Worker, WorkerAttendance, DepartmentAttendance, Office
)


# -------------------------
# User Serializers
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'phone', 'city', 'state')
        read_only_fields = ('id',)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'confirm_password', 
                  'first_name', 'last_name', 'phone', 'city', 'state')
    
    def validate_phone(self, value):
        """Validate phone number format and uniqueness"""
        if not value:
            raise serializers.ValidationError("Phone number is required")
        
        # Check format: exactly 10 digits, starting with 6, 7, 8, or 9
        import re
        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError(
                "Phone number must be exactly 10 digits and start with 6, 7, 8, or 9"
            )
        
        # Check uniqueness
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "This phone number is already registered. Please use a different number."
            )
        
        return value
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type='CITIZEN',
            phone=validated_data.get('phone', ''),
            city=validated_data.get('city', ''),
            state=validated_data.get('state', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")


# -------------------------
# Department Serializers
# -------------------------
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class SubAdminCategorySerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = SubAdminCategory
        fields = '__all__'


class ComplaintCategorySerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = ComplaintCategory
        fields = '__all__'


class OfficeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    worker_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Office
        fields = '__all__'
    
    def get_worker_count(self, obj):
        return obj.workers.filter(is_active=True).count()


# -------------------------
# Complaint Serializers
# -------------------------
class ComplaintVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintVote
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class ComplaintSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    office_name = serializers.CharField(source='office.name', read_only=True, allow_null=True)
    office_address = serializers.CharField(source='office.address', read_only=True, allow_null=True)
    current_worker_name = serializers.SerializerMethodField()
    upvote_count = serializers.IntegerField(read_only=True)
    user_has_voted = serializers.SerializerMethodField()
    
    # SLA Timer fields
    sla_timer = serializers.SerializerMethodField()

    # Dynamic SLA & Priority Intelligence fields (read-only)
    priority_level_display = serializers.SerializerMethodField()
    emergency_badge = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ('user', 'status', 'current_worker', 'current_officer', 
                            'priority', 'upvote_count', 'filter_checked', 'filter_passed',
                            'sorted', 'assigned', 'is_deleted', 'is_spam', 'is_genuine', 'office',
                            'smart_hash', 'sla_hours', 'priority_level', 'is_emergency')
    
    def get_user_has_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ComplaintVote.objects.filter(complaint=obj, user=request.user).exists()
        return False
    
    def get_current_worker_name(self, obj):
        if obj.current_worker:
            return f"{obj.current_worker.user.first_name} {obj.current_worker.user.last_name}"
        return None
    
    def get_priority_level_display(self, obj):
        labels = {1: 'Minimal', 2: 'Low', 3: 'Medium', 4: 'High', 5: 'Emergency'}
        return labels.get(obj.priority_level, 'Normal')

    def get_emergency_badge(self, obj):
        if obj.is_emergency:
            return {'label': 'EMERGENCY', 'icon': '🚨', 'color': '#dc2626'}
        return None

    def get_sla_timer(self, obj):
        """Calculate SLA timer information for frontend display"""
        from django.utils import timezone
        
        if not obj.category or not hasattr(obj.category, 'sla_config'):
            # Fallback: use AI-determined sla_hours if SLAConfig is absent
            if obj.sla_hours and obj.sla_hours != 48:
                from django.utils import timezone as tz_fb
                h_elapsed = (tz_fb.now() - obj.created_at).total_seconds() / 3600
                h_remaining = obj.sla_hours - h_elapsed
                status_fb = 'overdue' if h_remaining <= 0 else ('critical' if h_remaining <= 2 else ('warning' if h_remaining <= 6 else 'ok'))
                icon_fb = {'overdue': '⚠️', 'critical': '🔥', 'warning': '⏰', 'ok': '✓'}[status_fb]
                priority_map_fb = {1: 'Minimal', 2: 'Low', 3: 'Medium', 4: 'High', 5: 'Emergency'}
                return {
                    'status': status_fb, 'icon': icon_fb, 'title': status_fb.upper(),
                    'hours_elapsed': round(h_elapsed, 1),
                    'hours_remaining': round(max(0, h_remaining), 1),
                    'hours_overdue': round(max(0, -h_remaining), 1),
                    'escalation_deadline': obj.sla_hours,
                    'resolution_deadline': obj.sla_hours,
                    'hours_until_resolution': round(h_remaining, 1),
                    'is_overdue': h_remaining <= 0,
                    'priority': obj.priority,
                    'priority_text': priority_map_fb.get(obj.priority_level, 'Normal'),
                    'priority_level': obj.priority_level,
                    'is_emergency': obj.is_emergency,
                    'sla_hours': obj.sla_hours,
                    'escalation_count': obj.escalations.count(),
                }
            return None
        
        priority_map = {1: 'Minimal', 2: 'Low', 3: 'Medium', 4: 'High', 5: 'Emergency'}
        
        # If complaint is declined or rejected, show declined status with no timer
        if obj.status in ['DECLINED', 'REJECTED']:
            return {
                'status': 'declined',
                'icon': '❌',
                'title': 'DECLINED',
                'hours_elapsed': 0,
                'hours_remaining': 0,
                'hours_overdue': 0,
                'escalation_deadline': obj.category.sla_config.escalation_hours,
                'resolution_deadline': obj.category.sla_config.resolution_hours,
                'hours_until_resolution': 0,
                'is_overdue': False,
                'priority': obj.priority,
                'priority_text': priority_map.get(obj.priority_level, 'Normal'),
                'priority_level': obj.priority_level,
                'is_emergency': obj.is_emergency,
                'sla_hours': obj.sla_hours,
                'escalation_count': obj.escalations.count(),
            }
        
        # If complaint is completed or resolved, show completed status
        if obj.status in ['COMPLETED', 'RESOLVED']:
            # Calculate total time taken
            hours_elapsed = (timezone.now() - obj.created_at).total_seconds() / 3600
            
            return {
                'status': 'completed',
                'icon': '✅',
                'title': 'COMPLETED',
                'hours_elapsed': round(hours_elapsed, 1),
                'hours_remaining': 0,
                'hours_overdue': 0,
                'escalation_deadline': obj.category.sla_config.escalation_hours,
                'resolution_deadline': obj.category.sla_config.resolution_hours,
                'hours_until_resolution': 0,
                'is_overdue': False,
                'priority': obj.priority,
                'priority_text': priority_map.get(obj.priority_level, 'Normal'),
                'priority_level': obj.priority_level,
                'is_emergency': obj.is_emergency,
                'sla_hours': obj.sla_hours,
                'escalation_count': obj.escalations.count(),
            }
        
        sla = obj.category.sla_config
        # Use AI-determined SLA hours when available, otherwise fall back to category config
        effective_sla_hours = obj.sla_hours if (obj.sla_hours and obj.sla_hours != 48) else sla.resolution_hours
        hours_elapsed = (timezone.now() - obj.created_at).total_seconds() / 3600
        hours_until_escalation = effective_sla_hours - hours_elapsed
        hours_until_resolution = sla.resolution_hours - hours_elapsed
        
        # For pending/submitted complaints (not assigned yet)
        if obj.status in ['SUBMITTED', 'PENDING', 'FILTERING', 'SORTING']:
            # Determine status based on time
            if hours_until_escalation <= 0:
                status = 'overdue'
                icon = '⚠️'
                title = 'PENDING - OVERDUE!'
            elif hours_until_escalation <= 2:
                status = 'critical'
                icon = '🔥'
                title = 'PENDING - URGENT'
            elif hours_until_escalation <= 6:
                status = 'warning'
                icon = '⏰'
                title = 'PENDING - Needs Attention'
            else:
                status = 'pending'
                icon = '⏳'
                title = 'PENDING'
        # For in-progress complaints (assigned/being worked on)
        elif obj.status in ['ASSIGNED', 'IN_PROGRESS']:
            # Determine status based on time
            if hours_until_escalation <= 0:
                status = 'overdue'
                icon = '⚠️'
                title = 'IN PROGRESS - OVERDUE!'
            elif hours_until_escalation <= 2:
                status = 'critical'
                icon = '🔥'
                title = 'IN PROGRESS - URGENT'
            elif hours_until_escalation <= 6:
                status = 'warning'
                icon = '⏰'
                title = 'IN PROGRESS - Approaching Deadline'
            else:
                status = 'ok'
                icon = '✓'
                title = 'IN PROGRESS - On Track'
        else:
            # Default fallback
            if hours_until_escalation <= 0:
                status = 'overdue'
                icon = '⚠️'
                title = 'OVERDUE!'
            elif hours_until_escalation <= 2:
                status = 'critical'
                icon = '🔥'
                title = 'URGENT'
            elif hours_until_escalation <= 6:
                status = 'warning'
                icon = '⏰'
                title = 'Approaching Deadline'
            else:
                status = 'ok'
                icon = '✓'
                title = 'On Track'
        
        # Priority text
        priority_map = {1: 'Minimal', 2: 'Low', 3: 'Medium', 4: 'High', 5: 'Emergency'}
        
        return {
            'status': status,
            'icon': icon,
            'title': title,
            'hours_elapsed': round(hours_elapsed, 1),
            'hours_remaining': round(max(0, hours_until_escalation), 1),
            'hours_overdue': round(max(0, -hours_until_escalation), 1),
            'escalation_deadline': effective_sla_hours,
            'resolution_deadline': sla.resolution_hours,
            'hours_until_resolution': round(hours_until_resolution, 1),
            'is_overdue': hours_until_escalation <= 0,
            'priority': obj.priority,
            'priority_text': priority_map.get(obj.priority_level, 'Normal'),
            'priority_level': obj.priority_level,
            'is_emergency': obj.is_emergency,
            'sla_hours': obj.sla_hours,
            'escalation_count': obj.escalations.count(),
        }


class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ('title', 'description', 'department', 'location', 'latitude', 
                  'longitude', 'city', 'state', 'image')
    
    def create(self, validated_data):
        validated_data['status'] = 'SUBMITTED'
        return super().create(validated_data)


class ComplaintUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ('status', 'current_worker', 'completion_image', 'completion_note')


class ComplaintLogSerializer(serializers.ModelSerializer):
    action_by_username = serializers.CharField(source='action_by.username', read_only=True, default='System')
    action = serializers.SerializerMethodField()

    STATUS_LABELS = {
        'SUBMITTED': 'Submitted',
        'FILTERING': 'Under Filter Check',
        'DECLINED': 'Declined',
        'VERIFIED': 'Verified',
        'SORTING': 'Being Sorted',
        'PENDING': 'Pending Assignment',
        'ASSIGNED': 'Assigned to Worker',
        'IN_PROGRESS': 'In Progress',
        'RESOLVED': 'Resolved',
        'COMPLETED': 'Completed',
        'REJECTED': 'Rejected',
    }

    def get_action(self, obj):
        if obj.old_status and obj.new_status and obj.old_status != obj.new_status:
            old_label = self.STATUS_LABELS.get(obj.old_status, obj.old_status.replace('_', ' ').title())
            new_label = self.STATUS_LABELS.get(obj.new_status, obj.new_status.replace('_', ' ').title())
            return f'Status changed: {old_label} → {new_label}'
        if obj.new_assignee:
            return f'Assigned to {obj.new_assignee}'
        if obj.old_assignee and not obj.new_assignee:
            return f'Unassigned from {obj.old_assignee}'
        if obj.note:
            return obj.note
        return 'Updated'
    
    class Meta:
        model = ComplaintLog
        fields = '__all__'


# -------------------------
# Worker & Attendance Serializers
# -------------------------
class WorkerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    city = serializers.CharField(source='user.city', read_only=True)
    state = serializers.CharField(source='user.state', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    office_name = serializers.CharField(source='office.name', read_only=True, allow_null=True)
    
    user = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email,
            'phone': obj.user.phone,
        }
    
    def get_department(self, obj):
        if obj.department:
            return {
                'id': obj.department.id,
                'name': obj.department.name,
            }
        return None
    
    def get_office(self, obj):
        if obj.office:
            return {
                'id': obj.office.id,
                'name': obj.office.name,
            }
        return None
    
    class Meta:
        model = Worker
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'phone',
                  'department', 'department_name', 'office', 'office_name', 
                  'role', 'city', 'state', 'joining_date', 'is_active', 'user')


class WorkerAttendanceSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='worker.user.username', read_only=True)
    
    class Meta:
        model = WorkerAttendance
        fields = '__all__'


class DepartmentAttendanceSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = DepartmentAttendance
        fields = '__all__'
