from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework import status


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.role == "ADMIN" and request.user.is_staff)


class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "TEACHER":
            return True
        raise PermissionDenied()


class IsStudentOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "STUDENT":
            return True
        raise PermissionDenied()
