from rest_framework.permissions import BasePermission


class IsApprovedUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_approved)
