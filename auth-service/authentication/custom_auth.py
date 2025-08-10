from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookiesJWTAuthentication(JWTAuthentication):
    """
    Classe personalizada de autenticação JWT que lê o token de acesso
    a partir dos cookies HTTPOnly, em vez do header 'Authorization'.
    """
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None

        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except AuthenticationFailed:
            # Tenta usar o refresh token se o access token falhar (opcional, mas bom para UX)
            return None
        except Exception:
            return None
