from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid


class Meeting(models.Model):
    """Modèle pour les réunions vidéo"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Planifiée'),
        ('ongoing', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    # Identifiant unique
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Instructeur
    instructor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='hosted_meetings',
        verbose_name="Instructeur"
    )
    
    # Planification
    scheduled_date = models.DateTimeField(verbose_name="Date et heure prévue")
    duration = models.IntegerField(
        default=60, 
        verbose_name="Durée (minutes)",
        help_text="Durée estimée en minutes"
    )
    
    # Lien de visioconférence
    meeting_link = models.URLField(
        max_length=500, 
        blank=True,
        verbose_name="Lien de la réunion",
        help_text="Lien Zoom, Jitsi, Google Meet, etc."
    )
    
    meeting_id = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="ID de réunion",
        help_text="ID unique pour Jitsi/Zoom"
    )
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name="Statut"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifiée le")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Démarrée le")
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminée le")
    
    # Participants (ManyToMany via MeetingParticipant)
    students = models.ManyToManyField(
        User,
        through='MeetingParticipant',
        related_name='invited_meetings',
        verbose_name="Étudiants"
    )
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = "Réunion"
        verbose_name_plural = "Réunions"
        indexes = [
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date.strftime('%d/%m/%Y %H:%M')}"
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Vérifier que la date est dans le futur (sauf si la réunion est déjà créée)
        if not self.pk and self.scheduled_date <= timezone.now():
            raise ValidationError({
                'scheduled_date': _('La date de réunion doit être dans le futur.')
            })
        
        # Vérifier la durée
        if self.duration <= 0:
            raise ValidationError({
                'duration': _('La durée doit être supérieure à 0.')
            })
    
    def save(self, *args, **kwargs):
        # Générer un meeting_id si vide
        if not self.meeting_id:
            self.meeting_id = f"meet-{str(self.id).replace('-', '')[:12]}"
        
        # Générer le lien Jitsi par défaut si vide
        if not self.meeting_link:
            self.meeting_link = f"https://meet.jit.si/SmartCampus-{self.meeting_id}"
        
        super().save(*args, **kwargs)
    
    @property
    def is_past(self):
        """Vérifie si la réunion est passée"""
        return self.scheduled_date < timezone.now()
    
    @property
    def is_upcoming(self):
        """Vérifie si la réunion est à venir"""
        return self.scheduled_date > timezone.now() and self.status == 'scheduled'
    
    @property
    def can_start(self):
        """Vérifie si la réunion peut être démarrée"""
        now = timezone.now()
        # Peut démarrer 15 minutes avant l'heure prévue
        start_window = self.scheduled_date - timezone.timedelta(minutes=15)
        return self.status == 'scheduled' and now >= start_window
    
    @property
    def can_join(self):
        """Vérifie si on peut rejoindre la réunion"""
        return self.status == 'ongoing'
    
    @property
    def participant_count(self):
        """Nombre de participants invités"""
        return self.students.count()
    
    @property
    def attended_count(self):
        """Nombre de participants présents"""
        return self.participants.filter(status='attended').count()
    
    def start_meeting(self):
        """Démarre la réunion"""
        if self.can_start:
            self.status = 'ongoing'
            self.started_at = timezone.now()
            self.save(update_fields=['status', 'started_at', 'updated_at'])
            return True
        return False
    
    def end_meeting(self):
        """Termine la réunion"""
        if self.status == 'ongoing':
            self.status = 'completed'
            self.ended_at = timezone.now()
            self.save(update_fields=['status', 'ended_at', 'updated_at'])
            return True
        return False
    
    def cancel_meeting(self):
        """Annule la réunion"""
        if self.status in ['scheduled', 'ongoing']:
            self.status = 'cancelled'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False


class MeetingParticipant(models.Model):
    """Modèle pour les participants d'une réunion"""
    
    STATUS_CHOICES = [
        ('invited', 'Invité'),
        ('accepted', 'Accepté'),
        ('declined', 'Refusé'),
        ('attended', 'Présent'),
        ('absent', 'Absent'),
    ]
    
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name="Réunion"
    )
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meeting_participations',
        verbose_name="Étudiant"
    )
    
    # Statut de participation
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='invited',
        verbose_name="Statut"
    )
    
    # Timestamps
    invited_at = models.DateTimeField(auto_now_add=True, verbose_name="Invité le")
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name="Répondu le")
    joined_at = models.DateTimeField(null=True, blank=True, verbose_name="Rejoint le")
    left_at = models.DateTimeField(null=True, blank=True, verbose_name="Quitté le")
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        unique_together = ['meeting', 'student']
        ordering = ['student__last_name', 'student__first_name']
        verbose_name = "Participant"
        verbose_name_plural = "Participants"
    
    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} - {self.meeting.title}"
    
    def accept_invitation(self):
        """Accepter l'invitation"""
        if self.status == 'invited':
            self.status = 'accepted'
            self.responded_at = timezone.now()
            self.save(update_fields=['status', 'responded_at'])
            return True
        return False
    
    def decline_invitation(self):
        """Refuser l'invitation"""
        if self.status == 'invited':
            self.status = 'declined'
            self.responded_at = timezone.now()
            self.save(update_fields=['status', 'responded_at'])
            return True
        return False
    
    def mark_attended(self):
        """Marquer comme présent"""
        self.status = 'attended'
        if not self.joined_at:
            self.joined_at = timezone.now()
        self.save(update_fields=['status', 'joined_at'])
    
    def mark_absent(self):
        """Marquer comme absent"""
        if self.status != 'attended':
            self.status = 'absent'
            self.save(update_fields=['status'])
    
    def join_meeting(self):
        """Rejoindre la réunion"""
        if not self.joined_at:
            self.joined_at = timezone.now()
            self.status = 'attended'
            self.save(update_fields=['joined_at', 'status'])
    
    def leave_meeting(self):
        """Quitter la réunion"""
        if not self.left_at:
            self.left_at = timezone.now()
            self.save(update_fields=['left_at'])
    
    @property
    def duration_in_meeting(self):
        """Calcule le temps passé dans la réunion"""
        if self.joined_at:
            end_time = self.left_at or timezone.now()
            duration = end_time - self.joined_at
            return duration.total_seconds() / 60  # En minutes
        return 0
