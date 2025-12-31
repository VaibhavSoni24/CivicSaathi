# Municipal Governance System - Quick Start Guide

## 🎯 Overview

A comprehensive Municipal Governance System with **SLA-based auto-escalation**, complete complaint tracking, and automated notifications. Built with Django + REST API.

## ✨ Key Features

### ✅ Complete Implementation (As Per Detail.md)

- ✅ **SLA-Based Auto-Escalation**: Complaints automatically escalate if not resolved on time
- ✅ **Timer Algorithm**: Tracks time and notifies upper authority about who didn't complete tasks
- ✅ **Multi-Level Hierarchy**: Admin → Sub-Admin → Department Admin → Officer → Worker
- ✅ **Email Notifications**: Automated emails for all complaint lifecycle events
- ✅ **Audit Trail**: Immutable logs tracking every action and status change
- ✅ **Department Management**: 8 departments with 31+ complaint categories
- ✅ **Worker Management**: Attendance tracking, task assignment, performance monitoring
- ✅ **Filter System**: Spam detection and complaint validation
- ✅ **Upvote System**: Community-driven priority adjustment
- ✅ **Office Management**: City-wise department offices
- ✅ **Advanced Admin Interface**: Enhanced Django admin with SLA indicators, color-coded badges

### 🚀 New Features Added

1. **SLA Configuration Model**: Per-category resolution and escalation timings
2. **Auto-Escalation Command**: `python manage.py auto_escalate` with dry-run support
3. **Email Service**: Complete notification system for all events
4. **Django Signals**: Automatic email triggers on complaint events
5. **Enhanced Admin**: SLA indicators, priority badges, bulk actions
6. **Management Commands**: Setup, testing, and automation utilities

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup

```bash
# Navigate to project directory
cd "d:\Hackathons\VGU\Final\Final"

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Run setup script (creates departments, categories, SLAs)
python setup_system.py

# Create superuser
python manage.py createsuperuser
# Username: admin
# Email: admin@municipal.gov
# Password: (your choice)
```

### 3. Configure Email (Optional but Recommended)

Edit `municipal/settings.py` or set environment variables:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Gmail App Password
DEFAULT_FROM_EMAIL = 'noreply@municipal.gov'
```

**For Gmail:**
1. Enable 2-Step Verification
2. Generate App Password: Google Account → Security → App Passwords
3. Use the 16-character password

Test email configuration:
```bash
python manage.py test_email your-email@example.com
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Access:
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: See `Detail.md` for complete API reference

### 5. Set Up Auto-Escalation (Production)

**Option A: Windows Task Scheduler**
1. Open Task Scheduler
2. Create Basic Task → "Municipal Auto-Escalation"
3. Trigger: Daily, Repeat every 1 hour
4. Action: Start a Program
   - Program: `C:\Path\To\venv\Scripts\python.exe`
   - Arguments: `manage.py auto_escalate`
   - Start in: `D:\Hackathons\VGU\Final\Final`

**Option B: Linux Cron Job**
```bash
crontab -e
# Add this line:
0 * * * * cd /path/to/project && /path/to/venv/bin/python manage.py auto_escalate >> /var/log/municipal.log 2>&1
```

**Option C: Test Manually**
```bash
# Dry run (shows what would be escalated)
python manage.py auto_escalate --dry-run

# Actual run
python manage.py auto_escalate
```

## 📁 Project Structure

```
Final/
├── civic_saathi/           # Main app
│   ├── models.py          # Database models (with SLAConfig)
│   ├── admin.py           # Enhanced admin interface
│   ├── views_api.py       # REST API views
│   ├── serializers.py     # API serializers
│   ├── email_service.py   # Email notification system (NEW)
│   ├── signals.py         # Auto-notification triggers (NEW)
│   ├── filter_system.py   # Spam detection
│   ├── permissions.py     # Custom permissions
│   └── management/commands/
│       ├── auto_escalate.py        # Auto-escalation logic (NEW)
│       ├── create_sla_configs.py   # SLA setup (NEW)
│       └── test_email.py           # Email testing (NEW)
│
├── municipal/             # Project settings
│   ├── settings.py       # Config (with email setup)
│   └── urls.py           # URL routing
│
├── setup_system.py       # Quick setup script (NEW)
├── Detail.md            # Complete documentation
├── ESCALATION_GUIDE.md  # Escalation system guide (NEW)
├── README.md            # This file
└── requirements.txt     # Dependencies
```

