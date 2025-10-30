from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .mongo_models import ChatRoomMongo, ChatMessageMongo, ChatParticipantMongo
from bson import ObjectId


@login_required
def room_list(request):
    """Liste de tous les salons de chat (MongoDB)"""
    # Tous les salons actifs
    all_rooms = ChatRoomMongo.get_all()
    
    # Filtrer les salons publics et ajouter 'id' pour les templates
    public_rooms = []
    for room in all_rooms:
        if room.get('room_type') == 'public' and room.get('is_active', True):
            room['id'] = str(room.get('_id', ''))
            public_rooms.append(room)
    
    # Salons auxquels l'utilisateur participe
    user_rooms = ChatRoomMongo.get_user_rooms(request.user.id)
    filtered_user_rooms = []
    for room in user_rooms:
        if room.get('room_type') != 'public' and room.get('is_active', True):
            room['id'] = str(room.get('_id', ''))
            filtered_user_rooms.append(room)
    
    context = {
        'public_rooms': public_rooms,
        'user_rooms': filtered_user_rooms,
    }
    return render(request, 'chat/room_list.html', context)


@login_required
def chat_room(request, slug):
    """Interface de chat pour un salon spécifique (MongoDB)"""
    room = ChatRoomMongo.get_by_slug(slug)
    
    if not room or not room.get('is_active', True):
        messages.error(request, "Salon introuvable.")
        return redirect('chat:room_list')
    
    room_id = str(room['_id'])
    
    # Vérifier les permissions
    if room.get('room_type') != 'public':
        if request.user.id not in room.get('participant_ids', []):
            messages.error(request, "Vous n'avez pas accès à ce salon.")
            return redirect('chat:room_list')
    
    # Ajouter l'utilisateur aux participants s'il n'y est pas déjà
    participant = ChatParticipantMongo.get_or_create(
        room_id=room_id,
        user_id=request.user.id,
        user_email=request.user.email,
        user_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    )
    
    # Réinitialiser le compteur de messages non lus
    ChatParticipantMongo.reset_unread_count(room_id, request.user.id)
    
    # Récupérer les 50 derniers messages
    messages_list = ChatMessageMongo.get_room_messages(room_id, limit=50)
    
    # Convertir _id en id pour chaque message (Django templates n'acceptent pas les underscores)
    for msg in messages_list:
        msg['id'] = str(msg.get('_id', ''))
    
    # Récupérer les participants
    participants = ChatParticipantMongo.get_room_participants(room_id)
    online_participants = [p for p in participants if p.get('is_online', False)]
    
    # Convertir _id en id pour le room aussi
    room['id'] = str(room.get('_id', ''))
    
    # Obtenir l'ID de l'utilisateur
    user_id = getattr(request.user, 'id', None) or getattr(request.user, 'pk', None)
    
    context = {
        'room': room,
        'messages': messages_list,
        'online_participants': online_participants,
        'participants_count': len(participants),
        'user_id': user_id,
    }
    return render(request, 'chat/chat_room.html', context)


@login_required
def create_room(request):
    """Créer un nouveau salon de chat (MongoDB)"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        room_type = request.POST.get('room_type', 'public')
        
        if not name:
            messages.error(request, "Le nom du salon est requis.")
            return render(request, 'chat/create_room.html')
        
        # Générer le slug
        from django.utils.text import slugify
        slug = slugify(name)
        
        # Vérifier si un salon avec ce slug existe déjà
        if ChatRoomMongo.get_by_slug(slug):
            messages.error(request, "Un salon avec ce nom existe déjà.")
            return render(request, 'chat/create_room.html')
        
        # Créer le salon
        room = ChatRoomMongo.create(
            name=name,
            slug=slug,
            description=description,
            room_type=room_type,
            created_by_id=request.user.id,
            created_by_email=request.user.email,
            created_by_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            participant_ids=[request.user.id]
        )
        
        # Ajouter le créateur comme participant
        ChatParticipantMongo.create(
            room_id=str(room['_id']),
            user_id=request.user.id,
            user_email=request.user.email,
            user_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        )
        
        messages.success(request, f"Salon '{name}' créé avec succès!")
        return redirect('chat:chat_room', slug=slug)
    
    return render(request, 'chat/create_room.html')


@login_required
@require_POST
def delete_message(request, message_id):
    """Supprimer un message (soft delete) - MongoDB"""
    try:
        # Convertir message_id en ObjectId
        try:
            obj_id = ObjectId(message_id)
        except:
            return JsonResponse({
                'success': False,
                'error': "ID de message invalide."
            }, status=400)
        
        message = ChatMessageMongo.get_by_id(obj_id)
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': "Message introuvable."
            }, status=404)
        
        # Vérifier que l'utilisateur est bien l'expéditeur
        if message.get('sender_id') != request.user.id:
            return JsonResponse({
                'success': False,
                'error': "Vous ne pouvez supprimer que vos propres messages."
            }, status=403)
        
        # Vérifier que le message n'est pas déjà supprimé
        if message.get('is_deleted', False):
            return JsonResponse({
                'success': False,
                'error': "Ce message a déjà été supprimé."
            }, status=400)
        
        # Soft delete du message
        ChatMessageMongo.soft_delete(obj_id, request.user.id, message.get('sender_name'))
        
        return JsonResponse({
            'success': True,
            'message_id': message_id,
            'deleted_text': f"{message.get('sender_name')} a supprimé ce message"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def edit_message(request, message_id):
    """Modifier un message - MongoDB"""
    try:
        import json
        from datetime import datetime
        
        # Convertir message_id en ObjectId
        try:
            obj_id = ObjectId(message_id)
        except:
            return JsonResponse({
                'success': False,
                'error': "ID de message invalide."
            }, status=400)
        
        message = ChatMessageMongo.get_by_id(obj_id)
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': "Message introuvable."
            }, status=404)
        
        # Vérifier que l'utilisateur est bien l'expéditeur
        if message.get('sender_id') != request.user.id:
            return JsonResponse({
                'success': False,
                'error': "Vous ne pouvez modifier que vos propres messages."
            }, status=403)
        
        # Vérifier que le message n'est pas supprimé
        if message.get('is_deleted', False):
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
        result = ChatMessageMongo.edit_message(obj_id, new_content)
        
        return JsonResponse({
            'success': True,
            'message_id': message_id,
            'content': new_content,
            'edited_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
