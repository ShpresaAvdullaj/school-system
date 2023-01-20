from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework import status


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user and request.user.is_staff)


class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == "TEACHER":
            return True
        raise PermissionDenied()


class IsStudentOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == "STUDENT":
            return True
        raise PermissionDenied()