## 🎮 Usage

### Admin Tasks

1. **Login to Admin**: http://localhost:8000/admin/
2. **Create Officers**: Civic Saathi → Officers → Add Officer
3. **Create Workers**: Civic Saathi → Workers → Add Worker
4. **View SLA Configs**: Civic Saathi → SLA Configurations
5. **Monitor Complaints**: Civic Saathi → Complaints (see SLA indicators)
6. **View Escalations**: Civic Saathi → Complaint Escalations

### API Usage (Citizens)

See `Detail.md` for complete API documentation.

**Quick Example:**
```bash
# Register
POST http://localhost:8000/auth/register/
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure123",
  "confirm_password": "secure123"
}

# Login (get token)
POST http://localhost:8000/auth/login/
{
  "email": "john@example.com",
  "password": "secure123"
}

# File complaint
POST http://localhost:8000/complaints/create/
Authorization: Token <your-token>
{
  "title": "Broken streetlight on Main Road",
  "description": "Streetlight not working for 3 days",
  "location": "Main Road, Sector 5",
  "city": "Mumbai",
  "state": "Maharashtra",
  "category": 9  # Street Light Not Working
}
```

### SLA Monitoring

The system automatically:
1. **Tracks time** since complaint creation
2. **Sends warnings** 2 hours before deadline (to worker & officer)
3. **Auto-escalates** when deadline is exceeded
4. **Notifies everyone**:
   - Senior officer: Full context + who didn't complete
   - Citizen: Reassurance about escalation
   - Worker: Performance notice
   - Previous officer: FYI

### Escalation Workflow

```
Complaint Filed (SLA Timer Starts)
        ↓
Officer Assigns to Worker
        ↓
Time passes... (System monitors)
        ↓
If > SLA Escalation Hours:
    ├─ Create Escalation Record
    ├─ Identify Responsible Party (worker/officer who didn't complete)
    ├─ Find Senior Officer
    ├─ Update Status to PENDING
    ├─ Increase Priority
    └─ Send Emails:
        • Senior Officer: "Complaint escalated from [Worker Name]"
        • Citizen: "Your complaint has been escalated"
        • Worker: "Performance notice: Task not completed"
        • Officer: "FYI: Complaint escalated"
```

## 🔧 Management Commands

| Command | Purpose | Usage |
|---------|---------|-------|
| `auto_escalate` | Run auto-escalation check | `python manage.py auto_escalate [--dry-run]` |
| `create_sla_configs` | Setup default SLA configs | `python manage.py create_sla_configs` |
| `test_email` | Test email configuration | `python manage.py test_email email@example.com` |
| `create_offices` | Create city offices | `python manage.py create_offices` |
| `create_workers` | Create sample workers | `python manage.py create_workers` |
| `init_data` | Initialize test data | `python manage.py init_data` |

## 📊 Admin Features

### Complaint List View
- **SLA Indicator**: Color-coded time remaining
  - 🔥 Red: < 2 hours or overdue
  - ⏰ Orange: < 6 hours  
  - ✓ Green: > 6 hours
- **Priority Badge**: Visual priority levels
- **Status Badge**: Color-coded status
- **Bulk Actions**: Escalate, assign, mark spam

### Complaint Detail View
- **Tabs**: Basic Info, Assignment, Priority, Logs, Escalations
- **Inline Escalations**: See full escalation history
- **Inline Logs**: Complete audit trail

### New Admin Sections
- **SLA Configurations**: Edit resolution/escalation hours
- **Complaint Escalations**: View all escalations with reasons
- **Complaint Logs**: Immutable audit trail

