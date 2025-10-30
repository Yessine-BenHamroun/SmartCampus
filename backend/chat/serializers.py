from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatParticipant


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer pour les salons de chat"""
    online_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            '_id', 'name', 'slug', 'room_type', 'description',
            'created_by_id', 'created_by_email', 'created_by_name',
            'created_at', 'is_active', 'participant_ids',
            'online_count', 'last_message'
        ]
        read_only_fields = ['_id', 'created_at', 'slug']
    
    def get_online_count(self, obj):
        return obj.get_online_count()
    
    def get_last_message(self, obj):
        last_msg = obj.get_last_message()
        if last_msg:
            return ChatMessageSerializer(last_msg).data
        return None


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer pour les messages de chat"""
    
    class Meta:
        model = ChatMessage
        fields = [
            '_id', 'room_id', 'sender_id', 'sender_email', 'sender_name',
            'content', 'timestamp', 'is_edited', 'edited_at',
            'is_deleted', 'deleted_at', 'deleted_by_id', 'deleted_by_name',
            'attachment'
        ]
        read_only_fields = ['_id', 'timestamp']


class ChatParticipantSerializer(serializers.ModelSerializer):
    """Serializer pour les participants"""
    
    class Meta:
        model = ChatParticipant
        fields = [
            '_id', 'room_id', 'user_id', 'user_email', 'user_name',
            'joined_at', 'last_seen', 'is_online', 'unread_count'
        ]
        read_only_fields = ['_id', 'joined_at']


class CreateRoomSerializer(serializers.Serializer):
    """Serializer pour créer un nouveau salon"""
    name = serializers.CharField(max_length=255, required=True)
    room_type = serializers.ChoiceField(
        choices=['public', 'private', 'course', 'group'],
        default='public'
    )
    description = serializers.CharField(required=False, allow_blank=True)
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
