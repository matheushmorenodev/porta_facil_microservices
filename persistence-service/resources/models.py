# -----------------------------------------------------------------------------
# ARQUIVO: persistence-service/resources/models.py (VERSÃO ATUALIZADA)
# -----------------------------------------------------------------------------
from django.db import models
from profiles.models import Coordinator, Admin, Common

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    coordinators = models.ManyToManyField(Coordinator, related_name='departments', blank=True)
    def __str__(self):
        return f'{self.code} - {self.name}'

class Room(models.Model):
    # NOVO: Adicionando o campo de status com opções pré-definidas.
    class RoomStatusChoices(models.TextChoices):
        DISPONIVEL = 'Disponível'
        OCUPADA = 'Ocupada'
        MANUTENCAO = 'Em Manutenção'

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='rooms')
    admins = models.ManyToManyField(Admin, related_name='rooms_administered', blank=True)
    users = models.ManyToManyField(Common, related_name='rooms_accessed', blank=True)
    
    # NOVO: Relação para coordenadores específicos da sala (salas "especiais").
    special_coordinators = models.ManyToManyField(
        Coordinator, related_name='special_rooms_coordinated', blank=True
    )

    # NOVO: Campo de status.
    status = models.CharField(
        max_length=20,
        choices=RoomStatusChoices.choices,
        default=RoomStatusChoices.DISPONIVEL
    )

    def __str__(self):
        return f'{self.code} - {self.name} ({self.status})'

class IOTObject(models.Model):
    # O status do objeto IoT (conectado/desconectado) pode ser mantido aqui,
    # enquanto o status de uso da sala fica no modelo Room.
    status = models.CharField(max_length=50, blank=True, default="Aguardando Conexão")
    mac = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, default="Porta")
    room = models.ForeignKey(Room, related_name='iot_objects', on_delete=models.RESTRICT)
    def __str__(self):
        return f'{self.mac} - {self.description}'

# O modelo Log não precisa estar aqui, ele pertence ao log-service.
# Removi para manter a separação de responsabilidades.