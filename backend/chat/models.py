from djongo import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


class ChatRoom(models.Model):
    """Model pour les salons de chat - Stocké dans MongoDB"""
    ROOM_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('course', 'Course'),
        ('group', 'Group'),
    ]
    
    _id = models.ObjectIdField()
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='public')
    description = models.TextField(blank=True)
    created_by_id = models.IntegerField()  # ID de l'utilisateur
    created_by_email = models.EmailField()  # Email de l'utilisateur
    created_by_name = models.CharField(max_length=255)  # Nom complet
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    # Liste des participants (IDs)
    participant_ids = models.JSONField(default=list)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.room_type})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_online_count(self):
        """Compte le nombre de participants en ligne"""
        return ChatParticipant.objects.filter(room_id=str(self._id), is_online=True).count()
    
    def get_last_message(self):
        """Récupère le dernier message du salon"""
        return ChatMessage.objects.filter(room_id=str(self._id), is_deleted=False).order_by('-timestamp').first()


class ChatParticipant(models.Model):
    """Model pour gérer les participants d'un salon - Stocké dans MongoDB"""
    _id = models.ObjectIdField()
    room_id = models.CharField(max_length=255)  # ObjectId du salon
    user_id = models.IntegerField()  # ID de l'utilisateur
    user_email = models.EmailField()
    user_name = models.CharField(max_length=255)
    joined_at = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=False)
    unread_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'chat_participants'
        unique_together = [['room_id', 'user_id']]
    
    def __str__(self):
        return f"{self.user_name} in room {self.room_id}"


class ChatMessage(models.Model):
    """Model pour les messages de chat - Stocké dans MongoDB"""
    _id = models.ObjectIdField()
    room_id = models.CharField(max_length=255)  # ObjectId du salon
    sender_id = models.IntegerField()  # ID de l'expéditeur
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by_id = models.IntegerField(null=True, blank=True)
    deleted_by_name = models.CharField(max_length=255, blank=True)
    
    # Pour les fichiers/images (optionnel)
    attachment = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message from {self.sender_name} at {self.timestamp}"
    
    def soft_delete(self, user_id, user_name):
        """Suppression douce du message"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by_id = user_id
        self.deleted_by_name = user_name
        self.save()
