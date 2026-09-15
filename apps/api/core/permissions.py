from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Permite acesso apenas a usuários com papel de administrador (is_staff=True)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
