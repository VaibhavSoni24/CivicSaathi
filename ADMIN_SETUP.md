# 🔐 Admin Setup & Configuration Guide

## Initial System Setup

### Step 1: Create Root Admin

```powershell
python manage.py createsuperuser
```

**Example:**
- Username: `admin_ulb`
- Email: `admin@civicsaathi.gov.in`
- Password: `[Your Secure Password]`

### Step 2: Initialize Departments and Categories

```powershell
python manage.py init_data
```

This creates:
- 4 Sub-Admin Categories
- 14 Departments
- 20+ Complaint Categories

### Step 3: Access Django Admin

1. Start server: `python manage.py runserver`
2. Go to: http://localhost:8000/admin
3. Login with superuser credentials

## Creating Sub-Admins

### Via Django Admin Panel

1. **Navigate to Custom Users**
   - Click "Add Custom User"

2. **Fill User Details**
   ```
   Username: sub_admin_core_civic
   Email: core.civic@civicsaathi.gov.in
   User Type: Sub-Admin
   City: Jaipur
   State: Rajasthan
   ```

3. **Set Password**
   - Use strong password
   - Note down credentials

4. **Create Sub-Admin Profile**
   - Navigate to "Sub Admin Profiles"
   - Click "Add"
   - Link to created user
   - Select category (e.g., Core Civic Departments)
   - Set city and state

### Recommended Sub-Admin Accounts

```
1. sub_admin_core_civic
   Category: Core Civic Departments
   
2. sub_admin_monitoring
   Category: Monitoring & Compliance
   
3. sub_admin_admin_tech
   Category: Admin, Workforce & Tech
   
4. sub_admin_special_programs
   Category: Special Program Units
```

## Creating Department Admins

### Via Django Shell (Batch Creation)

```python
python manage.py shell

from civic_saathi.models import CustomUser, Department, DepartmentAdminProfile

# List of departments and cities
departments_data = [
    ('Public Works', 'Jaipur', 'Rajasthan', 'dept_pwd_jaipur'),
    ('Solid Waste', 'Jaipur', 'Rajasthan', 'dept_swm_jaipur'),
    ('Health', 'Jaipur', 'Rajasthan', 'dept_health_jaipur'),
    ('Electrical', 'Jaipur', 'Rajasthan', 'dept_elec_jaipur'),
    # Add more as needed
]

for dept_name, city, state, username in departments_data:
    # Create user
    user = CustomUser.objects.create_user(
        username=username,
        email=f'{username}@civic.gov.in',
        password='DefaultPass@123',  # Change immediately
        user_type='DEPT_ADMIN',
        city=city,
        state=state
    )
    
    # Get department
    dept = Department.objects.get(name__icontains=dept_name)
    
    # Create profile
    profile = DepartmentAdminProfile.objects.create(
        user=user,
        department=dept,
        city=city,
        state=state,
        can_login_multiple_devices=True
    )
    
    print(f'✓ Created: {username} for {dept.name}')
```

### Manual Creation via Admin Panel

1. **Create User**
   - Username: `dept_pwd_delhi`
   - Email: `pwd.delhi@civic.gov.in`
   - Password: Set secure password
   - User Type: **Department Admin**
   - City: Delhi
   - State: Delhi

2. **Create Department Admin Profile**
   - User: Select created user
   - Department: Select "Engineering / Public Works"
   - City: Delhi
   - State: Delhi
   - Can login multiple devices: ✓ (checked)

### All 14 Department Admins Template

```
Core Civic Departments:
1. dept_pwd_[city] - Engineering / PWD
2. dept_swm_[city] - Solid Waste Management
3. dept_health_[city] - Health Department
4. dept_electrical_[city] - Electrical / Street Lighting
5. dept_water_[city] - Water Supply & Sewerage
6. dept_drainage_[city] - Drainage / Storm Water

Monitoring & Compliance:
7. dept_sanitation_[city] - Sanitation & Public Toilet
8. dept_enforcement_[city] - Municipal Enforcement
9. dept_animal_[city] - Animal Husbandry

Admin, Workforce & Tech:
10. dept_hr_[city] - Municipal HR
11. dept_it_[city] - IT / e-Governance
12. dept_finance_[city] - Finance & Accounts

Special Programs:
13. dept_swachh_[city] - Swachh Bharat Mission
14. dept_smartcity_[city] - Smart City SPV
```

## Setting Up Attendance System

### For Each Department-City Combination

```python
from civic_saathi.models import Department, DepartmentAttendance
from django.contrib.auth.hashers import make_password

dept = Department.objects.get(name__icontains='Public Works')

attendance_system = DepartmentAttendance.objects.create(
    department=dept,
    city='Jaipur',
    access_password=make_password('pwd_jaipur_2024')  # Secure password
)
```

### Password Management

