# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Backend (Django) Issues

#### 1. "ModuleNotFoundError: No module named 'civic_saathi'"

**Problem:** Virtual environment not activated or dependencies not installed.

**Solution:**
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

---

#### 2. "django.db.utils.OperationalError: FATAL: database does not exist"

**Problem:** Database connection issue or wrong credentials.

**Solution:**
```python
# Check settings.py DATABASES configuration
# Verify Supabase credentials are correct
# Test connection:
python manage.py dbshell
```

---

#### 3. "You have unapplied migrations"

**Problem:** Database migrations not applied.

**Solution:**
```powershell
python manage.py makemigrations
python manage.py migrate
```

If conflicts:
```powershell
python manage.py migrate --fake civic_saathi zero
python manage.py migrate civic_saathi
```

---

#### 4. "AUTH_USER_MODEL is not defined"

**Problem:** Custom user model not properly configured.

**Solution:**
Ensure `settings.py` has:
```python
AUTH_USER_MODEL = 'civic_saathi.CustomUser'
```

Then run fresh migrations:
```powershell
python manage.py makemigrations civic_saathi
python manage.py migrate
```

---

#### 5. "Token authentication failed"

**Problem:** Token expired or invalid.

**Solution:**
```powershell
# Clear browser localStorage
# Login again to get fresh token
```

In Django shell:
```python
from rest_framework.authtoken.models import Token
from civic_saathi.models import CustomUser

user = CustomUser.objects.get(username='your_username')
Token.objects.filter(user=user).delete()
token = Token.objects.create(user=user)
print(token.key)
```

---

#### 6. "CORS header 'Access-Control-Allow-Origin' missing"

**Problem:** CORS not configured properly.

**Solution:**
Check `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

---

#### 7. "RuntimeError: Model class doesn't declare explicit app_label"

**Problem:** App not in INSTALLED_APPS.

**Solution:**
Add to `settings.py`:
```python
INSTALLED_APPS = [
    'civic_saathi',  # Should be at top
    ...
]
```

---

### Frontend (Next.js) Issues

#### 1. "Error: Cannot find module"

**Problem:** Dependencies not installed.

**Solution:**
```powershell
cd frontend
rm -rf node_modules
rm package-lock.json
npm install
```

---

#### 2. "Network Error" or "Failed to fetch"

**Problem:** Backend not running or wrong API URL.

**Solution:**
1. Check backend is running: `http://localhost:8000/api`
2. Verify `.env.local` has correct URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```
3. Restart Next.js dev server

---

#### 3. "401 Unauthorized" on every request

**Problem:** Token not being sent or expired.

**Solution:**
1. Check browser localStorage has 'token'
2. Clear localStorage and login again
3. Verify axios interceptor in `utils/api.js`

---

#### 4. "useRouter must be used inside Router context"

**Problem:** Using useRouter outside Next.js pages.

**Solution:**
Only use `useRouter` in page components or wrap in `AuthProvider`.

---

#### 5. Images not loading

**Problem:** Next.js image domains not configured.

**Solution:**
In `next.config.js`:
```javascript
module.exports = {
  images: {
    domains: ['localhost', '127.0.0.1', 'your-backend-domain.com'],
  },
}
```

---

#### 6. "Hydration failed" error

**Problem:** Server and client HTML mismatch.

**Solution:**
- Don't use `localStorage` during initial render
- Use `useEffect` for client-only code
- Check for undefined values

---

#### 7. Styles not applying

**Problem:** CSS import issue or specificity problem.

**Solution:**
1. Verify `_app.js` imports `globals.css`
2. Check CSS syntax
3. Clear Next.js cache:
```powershell
rm -rf .next
npm run dev
```

---

### Integration Issues

#### 1. File upload fails

**Problem:** Wrong Content-Type header or size limit.

**Solution:**
Backend - `settings.py`:
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760
```

Frontend - `api.js`:
```javascript
const formData = new FormData();
formData.append('image', file);
// Don't set Content-Type, let browser set it
```

---

#### 2. Location not detecting

**Problem:** Browser permission or HTTPS required.

**Solution:**
```javascript
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(
    (position) => {
      // Success
    },
    (error) => {
      console.error('Geolocation error:', error);
      // Handle error
    }
  );
} else {
  // Geolocation not supported
}
```

Note: HTTPS required for geolocation in production.

---

#### 3. Status updates not reflecting

**Problem:** Frontend not fetching latest data.

