# -----------------------------------------------------------------------------
# ARQUIVO: profiles/models.py
# (Copiado diretamente do seu api_permission/models.py)
# -----------------------------------------------------------------------------
from django.db import models

# NOTA: Em um ambiente de microsserviços, não usamos o User do Django.
# Em vez disso, armazenamos o ID do usuário que vem do Auth Service.
# O modelo User do Django só existe no Auth Service.

class ActorUser(models.Model):
    class ActorUserRolesChoices(models.TextChoices):
        USUARIO_PADRAO = 'padrao'
        COORDENADOR = 'coordenador'
        ADMINISTRADOR = 'administrador'
        SERVIDOR = 'servidor'
        # Adicionei o de segurança que faltava no seu SUAPLoginView
        SEGURANCA = 'seguranca'

    user_id = models.IntegerField(unique=True) # ID do usuário vindo do Auth Service
    username = models.CharField(max_length=150, unique=True) # Username para referência
    role = models.CharField(
        max_length=20,
        choices=ActorUserRolesChoices.choices,
        default=ActorUserRolesChoices.USUARIO_PADRAO
    )

class Coordinator(models.Model):
    user_id = models.IntegerField(unique=True)
    def __str__(self):
        return f'Coordenador - ID: {self.user_id}'

class Common(models.Model):
    user_id = models.IntegerField(unique=True)
    def __str__(self):
        return f'Comum - ID: {self.user_id}'

class Service(models.Model):
    user_id = models.IntegerField(unique=True)
    def __str__(self):
        return f'Servidor - ID: {self.user_id}'

class Admin(models.Model):
    user_id = models.IntegerField(unique=True)
    def __str__(self):
        return f'Admin - ID: {self.user_id}'

class Security(models.Model):
    user_id = models.IntegerField(unique=True)
    def __str__(self):
        return f'Segurança - ID: {self.user_id}'