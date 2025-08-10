from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    SUAPLoginView,
    register_user,
    logout_view,
    check_authenticated_view,
    mock_login,
)

urlpatterns = [
    # Login padrão (usuário/senha locais)
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Login via SUAP
    path('suap-login/', SUAPLoginView.as_view(), name="suap_login"),

    # Gestão de Tokens
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Registro e Logout
    path('register/', register_user, name='register_user'),
    path('logout/', logout_view, name='logout'),

    # Verificação de status
    path('authenticated/', check_authenticated_view, name='check_authenticated'),
    
    # NOVO: Rota para o login simulado
    path('mock-login/', mock_login, name='mock_login'),
]