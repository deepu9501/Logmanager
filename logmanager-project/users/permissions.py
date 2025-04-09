"""
Custom permissions for the users app.
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission to allow only administrators.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrManager(permissions.BasePermission):
    """
    Permission to allow only administrators or managers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_manager
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow only the owner of the object or administrators.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_admin or 
            request.user.is_manager or 
            obj.id == request.user.id
        ) 