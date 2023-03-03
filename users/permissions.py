from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action or your access token has expired.'
    default_code = 'permission_denied'


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        refresh = RefreshToken.for_user(request.user)
        return bool(request.user.role == "ADMIN" and request.user.is_staff and refresh.blacklist())


class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        refresh = RefreshToken.for_user(request.user)
        if request.user.role == "TEACHER" and refresh.blacklist():
            return True
        raise PermissionDenied()


class IsStudentOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        refresh = RefreshToken.for_user(request.user)
        if request.user.role == "STUDENT" and refresh.blacklist():
            return True
        raise PermissionDenied()
