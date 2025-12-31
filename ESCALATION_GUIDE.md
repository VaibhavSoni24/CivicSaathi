# SLA-Based Escalation System - Setup and Usage Guide

## Overview

The Municipal Governance System now includes a comprehensive **SLA (Service Level Agreement) based escalation system** that automatically escalates complaints when they are not resolved within the specified timeframe.

## Key Features

### 1. **Timer-Based Escalation**
- Complaints are automatically monitored based on their SLA configuration
- If not resolved within the escalation timeframe, complaints are automatically escalated to senior officers
- The system identifies who didn't complete the task and notifies all relevant parties

### 2. **Email Notifications**
- **Citizen**: Notified when complaint is registered, status changes, or escalated
- **Worker**: Notified when assigned a task; warned when approaching deadline; notified if escalated due to delay
- **Officer**: Notified of new complaints, escalations, and SLA warnings
- **Senior Officer**: Notified when complaints are escalated with full context

### 3. **SLA Configuration**
- Customizable SLA timings per complaint category
- Two key metrics:
  - **Resolution Hours**: Expected time to resolve
  - **Escalation Hours**: Time before auto-escalation if not resolved

### 4. **Audit Trail**
- Complete history of all escalations
- Immutable complaint logs tracking every status change
- Performance metrics for workers and officers

## Installation and Setup

### Step 1: Run Migrations

```bash
python manage.py migrate
```

This creates the new `SLAConfig` table and updates existing models.

### Step 2: Create Default SLA Configurations

```bash
python manage.py create_sla_configs
```

This command creates default SLA configurations for all existing complaint categories:

- **Critical** (Pothole, Streetlight, Water, Electricity): 12-24 hours escalation
- **Regular** (Garbage, Sanitation, Drainage): 24-48 hours escalation
- **Low Priority** (Parks, Buildings): 72 hours escalation

### Step 3: Configure Email Settings

Add these settings to your environment variables or `settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password for Gmail
DEFAULT_FROM_EMAIL = 'noreply@municipal.gov'
SITE_URL = 'http://localhost:8000'
```

**For Gmail Users:**
1. Enable 2-Step Verification on your Google Account
2. Go to Security → App Passwords
3. Generate an App Password for "Mail"
4. Use the 16-character password in `EMAIL_HOST_PASSWORD`

### Step 4: Test Email Configuration

```bash
python manage.py test_email your-email@example.com
```

This sends a test email to verify your configuration is working.

### Step 5: Set Up Auto-Escalation (Cron Job)

The auto-escalation command should run periodically. Set up a cron job or task scheduler:

#### On Linux/Mac (Crontab)

```bash
crontab -e
```

Add this line to run every hour:

```
0 * * * * cd /path/to/project && /path/to/venv/bin/python manage.py auto_escalate >> /var/log/municipal_escalation.log 2>&1
```

#### On Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, Repeat every 1 hour
4. Action: Start a Program
   - Program: `python.exe` (full path to your Python)
   - Arguments: `manage.py auto_escalate`
   - Start in: Your project directory

#### Testing Auto-Escalation (Dry Run)

```bash
python manage.py auto_escalate --dry-run
```

This shows what would be escalated without actually doing it.

