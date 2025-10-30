from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Meeting, MeetingParticipant


class MeetingParticipantInline(admin.TabularInline):
    """Inline pour gérer les participants dans l'admin des meetings"""
    model = MeetingParticipant
    extra = 1
    fields = ['student', 'status', 'invited_at', 'joined_at', 'left_at']
    readonly_fields = ['invited_at', 'joined_at', 'left_at']
    autocomplete_fields = ['student']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    """Administration des réunions"""
    
    list_display = [
        'title', 
        'instructor', 
        'scheduled_date_display',
        'duration', 
        'status_badge',
        'participant_count',
        'attended_count',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'scheduled_date',
        'created_at',
        'instructor'
    ]
    
    search_fields = [
        'title',
        'description',
        'instructor__username',
        'instructor__first_name',
        'instructor__last_name',
        'meeting_id'
    ]
    
    readonly_fields = [
        'id',
        'meeting_id',
        'created_at',
        'updated_at',
        'started_at',
        'ended_at',
        'meeting_link_display'
    ]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'instructor')
        }),
        ('Planification', {
            'fields': ('scheduled_date', 'duration')
        }),
        ('Lien de visioconférence', {
            'fields': ('meeting_link', 'meeting_link_display', 'meeting_id'),
            'description': 'Le lien sera généré automatiquement si laissé vide (Jitsi Meet)'
        }),
        ('Statut', {
            'fields': ('status', 'started_at', 'ended_at')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MeetingParticipantInline]
    
    actions = ['start_meetings', 'end_meetings', 'cancel_meetings']
    
    def scheduled_date_display(self, obj):
        """Affichage coloré de la date"""
        now = timezone.now()
        if obj.scheduled_date < now:
            color = 'red'
            icon = '🔴'
        elif obj.scheduled_date < now + timezone.timedelta(hours=1):
            color = 'orange'
            icon = '🟠'
        else:
            color = 'green'
            icon = '🟢'
        
        return format_html(
            '<span style="color: {};">{} {}</span>',
            color,
            icon,
            obj.scheduled_date.strftime('%d/%m/%Y %H:%M')
        )
    scheduled_date_display.short_description = 'Date prévue'
    scheduled_date_display.admin_order_field = 'scheduled_date'
    
    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'scheduled': '#17a2b8',  # info
            'ongoing': '#28a745',    # success
            'completed': '#6c757d',  # secondary
            'cancelled': '#dc3545',  # danger
        }
        
        icons = {
            'scheduled': '📅',
            'ongoing': '🔴',
            'completed': '✅',
            'cancelled': '❌',
        }
        
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, '❓')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    status_badge.admin_order_field = 'status'
    
    def meeting_link_display(self, obj):
        """Lien cliquable"""
        if obj.meeting_link:
            return format_html(
                '<a href="{}" target="_blank" style="color: #007bff;">🔗 Ouvrir la réunion</a>',
                obj.meeting_link
            )
        return "Aucun lien"
    meeting_link_display.short_description = 'Lien de réunion'
    
    # Actions personnalisées
    def start_meetings(self, request, queryset):
        """Démarrer les réunions sélectionnées"""
        count = 0
        for meeting in queryset:
            if meeting.start_meeting():
                count += 1
        
        self.message_user(request, f'{count} réunion(s) démarrée(s) avec succès.')
    start_meetings.short_description = "▶️ Démarrer les réunions sélectionnées"
    
    def end_meetings(self, request, queryset):
        """Terminer les réunions sélectionnées"""
        count = 0
        for meeting in queryset:
            if meeting.end_meeting():
                count += 1
        
        self.message_user(request, f'{count} réunion(s) terminée(s) avec succès.')
    end_meetings.short_description = "⏹️ Terminer les réunions sélectionnées"
    
    def cancel_meetings(self, request, queryset):
        """Annuler les réunions sélectionnées"""
        count = 0
        for meeting in queryset:
            if meeting.cancel_meeting():
                count += 1
        
        self.message_user(request, f'{count} réunion(s) annulée(s) avec succès.')
    cancel_meetings.short_description = "❌ Annuler les réunions sélectionnées"


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    """Administration des participants"""
    
    list_display = [
        'student_name',
        'meeting',
        'status_badge',
        'invited_at',
        'joined_at',
        'duration_display'
    ]
    
    list_filter = [
        'status',
        'invited_at',
        'meeting__status'
    ]
    
    search_fields = [
        'student__username',
        'student__first_name',
        'student__last_name',
        'meeting__title'
    ]
    
    readonly_fields = [
        'invited_at',
        'joined_at',
        'left_at',
        'duration_display'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('meeting', 'student')
        }),
        ('Statut de participation', {
            'fields': ('status', 'responded_at')
        }),
        ('Participation à la réunion', {
            'fields': ('invited_at', 'joined_at', 'left_at', 'duration_display')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def student_name(self, obj):
        """Nom complet de l'étudiant"""
        return obj.student.get_full_name() or obj.student.username
    student_name.short_description = 'Étudiant'
    student_name.admin_order_field = 'student__last_name'
    
    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'invited': '#17a2b8',    # info
            'accepted': '#28a745',   # success
            'declined': '#ffc107',   # warning
            'attended': '#28a745',   # success
            'absent': '#dc3545',     # danger
        }
        
        icons = {
            'invited': '📧',
            'accepted': '✅',
            'declined': '❌',
            'attended': '✅',
            'absent': '❌',
        }
        
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, '❓')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    status_badge.admin_order_field = 'status'
    
    def duration_display(self, obj):
        """Affichage de la durée"""
        duration = obj.duration_in_meeting
        if duration > 0:
            hours = int(duration // 60)
            minutes = int(duration % 60)
            if hours > 0:
                return f"{hours}h {minutes}min"
            return f"{minutes}min"
        return "-"
    duration_display.short_description = 'Temps de participation'
