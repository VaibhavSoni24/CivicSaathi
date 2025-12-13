# 🚀 Civic Saathi - Quick Start Guide

## Overview
Civic Saathi is a modern dark-themed complaint management system for Urban Local Bodies (ULBs) in India.

## Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- PostgreSQL (already configured with Supabase)

## Quick Setup (Automated)

### Option 1: Run Setup Script
```powershell
.\setup.ps1
```

This will automatically:
- Create Python virtual environment
- Install all dependencies
- Run database migrations
- Prompt for admin account creation
- Set up frontend environment

### Option 2: Manual Setup

#### Backend Setup

1. **Create and activate virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Install dependencies**
```powershell
pip install -r requirements.txt
```

3. **Run migrations**
```powershell
python manage.py makemigrations
python manage.py migrate
```

4. **Initialize departments and categories**
```powershell
python manage.py init_data
```

5. **Create admin account**
```powershell
python manage.py createsuperuser
```

6. **Start Django server**
```powershell
python manage.py runserver
```

#### Frontend Setup

1. **Navigate to frontend**
```powershell
cd frontend
```

2. **Install dependencies**
```powershell
npm install
```

3. **Create .env.local**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

4. **Start Next.js server**
```powershell
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Django Admin**: http://localhost:8000/admin

## Default User Roles

### Admin (Root Authority)
- Username: (created via createsuperuser)
- Access: Full system control
- Dashboard: /admin/dashboard

### Citizens
- Register at: http://localhost:3000/register
- Access: Submit and track complaints
- Dashboard: /dashboard

### Department Admins & Sub-Admins
- Created via Django Admin panel
- Access: Department-specific management
- Dashboard: /department/dashboard

## First Steps

### 1. Create Admin Account
```powershell
python manage.py createsuperuser
```
Enter username, email, and password when prompted.

### 2. Initialize Departments
```powershell
python manage.py init_data
```
This creates:
- 4 Sub-Admin categories
- 14 Departments
- 20+ Complaint categories

### 3. Access Django Admin
1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Verify departments and categories are created

### 4. Register as Citizen
1. Go to http://localhost:3000
2. Click "Get Started"
3. Fill registration form
4. Login and start using the system

## User Roles Structure

```
Admin (Root Authority)
├── Sub-Admin (Core Civic)
│   ├── PWD Department Admin
│   ├── SWM Department Admin
│   ├── Health Department Admin
│   ├── Electrical Department Admin
│   ├── Water Supply Department Admin
│   └── Drainage Department Admin
├── Sub-Admin (Monitoring & Compliance)
│   ├── Sanitation Department Admin
│   ├── Enforcement Department Admin
│   └── Animal Husbandry Department Admin
├── Sub-Admin (Admin, Workforce & Tech)
│   ├── HR Department Admin
│   ├── IT Department Admin
│   └── Finance Department Admin
└── Sub-Admin (Special Programs)
    ├── Swachh Bharat Mission Admin
    └── Smart City SPV Admin
```

## Creating Department Admins

### Via Django Admin Panel

1. Go to http://localhost:8000/admin
2. Navigate to "Custom Users"
3. Click "Add Custom User"
4. Fill in details:
   - Username: `dept_pwd_jaipur`
   - Password: Set secure password
   - User type: Select "Department Admin"
   - City: Jaipur
   - State: Rajasthan
5. Save user
6. Navigate to "Department Admin Profiles"
7. Create profile linking user to department

### Via Django Shell
```python
python manage.py shell

from civic_saathi.models import CustomUser, Department, DepartmentAdminProfile

# Create user
user = CustomUser.objects.create_user(
    username='dept_pwd_jaipur',
    email='pwd.jaipur@civic.gov.in',
    password='securepassword',
    user_type='DEPT_ADMIN',
    city='Jaipur',
    state='Rajasthan'
)

# Get department
dept = Department.objects.get(name__icontains='Public Works')

# Create profile
profile = DepartmentAdminProfile.objects.create(
    user=user,
    department=dept,
    city='Jaipur',
    state='Rajasthan'
)
```

## Testing the System

### Test Citizen Flow

1. **Register as citizen**
   - URL: http://localhost:3000/register
   - Fill all required fields

2. **Submit complaint**
   - Click "New Complaint"
   - Fill form with description (min 20 chars)
   - Upload photo
   - Select category
   - Submit

3. **Track complaint**
   - View in "My Complaints"
   - Check status updates
   - View logs

4. **Upvote complaints**
   - Browse "All Complaints"
   - Upvote existing issues

### Test Department Admin Flow

1. **Login as department admin**
   - URL: http://localhost:3000/login
   - Use department admin credentials

2. **View complaints**
   - See all complaints for your department and city
   - Filter by status

3. **Process complaint**
   - Verify complaint is genuine
   - Assign to worker
   - Update status
   - Mark as completed with photo

## Troubleshooting

### Backend Issues

**Error: No module named 'civic_saathi'**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1
# Reinstall requirements
pip install -r requirements.txt
```

**Error: Database connection failed**
```
# Check settings.py database configuration
# Supabase credentials should be correct
```

**Error: Migration conflicts**
```powershell
python manage.py migrate --fake civic_saathi zero
python manage.py migrate civic_saathi
```

### Frontend Issues

**Error: Cannot find module**
```powershell
cd frontend
npm install
```

**Error: API connection refused**
```
# Ensure backend is running on port 8000
# Check .env.local has correct API URL
```

**Error: 401 Unauthorized**
```
# Clear browser localStorage
# Re-login to get fresh token
```

## Development Tips

### Adding New Department
1. Create via Django Admin or shell
2. Link to appropriate Sub-Admin category
3. Create complaint categories for it
4. Create department admin users

### Adding New Complaint Category
1. Go to Django Admin
2. Navigate to "Complaint Categories"
3. Add category with name and department
4. It will auto-appear in frontend dropdown

### Customizing Theme
- Edit: `frontend/styles/globals.css`
- Modify CSS variables under `:root`
- Colors, spacing, and typography defined there

### API Testing
Use tools like Postman or curl:
```powershell
# Login
curl -X POST http://localhost:8000/api/auth/login/ `
  -H "Content-Type: application/json" `
  -d '{"username":"testuser","password":"testpass"}'

# Get complaints (with token)
curl -X GET http://localhost:8000/api/complaints/all/ `
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## Production Deployment

### Backend
1. Set `DEBUG = False` in settings.py
2. Configure proper `SECRET_KEY`
3. Update `ALLOWED_HOSTS`
4. Set up production database
5. Configure static files serving
6. Use gunicorn or uwsgi

### Frontend
1. Run `npm run build`
2. Deploy to Vercel, Netlify, or custom server
3. Update API URL in environment variables

## Support

For issues or questions:
- Check Django logs: Terminal running `manage.py runserver`
- Check Next.js logs: Terminal running `npm run dev`
- Review browser console for frontend errors
- Check network tab for API request failures

## Next Steps

1. ✅ Complete setup
2. ✅ Create admin account
3. ✅ Initialize departments
4. ✅ Register test citizen account
5. ✅ Submit test complaint
6. ✅ Create department admin accounts
7. ✅ Test full workflow
8. 🎉 Deploy to production!

---

**Happy Building! 🚀**
