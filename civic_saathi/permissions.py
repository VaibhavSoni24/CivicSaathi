from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Check if user is Admin"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'ADMIN'


class IsSubAdmin(permissions.BasePermission):
    """Check if user is Sub-Admin"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'SUB_ADMIN'


class IsDepartmentAdmin(permissions.BasePermission):
    """Check if user is Department Admin"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'DEPT_ADMIN'


class IsCitizen(permissions.BasePermission):
    """Check if user is Citizen"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'CITIZEN'


class IsAdminOrSubAdmin(permissions.BasePermission):
    """Check if user is Admin or Sub-Admin"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['ADMIN', 'SUB_ADMIN']
