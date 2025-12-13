# Civic Saathi - Modern Civic Complaint Management System

A comprehensive dark-themed web application for managing civic complaints across Urban Local Bodies (ULBs) in India.

## 🚀 Features

### User Roles & Access

#### **Citizens**
- Submit complaints with description, photo, category, and location (manual/auto-detection)
- View all complaints in their local area
- Upvote existing complaints instead of creating duplicates
- Track complaint status in real-time
- View complaint history and progress logs

#### **Admin (Root Authority - ULB)**
- Full access to all sub-admin and department admin rights
- Monitor all departments across all cities
- View comprehensive analytics and reports
- Manage system-wide settings

#### **Sub-Admins** (4 Categories)
1. **Core Civic Departments**
2. **Monitoring & Compliance Departments**
3. **Admin, Workforce & Tech**
4. **Special Program Units**

- Oversee multiple departments under their category
- Delete unnecessary/wrong complaints that slip through filters
- Move solved complaints to solved section

#### **Department Admins** (14 Departments)
##### Core Civic Departments:
1. Engineering / Public Works Department (PWD – Urban)
2. Solid Waste Management (SWM) Department
3. Health Department (Municipal)
4. Electrical / Street Lighting Department
5. Water Supply & Sewerage Department
6. Drainage / Storm Water Department

##### Monitoring & Compliance:
7. Sanitation & Public Toilet Department
8. Municipal Enforcement / Vigilance Department
9. Animal Husbandry / Cattle Nuisance Department

##### Admin, Workforce & Tech:
10. Municipal HR / Establishment Department
11. IT / e-Governance Department
12. Finance & Accounts Department

##### Special Program Units:
13. Swachh Bharat Mission (Urban)
14. Smart City SPV

**Features:**
- Multi-device login support
- City-wise complaint management
- Worker assignment and tracking
- Complaint verification and validation
- Status updates with photo proof
- Attendance system access (password-protected per city)

### Intelligent Systems

#### **Filter System**
- AI-powered validation of complaints
- Checks description-photo-category match
- Spam detection
- Automatic approval/rejection

#### **Sorting System**
- Automatic routing to correct department
- Category-based classification
- Priority calculation based on upvotes

#### **Assignment System**
- Location-based assignment (city/district)
- Automatic department routing
- Worker allocation

## 🛠 Tech Stack

### Backend
- **Django** - REST API framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database (Supabase)
- **Custom User Model** - Role-based authentication
- **Token Authentication** - Secure API access

### Frontend
- **Next.js 14** - React framework
- **Pure CSS** - No Tailwind, custom dark theme
- **JavaScript** - No TypeScript
- **Axios** - API communication

## 📦 Installation

### Backend Setup

1. **Clone the repository**
```bash
cd "d:\New"
```

2. **Create virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Configure environment**
The database is already configured in `settings.py` with Supabase PostgreSQL.

5. **Create custom user migrations**
```powershell
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (Admin)**
```powershell
python manage.py createsuperuser
```

7. **Load demo data (optional)**
```powershell
python load_demo_data.py
```

8. **Run the server**
```powershell
python manage.py runserver
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```powershell
cd frontend
```

2. **Install dependencies**
```powershell
npm install
```

3. **Create environment file**
Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

