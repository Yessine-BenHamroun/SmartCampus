from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('room/<slug:slug>/', views.chat_room, name='chat_room'),
    path('create/', views.create_room, name='create_room'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
]
