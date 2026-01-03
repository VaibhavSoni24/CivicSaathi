# 🏛️ CivicSaathi - Municipal Complaint Management System

A comprehensive full-stack web application for managing civic complaints with role-based access control, built with **Django REST Framework** (Backend) and **Next.js** (Frontend).

## ✨ Features

### 👥 Multi-Role System
- **Citizens** - File and track complaints
- **Root Admin (ULB)** - Complete system oversight across all departments
- **Sub-Admins** - Cluster-level management (4 clusters for 14 departments)
- **Department Admins** - Department-specific operations with multi-city support
- **Workers** - Field staff for complaint resolution

### 📋 Complaint Management
- Citizen complaint filing with category selection
- Auto-filtering and sorting system
- Department-wise complaint routing
- Office and worker assignment
- SLA-based escalation system
- Status tracking (Pending, In Progress, Completed, Rejected)
- Upvote system for complaint prioritization
- Real-time complaint logs and history

### 🏢 Administrative Features
- 14 Municipal departments with hierarchical structure
- 42 Offices across multiple cities (Jaipur, Delhi, Mumbai)
- Worker management with role assignments
- Attendance tracking system with bulk operations
- Department-wise statistics and analytics
- Office location management

### 📱 User Features
- User registration with mobile number validation (10 digits, starts with 6-9)
- Unique mobile number constraint
- Complaint history and status tracking
- Dashboard with complaint statistics
- Category-based complaint filtering

### 🔒 Security
- Token-based authentication (Django REST Framework)
- Role-based access control
- Phone number uniqueness validation
- Secure admin authentication

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm
- Windows PowerShell 5.1 (or compatible terminal)

### Backend Setup

1. **Clone and navigate to project**
```powershell
cd CivicSaathi
```

2. **Create and activate virtual environment**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. **Install Python dependencies**
```powershell
pip install -r requirements.txt
```

4. **Apply database migrations**
```powershell
python manage.py migrate
```

5. **Run Django development server**
```powershell
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```powershell
cd frontend
```

2. **Install Node dependencies**
```powershell
npm install
```

3. **Run Next.js development server**
```powershell
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 📁 Project Structure

```
CivicSaathi/
├── civic_saathi/              # Django app
│   ├── models.py             # Database models (User, Complaint, Department, Worker, etc.)
│   ├── serializers.py        # DRF serializers
│   ├── views_api.py          # API views
│   ├── urls.py               # API routes
│   ├── admin.py              # Django admin configuration
│   ├── permissions.py        # Custom permissions
│   ├── filter_system.py      # Complaint filtering logic
│   ├── email_service.py      # Email notifications
│   ├── signals.py            # Django signals
│   ├── migrations/           # Database migrations
│   ├── management/           # Custom management commands
│   │   └── commands/
│   │       └── auto_escalate.py  # Auto-escalation cron job
│   └── templates/            # Django templates
├── municipal/                # Django project settings
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI configuration
├── frontend/                 # Next.js application
│   ├── pages/                # Next.js pages
│   │   ├── index.js          # Landing page
│   │   ├── login.js          # User login
│   │   ├── register.js       # User registration
│   │   ├── dashboard.js      # User dashboard
│   │   ├── complaints/       # Complaint pages
│   │   ├── admin/            # Admin pages
│   │   └── worker/           # Worker pages
│   ├── components/           # Reusable components
│   │   ├── Navbar.js
│   │   ├── AdminNavbar.js
│   │   └── WorkerNavbar.js
│   ├── context/              # React Context (Auth)
│   │   ├── AuthContext.js
│   │   ├── AdminAuthContext.js
│   │   └── WorkerAuthContext.js
│   ├── utils/                # API utilities
│   │   ├── api.js            # Citizen API calls
│   │   ├── adminApi.js       # Admin API calls
│   │   └── workerApi.js      # Worker API calls
│   └── styles/               # CSS styles
├── db.sqlite3                # SQLite database (included for demo)
├── adminCredentials.json     # Admin login credentials
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🗄️ Database Models

### Core Models
- **CustomUser** - Extended user model with roles (Citizen, Admin, Worker)
- **Department** - 14 municipal departments
- **SubAdminCategory** - 4 department clusters
- **Office** - Department offices across cities
- **Worker** - Field workers with department and office assignment
- **Complaint** - Citizen complaints with status tracking
- **ComplaintCategory** - Categories mapped to departments
- **ComplaintLog** - Complaint history and actions
- **ComplaintVote** - Upvote system
- **WorkerAttendance** - Worker attendance records

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/me/` - Current user info
- `POST /api/worker/login/` - Worker login

