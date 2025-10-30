from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, Count
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Meeting, MeetingParticipant
from .forms import MeetingForm, MeetingUpdateForm, MeetingFilterForm


# ============= HELPER FUNCTIONS =============

def get_user_role(request):
    """
    Récupère le rôle de l'utilisateur depuis MongoDB
    Returns: 'instructor', 'student', ou 'admin'
    """
    # Vérifier si les données de session sont disponibles
    if hasattr(request.user, 'session_data'):
        return request.user.session_data.get('role', 'student')
    
    # Fallback : utiliser is_staff (compatibilité)
    if request.user.is_staff:
        return 'instructor'
    
    return 'student'


def is_instructor(request):
    """Vérifie si l'utilisateur est un instructeur"""
    role = get_user_role(request)
    return role in ['instructor', 'admin']


# ============= VUES INSTRUCTEUR =============

@login_required
def meeting_list(request):
    """
    Liste de toutes les réunions pour l'instructeur
    Avec filtres : statut, date, recherche
    """
    # Vérifier que l'utilisateur est un instructeur
    if not is_instructor(request):
        messages.error(request, "Seuls les instructeurs peuvent accéder à cette page.")
        return redirect('student_meetings')
    
    # Récupérer toutes les réunions de l'instructeur
    meetings = Meeting.objects.filter(instructor=request.user).select_related('instructor')
    
    # Appliquer les filtres
    filter_form = MeetingFilterForm(request.GET)
    
    if filter_form.is_valid():
        # Filtre par statut
        status = filter_form.cleaned_data.get('status')
        if status and status != 'all':
            meetings = meetings.filter(status=status)
        
        # Filtre par période
        time_filter = filter_form.cleaned_data.get('time_filter')
        now = timezone.now()
        
        if time_filter == 'upcoming':
            meetings = meetings.filter(scheduled_date__gte=now)
        elif time_filter == 'past':
            meetings = meetings.filter(scheduled_date__lt=now)
        elif time_filter == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            meetings = meetings.filter(scheduled_date__gte=today_start, scheduled_date__lt=today_end)
        elif time_filter == 'week':
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=7)
            meetings = meetings.filter(scheduled_date__gte=week_start, scheduled_date__lt=week_end)
        elif time_filter == 'month':
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                month_end = month_start.replace(year=now.year + 1, month=1)
            else:
                month_end = month_start.replace(month=now.month + 1)
            meetings = meetings.filter(scheduled_date__gte=month_start, scheduled_date__lt=month_end)
        
        # Recherche par titre
        search = filter_form.cleaned_data.get('search')
        if search:
            meetings = meetings.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    # Annoter avec le nombre de participants
    meetings = meetings.annotate(
        total_participants=Count('participants'),
        attended_participants=Count('participants', filter=Q(participants__status='attended'))
    )
    
    # Trier par date (les plus récentes en premier)
    meetings = meetings.order_by('-scheduled_date')
    
    # Statistiques
    total_meetings = meetings.count()
    upcoming_meetings = meetings.filter(scheduled_date__gte=timezone.now()).count()
    ongoing_meetings = meetings.filter(status='ongoing').count()
    
    context = {
        'meetings': meetings,
        'filter_form': filter_form,
        'total_meetings': total_meetings,
        'upcoming_meetings': upcoming_meetings,
        'ongoing_meetings': ongoing_meetings,
    }
    
    return render(request, 'meetings/meeting_list.html', context)


@login_required
def meeting_create(request):
    """Créer une nouvelle réunion (uniquement pour les instructeurs)"""
    if not is_instructor(request):
        messages.error(request, "Seuls les instructeurs peuvent créer des réunions.")
        return redirect('student_meetings')
    
    if request.method == 'POST':
        form = MeetingForm(request.POST, instructor=request.user)
        if form.is_valid():
            meeting = form.save()
            messages.success(
                request,
                f'Réunion "{meeting.title}" créée avec succès ! '
                f'{meeting.students.count()} étudiant(s) invité(s).'
            )
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = MeetingForm(instructor=request.user)
    
    context = {
        'form': form,
        'title': 'Créer une réunion',
    }
    
    return render(request, 'meetings/meeting_form.html', context)


