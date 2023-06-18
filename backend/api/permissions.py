from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Права доступа для Админа.
    Остальным данные доступны только для чтения.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_staff
            or request.method in permissions.SAFE_METHODS
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Права доступа для автора рецепта.
    Остальным данные доступны только для чтения.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.author
            or request.method in permissions.SAFE_METHODS
        )