### Complaints (Citizen)
- `POST /api/complaints/create/` - Create complaint
- `GET /api/complaints/all/` - All public complaints
- `GET /api/complaints/my/` - User's complaints
- `GET /api/complaints/<id>/` - Complaint detail
- `POST /api/complaints/<id>/upvote/` - Upvote complaint
- `GET /api/complaints/<id>/logs/` - Complaint logs

### Admin Operations
- `GET /api/department/complaints/` - Department complaints
- `POST /api/complaints/<id>/verify/` - Verify complaint
- `POST /api/complaints/<id>/assign/` - Assign to worker
- `PUT /api/complaints/<id>/update-status/` - Update status
- `POST /api/complaints/<id>/reject/` - Reject complaint

### Workers
- `GET /api/workers/` - List workers
- `POST /api/workers/create/` - Create worker
- `GET /api/workers/<id>/` - Worker detail
- `PUT /api/workers/<id>/update/` - Update worker
- `GET /api/worker/assignments/` - Worker's assigned complaints
- `POST /api/worker/complaints/<id>/complete/` - Complete complaint

### System
- `GET /api/departments/` - List all departments
- `GET /api/categories/` - Complaint categories
- `GET /api/offices/` - List offices
- `POST /api/offices/create/` - Create office
- `GET /api/dashboard/stats/` - Dashboard statistics

## 🎨 Frontend Pages

### Public Pages
- `/` - Landing page
- `/login` - User login
- `/register` - User registration (with mobile validation)

### User Dashboard
- `/dashboard` - User dashboard with statistics
- `/complaints` - User's complaints
- `/complaints/new` - File new complaint
- `/complaints/[id]` - Complaint details
- `/complaints/all` - Browse all complaints
- `/complaints/status/[status]` - Filter by status

### Admin Portal
- `/admin/login` - Admin login
- `/admin/dashboard` - Admin dashboard
- `/admin/complaints` - Manage complaints
- `/admin/departments` - Department overview
- `/admin/offices` - Manage offices
- `/admin/offices/add` - Add new office
- `/admin/workers` - Manage workers
- `/admin/workers/add` - Add new worker
- `/admin/attendance` - Attendance system
- `/admin/settings` - System settings

### Worker Portal
- `/worker/login` - Worker login
- `/worker/dashboard` - Worker dashboard
- `/worker/assigned` - Assigned complaints
- `/worker/pending` - Pending assignments
- `/worker/completed` - Completed work
- `/worker/overdue` - Overdue complaints

## 🔧 Configuration

### Environment Variables
Create `.env` file in project root:
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Mobile Number Validation
- Exactly 10 digits
- Must start with 6, 7, 8, or 9
- Unique across all users
- Validated on both frontend and backend

## 👨‍💻 Development

### Create Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```powershell
python manage.py createsuperuser
```

### Run Auto-Escalation Command
```powershell
python manage.py auto_escalate
```

### Access Django Admin
Navigate to `http://localhost:8000/admin`

## 📊 Department Structure

### Core Civic Departments
1. Engineering / Public Works Department (PWD – Urban)
2. Solid Waste Management (SWM) Department
3. Health Department (Municipal)
4. Electrical / Street Lighting Department
5. Water Supply & Sewerage Department

### Monitoring & Compliance
6. Property Tax Department
7. Building Plan Department
8. Fire & Emergency Services Department

### Admin & Tech
9. IT & Smart City Department
10. Human Resources Department
11. Finance & Accounts Department

### Special Programs
12. Parks & Horticulture Department
13. Public Relations & Grievance Redressal Department
14. Traffic Management Department

## 🚢 Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in settings
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Set up HTTPS
- [ ] Configure CORS settings
- [ ] Set up email backend for notifications
- [ ] Deploy with gunicorn/uwsgi
- [ ] Use reverse proxy (Nginx/Apache)

## 🛠️ Technologies Used

### Backend
- Django 4.2+
- Django REST Framework
- SQLite (dev) / PostgreSQL (prod)
- Django CORS Headers
- Django Jazzmin (Admin UI)

### Frontend
- Next.js 14
- React 18
- Axios (API calls)
- Context API (State management)

## 📝 License

This project is developed for VGU Hackathon. All rights reserved.

## 🤝 Contributing

This is a hackathon project. For any issues or suggestions, please contact the development team.

## 📧 Support

For support and queries, please refer to the project documentation or contact the admin team.
