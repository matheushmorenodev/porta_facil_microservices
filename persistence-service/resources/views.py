# -----------------------------------------------------------------------------
# ARQUIVO: persistence-service/resources/views.py (VERSÃO FINAL E CORRIGIDA)
# -----------------------------------------------------------------------------
from rest_framework import generics, permissions
from rest_framework.permissions import BasePermission
from django.db.models import Q

from persistence_project.utils import get_user_info_from_token


from .models import Room, Department
from .serializers import (
    RoomSerializer, DepartmentSerializer,
    DepartmentCreateUpdateSerializer, RoomCreateUpdateSerializer
)


class HasRole(permissions.BasePermission):
    """
    Permissão customizada que verifica o papel do usuário a partir do token.
    """
    allowed_roles = []

    def has_permission(self, request, view):
        # MUDANÇA: Adicionamos um print para ver TODOS os headers
        print("--- 🕵️ Depurando Permissão HasRole (Etapa Final) 🕵️ ---")
        print(f"HEADERS COMPLETOS RECEBIDOS PELO SERVIÇO:\n{request.headers}")
        
        self.allowed_roles = getattr(view, 'allowed_roles', [])
        print(f"✔️ Roles permitidos para esta view: {self.allowed_roles}")

        user_info = get_user_info_from_token(request)
        if not user_info:
            print("❌ ERRO: Token não encontrado ou inválido na função get_user_info_from_token.")
            # Este print agora é redundante se o de cima funcionar, mas vamos manter por enquanto.
            return False
            
        user_role = user_info.get('role')
        print(f"✔️ Role encontrado no token: '{user_role}' (Tipo: {type(user_role)})")
        
        is_allowed = user_role in self.allowed_roles
        print(f"👉 O usuário tem permissão? {is_allowed}")
        print("------------------------------------------")
        
        return is_allowed
# --- Views de LEITURA ---

class ListAllRoomsAPIView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [HasRole]
    allowed_roles = ['seguranca', 'administrador']

class ListRoomsWithAccessAPIView(generics.ListAPIView):
    serializer_class = RoomSerializer
    def get_queryset(self):
        # MUDANÇA: Lendo o novo header 'X-Claim-User-Id'.
        user_info = get_user_info_from_token(self.request)
        if not user_info:
            return Room.objects.none()
        
        user_id = user_info.get('user_id')
        if not user_id:
            return Room.objects.none()
        return Room.objects.filter(
            Q(admins__user_id=user_id) |
            Q(users__user_id=user_id) |
            Q(department__coordinators__user_id=user_id) |
            Q(special_coordinators__user_id=user_id)
        ).distinct()

class ListAvailableRoomsAPIView(generics.ListAPIView):
    queryset = Room.objects.filter(status=Room.RoomStatusChoices.DISPONIVEL)
    serializer_class = RoomSerializer
    permission_classes = []

# --- Views de ESCRITA (CRUD) ---

class DepartmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    permission_classes = [HasRole]
    allowed_roles = ['administrador']
    def get_serializer_class(self):
        return DepartmentCreateUpdateSerializer if self.request.method == 'POST' else DepartmentSerializer

class DepartmentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    permission_classes = [HasRole]
    allowed_roles = ['administrador']
    def get_serializer_class(self):
        return DepartmentCreateUpdateSerializer if self.request.method in ['PUT', 'PATCH'] else DepartmentSerializer

class RoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    permission_classes = [HasRole]
    allowed_roles = ['administrador', 'coordenador']
    def get_serializer_class(self):
        return RoomCreateUpdateSerializer if self.request.method == 'POST' else RoomSerializer

class RoomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    permission_classes = [HasRole]
    allowed_roles = ['administrador', 'coordenador']
    def get_serializer_class(self):
        return RoomCreateUpdateSerializer if self.request.method in ['PUT', 'PATCH'] else RoomSerializer
