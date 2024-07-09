from rest_framework.permissions import BasePermission
import core.exception.permissions as exception


class IsApprovedUser(BasePermission):
    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.is_approved):
            raise exception.IsNotApprovedUserError()

        return True


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_staff):
            raise exception.IsNotAdminUSerError()

        return True
