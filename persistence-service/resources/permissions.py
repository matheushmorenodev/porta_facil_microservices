# -----------------------------------------------------------------------------
# ARQUIVO: resources/permissions.py (NOVO ARQUIVO!)
# DESCRIÇÃO: Permissões customizadas baseadas em headers HTTP.
# -----------------------------------------------------------------------------
from rest_framework.permissions import BasePermission
from profiles.models import ActorUser

class HasRole(BasePermission):
    """
    Permite acesso apenas se o usuário tiver um dos papéis (roles) especificados.
    Lê o papel do usuário a partir de um header HTTP (ex: X-User-Role).
    """
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        user_role = request.headers.get('X-User-Role', None)
        return user_role in self.allowed_roles

class IsResourceOwnerOrAdmin(BasePermission):
    """
    Permissão para verificar se o usuário é "dono" do recurso ou tem um papel
    administrativo. Esta classe é mais complexa e pode ser implementada depois.
    """
    def has_object_permission(self, request, view, obj):
        # Lógica para verificar se o request.headers.get('X-User-ID')
        # tem permissão sobre o objeto 'obj'.
        return True # Simplificado por enquanto