from django.urls import path
from . import views, ai_views

app_name = 'chat'

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('room/<slug:slug>/', views.chat_room, name='chat_room'),
    path('create/', views.create_room, name='create_room'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    
    # AI API Endpoints
    path('api/ai/analyze-sentiment/', ai_views.analyze_message_sentiment, name='ai_analyze_sentiment'),
    path('api/ai/room/<slug:room_slug>/sentiment-stats/', ai_views.get_room_sentiment_stats, name='ai_room_sentiment_stats'),
    path('api/ai/room/<slug:room_slug>/analyze/', ai_views.analyze_conversation, name='ai_analyze_conversation'),
    path('api/ai/message/<str:message_id>/sentiment/', ai_views.get_message_sentiment, name='ai_message_sentiment'),
]
