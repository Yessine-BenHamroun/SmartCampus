from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models
from .models import ChatRoom, ChatMessage, ChatParticipant
from .serializers import (
    ChatRoomSerializer, ChatMessageSerializer,
    ChatParticipantSerializer, CreateRoomSerializer
)


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les salons de chat"""
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filtrer les salons accessibles par l'utilisateur"""
        user = self.request.user
        # Salons publics + salons où l'utilisateur est participant
        return ChatRoom.objects.filter(
            is_active=True
        ).filter(
            models.Q(room_type='public') |
            models.Q(participant_ids__contains=user.id)
        )
    
    def create(self, request):
        """Créer un nouveau salon de chat"""
        serializer = CreateRoomSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user = request.user
        
        # Créer le salon
        room = ChatRoom.objects.create(
            name=data['name'],
            room_type=data.get('room_type', 'public'),
            description=data.get('description', ''),
            created_by_id=user.id,
            created_by_email=user.email,
            created_by_name=f"{user.first_name} {user.last_name}".strip() or user.username,
            participant_ids=[user.id] + data.get('participant_ids', [])
        )
        
        # Ajouter le créateur comme participant
        ChatParticipant.objects.create(
            room_id=str(room._id),
            user_id=user.id,
            user_email=user.email,
            user_name=f"{user.first_name} {user.last_name}".strip() or user.username
        )
        
        return Response(
            ChatRoomSerializer(room).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, slug=None):
        """Récupérer les messages d'un salon"""
        room = self.get_object()
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        messages = ChatMessage.objects.filter(
            room_id=str(room._id),
            is_deleted=False
        ).order_by('-timestamp')[offset:offset+limit]
        
        messages = list(reversed(messages))
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def participants(self, request, slug=None):
        """Récupérer les participants d'un salon"""
        room = self.get_object()
        participants = ChatParticipant.objects.filter(room_id=str(room._id))
        serializer = ChatParticipantSerializer(participants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, slug=None):
        """Rejoindre un salon"""
        room = self.get_object()
        user = request.user
        
        # Vérifier si déjà participant
        participant, created = ChatParticipant.objects.get_or_create(
            room_id=str(room._id),
            user_id=user.id,
            defaults={
                'user_email': user.email,
                'user_name': f"{user.first_name} {user.last_name}".strip() or user.username
            }
        )
        
        if created:
            # Ajouter à la liste des participants
            if user.id not in room.participant_ids:
                room.participant_ids.append(user.id)
                room.save()
        
        return Response({
            'message': 'Joined successfully',
            'participant': ChatParticipantSerializer(participant).data
        })


class ChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les messages"""
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les messages par salon"""
        room_id = self.request.query_params.get('room_id')
        if room_id:
            return ChatMessage.objects.filter(room_id=room_id, is_deleted=False)
        return ChatMessage.objects.filter(is_deleted=False)
    
    def create(self, request):
        """Envoyer un nouveau message"""
        user = request.user
        room_id = request.data.get('room_id')
        content = request.data.get('content', '').strip()
        
        if not room_id or not content:
            return Response(
                {'error': 'room_id and content are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que le salon existe
        try:
            room = ChatRoom.objects.get(_id=room_id)
        except ChatRoom.DoesNotExist:
            return Response(
                {'error': 'Room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Créer le message
        message = ChatMessage.objects.create(
            room_id=str(room._id),
            sender_id=user.id,
            sender_email=user.email,
            sender_name=f"{user.first_name} {user.last_name}".strip() or user.username,
            content=content
        )
        
        return Response(
            ChatMessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['put'])
    def edit(self, request, pk=None):
        """Modifier un message"""
        message = self.get_object()
        user = request.user
        
        # Vérifier que l'utilisateur est l'expéditeur
        if message.sender_id != user.id:
            return Response(
                {'error': 'You can only edit your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        content = request.data.get('content', '').strip()
        if not content:
            return Response(
                {'error': 'Content cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message.content = content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()
        
        return Response(ChatMessageSerializer(message).data)
    
    @action(detail=True, methods=['delete'])
    def soft_delete(self, request, pk=None):
        """Supprimer un message (soft delete)"""
        message = self.get_object()
        user = request.user
        
        # Vérifier que l'utilisateur est l'expéditeur
        if message.sender_id != user.id:
            return Response(
                {'error': 'You can only delete your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_name = f"{user.first_name} {user.last_name}".strip() or user.username
        message.soft_delete(user.id, user_name)
        
        return Response({
            'message': 'Message deleted successfully',
            'deleted_text': f"{user_name} a supprimé ce message"
        })
