#from rest_framework import serializers
from django.contrib.auth.models import User

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     """Serializer para registrar um novo usuário."""
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'password']

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password']
#         )
#         return user

# class UserSerializer(serializers.ModelSerializer):
#     """Serializer para exibir dados básicos de um usuário."""
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'first_name', 'last_name', 'email']

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer para customizar o payload do JWT
    """
    def validate(self, attrs):
        # Chama a validação padrão para obter o token
        data = super().validate(attrs)

        # Pega o usuário autenticado
        user = self.user

        # Adiciona dados personalizados no payload
        data['username'] = user.username
        data['email'] = user.email
        data['first_name'] = user.first_name  # Nome do usuário
        data['user_id'] = user.id  # ID do usuário
        data['is_active'] = user.is_active  # Se o usuário está ativo

        return data

