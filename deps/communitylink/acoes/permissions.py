from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizadorOrReadOnly(BasePermission):
    """
    Permite leitura para qualquer usuário.
    Escrita apenas para usuários do grupo 'Organizadores'.
    """

    def has_permission(self, request, view):
        # Métodos de leitura (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Escrita apenas para organizadores autenticados
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name='Organizadores').exists()
        )

    def has_object_permission(self, request, view, obj):
        # Leitura liberada
        if request.method in SAFE_METHODS:
            return True

        # Só o organizador da ação pode editar/deletar
        return obj.organizador == request.user
    
class IsVoluntarioOrReadOnly(BasePermission):
    """
    Permite leitura para qualquer usuário.
    Escrita apenas para usuários do grupo 'Voluntários'.
    """

    def has_permission(self, request, view):
        # Métodos de leitura (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Escrita apenas para voluntários autenticados
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name='Voluntários').exists()
        )

from rest_framework.permissions import BasePermission, SAFE_METHODS