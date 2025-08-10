from rest_framework import serializers
from django.contrib.auth.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registrar um novo usuário."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    """Serializer para exibir dados básicos de um usuário."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
