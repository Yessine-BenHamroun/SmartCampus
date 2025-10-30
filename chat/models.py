from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


class ChatRoom(models.Model):
    """Model pour les salons de chat"""
    ROOM_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('course', 'Course'),
        ('group', 'Group'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='public')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Pour les salons privés et de groupe
    participants = models.ManyToManyField(User, related_name='chat_rooms', through='ChatParticipant')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_online_count(self):
        """Retourne le nombre d'utilisateurs en ligne"""
        return self.participants.filter(chatparticipant__is_online=True).count()
    
    def get_last_message(self):
        """Retourne le dernier message du salon"""
        return self.messages.filter(is_deleted=False).order_by('-timestamp').first()


class ChatParticipant(models.Model):
    """Model pour gérer les participants d'un salon"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=False)
    unread_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('room', 'user')
    
    def __str__(self):
        return f"{self.user.username} in {self.room.name}"


class ChatMessage(models.Model):
    """Model pour les messages de chat"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Pour les fichiers/images (optionnel)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    def soft_delete(self):
        """Soft delete - marquer comme supprimé au lieu de supprimer"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.content = "[Message supprimé]"
        self.save()
