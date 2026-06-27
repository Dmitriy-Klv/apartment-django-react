from rest_framework.permissions import BasePermission

from apps.users.models import UserRole


class IsLessor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.LESSOR


class IsTenant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.TENANT