4. **Run development server**
```powershell
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 📁 Project Structure

```
civic-saathi/
├── civic_saathi/              # Django app
│   ├── models.py             # Database models
│   ├── serializers.py        # DRF serializers
│   ├── views_api.py          # API views
│   ├── urls.py               # URL routing
│   ├── permissions.py        # Custom permissions
│   ├── filter_system.py      # Complaint validation
│   └── migrations/           # Database migrations
├── municipal/                # Django project
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL config
│   └── wsgi.py              # WSGI config
├── frontend/                 # Next.js app
│   ├── pages/               # App pages
│   │   ├── _app.js          # App wrapper
│   │   ├── login.js         # Login page
│   │   ├── register.js      # Registration page
│   │   ├── dashboard.js     # User dashboard
│   │   └── complaints/      # Complaint pages
│   ├── components/          # React components
│   │   └── Navbar.js        # Navigation bar
│   ├── context/             # React context
│   │   └── AuthContext.js   # Auth state management
│   ├── utils/               # Utilities
│   │   └── api.js           # API client
│   └── styles/              # CSS styles
│       └── globals.css      # Global dark theme
├── media/                    # Uploaded files
├── requirements.txt         # Python dependencies
└── package.json             # Node dependencies
```

## 🔐 Authentication

### Fixed Admin Credentials
- **Main Admin**: Set during `createsuperuser`
- **Sub-Admins**: One per category (4 total)
- **Department Admins**: One per department (14 total), multi-device login allowed

### User Registration
- Citizens can register via the signup page
- Email and password required
- Auto-assigned 'CITIZEN' role

## 🎨 Dark Theme

The application features a modern, eye-friendly dark theme:
- Primary Background: `#0f0f1e`
- Secondary Background: `#1a1a2e`
- Card Background: `#1f1f35`
- Accent Color: `#4f46e5` (Indigo)
- Success: `#10b981` (Green)
- Warning: `#f59e0b` (Amber)
- Danger: `#ef4444` (Red)

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/me/` - Get current user

### Complaints (Citizen)
- `POST /api/complaints/create/` - Submit complaint
- `GET /api/complaints/my/` - Get user's complaints
- `GET /api/complaints/all/` - Get all area complaints
- `GET /api/complaints/{id}/` - Get complaint detail
- `POST /api/complaints/{id}/upvote/` - Upvote complaint
- `GET /api/complaints/{id}/logs/` - Get complaint history

### Department Admin
- `GET /api/department/complaints/` - Get department complaints
- `POST /api/complaints/{id}/assign/` - Assign to worker
- `POST /api/complaints/{id}/update-status/` - Update status
- `POST /api/complaints/{id}/reject/` - Reject complaint
- `DELETE /api/complaints/{id}/delete/` - Delete complaint (Sub-Admin only)

### Attendance
- `POST /api/attendance/mark/` - Mark worker attendance
- `GET /api/attendance/` - Get attendance records

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics
- `GET /api/categories/` - Get all categories
- `GET /api/departments/` - Get all departments

## 🔄 Complaint Workflow

1. **Submission** → Citizen submits complaint
2. **Filter** → AI validates description-photo-category match
3. **Sort** → Routes to correct department
4. **Assign** → Assigns based on location (city/district)
5. **Verify** → Department admin verifies genuineness
6. **Allocate** → Assigns to field worker
7. **In Progress** → Worker marks as in progress
8. **Complete** → Worker submits completion photo
9. **Resolved** → Admin marks as resolved

## 🎯 Key Features

### For Citizens
✅ Easy complaint submission with photo
✅ Auto-location detection
✅ Upvote system to prioritize issues
✅ Real-time status tracking
✅ View nearby complaints
✅ Prevent duplicate submissions

### For Admins
✅ Comprehensive dashboard
✅ Multi-level access control
✅ Worker management
✅ Attendance tracking
✅ Complaint verification
✅ Performance analytics
✅ City-wise filtering

### Smart Systems
✅ AI-powered spam detection
✅ Auto-categorization
✅ Priority-based sorting
✅ Location-based routing
✅ Progress tracking
✅ Audit logs

## 🚦 Complaint Statuses

- **SUBMITTED** - Just submitted
- **FILTERING** - Under validation
- **DECLINED** - Failed validation
- **SORTING** - Being categorized
- **PENDING** - Awaiting assignment
- **ASSIGNED** - Assigned to worker
- **IN_PROGRESS** - Being worked on
- **RESOLVED** - Work completed
- **COMPLETED** - Verified complete
- **REJECTED** - Not genuine

## 👥 Department Categories

### Sub-Admin Categories:
1. **Core Civic** - Essential infrastructure departments
2. **Monitoring & Compliance** - Oversight and enforcement
3. **Admin, Workforce & Tech** - Support services
4. **Special Programs** - Government initiatives

## 🔒 Security Features

- Token-based authentication
- Role-based access control (RBAC)
- CORS protection
- SQL injection prevention (ORM)
- XSS protection
- CSRF protection
- Secure password hashing

## 📱 Responsive Design

The application is fully responsive and works seamlessly on:
- Desktop computers
- Tablets
- Mobile devices

## 🤝 Contributing

This is a government civic management system. For contributions:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is developed for Urban Local Bodies (ULBs) in India.

## 📞 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Contact the development team

## 🎉 Acknowledgments

- Django & Django REST Framework teams
- Next.js team
- React team
- All contributors

---

**Built with ❤️ for better civic governance in India**