@login_required
def meeting_detail(request, pk):
    """
    Détails d'une réunion
    Accessible par l'instructeur et les étudiants invités
    """
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Vérifier les permissions
    is_instructor = meeting.instructor == request.user
    is_participant = meeting.students.filter(pk=request.user.pk).exists()
    
    if not (is_instructor or is_participant):
        return HttpResponseForbidden("Vous n'avez pas accès à cette réunion.")
    
    # Récupérer les participants
    participants = meeting.participants.select_related('student').order_by('-status', 'student__username')
    
    # Récupérer le statut du participant actuel (si c'est un étudiant)
    current_participant = None
    if is_participant:
        current_participant = meeting.participants.filter(student=request.user).first()
    
    context = {
        'meeting': meeting,
        'is_instructor': is_instructor,
        'is_participant': is_participant,
        'participants': participants,
        'current_participant': current_participant,
        'can_start': meeting.can_start and is_instructor,
        'can_join': meeting.can_join and is_participant,
    }
    
    return render(request, 'meetings/meeting_detail.html', context)


@login_required
def meeting_update(request, pk):
    """Modifier une réunion (uniquement l'instructeur)"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Vérifier que l'utilisateur est l'instructeur
    if meeting.instructor != request.user:
        return HttpResponseForbidden("Seul l'instructeur peut modifier cette réunion.")
    
    # Ne pas permettre la modification si la réunion est terminée ou annulée
    if meeting.status in ['completed', 'cancelled']:
        messages.error(request, "Cette réunion ne peut plus être modifiée.")
        return redirect('meeting_detail', pk=meeting.pk)
    
    if request.method == 'POST':
        form = MeetingUpdateForm(request.POST, instance=meeting)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.save()
            
            # Mettre à jour les participants
            meeting.participants.all().delete()
            student_emails = form.cleaned_data.get('students')
            students = [form.students_map[email] for email in student_emails if email in form.students_map]
            for student in students:
                MeetingParticipant.objects.create(
                    meeting=meeting,
                    student=student,
                    status='invited'
                )
            
            messages.success(request, f'Réunion "{meeting.title}" modifiée avec succès.')
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = MeetingUpdateForm(instance=meeting)
    
    context = {
        'form': form,
        'meeting': meeting,
        'title': 'Modifier la réunion',
    }
    
    return render(request, 'meetings/meeting_form.html', context)


@login_required
def meeting_delete(request, pk):
    """Annuler une réunion (uniquement l'instructeur)"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Vérifier que l'utilisateur est l'instructeur
    if meeting.instructor != request.user:
        return HttpResponseForbidden("Seul l'instructeur peut annuler cette réunion.")
    
    if request.method == 'POST':
        meeting.cancel_meeting()
        messages.success(request, f'Réunion "{meeting.title}" annulée.')
        return redirect('meeting_list')
    
    context = {
        'meeting': meeting,
    }
    
    return render(request, 'meetings/meeting_confirm_delete.html', context)


@login_required
def meeting_start(request, pk):
    """Démarrer une réunion (uniquement l'instructeur)"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Vérifier que l'utilisateur est l'instructeur
    if meeting.instructor != request.user:
        return HttpResponseForbidden("Seul l'instructeur peut démarrer cette réunion.")
    
    if meeting.can_start:
        meeting.start_meeting()
        messages.success(request, f'Réunion "{meeting.title}" démarrée !')
        return redirect('meeting_room', pk=meeting.pk)
    else:
        messages.error(request, "Cette réunion ne peut pas être démarrée maintenant.")
        return redirect('meeting_detail', pk=meeting.pk)


@login_required
def meeting_end(request, pk):
    """Terminer une réunion (uniquement l'instructeur)"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Vérifier que l'utilisateur est l'instructeur
    if meeting.instructor != request.user:
        return HttpResponseForbidden("Seul l'instructeur peut terminer cette réunion.")
    
    if meeting.status == 'ongoing':
        meeting.end_meeting()
        messages.success(request, f'Réunion "{meeting.title}" terminée.')
        return redirect('meeting_detail', pk=meeting.pk)
    else:
        messages.error(request, "Cette réunion n'est pas en cours.")
        return redirect('meeting_detail', pk=meeting.pk)


# ============= VUES ÉTUDIANT =============

@login_required
def student_meetings(request):
    """
    Liste des réunions pour un étudiant
    Affiche uniquement les réunions auxquelles il est invité
    """
    # Récupérer toutes les réunions où l'étudiant est invité
    participants = MeetingParticipant.objects.filter(
        student=request.user
    ).select_related('meeting', 'meeting__instructor')
    
    # Séparer en catégories
    upcoming = []
    past = []
    now = timezone.now()
    
    for participant in participants:
        if participant.meeting.scheduled_date >= now:
            upcoming.append(participant)
        else:
            past.append(participant)
    
    # Trier
    upcoming.sort(key=lambda p: p.meeting.scheduled_date)
    past.sort(key=lambda p: p.meeting.scheduled_date, reverse=True)
    
    context = {
        'upcoming_participants': upcoming,
        'past_participants': past,
        'total_invited': len(upcoming) + len(past),
        'upcoming_count': len(upcoming),
    }
    
    return render(request, 'meetings/student_meetings.html', context)


@login_required
def meeting_join(request, pk):
    """Rejoindre une réunion (pour les étudiants invités)"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Vérifier que l'utilisateur est invité
    participant = meeting.participants.filter(student=request.user).first()
    if not participant:
        return HttpResponseForbidden("Vous n'êtes pas invité à cette réunion.")
    
    # Vérifier que la réunion est en cours
    if not meeting.can_join:
        messages.error(request, "Cette réunion n'est pas encore commencée ou est déjà terminée.")
        return redirect('meeting_detail', pk=meeting.pk)
    
    # Marquer le participant comme ayant rejoint
    if participant.status == 'invited' or participant.status == 'accepted':
        participant.status = 'attended'
        participant.joined_at = timezone.now()
        participant.save()
    
    # Rediriger vers la salle de réunion
    return redirect('meeting_room', pk=meeting.pk)


@login_required
def meeting_respond(request, pk, action):
    """Accepter ou refuser une invitation (pour les étudiants)"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Vérifier que l'utilisateur est invité
    participant = meeting.participants.filter(student=request.user).first()
    if not participant:
        return HttpResponseForbidden("Vous n'êtes pas invité à cette réunion.")
    
    if action == 'accept':
        participant.status = 'accepted'
        participant.save()
        messages.success(request, f'Vous avez accepté l\'invitation à "{meeting.title}".')
    elif action == 'decline':
        participant.status = 'declined'
        participant.save()
        messages.info(request, f'Vous avez refusé l\'invitation à "{meeting.title}".')
    
    return redirect('student_meetings')


# ============= SALLE DE RÉUNION (JITSI) =============

@login_required
def meeting_room(request, pk):
    """
    Salle de réunion virtuelle avec Jitsi Meet
    Accessible par l'instructeur et les participants
    """
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Vérifier les permissions
    is_instructor = meeting.instructor == request.user
    is_participant = meeting.students.filter(pk=request.user.pk).exists()
    
    if not (is_instructor or is_participant):
        return HttpResponseForbidden("Vous n'avez pas accès à cette réunion.")
    
    # Vérifier que la réunion est en cours
    if meeting.status != 'ongoing':
        messages.error(request, "Cette réunion n'est pas en cours.")
        return redirect('meeting_detail', pk=meeting.pk)
    
    # Marquer le participant comme présent
    if is_participant:
        participant = meeting.participants.filter(student=request.user).first()
        if participant and participant.status != 'attended':
            participant.status = 'attended'
            participant.joined_at = timezone.now()
            participant.save()
    
    context = {
        'meeting': meeting,
        'is_instructor': is_instructor,
        'user_display_name': request.user.get_full_name() or request.user.username,
    }
    
    return render(request, 'meetings/meeting_room.html', context)


@login_required
def meeting_leave(request, pk):
    """Quitter une réunion"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Si c'est un participant, enregistrer l'heure de départ
    participant = meeting.participants.filter(student=request.user).first()
    if participant and participant.status == 'attended' and not participant.left_at:
        participant.left_at = timezone.now()
        participant.save()
    
    messages.info(request, f'Vous avez quitté la réunion "{meeting.title}".')
    return redirect('meeting_detail', pk=meeting.pk)
