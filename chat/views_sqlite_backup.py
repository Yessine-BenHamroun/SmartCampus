from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatRoom, ChatMessage, ChatParticipant


@login_required
def room_list(request):
    """Liste de tous les salons de chat"""
    # Salons publics
    public_rooms = ChatRoom.objects.filter(room_type='public', is_active=True)
    
    # Salons auxquels l'utilisateur participe
    user_rooms = request.user.chat_rooms.filter(is_active=True).exclude(room_type='public')
    
    context = {
        'public_rooms': public_rooms,
        'user_rooms': user_rooms,
    }
    return render(request, 'chat/room_list.html', context)


@login_required
def chat_room(request, slug):
    """Interface de chat pour un salon spécifique"""
    room = get_object_or_404(ChatRoom, slug=slug, is_active=True)
    
    # Vérifier les permissions
    if room.room_type != 'public':
        if not room.participants.filter(id=request.user.id).exists():
            messages.error(request, "Vous n'avez pas accès à ce salon.")
            return redirect('chat:room_list')
    
    # Ajouter l'utilisateur aux participants s'il n'y est pas déjà
    participant, created = ChatParticipant.objects.get_or_create(
        room=room,
        user=request.user
    )
    
    # Marquer les messages comme lus
    participant.unread_count = 0
    participant.save()
    
    # Récupérer les 50 derniers messages
    messages_list = room.messages.filter(is_deleted=False).select_related('sender').order_by('-timestamp')[:50]
    messages_list = list(reversed(messages_list))
    
    # Récupérer les participants en ligne
    online_participants = room.participants.filter(
        chatparticipant__is_online=True
    ).distinct()
    
    # Obtenir l'ID de l'utilisateur (pk ou id)
    user_id = getattr(request.user, 'id', None) or getattr(request.user, 'pk', None)
    
    context = {
        'room': room,
        'messages': messages_list,
        'online_participants': online_participants,
        'participants_count': room.participants.count(),
        'user_id': user_id,
    }
    return render(request, 'chat/chat_room.html', context)


@login_required
def create_room(request):
    """Créer un nouveau salon de chat"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        room_type = request.POST.get('room_type', 'public')
        
        if not name:
            messages.error(request, "Le nom du salon est requis.")
            return render(request, 'chat/create_room.html')
        
        # Vérifier si un salon avec ce nom existe déjà
        if ChatRoom.objects.filter(name__iexact=name).exists():
            messages.error(request, "Un salon avec ce nom existe déjà.")
            return render(request, 'chat/create_room.html')
        
        # Créer le salon
        room = ChatRoom.objects.create(
            name=name,
            description=description,
            room_type=room_type,
            created_by=request.user
        )
        
        # Ajouter le créateur comme participant
        ChatParticipant.objects.create(
            room=room,
            user=request.user
        )
        
        messages.success(request, f"Salon '{name}' créé avec succès!")
        return redirect('chat:chat_room', slug=room.slug)
    
    return render(request, 'chat/create_room.html')


@login_required
@require_POST
def delete_message(request, message_id):
    """Supprimer un message (soft delete)"""
    try:
        message = get_object_or_404(ChatMessage, id=message_id)
        
        # Vérifier que l'utilisateur est bien l'expéditeur
        if message.sender != request.user:
            return JsonResponse({
                'success': False,
                'error': "Vous ne pouvez supprimer que vos propres messages."
            }, status=403)
        
        # Vérifier que le message n'est pas déjà supprimé
        if message.is_deleted:
            return JsonResponse({
                'success': False,
                'error': "Ce message a déjà été supprimé."
            }, status=400)
        
        # Soft delete du message
        message.soft_delete()
        
        return JsonResponse({
            'success': True,
            'message_id': message_id,
            'deleted_text': f"{message.sender.first_name} {message.sender.last_name} a supprimé ce message".strip() or f"{message.sender.username} a supprimé ce message"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def edit_message(request, message_id):
    """Modifier un message"""
    try:
        import json
        from django.utils import timezone
        
        message = get_object_or_404(ChatMessage, id=message_id)
        
        # Vérifier que l'utilisateur est bien l'expéditeur
        if message.sender != request.user:
            return JsonResponse({
                'success': False,
                'error': "Vous ne pouvez modifier que vos propres messages."
            }, status=403)
        
        # Vérifier que le message n'est pas supprimé
        if message.is_deleted:
            return JsonResponse({
                'success': False,
                'error': "Impossible de modifier un message supprimé."
            }, status=400)
        
        # Récupérer le nouveau contenu
        data = json.loads(request.body)
        new_content = data.get('content', '').strip()
        
        if not new_content:
            return JsonResponse({
                'success': False,
                'error': "Le message ne peut pas être vide."
            }, status=400)
        
        # Mettre à jour le message
        message.content = new_content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()
        
        return JsonResponse({
            'success': True,
            'message_id': message_id,
            'content': new_content,
            'edited_at': message.edited_at.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
