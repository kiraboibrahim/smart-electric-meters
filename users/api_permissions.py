from rest_framework import permissions


class IsAdminOrSuperAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin() or request.user.is_super_admin()
