# Testing Guide: Civic Saathi Complaint Management System

## System Overview

The system has been enhanced with a comprehensive SLA-based escalation mechanism with timer displays on both frontend and Django admin interfaces.

## What's Been Implemented

### 1. ✅ SLA Escalation System
- **SLA Configuration Model**: Each complaint category has configurable escalation and resolution hours
- **Auto-Escalation Command**: `python manage.py auto_escalate` automatically escalates overdue complaints
- **Email Notifications**: 5 types of email notifications (registration, complaint submission, escalation, etc.)
- **Escalation Hierarchy**: OFFICER → DEPT_ADMIN → SUB_ADMIN → ROOT_ADMIN

### 2. ✅ Dummy Test Data
- **50 Complaints**: Created across all 8 departments and 31 categories
- **10 Test Citizens**: citizen1@example.com through citizen10@example.com (password: "password123")
- **Varied Ages**: Complaints backdated to realistic ages (1h to 7 days) for SLA testing
- **Multiple Statuses**: SUBMITTED, PENDING, ASSIGNED, IN_PROGRESS, RESOLVED, COMPLETED

### 3. ✅ Django Admin UI Enhancements

#### List View (admin/civic_saathi/complaint/)
- **SLA Indicator Column**: Color-coded timer badges
  - 🔴 Red: OVERDUE
  - 🟠 Orange: < 2 hours remaining (CRITICAL)
  - 🟡 Yellow: < 6 hours remaining
  - 🟢 Green: > 6 hours remaining

#### Detail View (admin/civic_saathi/complaint/<id>/change/)
- **Animated Timer Box**: Large prominent display with:
  - Status indicator with emoji (⚠️ OVERDUE / 🔥 URGENT / ⏰ WARNING / ✓ ON TIME)
  - Time Elapsed counter
  - Time Remaining / Overdue By counter
  - SLA Deadline hours
  - Resolution Target hours
  - Priority badge (Normal/High/Critical)
  - Escalation count warning
- **Color-coded backgrounds**:
  - Red gradient with pulse animation for overdue
  - Orange gradient for critical (<2h)
  - Yellow gradient for warning (<6h)
  - Green gradient for on-time

### 4. ✅ Frontend UI Enhancements

#### User Complaint Detail (/complaints/[id])
- **SLA Timer Card**: Displayed prominently below header
  - Same features as admin: elapsed time, remaining time, SLA deadline
  - Responsive grid layout for timer stats
  - Color-coded status indicators
  - Priority badges
  - Escalation warnings

#### Admin Complaint Detail (/admin/complaints/[id])
- **SLA Timer Card**: Consistent design with user interface
  - Full timer information
  - Admin-specific styling
  - Integration with existing admin layout

### 5. ✅ API Enhancements
- **Serializer Update**: Added `sla_timer` field to ComplaintSerializer
- **Timer Calculation**: Backend calculates all timer data:
  ```json
  "sla_timer": {
    "status": "overdue",
    "icon": "⚠️",
    "title": "OVERDUE!",
    "hours_elapsed": 167.0,
    "hours_remaining": 0,
    "hours_overdue": 155.0,
    "escalation_deadline": 12,
    "resolution_deadline": 24,
    "priority": 2,
    "priority_text": "High",
    "escalation_count": 0
  }
  ```

## Test Credentials

### Admin Accounts
Check `adminCredentials.json` for all admin credentials. Key accounts:
- **Root Admin**: root@admin.com
- **Department Admins**: One per department (roads_admin@admin.com, sanitation_admin@admin.com, etc.)

### Test Citizens
All test citizens have the same password: `password123`
- citizen1@example.com
- citizen2@example.com
- citizen3@example.com
- ... up to citizen10@example.com

## How to Test

### 1. Start the Development Servers

#### Backend (Django)
```bash
cd d:\Hackathons\VGU\Final\Final
python manage.py runserver
```
Server runs at: http://127.0.0.1:8000/

#### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Server runs at: http://localhost:3000/

