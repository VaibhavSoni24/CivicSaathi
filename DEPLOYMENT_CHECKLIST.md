# 🎯 Deployment Checklist

## Pre-Deployment Steps

### 1. Backend Verification
- [ ] All migrations applied successfully
- [ ] Superuser account created
- [ ] Departments and categories initialized (`python manage.py init_data`)
- [ ] Sub-admin accounts created
- [ ] Department admin accounts created (for all cities)
- [ ] Worker accounts created
- [ ] Attendance systems configured (with city passwords)
- [ ] Test complaints submitted and processed
- [ ] API endpoints tested
- [ ] Django admin panel accessible

### 2. Frontend Verification
- [ ] All dependencies installed (`npm install`)
- [ ] Environment variables configured (`.env.local`)
- [ ] Login/logout working
- [ ] Registration working
- [ ] Dashboard loading correctly
- [ ] Complaint submission working
- [ ] File upload functioning
- [ ] Upvote system working
- [ ] All pages accessible
- [ ] Mobile responsive verified

### 3. Integration Testing
- [ ] Citizen can register and login
- [ ] Citizen can submit complaint with photo
- [ ] Filter system validates complaints
- [ ] Complaints auto-route to correct department
- [ ] Department admin can see city complaints
- [ ] Department admin can assign to worker
- [ ] Status updates reflect in real-time
- [ ] Upvote increases priority
- [ ] Completion photos upload successfully
- [ ] Attendance can be marked

### 4. Security Verification
- [ ] All passwords are strong and unique
- [ ] Default passwords changed
- [ ] CORS configured correctly
- [ ] Token authentication working
- [ ] Permission checks verified
- [ ] File upload restrictions tested
- [ ] SQL injection prevention verified
- [ ] XSS protection verified

### 5. Database
- [ ] Backup taken
- [ ] Connection stable
- [ ] Indexes optimized
- [ ] Foreign keys intact
- [ ] Data integrity verified

## Production Deployment

### Backend (Django)

#### 1. Environment Configuration
```python
# settings.py changes for production

DEBUG = False

ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

SECRET_KEY = 'your-new-secure-secret-key-here'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'production_db_name',
        'USER': 'production_db_user',
        'PASSWORD': 'production_db_password',
        'HOST': 'production_db_host',
        'PORT': '5432',
    }
}

# Static and Media
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

#### 2. Deployment Steps
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser (if not exists)
python manage.py createsuperuser

# Initialize data
python manage.py init_data

# Test server
python manage.py check --deploy
```

#### 3. Server Setup (Gunicorn + Nginx)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn municipal.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/your/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Frontend (Next.js)

#### 1. Environment Configuration
```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.your-domain.com/api
```

#### 2. Build and Deploy
```bash
# Build for production
npm run build

# Test production build locally
npm start

# Deploy to Vercel (recommended)
vercel deploy --prod

# Or export static files
npm run build
npm run export
# Upload 'out' directory to static host
```

#### 3. Vercel Deployment
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

## Post-Deployment

### 1. Verification
- [ ] Backend API accessible at production URL
- [ ] Frontend accessible at production URL
- [ ] HTTPS working (SSL certificate)
- [ ] Login working on production
- [ ] Complaint submission working
- [ ] File uploads working
- [ ] Email notifications working (if configured)
- [ ] All user roles tested

### 2. Monitoring Setup
- [ ] Error logging configured
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Database backup scheduled
- [ ] SSL certificate renewal scheduled

### 3. Documentation
- [ ] Production URLs documented
- [ ] Admin credentials stored securely
- [ ] API documentation updated
- [ ] User manual created
- [ ] Training materials prepared

### 4. Training
- [ ] Admin users trained
- [ ] Sub-admin users trained
- [ ] Department admins trained
- [ ] Workers trained
- [ ] Support staff trained

### 5. Communication
- [ ] Announce launch to users
- [ ] Share registration link
- [ ] Provide support contact
- [ ] Create FAQ page
- [ ] Set up helpdesk

## Maintenance Checklist

### Daily
- [ ] Check error logs
- [ ] Monitor system health
- [ ] Review new complaints
- [ ] Check for spam

### Weekly
- [ ] Database backup verification
- [ ] Review user feedback
- [ ] Check system performance
- [ ] Update spam filters if needed

### Monthly
- [ ] User audit (active/inactive)
- [ ] Security review
- [ ] Performance optimization
- [ ] Backup restoration test
- [ ] Update dependencies

### Quarterly
- [ ] Full security audit
- [ ] User satisfaction survey
- [ ] Feature usage analysis
- [ ] Capacity planning
- [ ] Documentation update

## Emergency Procedures

### System Down
1. Check server status
2. Check database connection
3. Check Nginx/Gunicorn logs
4. Restart services
5. Contact hosting provider
6. Communicate with users

### Database Issues
1. Stop accepting new data
2. Restore from latest backup
3. Verify data integrity
4. Resume operations
5. Post-mortem analysis

### Security Breach
1. Immediately disable affected accounts
2. Change all passwords
3. Review access logs
4. Patch vulnerability
5. Notify affected users
6. Document incident

## Support Resources

### Documentation
- README_COMPLETE.md
- QUICKSTART.md
- FEATURES.md
- ADMIN_SETUP.md
- PROJECT_SUMMARY.md

### Contact
- Technical Support: [email]
- Admin Support: [email]
- Emergency: [phone]

### Backup Contacts
- Database Admin: [contact]
- System Admin: [contact]
- Security Team: [contact]

## Performance Benchmarks

### Target Metrics
- [ ] Page load time < 3 seconds
- [ ] API response time < 500ms
- [ ] File upload < 5 seconds
- [ ] 99.9% uptime
- [ ] < 1% error rate

### Monitoring Tools
- [ ] Google Analytics configured
- [ ] Sentry for error tracking
- [ ] New Relic for performance
- [ ] UptimeRobot for availability

## Success Criteria

### Launch Day
- [ ] 0 critical errors
- [ ] All features working
- [ ] Users can register
- [ ] Complaints can be submitted
- [ ] Admins can manage

### First Week
- [ ] 100+ registered users
- [ ] 50+ complaints submitted
- [ ] 90% filter accuracy
- [ ] 80% response rate
- [ ] Positive user feedback

### First Month
- [ ] 1000+ registered users
- [ ] 500+ complaints processed
- [ ] 50+ complaints resolved
- [ ] 95% system uptime
- [ ] < 1% complaint rejection rate

## Sign-Off

- [ ] Technical Lead: _________________ Date: _______
- [ ] Project Manager: ________________ Date: _______
- [ ] Client: _________________________ Date: _______

---

**System Ready for Production! 🚀**
