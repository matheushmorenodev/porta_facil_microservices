from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Delega as rotas para os respectivos apps
    path('', include('profiles.urls')),
    path('', include('resources.urls')),
]

