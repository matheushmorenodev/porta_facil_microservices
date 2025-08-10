from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # MUDANÇA: Removemos o prefixo '/api/auth/'.
    # Agora, as rotas de 'authentication.urls' serão a raiz da API deste serviço.
    path('', include('authentication.urls')),
]