"""
Custom authentication backend for admin users
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class AdminTokenAuthentication(BaseAuthentication):
    """
    Custom authentication for admin users.
    Checks for X-Admin-Token and X-Admin-User headers.
    """
    
    def authenticate(self, request):
        admin_token = request.META.get('HTTP_X_ADMIN_TOKEN')
        admin_user = request.META.get('HTTP_X_ADMIN_USER')
        
        if admin_token and admin_user:
            # Admin is authenticated via frontend
            # Return a mock user object
            class AdminUser:
                def __init__(self, admin_data):
                    self.is_authenticated = True
                    self.is_admin = True
                    self.is_active = True  # Required by Django permissions
                    self.is_staff = True
                    self.admin_token = admin_token
                    self.admin_data = admin_data
                    self.id = 'admin'
                    self.username = 'admin'
                    self.pk = 'admin'  # Primary key
                    
                @property
                def is_anonymous(self):
                    return False
            
            return (AdminUser(admin_user), None)
        
        return None
