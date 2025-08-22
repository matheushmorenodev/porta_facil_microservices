from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserRegistrationSerializer, UserSerializer
from .models import SUAPTokenBackup
from .suap_utils import SuapUnauthorized, suap_login, get_user_info
from .event_publisher import publish_event

# importa as exceções que definimos no suap_login
from .suap_utils import (
    suap_login,
    SuapError,
    SuapInvalidCredentials,
    SuapForbidden,
    SuapNotFound,
    SuapServerError,
)



def set_auth_cookies(response, access_token, refresh_token):
    """Função auxiliar para configurar os cookies de autenticação na resposta."""
    response.set_cookie(
        key='access_token', value=access_token, httponly=True,
        secure=False, samesite='Lax' # Mudar para True e 'None' em produção com HTTPS
    )
    response.set_cookie(
        key='refresh_token', value=refresh_token, httponly=True,
        secure=False, samesite='Lax', path='/token/refresh/' # O path deve corresponder à URL de refresh
    )

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View de login padrão (usuário/senha).
    NOTA: O 'role' não é adicionado aqui, pois o Auth Service não conhece os perfis.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            
            user = User.objects.get(username=request.data['username'])
            publish_event('user_events', {
                'event_type': 'user_logged_in',
                'user_id': user.id,
                'username': user.username,
                'login_type': 'standard'
            })
            
            res = Response({'detail': 'Login bem-sucedido.'}, status=status.HTTP_200_OK)
            set_auth_cookies(res, access_token, refresh_token)
            return res
        return response

class CustomTokenRefreshView(TokenRefreshView):
    """View para renovar o token de acesso usando o refresh token do cookie."""
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token não encontrado no cookie.'}, status=status.HTTP_401_UNAUTHORIZED)
            
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data.get('access')
            res = Response({'detail': 'Token atualizado com sucesso.'}, status=status.HTTP_200_OK)
            res.set_cookie(key='access_token', value=access_token, httponly=True, secure=False, samesite='Lax')
            return res
            
        return Response({'detail': 'Refresh token inválido ou expirado.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Registra um usuário padrão e publica um evento para criação de perfil."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        publish_event('user_events', {
            'event_type': 'user_created',
            'user_id': user.id,
            'username': user.username,
            'role': 'padrao'
        })
        
        return Response({'detail': 'Usuário registrado com sucesso.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SUAPLoginView(APIView):
    """View para autenticação via API do SUAP, com tratamento de erros."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            data = suap_login(username, password)
            data = data | get_user_info(data.get("access"))
            return Response(data, status=status.HTTP_200_OK)

        except SuapInvalidCredentials as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
        except SuapUnauthorized as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        except SuapForbidden as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        except SuapNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except SuapServerError as e:
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        except SuapError as e:
            # erro genérico do SUAP (timeout, erro de conexão etc.)
            return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            # fallback final para evitar 500 sem mensagem clara
            return Response({"detail": f"Erro inesperado: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def mock_login(request):
    """Endpoint de login simulado para testes."""
    if not settings.DEBUG:
        return Response({"detail": "Endpoint não disponível em produção."}, status=status.HTTP_404_NOT_FOUND)

    username = request.data.get("username")
    role = request.data.get("role")
    if not username or not role:
        return Response({"detail": "Username e role são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

    user, created = User.objects.get_or_create(username=username)
    
    publish_event('user_events', {
        'event_type': 'user_created' if created else 'user_updated',
        'user_id': user.id,
        'username': user.username,
        'role': role
    })

    # MUDANÇA CRÍTICA: Adiciona o 'role' e o 'iss' (issuer) diretamente no payload do token
    refresh = RefreshToken.for_user(user)
    refresh['role'] = role
    refresh['iss'] = 'porta-facil-api' # Esta é a "marca" do nosso token

    res = Response({
        'detail': f'Login simulado como {role} bem-sucedido.',
        'user_info': UserSerializer(user).data
    }, status=status.HTTP_200_OK)
    
    set_auth_cookies(res, str(refresh.access_token), str(refresh))
    return res

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Remove os cookies de autenticação para fazer logout."""
    res = Response({'detail': 'Logout bem-sucedido.'}, status=status.HTTP_200_OK)
    res.delete_cookie('access_token')
    res.delete_cookie('refresh_token', path='/token/refresh/')
    return res

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_authenticated_view(request):
    """Verifica se o usuário está autenticado e retorna seus dados."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
