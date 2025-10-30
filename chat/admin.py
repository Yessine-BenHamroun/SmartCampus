from django.contrib import admin
from .models import ChatRoom, ChatParticipant, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'created_by', 'created_at', 'is_active', 'participants_count')
    list_filter = ('room_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'created_by__username')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Participants'


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'is_online', 'joined_at', 'last_seen', 'unread_count')
    list_filter = ('is_online', 'joined_at')
    search_fields = ('user__username', 'room__name')
    readonly_fields = ('joined_at',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'room', 'content_preview', 'timestamp', 'is_edited', 'is_deleted')
    list_filter = ('is_edited', 'is_deleted', 'timestamp')
    search_fields = ('sender__username', 'room__name', 'content')
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Aperçu du message'