## How It Works

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  1. COMPLAINT FILED                                          │
│     - Citizen files complaint                                │
│     - System assigns to department                           │
│     - SLA timer starts                                       │
│     - Email sent to citizen & officer                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. OFFICER ASSIGNS TO WORKER                                │
│     - Officer reviews and assigns                            │
│     - Worker receives email notification                     │
│     - SLA timer continues                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. WORKER PROCESSES (Within SLA Time)                       │
│     ├─ Worker marks status: IN_PROGRESS                      │
│     ├─ Citizen receives status update email                  │
│     └─ Worker completes and marks: RESOLVED                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. IF SLA EXCEEDED (Auto-Escalation Triggered)              │
│     ├─ System identifies complaint exceeded deadline         │
│     ├─ Creates escalation record                             │
│     ├─ Identifies responsible worker/officer                 │
│     ├─ Escalates to senior officer                           │
│     └─ Sends notifications to:                               │
│         • Senior officer (with full context)                 │
│         • Citizen (complaint escalated)                      │
│         • Worker (performance notice)                        │
│         • Previous officer (FYI)                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. SENIOR OFFICER REVIEW                                    │
│     - Reviews escalated complaint                            │
│     - Can reassign or take direct action                     │
│     - Priority automatically increased                       │
└─────────────────────────────────────────────────────────────┘
```

### Escalation Logic

The auto-escalation system checks:

1. **Time Elapsed**: Calculates hours since complaint creation
2. **SLA Deadline**: Compares with category's `escalation_hours`
3. **Status**: Only escalates if not resolved/completed
4. **Responsible Party**: Identifies who was assigned but didn't complete

When escalating:
- Creates `ComplaintEscalation` record with reason
- Updates complaint status to `PENDING` (for reassignment)
- Increases priority (max: 3 - Critical)
- Creates audit log entry
- Sends email to all relevant parties
- **Specifically identifies** the worker/officer who didn't complete the task

### Email Notifications

#### 1. Complaint Registered
- **To**: Citizen + Department Officers
- **When**: Immediately after complaint is filed
- **Contains**: Tracking ID, description, assigned department

#### 2. Worker Assignment
- **To**: Assigned Worker
- **When**: Officer assigns complaint to worker
- **Contains**: Task details, location, priority, deadline indication

#### 3. Status Updates
- **To**: Citizen
- **When**: Any status change (PENDING → IN_PROGRESS → RESOLVED)
- **Contains**: New status, estimated completion

#### 4. SLA Warning (2 hours before deadline)
- **To**: Worker + Supervising Officer
- **When**: Complaint approaching deadline
- **Contains**: Time remaining, urgency indicator

#### 5. Escalation Alert
- **To**: Senior Officer + Citizen + Previous Worker
- **When**: SLA exceeded
- **Contains**:
  - Senior Officer: Full complaint context, who didn't complete it, urgency
  - Citizen: Reassurance that issue is being prioritized
  - Worker: Performance notice about the delay

## Admin Interface

### New Admin Sections

#### 1. SLA Configurations (`/admin/civic_saathi/slaconfig/`)
- View all category-wise SLA settings
- Edit resolution and escalation hours
- Color-coded indicators (Strict/Standard/Relaxed)

#### 2. Complaint List (Enhanced)
- **SLA Indicator Column**: Shows time remaining or overdue status
  - 🔥 Red: < 2 hours or overdue
  - ⏰ Orange: < 6 hours
  - ✓ Green: > 6 hours
- **Priority Badge**: Color-coded (Green/Orange/Red)
- **Status Badge**: Color-coded by status type

#### 3. Complaint Detail (Enhanced Tabs)
- **Escalations Tab**: Inline view of all escalations
  - Who escalated (from/to)
  - Reason (includes who didn't complete)
  - Timestamp
- **Logs Tab**: Complete audit trail (read-only)

#### 4. Escalations List (`/admin/civic_saathi/complaintescalation/`)
- View all escalations system-wide
- Filter by date, department
- Links directly to complaint
- Shows reason including responsible party

### Admin Actions

#### Bulk Actions
1. **Escalate Selected Complaints**
   - Manually escalate multiple complaints
   - Finds senior officer automatically
   - Sends all notifications

2. **Mark as Spam**
   - Flag and reject spam complaints

3. **Assign to Me**
   - Self-assign complaints (for officers)

## Management Commands Reference

### `auto_escalate`
Run auto-escalation check

```bash
# Normal run
python manage.py auto_escalate

# Dry run (test without making changes)
python manage.py auto_escalate --dry-run