**Solution:**
```javascript
// After status update, refetch data
await updateStatus(id, newStatus);
fetchComplaints(); // Refresh list
```

---

### Database Issues

#### 1. "duplicate key value violates unique constraint"

**Problem:** Trying to create record with existing unique field.

**Solution:**
```python
# Use get_or_create instead of create
obj, created = Model.objects.get_or_create(
    unique_field=value,
    defaults={'other_field': 'value'}
)
```

---

#### 2. "relation does not exist"

**Problem:** Migrations not applied or wrong table name.

**Solution:**
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations  # Check status
```

---

#### 3. Foreign key constraint violation

**Problem:** Referencing non-existent related object.

**Solution:**
```python
# Ensure related object exists first
department = Department.objects.get(id=dept_id)
complaint.department = department
complaint.save()
```

---

### Authentication Issues

#### 1. Can't login after registration

**Problem:** User not activated or wrong credentials.

**Solution:**
```python
# Check user status
from civic_saathi.models import CustomUser
user = CustomUser.objects.get(username='username')
print(user.is_active)  # Should be True
user.is_active = True
user.save()
```

---

#### 2. "Invalid credentials" but password is correct

**Problem:** Case sensitivity or special characters.

**Solution:**
- Usernames are case-sensitive
- Check for extra spaces
- Reset password if needed:
```python
user = CustomUser.objects.get(username='username')
user.set_password('newpassword')
user.save()
```

---

#### 3. Multiple dashboard redirects

**Problem:** Role detection issue.

**Solution:**
Check `AuthContext.js` login function:
```javascript
switch (user.user_type) {
  case 'ADMIN':
  case 'SUB_ADMIN':
    router.push('/admin/dashboard');
    break;
  case 'DEPT_ADMIN':
    router.push('/department/dashboard');
    break;
  // ... etc
}
```

---

### Deployment Issues

#### 1. Static files not loading in production

**Problem:** Static files not collected.

**Solution:**
```powershell
python manage.py collectstatic --noinput
```

Configure Nginx to serve static files.

---

#### 2. 500 Internal Server Error

**Problem:** Check Django logs.

**Solution:**
```powershell
# In production, check error logs
tail -f /var/log/django/error.log

# Or use Django's logging
# Check settings.py LOGGING configuration
```

---

#### 3. Database connection refused

**Problem:** Production database credentials wrong.

**Solution:**
- Verify `settings.py` DATABASES
- Check firewall rules
- Verify SSL requirements
- Test with Django shell

---

## Performance Issues

#### 1. Slow page loads

**Solution:**
- Enable Django query caching
- Optimize database queries (use select_related, prefetch_related)
- Add database indexes
- Use pagination
- Implement Redis caching

---

#### 2. Large file uploads timing out

**Solution:**
Backend - `settings.py`:
```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800
```

Nginx:
```nginx
client_max_body_size 50M;
```

---

## Debugging Tips

### Backend Debugging

1. **Enable Debug Toolbar**
```python
pip install django-debug-toolbar

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'debug_toolbar',
]
```

2. **Use Django Shell**
```powershell
python manage.py shell

# Test queries
from civic_saathi.models import Complaint
complaints = Complaint.objects.all()
print(complaints.query)  # See SQL
```

3. **Check Logs**
```python
import logging
logger = logging.getLogger(__name__)
logger.debug('Debug message')
logger.error('Error message')
```

---

### Frontend Debugging

1. **Browser Console**
- Open DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls

2. **React DevTools**
- Install React Developer Tools extension
- Inspect component state and props

3. **API Testing**
Use browser or Postman:
```javascript
fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'test', password: 'test' })
})
.then(r => r.json())
.then(console.log);
```

---

## Getting Help

### Before Asking for Help

1. ✅ Check error message carefully
2. ✅ Review relevant documentation
3. ✅ Search for similar issues online
4. ✅ Try basic troubleshooting steps
5. ✅ Collect error logs and screenshots

### What to Include

When reporting an issue:
- Exact error message
- Steps to reproduce
- Environment (OS, Python/Node version)
- What you've tried
- Relevant code snippets
- Log files

### Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Stack Overflow**: Tag your questions with django, nextjs, react

---

## Prevention Tips

1. **Always use virtual environment**
2. **Keep dependencies updated**
3. **Write tests**
4. **Use version control (Git)**
5. **Regular backups**
6. **Monitor error logs**
7. **Document custom configurations**
8. **Use environment variables for secrets**

---

**Still having issues? Check the documentation or create an issue with detailed information!**
