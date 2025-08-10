# -----------------------------------------------------------------------------
# ARQUIVO: persistence-service/profiles/views.py (NOVO ARQUIVO!)
# -----------------------------------------------------------------------------
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import ActorUser, Common, Admin, Coordinator, Service, Security

class CleanupTestUserAPIView(APIView):
    """
    Endpoint interno para deletar um usuário de teste e seus perfis.
    SÓ DEVE ESTAR ATIVO EM AMBIENTE DE TESTE/DEBUG.
    """
    def delete(self, request, username):
        if not settings.DEBUG:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        try:
            actor = ActorUser.objects.get(username=username)
            user_id_to_delete = actor.user_id
            
            # Deleta todos os perfis associados
            Common.objects.filter(user_id=user_id_to_delete).delete()
            Admin.objects.filter(user_id=user_id_to_delete).delete()
            Coordinator.objects.filter(user_id=user_id_to_delete).delete()
            Service.objects.filter(user_id=user_id_to_delete).delete()
            Security.objects.filter(user_id=user_id_to_delete).delete()
            
            # Deleta o ActorUser
            actor.delete()
            
            return Response({"detail": f"Usuário de teste '{username}' e seus perfis foram removidos."}, status=status.HTTP_204_NO_CONTENT)
        except ActorUser.DoesNotExist:
            return Response({"detail": "Usuário de teste não encontrado."}, status=status.HTTP_404_NOT_FOUND)