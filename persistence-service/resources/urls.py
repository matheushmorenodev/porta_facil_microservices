# -----------------------------------------------------------------------------
# ARQUIVO: persistence-service/resources/urls.py (VERSÃO ATUALIZADA)
# -----------------------------------------------------------------------------
from django.urls import path
from .views import (
    ListAllRoomsAPIView, ListRoomsWithAccessAPIView, ListAvailableRoomsAPIView, # NOVO
    DepartmentListCreateAPIView, DepartmentRetrieveUpdateDestroyAPIView,
    RoomListCreateAPIView, RoomRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    
    path('departments/', DepartmentListCreateAPIView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentRetrieveUpdateDestroyAPIView.as_view(), name='department-detail'),

    path('rooms/', RoomListCreateAPIView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', RoomRetrieveUpdateDestroyAPIView.as_view(), name='room-detail'),
    
    path('rooms/all/', ListAllRoomsAPIView.as_view(), name='list_all_rooms'),
    path('rooms/my-access/', ListRoomsWithAccessAPIView.as_view(), name='list_my_rooms'),
    # NOVO: Rota para as salas disponíveis.
    path('rooms/available/', ListAvailableRoomsAPIView.as_view(), name='list-available-rooms'),
]