### 2. Test Django Admin Interface

#### Login
1. Go to http://127.0.0.1:8000/admin/
2. Login with root admin: root@admin.com (check adminCredentials.json for password)

#### View Complaints List
1. Navigate to: Civic Saathi → Complaints
2. **Verify**: SLA indicator column shows color-coded status
3. **Look for**: Red ⚠️ OVERDUE badges on old complaints

#### View Complaint Detail
1. Click on any complaint (preferably one marked as overdue)
2. **Verify**: Large animated timer box at top of form
3. **Check**: Timer shows correct elapsed time, remaining time, SLA deadline
4. **Verify**: Color coding:
   - Overdue complaints have red background with pulse animation
   - Recent complaints have green background
5. **Check**: Escalation count warning if complaint was escalated

### 3. Test Frontend User Interface

#### Login as Citizen
1. Go to http://localhost:3000/login
2. Login with: citizen1@example.com / password123

#### View Complaint
1. Navigate to "My Complaints" or "All Complaints"
2. Click on any complaint
3. **Verify**: SLA Timer card displayed prominently below header
4. **Check**: All timer stats visible (elapsed, remaining, SLA, resolution target)
5. **Verify**: Priority badge color (blue=Normal, orange=High, red=Critical)

#### View Different Complaint Statuses
Test complaints with different ages:
- Recent (< 6h): Green background, "On Track"
- Warning (< 6h remaining): Yellow, "Approaching Deadline"
- Critical (< 2h remaining): Orange, "URGENT" with 🔥
- Overdue: Red, "OVERDUE!" with ⚠️

### 4. Test Auto-Escalation

#### Dry Run (Preview without changes)
```bash
python manage.py auto_escalate --dry-run
```
**Expected**: Shows list of complaints that would be escalated

#### Check SLA Status
```bash
python manage.py check_sla
```
**Expected**: Shows first 15 complaints with age, SLA deadline, and overdue status

#### Actual Escalation (Makes changes)
```bash
python manage.py auto_escalate
```
**Expected**:
- Creates escalation records
- Increases priority
- Reassigns to higher authority
- Sends email notifications
- Creates complaint logs

#### Verify Escalation Results
1. Check console for email outputs (SMTP console backend)
2. Go to admin interface
3. View escalated complaint detail
4. **Verify**: "Escalation count" warning appears
5. Check ComplaintLog for escalation action
6. Check ComplaintEscalation model for escalation records

### 5. Test Different Complaint Ages

Use the backdate command to create specific scenarios:
```bash
python manage.py backdate_complaints
```
This randomly assigns ages to all complaints. Run multiple times to get different distributions.

### 6. Test Email Notifications

All emails are currently sent to console (settings.EMAIL_BACKEND = 'console').

**Test scenarios**:
1. Create new complaint → Check console for submission email
2. Run auto_escalate → Check console for escalation emails
3. Verify email includes:
   - Complaint details
   - Timer information
   - Next actions

## Current Test Results

### Database Status
- ✅ 8 Departments
- ✅ 31 Complaint Categories
- ✅ 31 SLA Configurations
- ✅ 50 Test Complaints
- ✅ 10 Test Citizens
- ✅ Multiple Officers per department

### SLA Test Results (from last check)
```
Summary: 8 out of 15 complaints are overdue
```

### Auto-Escalation Test Results
```
Would escalate: 27 complaints
Would warn: 3 complaints
```

## Verification Checklist

### Django Admin
- [ ] Login successful
- [ ] Complaint list shows SLA indicators
- [ ] Complaint detail shows timer box
- [ ] Timer box has correct colors based on status
- [ ] Overdue complaints show red with pulse animation
- [ ] Timer values are accurate (elapsed, remaining, SLA)
- [ ] Escalation count appears if complaint escalated
- [ ] Priority badge shows correct level

