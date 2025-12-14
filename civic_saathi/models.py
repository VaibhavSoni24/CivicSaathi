from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# -------------------------
# Custom User Model with Roles
# -------------------------
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('CITIZEN', 'Citizen'),
        ('ADMIN', 'Admin'),
        ('SUB_ADMIN', 'Sub-Admin'),
        ('DEPT_ADMIN', 'Department Admin'),
        ('WORKER', 'Worker'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='CITIZEN')
    phone = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)


# -------------------------
# Sub-Admin Categories
# -------------------------
class SubAdminCategory(models.Model):
    CATEGORY_CHOICES = [
        ('CORE_CIVIC', 'Core Civic Departments'),
        ('MONITORING_COMPLIANCE', 'Monitoring & Compliance Departments'),
        ('ADMIN_WORKFORCE_TECH', 'Admin, Workforce & Tech'),
        ('SPECIAL_PROGRAMS', 'Special Program Units'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


# -------------------------
# Departments (14 departments)
# -------------------------
class Department(models.Model):
    name = models.CharField(max_length=100)
    sub_admin_category = models.ForeignKey(SubAdminCategory, on_delete=models.CASCADE, related_name='departments')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# -------------------------
# Complaint Categories
# (maps problem → department)
# -------------------------
class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.department.name})"


# -------------------------
# Admin Profile (Root Authority)
# -------------------------
class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Admin - {self.user.username}"


# -------------------------
# Sub-Admin Profile
# -------------------------
class SubAdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(SubAdminCategory, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Sub-Admin - {self.user.username} ({self.category.name})"


# -------------------------
# Department Admin Profile
# -------------------------
class DepartmentAdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    can_login_multiple_devices = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Dept Admin - {self.user.username} ({self.department.name})"


# -------------------------
# Office (Department Offices by Location)
# -------------------------
class Office(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='offices')
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('department', 'city')
        ordering = ['city']
    
    def __str__(self):
        return f"{self.department.name} - {self.city} Office"


# -------------------------
# Officers (Dept Admins) - Legacy
# -------------------------
class Officer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default="officer")

    def __str__(self):
        return self.user.username


# -------------------------
# Workers (Ground Staff)
# -------------------------
class Worker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# -------------------------
# Complaint Votes (Upvote System)
# -------------------------
class ComplaintVote(models.Model):
    complaint = models.ForeignKey('Complaint', on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('complaint', 'user')
    
    def __str__(self):
        return f"Vote by {self.user.username} on Complaint {self.complaint.id}"


# -------------------------
# Complaint (Current State)
# -------------------------
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('FILTERING', 'Under Filter Check'),
        ('DECLINED', 'Declined'),
        ('SORTING', 'Being Sorted'),
        ('PENDING', 'Pending Assignment'),
        ('ASSIGNED', 'Assigned to Worker'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # citizen

    category = models.ForeignKey(
        ComplaintCategory,
        on_delete=models.SET_NULL,
        null=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    office = models.ForeignKey(
        'Office',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    image = models.ImageField(upload_to="complaints/", blank=True, null=True)
    
    # Completion proof
    completion_image = models.ImageField(upload_to="complaints/completed/", blank=True, null=True)
    completion_note = models.TextField(blank=True)

    priority = models.PositiveSmallIntegerField(
        default=1,
        help_text="1=Normal, Higher number = Higher priority (based on votes)"
    )
    
    upvote_count = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="SUBMITTED")
    
    # Filter system flags
    filter_checked = models.BooleanField(default=False)
    filter_passed = models.BooleanField(default=False)
    filter_reason = models.TextField(blank=True)
    
    # Sorting system
    sorted = models.BooleanField(default=False)
    
    # Assignment system
    assigned = models.BooleanField(default=False)

    current_officer = models.ForeignKey(
        Officer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complaints"
    )

    current_worker = models.ForeignKey(
        Worker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_work"
    )

    is_deleted = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    is_genuine = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.category and not self.department:
            self.department = self.category.department
        # Update priority based on votes
        self.priority = 1 + (self.upvote_count // 10)  # Every 10 votes increases priority
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.status})"
        

# -------------------------
# Assignment History
# -------------------------
class Assignment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    assigned_to_worker = models.ForeignKey(
        Worker, on_delete=models.SET_NULL, null=True, blank=True
    )
    assigned_by_officer = models.ForeignKey(
        Officer, on_delete=models.SET_NULL, null=True
    )
    status = models.CharField(max_length=50, default="assigned")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assignment for Complaint {self.complaint.id}"


# -------------------------
# Complaint Logs (Immutable History)
# -------------------------
class ComplaintLog(models.Model):
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name="logs"
    )

    action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    note = models.TextField(blank=True)

    old_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50, blank=True)

    old_dept = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="old_logs"
    )

    new_dept = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="new_logs"
    )

    old_assignee = models.CharField(max_length=200, blank=True)
    new_assignee = models.CharField(max_length=200, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log {self.id} - Complaint {self.complaint.id}"
    

class ComplaintEscalation(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    escalated_from = models.ForeignKey(
        Officer, on_delete=models.SET_NULL, null=True, related_name="escalated_from"
    )
    escalated_to = models.ForeignKey(
        Officer, on_delete=models.SET_NULL, null=True, related_name="escalated_to"
    )
    reason = models.CharField(max_length=255)
    escalated_at = models.DateTimeField(auto_now_add=True)


# -------------------------
# Attendance System
# -------------------------
class DepartmentAttendance(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    access_password = models.CharField(max_length=255)  # Unique per city per department
    
    class Meta:
        unique_together = ('department', 'city')
    
    def __str__(self):
        return f"{self.department.name} - {self.city}"


class WorkerAttendance(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
        ('ON_LEAVE', 'On Leave'),
    ], default='ABSENT')
    notes = models.TextField(blank=True)
    marked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ('worker', 'date')
    
    def __str__(self):
        return f"{self.worker.user.username} - {self.date} - {self.status}"