## 🔐 Security & Permissions

- Department-based data isolation
- Officer can only see their department's complaints
- Workers have limited view access
- Audit trail for all actions
- CORS configured for frontend

## 🐛 Troubleshooting

### Email Not Sending

```bash
# Test email config
python manage.py test_email your-email@example.com

# Check settings
# - EMAIL_HOST_USER must be set
# - For Gmail, use App Password (not regular password)
# - Check port 587 is not blocked

# Use console backend for development (no SMTP needed)
# In settings.py:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### SLA Not Showing

```bash
# Ensure migrations are run
python manage.py migrate

# Create SLA configs
python manage.py create_sla_configs

# Check in admin: Civic Saathi → SLA Configurations
```

### Auto-Escalation Not Working

```bash
# Test manually
python manage.py auto_escalate --dry-run

# Check cron job / task scheduler is running
# Check logs for errors
```

## 📚 Documentation

- **Detail.md**: Complete project documentation (models, API, features)
- **ESCALATION_GUIDE.md**: Detailed escalation system guide
- **README.md**: This quick start guide

## 🎓 Learning Resources

1. Start with Admin Panel: http://localhost:8000/admin/
2. Read `Detail.md` for complete system understanding
3. Read `ESCALATION_GUIDE.md` for escalation details
4. Explore API: Try registering → filing complaint → checking status
5. Test escalation: Create complaint with short SLA, wait, run `auto_escalate`

## 🚀 Deployment (Production)

### Environment Variables

```bash
# Required
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:port/dbname

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@municipal.gov
SITE_URL=https://yourdomain.com
```

### Steps

1. **Update settings.py** for production
2. **Setup PostgreSQL** database
3. **Run migrations**: `python manage.py migrate`
4. **Setup system**: `python setup_system.py`
5. **Collect static**: `python manage.py collectstatic`
6. **Setup cron/scheduler** for auto-escalation
7. **Configure HTTPS** and domain
8. **Test thoroughly**

## 🤝 Support

- **Documentation**: See `Detail.md` and `ESCALATION_GUIDE.md`
- **Issues**: Check troubleshooting section above
- **Contact**: akshatjain1678@gmail.com

## ✅ Checklist: Is Everything Implemented?

Based on `Detail.md` requirements:

- ✅ Multi-level admin hierarchy (Admin → Sub-Admin → Dept Admin → Officer → Worker)
- ✅ Department management (8 departments + 31 categories)
- ✅ Complaint lifecycle (Submit → Filter → Sort → Assign → Resolve)
- ✅ **SLA-based escalation with timer algorithm**
- ✅ **Auto-escalation identifying who didn't complete**
- ✅ Email notifications (all events)
- ✅ Worker attendance system
- ✅ Office management (city-wise)
- ✅ Complaint logs (audit trail)
- ✅ Filter system (spam detection)
- ✅ Upvote system (priority adjustment)
- ✅ REST API (complete)
- ✅ Enhanced admin interface
- ✅ Management commands
- ✅ Signals for automation

## 🎉 Quick Win

Run this in sequence to see the complete system in action:

```bash
# 1. Setup
python manage.py migrate
python setup_system.py
python manage.py createsuperuser

# 2. Run server
python manage.py runserver

# 3. In another terminal - test escalation (dry run)
python manage.py auto_escalate --dry-run

# 4. Open admin
# http://localhost:8000/admin/
# Login and explore:
# - Departments (8 created)
# - Complaint Categories (31 created)
# - SLA Configurations (31 created)

# 5. Create test complaint via API or admin
# 6. Wait for SLA to exceed (or manually change created_at in DB)
# 7. Run: python manage.py auto_escalate
# 8. Check Complaint Escalations in admin - see who didn't complete!
```

---

**Version**: 2.0 (With Complete SLA Escalation System)  
**Last Updated**: December 31, 2025  
**Author**: Akshat Jain

**All requirements from Detail.md satisfied! ✨**
