from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Créer le router pour les ViewSets
router = DefaultRouter()
router.register(r'rooms', views.ChatRoomViewSet, basename='chatroom')
router.register(r'messages', views.ChatMessageViewSet, basename='chatmessage')

app_name = 'chat'

urlpatterns = [
    path('', include(router.urls)),
]