# Custom warning threshold (default: 2 hours)
python manage.py auto_escalate --warning-threshold 4
```

### `create_sla_configs`
Create default SLA configurations

```bash
python manage.py create_sla_configs
```

### `test_email`
Test email configuration

```bash
python manage.py test_email recipient@example.com
```

## Customization

### Adjusting SLA Timings

1. Go to Admin → SLA Configurations
2. Click on a category
3. Edit:
   - **Resolution Hours**: Expected completion time
   - **Escalation Hours**: Auto-escalation threshold
4. Save

**Recommended Values:**
- Emergency services: 12-24 hours
- Infrastructure: 24-48 hours
- Maintenance: 48-72 hours
- Cosmetic issues: 72-120 hours

### Customizing Email Templates

Edit `civic_saathi/email_service.py` to customize email content:

```python
def send_escalation_email(escalation):
    # Customize message content here
    message = f"""
    Your custom message...
    """
```

### Changing Escalation Logic

Edit `civic_saathi/management/commands/auto_escalate.py`:

```python
def _find_senior_officer(self, complaint):
    # Customize how senior officers are selected
    # Current: Least loaded officer in same department
    # You can change to: Most experienced, specific role, etc.
```

## Monitoring and Reports

### Dashboard Metrics (Admin Panel)

- Total complaints pending
- Complaints approaching SLA deadline
- Escalations in last 24 hours
- Average resolution time by department
- Worker performance (completion rate, on-time %)

### Log Analysis

All escalations are logged with:
- Reason (includes who didn't complete)
- Time exceeded
- Previous assignee
- New assignee

Query escalations:

```python
from civic_saathi.models import ComplaintEscalation, ComplaintLog

# Recent escalations
recent = ComplaintEscalation.objects.filter(
    escalated_at__gte=timezone.now() - timedelta(days=7)
).select_related('complaint', 'escalated_from', 'escalated_to')

# Complaints with multiple escalations
from django.db.models import Count
frequent = Complaint.objects.annotate(
    escalation_count=Count('escalations')
).filter(escalation_count__gt=1)
```

## Troubleshooting

### Emails Not Sending

1. Check email configuration: `python manage.py test_email test@example.com`
2. Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
3. For Gmail: Use App Password, not regular password
4. Check firewall/antivirus blocking port 587
5. In development, use console backend: `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`

### Auto-Escalation Not Running

1. Verify cron job is set up: `crontab -l` (Linux) or Task Scheduler (Windows)
2. Check log files for errors
3. Test manually: `python manage.py auto_escalate`
4. Ensure SLA configs exist: `python manage.py create_sla_configs`

### SLA Not Appearing in Admin

1. Run migrations: `python manage.py migrate`
2. Create configs: `python manage.py create_sla_configs`
3. Clear browser cache
4. Check category has SLA: Admin → Complaint Categories

## Best Practices

1. **Set Realistic SLAs**: Don't make deadlines too tight
2. **Monitor Regularly**: Check escalations dashboard weekly
3. **Train Staff**: Ensure workers understand the importance of timely updates
4. **Regular Backups**: Escalation and log data is valuable for analysis
5. **Review SLAs Quarterly**: Adjust based on actual performance data
6. **Test Email System**: Monthly test to ensure notifications are working

## API Integration (Future)

The escalation system is designed to work with mobile apps and external systems:

```python
# Get complaint SLA status
GET /api/complaints/{id}/sla-status/

# Response
{
    "hours_elapsed": 15.5,
    "hours_until_escalation": 8.5,
    "sla_status": "warning",  # ok, warning, critical, overdue
    "escalation_count": 0
}
```

## Support

For issues or questions:
1. Check this documentation
2. Review logs: `civic_saathi/management/commands/auto_escalate.py` output
3. Check admin panel: Admin → Complaint Logs
4. Contact: akshatjain1678@gmail.com

---

**Version**: 1.0  
**Last Updated**: December 31, 2025  
**Author**: Akshat Jain
