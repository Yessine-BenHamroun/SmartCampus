from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatParticipant


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_type', 'created_by_name', 'created_at', 'is_active']
    list_filter = ['room_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by_name', 'created_by_email']
    readonly_fields = ['_id', 'created_at', 'slug']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender_name', 'room_id', 'timestamp', 'is_edited', 'is_deleted']
    list_filter = ['is_edited', 'is_deleted', 'timestamp']
    search_fields = ['content', 'sender_name', 'sender_email']
    readonly_fields = ['_id', 'timestamp', 'edited_at', 'deleted_at']


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'room_id', 'is_online', 'last_seen', 'unread_count']
    list_filter = ['is_online', 'joined_at']
    search_fields = ['user_name', 'user_email', 'room_id']
    readonly_fields = ['_id', 'joined_at']
