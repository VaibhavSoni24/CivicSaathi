from rest_framework import permissions


def _is_admin_user(user):
    """Return True if the request user is the frontend AdminUser mock object."""
    return getattr(user, 'is_admin', False) is True


def _user_type(user):
    """Safely get user_type; returns '' for AdminUser which has none."""
    return getattr(user, 'user_type', '')


class IsAdmin(permissions.BasePermission):
    """Check if user is Admin (including frontend AdminUser token auth)."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if _is_admin_user(request.user):
            return True
        return _user_type(request.user) == 'ADMIN'


class IsSubAdmin(permissions.BasePermission):
    """Check if user is Sub-Admin"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if _is_admin_user(request.user):
            return True
        return _user_type(request.user) == 'SUB_ADMIN'


class IsDepartmentAdmin(permissions.BasePermission):
    """Check if user is Department Admin"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if _is_admin_user(request.user):
            return True
        return _user_type(request.user) == 'DEPT_ADMIN'


class IsCitizen(permissions.BasePermission):
    """Check if user is Citizen"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return _user_type(request.user) == 'CITIZEN'


class IsAdminOrSubAdmin(permissions.BasePermission):
    """Check if user is Admin or Sub-Admin"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if _is_admin_user(request.user):
            return True
        return _user_type(request.user) in ['ADMIN', 'SUB_ADMIN']


class IsAuthenticatedOrAdmin(permissions.BasePermission):
    """Allow access to authenticated users or frontend admins"""
    def has_permission(self, request, view):
        # Check if this is an admin request (has admin headers)
        if _is_admin_user(getattr(request, 'user', None)):
            return True
        # Otherwise check normal authentication
        return request.user and request.user.is_authenticated
