from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SUAPTokenBackup(models.Model):
    """
    Armazena um backup do token do SUAP e um hash da senha do usuário
    para permitir o login caso o serviço do SUAP esteja offline.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    suap_token = models.TextField()
    expires_at = models.DateTimeField()
    password_hash = models.CharField(max_length=255, null=True, blank=True)

    def is_valid(self):
        """Verifica se o token de backup ainda é válido."""
        return timezone.now() < self.expires_at
