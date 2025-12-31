# CivicSaathi - Municipal Governance System
## Complete Project Documentation

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [Database Schema](#database-schema)
5. [User Roles & Permissions](#user-roles--permissions)
6. [Core Features](#core-features)
7. [API Documentation](#api-documentation)
8. [Admin Interface](#admin-interface)
9. [Email Notifications](#email-notifications)
10. [UI/UX Design](#uiux-design)
11. [Configuration](#configuration)

---

## 1. Project Overview

**CivicSaathi** is a comprehensive **Municipal Governance System** designed to streamline civic complaint management and municipal operations. The platform connects citizens, municipal officers, and ground workers in a unified ecosystem for efficient problem resolution and public service delivery.

### Purpose
- Enable citizens to report civic issues (potholes, streetlights, sanitation, etc.)
- Facilitate complaint assignment and tracking by municipal officers
- Manage worker attendance, facility inspections, and field operations
- Provide transparency through real-time status updates
- Automate escalation for SLA violations

### Key Benefits
- **For Citizens**: Easy complaint filing, real-time tracking, facility ratings
- **For Officers**: Centralized dashboard, automated assignments, analytics
- **For Workers**: Mobile-friendly attendance marking, task visibility
- **For Administrators**: Complete oversight, performance metrics, data-driven decisions

---

## 2. Technology Stack

### Backend
- **Framework**: Django 5.0.14
- **REST API**: Django REST Framework 3.14+
- **Authentication**: Token-based (DRF Token Authentication)
- **Database**: 
  - Local: SQLite3
  - Production: PostgreSQL (Railway)
- **ORM**: Django ORM

### Frontend
- **Admin Interface**: Django Jazzmin (customized)
- **Home Page**: Custom HTML/CSS/JavaScript with modern animations
- **API Consumer**: REST API for mobile/web clients

### Infrastructure
- **Hosting**: Railway (Platform as a Service)
- **Static Files**: WhiteNoise
- **Email**: Gmail SMTP (configurable)
- **CORS**: django-cors-headers

### Additional Tools
- **Faker**: Demo data generation
- **Pillow**: Image processing
- **dj-database-url**: Database URL configuration
- **gunicorn**: Production WSGI server

---

## 3. System Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  - Django Admin (Jazzmin UI)                                │
│  - REST API Endpoints                                        │
│  - Home Page (Static HTML)                                   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│  - Views (API endpoints)                                     │
│  - Serializers (Data validation)                            │
│  - Middleware (Auto-permissions, CORS)                       │
│  - Email Service (Notifications)                            │
│  - Signals (Automated logging)                              │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  - Django ORM Models                                         │
│  - PostgreSQL / SQLite                                       │
│  - Media Storage (Images)                                    │
└─────────────────────────────────────────────────────────────┘
```

### User Flow

```
CITIZEN → Files Complaint → System Auto-assigns to Department
                                    ↓
                            OFFICER Reviews → Assigns to Worker
                                    ↓
                            WORKER Resolves → Updates Status
                                    ↓
                            CITIZEN Notified → Can Rate/Close
```

---

## 4. Database Schema

### Core Models

#### 4.1 User Management

**User** (Django Built-in)
- `id`: Primary key
- `username`: Unique username
- `email`: Email address
- `first_name`, `last_name`: Name fields
- `password`: Hashed password
- `is_staff`: Admin access flag
- `is_superuser`: Superuser flag
- `date_joined`: Registration timestamp

**Department**
- `id`: Primary key
- `name`: Department name (e.g., "Sanitation", "Roads", "Electricity")
- `description`: Department description

**Officer**
- `id`: Primary key
- `user`: OneToOne → User
- `department`: ForeignKey → Department
- `role`: Role/designation (e.g., "Department Head", "Senior Officer")

**Worker**
- `id`: Primary key
- `user`: OneToOne → User
- `department`: ForeignKey → Department
- `role`: Role (e.g., "Sanitation Worker", "Electrician")
- `address`: Worker's address
- `joining_date`: Date of joining
- `is_active`: Active status

#### 4.2 Complaint Management

**ComplaintCategory**
- `id`: Primary key
- `name`: Category name (e.g., "Pothole", "Streetlight", "Garbage")
- `department`: ForeignKey → Department

**Complaint**
- `id`: Primary key
- `user`: ForeignKey → User (citizen)
- `category`: ForeignKey → ComplaintCategory (optional)
- `department`: ForeignKey → Department (auto-assigned)
- `title`: Complaint title
- `description`: Detailed description
- `location`: Location text
- `latitude`, `longitude`: GPS coordinates (optional)
- `image`: Uploaded image (optional)
- `priority`: Integer (1=Normal, 2=High, 3=Critical)
- `status`: Current status (pending, assigned, in_progress, resolved, closed, escalated)
- `current_officer`: ForeignKey → Officer (assigned officer)
- `current_worker`: ForeignKey → Worker (assigned worker)
- `is_deleted`: Soft delete flag
- `is_spam`: Spam marker
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**ComplaintLog** (Immutable Audit Trail)
- `id`: Primary key
- `complaint`: ForeignKey → Complaint
- `action_by`: ForeignKey → User
- `note`: Action description
- `old_status`, `new_status`: Status transition
- `old_dept`, `new_dept`: Department transfer
- `old_assignee`, `new_assignee`: Assignment changes
- `timestamp`: Log timestamp

**Assignment**
- `id`: Primary key
- `complaint`: ForeignKey → Complaint
- `assigned_to_worker`: ForeignKey → Worker
- `assigned_by_officer`: ForeignKey → Officer
- `status`: Assignment status
- `timestamp`: Assignment time

**ComplaintEscalation**
- `id`: Primary key
- `complaint`: ForeignKey → Complaint
- `escalated_from`: ForeignKey → Officer
- `escalated_to`: ForeignKey → Officer (senior)
- `reason`: Escalation reason
- `escalated_at`: Escalation timestamp

**SLAConfig** (Service Level Agreement)
- `id`: Primary key
- `category`: OneToOne → ComplaintCategory
- `resolution_hours`: Hours to resolve
- `escalation_hours`: Hours before auto-escalation

#### 4.3 Worker Operations

**WorkerAttendance**
- `id`: Primary key
- `worker`: ForeignKey → Worker
- `date`: Attendance date
- `status`: Attendance status (present, absent, half_day, on_leave)
- `check_in`, `check_out`: Time fields
- `location_lat`, `location_lng`: GPS location
- `notes`: Additional notes
- `marked_by`: ForeignKey → User (who marked)

#### 4.4 Facility Management

**Facility**
- `id`: Primary key
- `name`: Facility name
- `facility_type`: Type (public_toilet, govt_building, park, bus_stop, streetlight_zone, other)
- `address`: Location address
- `location_lat`, `location_lng`: GPS coordinates
- `department`: ForeignKey → Department
- `assigned_worker`: ForeignKey → Worker
- `is_active`: Active status
- `created_at`: Creation timestamp

**FacilityRating** (Public Reviews)
- `id`: Primary key
- `facility`: ForeignKey → Facility
- `user`: ForeignKey → User (nullable for anonymous)
- `cleanliness_rating`: Integer (1-5 stars)
- `comment`: Text feedback
- `photo`: Optional image
- `is_anonymous`: Anonymous flag
- `ip_address`: User IP (for verification)
- `is_verified`: Staff verification flag
- `created_at`: Rating timestamp

**FacilityInspection** (Staff Inspections)
- `id`: Primary key
- `facility`: ForeignKey → Facility
- `inspected_by`: ForeignKey → Worker
- `inspection_date`: Inspection timestamp
- `cleanliness_rating`: Staff rating (1-5)
- `functional_status`: Boolean (working/not working)
- `issues_found`: Text description
- `photo`: Inspection photo
- `notes`: Additional notes

**Streetlight**
- `id`: Primary key
- `pole_id`: Unique pole identifier
- `location`: Location text
- `location_lat`, `location_lng`: GPS coordinates
- `ward`: Administrative ward
- `status`: Status (functional, non_functional, under_repair)
- `last_maintenance`: Date of last maintenance
- `assigned_worker`: ForeignKey → Worker
- `department`: ForeignKey → Department

### Entity Relationships

```
Department (1) ──→ (∞) Officer
Department (1) ──→ (∞) Worker
Department (1) ──→ (∞) ComplaintCategory
Department (1) ──→ (∞) Facility

User (1) ──→ (∞) Complaint [as citizen]
User (1) ──→ (1) Officer [staff]
User (1) ──→ (1) Worker [staff]

Complaint (∞) ──→ (1) ComplaintCategory
Complaint (∞) ──→ (1) Department
Complaint (1) ──→ (∞) ComplaintLog
Complaint (1) ──→ (∞) Assignment
Complaint (1) ──→ (∞) ComplaintEscalation

Facility (1) ──→ (∞) FacilityRating
Facility (1) ──→ (∞) FacilityInspection

Worker (1) ──→ (∞) WorkerAttendance
```

---

## 5. User Roles & Permissions

### 5.1 Citizen (Default User)
**Capabilities:**
- Register/login via API
- File complaints with photos
- Track own complaints
- View complaint history
- Rate public facilities
- Update profile

**Permissions:**
- No Django admin access
- API-only access via token authentication

### 5.2 Worker (Ground Staff)
**Capabilities:**
- Login to admin (limited view)
- View assigned complaints
- Update complaint status
- Mark attendance
- Submit facility inspections
- View department data

**Permissions:**
- `is_staff = True`
- Auto-assigned permissions via middleware
- Department-filtered data access

### 5.3 Officer (Department Admin)
**Capabilities:**
- Full admin dashboard access
- Assign complaints to workers
- Transfer complaints between departments
- Escalate to senior officers
- Mark worker attendance
- View analytics
- Manage facility inspections
- Approve/verify public ratings

**Permissions:**
- `is_staff = True`
- Full CRUD on complaints, workers, facilities
- Department-filtered data access

### 5.4 Superuser (System Admin)
**Capabilities:**
- All officer capabilities
- Manage departments
- Create/edit officers and workers
- View all departments
- System configuration
- User management

**Permissions:**
- `is_superuser = True`
- No data filtering

### Permission Middleware
The system uses **AutoStaffPermissionsMiddleware** to automatically grant permissions:
```python
# Auto-assigns permissions on login for staff users
# Data isolation via get_queryset() in admin classes
```

---

## 6. Core Features

### 6.1 Complaint Lifecycle Management

**Filing**
- Citizen files complaint via API
- Optional category selection
- Photo upload support
- GPS location tagging
- Auto-assignment to department

**Assignment**
- Officer reviews pending complaints
- Assigns to appropriate worker
- Sets priority (Normal/High/Critical)
- Sends email notification

**Resolution**
- Worker receives assignment notification
- Updates status: in_progress → resolved
- Adds resolution notes
- Uploads completion photo (optional)

**Escalation**
- Auto-escalation after SLA breach
- Manual escalation by officer
- Notification to senior officer
- Priority re-evaluation

**Closure**
- Citizen confirms resolution
- Or auto-close after X days
- Rating/feedback collection

### 6.2 Worker Management

**Attendance System**
- Daily attendance marking by officer
- GPS location tracking
- Status options: Present, Absent, Half Day, On Leave
- Attendance reports per worker
- Auto-marking absent workers (scheduled job)

**Task Assignment**
- Real-time complaint assignment
- Task prioritization
- Workload distribution
- Performance tracking

### 6.3 Facility Management

**Public Facility Tracking**
- Database of public facilities
- Types: Toilets, Buildings, Parks, Bus Stops, Streetlight Zones
- GPS coordinates
- Assigned maintenance workers

**Citizen Ratings**
- 1-5 star cleanliness ratings
- Text feedback
- Photo uploads
- Anonymous option
- Aggregated average rating

**Staff Inspections**
- Regular inspection scheduling
- Cleanliness assessment
- Functional status reporting
- Issue documentation
- Photo evidence

### 6.4 Automated Notifications

**Email Triggers:**
1. Complaint registered → Citizen + Officer
2. Worker assigned → Worker
3. Status updated → Citizen
4. Complaint escalated → Senior Officer
5. Resolution pending reminder

**Email Features:**
- HTML templates with branding
- Tracking IDs
- Direct action links
- Professional formatting

### 6.5 Analytics & Reporting

**Dashboard Metrics:**
- Total complaints (pending/resolved)
- Department-wise breakdown
- Worker performance
- Average resolution time
- SLA compliance rate
- Facility ratings overview

**Visualizations:**
- Complaint trends
- Category distribution
- Priority breakdown
- Geographic heatmaps

---

## 7. API Documentation

### 7.1 Authentication Endpoints

**Register**
```http
POST /auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure123",
  "confirm_password": "secure123",
  "first_name": "John",
  "last_name": "Doe"
}

Response (201):
{
  "success": true,
  "message": "Registration successful!",
  "data": {
    "user": { "id": 1, "username": "john_doe", ... },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
  }
}
```

**Login**
```http
POST /auth/login/
Content-Type: application/json

{
  "email": "john@example.com",  // or "username"
  "password": "secure123"
}

Response (200):
{
  "success": true,
  "message": "Login successful!",
  "data": {
    "user": { ... },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user_type": "citizen",  // or "officer", "worker"
    "department": null
  }
}
```

**Logout**
```http
POST /auth/logout/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

Response (200):
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Profile**
```http
GET /auth/profile/
Authorization: Token <token>

Response (200):
{
  "success": true,
  "data": {
    "user": { ... },
    "user_type": "citizen",
    "department": null,
    "role": null,
    "stats": {
      "total_complaints": 5,
      "resolved_complaints": 2,
      "pending_complaints": 3
    }
  }
}
```

**Change Password**
```http
POST /auth/change-password/
Authorization: Token <token>
Content-Type: application/json

{
  "old_password": "secure123",
  "new_password": "newsecure456",
  "confirm_password": "newsecure456"
}
```

**Forgot Password (OTP)**
```http
POST /auth/forgot-password/
Content-Type: application/json

{
  "email": "john@example.com"
}

Response (200):
{
  "success": true,
  "message": "OTP sent to email"
}
```

**Verify OTP**
```http
POST /auth/verify-otp/
Content-Type: application/json

{
  "email": "john@example.com",
  "otp": "123456"
}
```

**Reset Password**
```http
POST /auth/reset-password/
Content-Type: application/json

{
  "email": "john@example.com",
  "otp": "123456",
  "new_password": "newsecure789",
  "confirm_password": "newsecure789"
}
```

### 7.2 Complaint Endpoints

**Create Complaint**
```http
POST /complaints/create/
Authorization: Token <token>
Content-Type: multipart/form-data

{
  "title": "Broken streetlight on Main Road",
  "description": "The streetlight near house #45 has been non-functional for 3 days",
  "location": "Main Road, Sector 5",
  "category": 3,  // Category ID
  "latitude": 28.6139,  // optional
  "longitude": 77.2090,  // optional
  "image": <file>,  // optional
  "priority": 2  // 1=Normal, 2=High, 3=Critical
}

Response (201):
{
  "success": true,
  "message": "Complaint filed successfully",
  "data": {
    "complaint": {
      "id": 42,
      "tracking_id": "CMP-2025-00042",
      "title": "...",
      "status": "pending",
      "created_at": "2025-12-31T10:30:00Z"
    }
  }
}
```

**My Complaints**
```http
GET /complaints/
Authorization: Token <token>

Response (200):
{
  "success": true,
  "data": [
    {
      "id": 42,
      "tracking_id": "CMP-2025-00042",
      "title": "Broken streetlight on Main Road",
      "status": "in_progress",
      "priority_display": "High",
      "department": { "id": 2, "name": "Electricity" },
      "created_at_display": "Dec 31, 2025 at 10:30 AM"
    },
    ...
  ]
}
```

**Complaint Detail**
```http
GET /complaints/42/
Authorization: Token <token>

Response (200):
{
  "success": true,
  "data": {
    "id": 42,
    "tracking_id": "CMP-2025-00042",
    "title": "...",
    "description": "...",
    "location": "...",
    "image": "/media/complaints/photo.jpg",
    "status": "in_progress",
    "priority_display": "High",
    "current_worker": {
      "id": 5,
      "name": "Rajesh Kumar",
      "role": "Electrician"
    },
    "category": { ... },
    "department": { ... }
  }
}
```

**Complaint Logs (Timeline)**
```http
GET /complaints/42/logs/
Authorization: Token <token>

Response (200):
{
  "success": true,
  "data": [
    {
      "id": 1,
      "note": "Complaint filed by citizen",
      "old_status": "",
      "new_status": "pending",
      "action_by_name": "John Doe",
      "timestamp_display": "Dec 31, 2025 at 10:30 AM"
    },
    {
      "id": 2,
      "note": "Assigned to worker",
      "new_assignee": "Rajesh Kumar",
      "action_by_name": "Officer Sharma",
      "timestamp_display": "Dec 31, 2025 at 11:00 AM"
    }
  ]
}
```

### 7.3 Category & Department Endpoints

**List Categories**
```http
GET /categories/

Response (200):
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Pothole",
      "department": { "id": 1, "name": "Roads" }
    },
    {
      "id": 2,
      "name": "Garbage Collection",
      "department": { "id": 2, "name": "Sanitation" }
    }
  ]
}
```

**List Departments**
```http
GET /departments/

Response (200):
{
  "success": true,
  "data": [
    { "id": 1, "name": "Roads", "description": "..." },
    { "id": 2, "name": "Sanitation", "description": "..." }
  ]
}
```

### 7.4 Facility Endpoints

**List Facilities**
```http
GET /facilities/
GET /facilities/?type=public_toilet  // Filter by type

Response (200):
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Community Toilet - Sector 5",
      "facility_type": "public_toilet",
      "facility_type_display": "Public Toilet",
      "address": "Sector 5, Near Market",
      "latitude": 28.6139,
      "longitude": 77.2090,
      "average_rating": 4.2,
      "total_ratings": 15,
      "department_name": "Sanitation"
    }
  ]
}
```

**Facility Detail**
```http
GET /facilities/1/

Response (200):
{
  "success": true,
  "data": {
    "facility": { ... },
    "recent_ratings": [
      {
        "id": 10,
        "cleanliness_rating": 5,
        "rating_display": "⭐⭐⭐⭐⭐",
        "comment": "Very clean and well-maintained",
        "user_name": "Anonymous",
        "created_at_display": "Dec 30, 2025"
      }
    ]
  }
}
```

**Rate Facility**
```http
POST /facilities/1/rate/
Authorization: Token <token>
Content-Type: application/json

{
  "cleanliness_rating": 4,
  "comment": "Clean but needs soap dispenser",
  "is_anonymous": false
}

Response (201):
{
  "success": true,
  "message": "Thank you for your rating!",
  "data": { ... }
}
```

**Nearby Facilities**
```http
GET /facilities/nearby/?lat=28.6139&lng=77.2090&radius=5

Response (200):
{
  "success": true,
  "data": [ ... facilities within 5km ... ]
}
```

---

## 8. Admin Interface

### 8.1 Jazzmin UI Customization

**Theme:**
- Color scheme: Green (navbar-success, sidebar-dark-success)
- Icons: Font Awesome
- Layout: Fixed sidebar, horizontal tabs

**Navigation Structure:**
```
Dashboard Overview
├── 📊 Complaints
│   ├── Pending Complaints
│   ├── Escalated Issues
│   ├── Complaint Categories
│   └── SLA Configuration
├── 👥 People
│   ├── Officers
│   ├── Workers
│   └── Attendance
├── 🏛️ Assets
│   ├── Facilities
│   ├── Facility Inspections
│   ├── Facility Ratings
│   └── Streetlights
└── ⚙️ Admin
    ├── Departments
    └── User Management
```

### 8.2 Dashboard Statistics

**Key Metrics:**
- Total complaints (with trend)
- Pending vs. Resolved ratio
- Active workers count
- Today's attendance summary
- Department-wise complaint distribution
- SLA compliance percentage
- Average resolution time
- Critical priority alerts

### 8.3 Complaint Admin Features

**List View:**
- Tracking ID (clickable)
- Title with priority badge
- Department (color-coded)
- Status (with icons)
- Assigned worker
- Age (days since filing)
- Quick action buttons

**Detail View (Tabs):**
1. **Basic Info**: Title, description, location, image
2. **Assignment**: Current officer, worker, department
3. **Priority & SLA**: Priority level, SLA deadline
4. **Logs**: Full audit trail (read-only inline)
5. **Escalations**: Escalation history

**Custom Actions:**
- Assign to worker
- Change status
- Mark as spam
- Escalate to senior
- Bulk status update

### 8.4 Worker Admin Features

**List View:**
- Name with avatar
- Department
- Role
- Today's attendance (color-coded)
- Active tasks count
- Attendance summary (last 30 days)

**Detail View:**
- Basic info
- Attendance history (inline, last 30 days)
- Assigned complaints
- Performance metrics

**Attendance Marking:**
- Custom admin view: `/admin-tools/mark-attendance/`
- Department-filtered worker list
- Bulk attendance marking
- Today's date pre-filled

### 8.5 Facility Admin Features

**Facility Management:**
- Facility list with type icons
- Average rating display
- Total public ratings
- Quick inspection link

**Inspection Logs:**
- Staff inspection history
- Cleanliness trends
- Issue tracking
- Photo gallery

**Public Ratings:**
- Review moderation
- Verification flags
- Anonymous vs. named
- IP-based spam detection

---

## 9. Email Notifications

### 9.1 Email Service Architecture

**Service File:** `civic_saathi/email_service.py`

**Functions:**
1. `send_complaint_registered_email(complaint)` - New complaint notification
2. `send_worker_assignment_email(complaint, worker, officer)` - Assignment alert
3. `send_status_update_email(complaint, old_status, new_status)` - Status change
4. `send_escalation_email(escalation)` - Escalation notification

### 9.2 Email Templates

**Style:**
- HTML with inline CSS
- Responsive design
- Municipal branding colors
- Professional formatting

**Structure:**
```html
┌────────────────────────────┐
│  🏛️ Municipal Portal       │
│  [Notification Type]       │
├────────────────────────────┤
│  Dear [Name],              │
│                            │
│  [Message]                 │
│                            │
│  ╔══════════════════════╗  │
│  ║ Tracking ID: #12345  ║  │
│  ╚══════════════════════╝  │
│                            │
│  Details:                  │
│  • Title: ...              │
│  • Status: ...             │
│  • Priority: ...           │
│                            │
│  [Description box]         │
│                            │
│  Thank you,                │
│  Municipal Team            │
└────────────────────────────┘
```

### 9.3 Gmail SMTP Configuration

**Settings:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'municipal@example.com'
EMAIL_HOST_PASSWORD = 'app_specific_password'  # Not regular password!
```

**App Password Setup:**
1. Enable 2-Step Verification on Google Account
2. Go to Security → App Passwords
3. Generate password for "Mail" + "Windows Computer"
4. Use 16-character password in settings

### 9.4 Notification Triggers

**Complaint Lifecycle:**
```
File → Email to Citizen + Officer
  ↓
Assign → Email to Worker
  ↓
Status Change → Email to Citizen
  ↓
Escalate → Email to Senior Officer
  ↓
Resolve → Email to Citizen (with rating request)
```

---

## 10. UI/UX Design

### 10.1 Home Page

**File:** `templates/home.html`

**Design Features:**
- Animated gradient background
- Floating geometric shapes (CSS animations)
- Glassmorphism effects
- Smooth scroll animations
- Responsive design (mobile-first)

**Sections:**
1. **Hero Section**
   - Large heading with gradient text
   - CTA buttons (Login, Register, File Complaint)
   - Animated background circles

2. **Stats Section**
   - Real-time metrics cards
   - Count-up animations
   - Icon badges

3. **Features Grid**
   - 3-column layout
   - Icon + Title + Description
   - Hover effects

4. **How It Works**
   - 4-step process with numbers
   - Visual timeline
   - Icons for each step

5. **Testimonials**
   - Citizen reviews
   - Star ratings
   - Avatar placeholders

6. **Footer**
   - Contact info
   - Social links
   - Copyright

**Color Scheme:**
```css
--primary: #FF6B6B (Red-Pink)
--primary-dark: #e55555
--secondary: #FFE5E5 (Light Pink)
--accent: #FF8E8E
--background: #FFF5F5
--card: #FFFFFF
--gradient: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 50%, #FFB4B4 100%)
```

**Typography:**
- Font: Poppins (Google Fonts)
- Weights: 300, 400, 500, 600, 700, 800

**Animations:**
```css
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -30px) scale(1.1); }
}

@keyframes slideInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### 10.2 Admin UI (Jazzmin)

**Customizations:**
- Custom site header: "🏛️ Municipal Governance"
- Color theme: Green navbar and sidebar
- Custom dashboard stats widgets
- Reorganized model ordering
- Custom icons (Font Awesome)
- Related modal popups
- Horizontal tabs for changeforms

**Dashboard Widgets:**
- Complaint count (with status breakdown)
- Today's attendance summary
- Recent escalations
- Critical priority alerts
- Department performance chart

### 10.3 Mobile Responsiveness

**Breakpoints:**
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

**Mobile Features:**
- Hamburger menu
- Stacked sections
- Touch-friendly buttons (min 44x44px)
- Optimized images
- Reduced animations

---

## 11. Configuration

### 12.1 Settings Overview

**File:** `municipal/settings.py`

**Key Sections:**

**Security:**
```python
SECRET_KEY = os.environ.get("SECRET_KEY", "default-dev-key")
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = [...]
```

**Database:**
```python
if USE_SQLITE:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', ...}}
else:
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}
```

**Apps:**
```python
INSTALLED_APPS = [
    'civic_saathi',
    'jazzmin',  # Before django.contrib.admin
    'django.contrib.admin',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    ...
]
```

**Middleware:**
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # First
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'civic_saathi.middleware.AutoStaffPermissionsMiddleware',  # Custom
    ...
]
```

**CORS:**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://civicsaathi.vercel.app',
]
CORS_ALLOW_CREDENTIALS = True
```

**REST Framework:**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### 11.2 URL Configuration

**Main URLs:** `municipal/urls.py`
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('civic_saathi.urls')),  # API + Home
]
```

**App URLs:** `civic_saathi/urls.py`
- Home: `/`
- Auth: `/auth/register/`, `/auth/login/`, etc.
- Complaints: `/complaints/`, `/complaints/<id>/`
- Facilities: `/facilities/`, `/facilities/<id>/rate/`
- Admin Tools: `/admin-tools/mark-attendance/`

### 11.3 Management Commands

**Custom Commands:** `civic_saathi/management/commands/`

1. **auto_escalate.py** - Auto-escalate SLA-breached complaints
   ```bash
   python manage.py auto_escalate
   ```
   - Checks complaints exceeding SLA hours
   - Escalates to senior officer
   - Sends email notifications
   - Runs via cron/scheduler

2. **mark_absent_workers.py** - Mark absent workers automatically
   ```bash
   python manage.py mark_absent_workers
   ```
   - Runs daily at end of day
   - Marks workers with no attendance as "absent"

3. **test_email.py** - Test email configuration
   ```bash
   python manage.py test_email user@example.com
   ```

### 11.4 Demo Data

**Script:** `load_demo_data.py`

**Generates:**
- 3 Departments (Roads, Sanitation, Electricity)
- 6 Officers (2 per dept)
- 12 Workers (4 per dept)
- 15 Complaint Categories
- 50 Complaints (various statuses)
- 30 Worker Attendance records
- 10 Facilities
- 20 Facility Ratings
- 5 Streetlights
- Complete user accounts

**Usage:**
```bash
python load_demo_data.py
```

---

## 12. How It Works

### 12.1 Complaint Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CITIZEN ACTIONS                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    File Complaint (API)
                    ├─ Title, Description
                    ├─ Location, Photo
                    ├─ Category (optional)
                    └─ Priority
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  SYSTEM AUTO-PROCESSING                      │
│  1. Save complaint to database                               │
│  2. Auto-assign to department (via category)                 │
│  3. Generate tracking ID (CMP-YYYY-XXXXX)                    │
│  4. Create log entry                                         │
│  5. Send email to citizen + dept officer                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    OFFICER ACTIONS                           │
│  - Reviews pending complaints (admin dashboard)              │
│  - Assigns to appropriate worker                             │
│  - Sets/updates priority                                     │
│  - Can transfer to another department                        │
│  - Can escalate to senior                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    Email to Worker
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    WORKER ACTIONS                            │
│  - Receives assignment notification                          │
│  - Views complaint details (admin)                           │
│  - Updates status to "in_progress"                           │
│  - Completes work                                            │
│  - Updates status to "resolved"                              │
│  - Adds resolution notes                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                 Email to Citizen (Resolved)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CITIZEN VERIFICATION                       │
│  - Views resolution status                                   │
│  - Can add feedback/rating                                   │
│  - System auto-closes after X days                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    SLA MONITORING                            │
│  - Scheduled job checks complaint age                        │
│  - If > SLA hours:                                           │
│    • Auto-escalate to senior officer                         │
│    • Send escalation email                                   │
│    • Update priority to Critical                             │
└─────────────────────────────────────────────────────────────┘
```

### 12.2 Authentication Flow

```
REGISTRATION:
User → /auth/register/ → Validate → Create User → Generate Token → Response

LOGIN:
User → /auth/login/ → Authenticate → Get/Create Token → Response with user_type

API REQUEST:
User → API Endpoint + Token Header → Verify Token → Process Request → Response

LOGOUT:
User → /auth/logout/ + Token → Delete Token → Response
```

### 12.3 Permission System

```
User Login → is_staff? 
              │
              ├─ No → Citizen (API only)
              │
              └─ Yes → Admin Access
                        │
                        ├─ is_superuser? → Full Access
                        │
                        └─ No → Department-filtered
                                 │
                                 ├─ has Officer? → Officer permissions
                                 └─ has Worker? → Worker permissions

AutoStaffPermissionsMiddleware runs on each admin request:
  - Checks user.user_permissions.count()
  - If < 10, assigns all civic_saathi permissions
  - Data isolation via get_queryset() in admin classes
```

---

## 13. Key Technical Decisions

### 13.1 Why Token Authentication?
- **Stateless**: No session management
- **Mobile-friendly**: Easy to implement in mobile apps
- **API-first**: RESTful design
- **Scalable**: Works with load balancers

### 13.2 Why PostgreSQL in Production?
- **Reliability**: ACID compliance
- **Scalability**: Handles concurrent users
- **Features**: JSON fields, full-text search

### 13.3 Why Jazzmin?
- **Modern UI**: Better than default Django admin
- **Customizable**: Easy theme configuration
- **No React/Vue**: Pure Django templates
- **Quick Setup**: Minimal configuration

### 13.4 Why Separate Models for Logs?
- **Audit Trail**: Immutable history
- **Compliance**: Track all changes
- **Debugging**: Easy to trace issues
- **Analytics**: Historical data analysis

### 13.5 Why Middleware for Permissions?
- **DRY Principle**: One place for logic
- **Automatic**: No manual permission assignment
- **Flexible**: Easy to modify rules
- **Performance**: Cached permissions

---

## 14. Future Enhancements

### 14.1 Planned Features
1. **Mobile App** (Flutter/React Native)
   - Native complaint filing
   - Push notifications
   - GPS-based complaint location
   - Photo capture

2. **SMS Notifications**
   - Status updates via SMS
   - Complaint registration confirmation
   - OTP for phone-based auth

3. **GIS Integration**
   - Interactive maps (Leaflet/Mapbox)
   - Heatmap of complaints
   - Worker location tracking
   - Facility proximity search

4. **Advanced Analytics**
   - Power BI/Tableau dashboards
   - Predictive analytics (ML)
   - Complaint trend forecasting
   - Resource optimization

5. **Payment Integration**
   - Citizen fees/fines
   - Online payments (Razorpay/Stripe)
   - Receipt generation

6. **Chatbot**
   - AI-powered support
   - Complaint filing via chat
   - Status inquiry
   - Category suggestion

7. **Multi-language**
   - i18n support
   - Hindi, regional languages
   - RTL support (Urdu)

8. **Document Management**
   - Store NOCs, certificates
   - Digital signatures
   - Version control

### 14.2 Technical Improvements
- Redis caching for performance
- Celery for background tasks
- WebSocket for real-time updates
- GraphQL API option
- Docker containerization
- Kubernetes orchestration
- CI/CD pipeline (GitHub Actions)
- Automated testing (pytest)

---

## 15. Troubleshooting

### Common Issues

**Email Not Sending:**
- Check Gmail App Password (not regular password)
- Ensure 2-Step Verification enabled
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Test with: `python manage.py test_email your@email.com`

**Token Authentication Failing:**
- Ensure `rest_framework.authtoken` in INSTALLED_APPS
- Run: `python manage.py migrate`
- Check Authorization header format: `Token <token>`

**Static Files Not Loading:**
- Run: `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL settings
- Verify WhiteNoise in MIDDLEWARE

**Department Filtering Not Working:**
- Check user has Officer/Worker profile
- Verify get_queryset() in admin classes
- Ensure user is_staff=True

**Database Connection Error:**
- Check DATABASE_URL environment variable
- Verify PostgreSQL credentials
- Ensure dj-database-url installed

---

## 16. Credits & License

**Project:** CivicSaathi - Municipal Governance System

**Developed By:** Akshat Jain (akshatjain1678@gmail.com)

**Technologies:**
- Django 5.0+ (Web framework)
- Django REST Framework (API)
- Jazzmin (Admin UI)
- PostgreSQL (Database)

**License:** Proprietary (Hackathon Project)

**Admin Access:**
- Username: `admin`
- Password: `admin123` (change after login)

---

## Appendix A: API Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/register/` | POST | No | Register new user |
| `/auth/login/` | POST | No | Login and get token |
| `/auth/logout/` | POST | Yes | Invalidate token |
| `/auth/profile/` | GET | Yes | Get user profile |
| `/auth/change-password/` | POST | Yes | Change password |
| `/complaints/` | GET | Yes | List my complaints |
| `/complaints/create/` | POST | Yes | File new complaint |
| `/complaints/<id>/` | GET | Yes | Get complaint detail |
| `/complaints/<id>/logs/` | GET | Yes | Get complaint timeline |
| `/categories/` | GET | No | List complaint categories |
| `/departments/` | GET | No | List departments |
| `/facilities/` | GET | No | List facilities |
| `/facilities/<id>/` | GET | No | Get facility detail |
| `/facilities/<id>/rate/` | POST | Yes | Rate facility |
| `/facilities/nearby/` | GET | No | Find nearby facilities |

---

## Appendix B: Database Schema Diagram

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│     User     │◄────┤   Officer    │      │   Worker     │
└──────────────┘      └──────────────┘      └──────────────┘
       │                     │                     │
       │                     └────────┬────────────┘
       │                              │
       │                       ┌──────────────┐
       │                       │  Department  │
       │                       └──────────────┘
       │                              │
       │                              ▼
       │                    ┌──────────────────┐
       │                    │ComplaintCategory │
       │                    └──────────────────┘
       │                              │
       ▼                              ▼
┌──────────────┐              ┌──────────────┐
│  Complaint   │◄────────────┤  SLAConfig   │
└──────────────┘              └──────────────┘
       │
       ├──────► ┌──────────────┐
       │        │ComplaintLog  │
       │        └──────────────┘
       │
       ├──────► ┌──────────────┐
       │        │ Assignment   │
       │        └──────────────┘
       │
       └──────► ┌──────────────────┐
                │ComplaintEscalation│
                └──────────────────┘

┌──────────────┐      ┌──────────────────┐
│  Facility    │◄────┤ FacilityRating   │
└──────────────┘      └──────────────────┘
       │
       └──────► ┌──────────────────────┐
                │ FacilityInspection   │
                └──────────────────────┘

┌──────────────┐      ┌──────────────────┐
│   Worker     │◄────┤WorkerAttendance  │
└──────────────┘      └──────────────────┘

┌──────────────┐
│ Streetlight  │
└──────────────┘
```

---

**End of Documentation**

Last Updated: December 31, 2025
Version: 1.0