Keep track of attendance passwords:

```
Department | City    | Password
-----------|---------|------------------
PWD        | Jaipur  | pwd_jaipur_2024
SWM        | Jaipur  | swm_jaipur_2024
PWD        | Delhi   | pwd_delhi_2024
...
```

## Creating Workers

### Via Admin Panel

1. **Create Worker User**
   - Username: `worker_pwd_001`
   - User Type: **Worker**
   - City: Jaipur
   - State: Rajasthan

2. **Create Worker Profile**
   - User: Select created user
   - Department: Engineering / PWD
   - Role: Field Worker
   - City: Jaipur
   - State: Rajasthan
   - Joining Date: 2024-01-01
   - Is Active: ✓

### Batch Worker Creation

```python
from civic_saathi.models import CustomUser, Department, Worker
from datetime import date

dept = Department.objects.get(name__icontains='Public Works')

for i in range(1, 11):  # Create 10 workers
    user = CustomUser.objects.create_user(
        username=f'worker_pwd_{i:03d}',
        email=f'worker.pwd.{i}@civic.gov.in',
        password='Worker@123',
        user_type='WORKER',
        city='Jaipur',
        state='Rajasthan'
    )
    
    Worker.objects.create(
        user=user,
        department=dept,
        role='Field Worker',
        city='Jaipur',
        state='Rajasthan',
        joining_date=date.today(),
        is_active=True
    )
    
    print(f'✓ Created: worker_pwd_{i:03d}')
```

## Default Credentials Summary

### Development/Testing

```
Admin (Root):
Username: admin_ulb
Password: [Set during createsuperuser]
Access: Full system

Sub-Admin (Core Civic):
Username: sub_admin_core_civic
Password: CoreCivic@2024
Access: 6 Core departments

Department Admin (PWD Jaipur):
Username: dept_pwd_jaipur
Password: PWD@Jaipur2024
Access: PWD department in Jaipur

Worker (PWD Jaipur):
Username: worker_pwd_001
Password: Worker@123
Access: Assigned work only

Citizen (Test):
Username: test_citizen
Password: Citizen@123
Access: Submit and track complaints
```

### Production

**⚠️ IMPORTANT: Change all default passwords immediately in production!**

Use strong passwords:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Unique for each account
- Stored securely

## User Management Best Practices

### 1. Password Policy
```python
# In settings.py (already configured)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### 2. Regular Audits
- Review user list monthly
- Deactivate inactive users
- Check login logs
- Monitor failed login attempts

### 3. Role Assignment
- Assign minimum required privileges
- Review permissions quarterly
- Document role changes

### 4. Backup Strategy
- Regular database backups
- User data export
- Credential storage (encrypted)

## Testing Admin Accounts

### Test Admin Login
```bash
# Via API
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin_ulb","password":"your_password"}'
```

### Test Department Admin
1. Login at http://localhost:3000/login
2. Should redirect to /department/dashboard
3. Verify department complaints visible
4. Test assigning complaint to worker

### Test Sub-Admin
1. Login at http://localhost:3000/login
2. Should redirect to /admin/dashboard
3. Verify all category departments visible
4. Test deleting spam complaint

## Troubleshooting

### User Can't Login
1. Check user.is_active = True
2. Verify password is correct
3. Check user_type is set
4. Ensure profile exists (for admins)

### Wrong Dashboard Shown
1. Verify user_type value
2. Check profile creation
3. Clear browser cache
4. Check frontend routing logic

### Can't Assign Complaints
1. Verify department match (user dept = complaint dept)
2. Check city match
3. Ensure user has DEPT_ADMIN role
4. Verify worker exists and is active

### Attendance System Issues
1. Check DepartmentAttendance entry exists
2. Verify city and department match
3. Check password hash is correct
4. Ensure worker profile is complete

## Quick Reference Commands

```bash
# Create superuser
python manage.py createsuperuser

# Initialize data
python manage.py init_data

# Django shell
python manage.py shell

# List all users
python manage.py shell
>>> from civic_saathi.models import CustomUser
>>> CustomUser.objects.all().values('username', 'user_type', 'city')

# List all departments
>>> from civic_saathi.models import Department
>>> Department.objects.all().values('name', 'sub_admin_category__name')

# Reset user password
>>> user = CustomUser.objects.get(username='dept_pwd_jaipur')
>>> user.set_password('NewPassword123')
>>> user.save()
```

## Next Steps After Setup

1. ✅ Create all admin accounts
2. ✅ Set up attendance systems
3. ✅ Create worker accounts
4. ✅ Test citizen registration
5. ✅ Submit test complaints
6. ✅ Test full workflow
7. ✅ Document city-specific configurations
8. ✅ Train department admins
9. ✅ Launch system

---

**System Administration Guide Complete! 🎉**