### Frontend - User View
- [ ] Citizen login successful
- [ ] Complaint list loads
- [ ] Complaint detail shows timer card
- [ ] Timer card shows all 4 stats (elapsed, remaining, SLA, resolution)
- [ ] Color coding matches status
- [ ] Priority badge visible
- [ ] Escalation warning appears if escalated

### Frontend - Admin View
- [ ] Admin login successful (at /admin/login)
- [ ] Complaint list loads
- [ ] Complaint detail shows timer card
- [ ] Timer displays correctly
- [ ] Can perform admin actions (assign, reassign, complete)

### Auto-Escalation
- [ ] Dry-run command works
- [ ] Shows correct overdue complaints
- [ ] Actual escalation creates records
- [ ] Email notifications sent (check console)
- [ ] ComplaintLog updated
- [ ] Priority increased
- [ ] Officer reassigned to higher authority

## Common Issues & Solutions

### Issue: Timer not showing
**Solution**: Check API response includes `sla_timer` field. Verify complaint has category with SLA config.

### Issue: All complaints show "ON TIME" despite being old
**Solution**: Run `python manage.py backdate_complaints` to set realistic ages.

### Issue: No escalations in dry-run
**Solution**: Check SLA settings are reasonable (not too high). Default is 6-72 hours depending on category.

### Issue: Frontend not connecting to API
**Solution**: 
1. Check Django server is running on port 8000
2. Check CORS settings in settings.py
3. Verify API URLs in frontend/utils/api.js

### Issue: Admin login fails
**Solution**: Check adminCredentials.json for correct passwords. Try root@admin.com first.

## Next Steps

### For Production
1. **Email Setup**: Configure SMTP settings in settings.py for real emails
2. **Scheduled Task**: Set up cron job or Celery to run auto_escalate every hour:
   ```bash
   # Crontab example
   0 * * * * cd /path/to/project && python manage.py auto_escalate
   ```
3. **Real-time Updates**: Consider WebSocket for live timer updates
4. **Mobile Responsive**: Test timer displays on mobile devices
5. **Performance**: Add caching for SLA calculations on high-traffic complaints

### Additional Features to Consider
1. **Email Preferences**: Allow officers to set notification preferences
2. **Escalation History**: Detailed escalation timeline view
3. **SLA Reports**: Dashboard showing department-wise SLA compliance
4. **Timer in Notifications**: Send push notifications when deadline approaching
5. **Bulk Operations**: Bulk escalation for critical situations

## Support Commands

### Check Database
```bash
python manage.py dbshell
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Clear Test Data
```bash
python manage.py flush  # WARNING: Deletes all data!
```

### Populate Fresh Data
```bash
python manage.py init_data
python manage.py create_offices
python manage.py create_workers
python manage.py create_dummy_complaints --count 50
python manage.py backdate_complaints
```

## Screenshots & Visual Verification

### Expected Django Admin Timer Box
```
┌─────────────────────────────────────────────┐
│ ⚠️ COMPLAINT OVERDUE!           🔴 Critical │
│                                             │
│  Time Elapsed  │  Overdue By  │  SLA  │ Res│
│     167.0h     │    155.0h    │  12h  │ 24h│
│                                             │
│ ⚠️ This complaint has been escalated 1 time(s) │
└─────────────────────────────────────────────┘
```

### Expected Frontend Timer Card
```
┌─────────────────────────────────────────────┐
│ 🔥 URGENT: Deadline Approaching  🟠 High    │
│                                             │
│  [Time Elapsed]  [Time Remaining]          │
│      23.5h            2.5h                 │
│                                             │
│  [SLA Deadline]  [Resolution Target]       │
│       24h              48h                 │
└─────────────────────────────────────────────┘
```

## Conclusion

All requested features have been successfully implemented:
1. ✅ 50 dummy complaints across departments
2. ✅ Django admin UI with timer displays
3. ✅ Frontend UI with timer displays for both user and admin
4. ✅ SLA-based escalation algorithm
5. ✅ Timer displays in complaint detail sections
6. ✅ Comprehensive testing tools and documentation

The system is ready for testing and demonstration!
