# -----------------------------------------------------------------------------
# ARQUIVO: persistence-service/resources/serializers.py (VERSÃO ATUALIZADA)
# -----------------------------------------------------------------------------
from rest_framework import serializers
from .models import Department, Room, IOTObject
from profiles.models import Coordinator, Admin, Common

# --- Serializers para LEITURA (Read) ---

class CoordinatorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinator
        fields = ['id', 'user_id'] # Adicionado ID para facilitar a referência

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['user_id']

class CommonProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Common
        fields = ['user_id']

class DepartmentSerializer(serializers.ModelSerializer):
    coordinators = CoordinatorProfileSerializer(many=True, read_only=True)
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'coordinators']

class IOTObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = IOTObject
        fields = ['id', 'mac', 'status', 'description']

class RoomSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    admins = AdminProfileSerializer(many=True, read_only=True)
    users = CommonProfileSerializer(many=True, read_only=True)
    iot_objects = IOTObjectSerializer(many=True, read_only=True)
    # MUDANÇA: Adicionado o campo de coordenadores especiais à resposta.
    special_coordinators = CoordinatorProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        # MUDANÇA: Adicionados os novos campos 'status' e 'special_coordinators'.
        fields = ['id', 'code', 'name', 'status', 'department', 'admins', 'users', 'special_coordinators', 'iot_objects']

# --- Serializers para ESCRITA (Create/Update) ---

class DepartmentCreateUpdateSerializer(serializers.ModelSerializer):
    coordinators_ids = serializers.PrimaryKeyRelatedField(
        queryset=Coordinator.objects.all(), source='coordinators', many=True, write_only=True, required=False
    )
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'coordinators_ids']

class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    users_ids = serializers.PrimaryKeyRelatedField(
        queryset=Common.objects.all(), source='users', many=True, write_only=True, required=False
    )
    admins_ids = serializers.PrimaryKeyRelatedField(
        queryset=Admin.objects.all(), source='admins', many=True, write_only=True, required=False
    )
    # NOVO: Campo para atribuir coordenadores especiais ao criar/atualizar uma sala.
    special_coordinators_ids = serializers.PrimaryKeyRelatedField(
        queryset=Coordinator.objects.all(), source='special_coordinators', many=True, write_only=True, required=False
    )
    class Meta:
        model = Room
        # MUDANÇA: Adicionados os novos campos 'status' e 'special_coordinators_ids'.
        fields = ['id', 'code', 'name', 'status', 'department', 'users_ids', 'admins_ids', 'special_coordinators_ids']
