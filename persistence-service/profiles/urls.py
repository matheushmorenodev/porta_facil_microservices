# -----------------------------------------------------------------------------
# ARQUIVO: profiles/urls.py
# (Ainda vazio, adicionaremos endpoints conforme necessário)
# -----------------------------------------------------------------------------
from django.urls import path
from .views import CleanupTestUserAPIView

urlpatterns = [
    # Ex: path('users/', UserProfileListView.as_view()),
    # NOVO: Rota para limpar usuários de teste
    path('internal/cleanup/user/<str:username>/', CleanupTestUserAPIView.as_view(), name='cleanup-test-user'),
]