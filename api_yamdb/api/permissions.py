from rest_framework import permissions


class IsAunthOrReadOnly(permissions.BasePermission):
    """Доступ анонимным пользователям только к SAFE запросам."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsSuperOrIsAdminOnly(permissions.BasePermission):
    """Доступ суперюзерам или админам к любым запросам."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_staff
                or request.user.is_admin
            )
        )


class IsSuperIsAdminIsModeratorIsAuthorOnly(permissions.BasePermission):
    """
    Доступ анонимным пользователям только к SAFE запросам.
    Админам, суперюзерам, модераторам и авторам доступны любые запросы.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_staff
                or request.user.is_admin
                or request.user.is_moderator
                or request.user == obj.author
            )
        )
