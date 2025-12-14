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
    
    class Meta:
        model = Office
        fields = '__all__'


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
    category_name = serializers.CharField(source='category.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    office_address = serializers.CharField(source='office.address', read_only=True, allow_null=True)
    upvote_count = serializers.IntegerField(read_only=True)
    user_has_voted = serializers.SerializerMethodField()
    
    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ('user', 'status', 'current_worker', 'current_officer', 
                            'priority', 'upvote_count', 'filter_checked', 'filter_passed',
                            'sorted', 'assigned', 'is_deleted', 'is_spam', 'is_genuine', 'office')
    
    def get_user_has_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ComplaintVote.objects.filter(complaint=obj, user=request.user).exists()
        return False


class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ('title', 'description', 'category', 'location', 'latitude', 
                  'longitude', 'city', 'state', 'image')
    
    def create(self, validated_data):
        validated_data['status'] = 'SUBMITTED'
        return super().create(validated_data)


class ComplaintUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ('status', 'current_worker', 'completion_image', 'completion_note')


class ComplaintLogSerializer(serializers.ModelSerializer):
    action_by_username = serializers.CharField(source='action_by.username', read_only=True)
    
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
    
    class Meta:
        model = Worker
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'phone',
                  'department', 'department_name', 'office', 'office_name', 
                  'role', 'city', 'state', 'joining_date', 'is_active')


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
