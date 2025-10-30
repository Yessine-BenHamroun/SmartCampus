"""
Modèles MongoDB pour le chat
Ces classes wrappent les opérations MongoDB pour une utilisation similaire à Django ORM
"""
from datetime import datetime
from bson import ObjectId
from .mongodb_manager import mongodb


class ChatRoomMongo:
    """Modèle MongoDB pour les salons de chat"""
    
    @staticmethod
    def create(name, slug, room_type='public', description='', created_by_id=None, 
               created_by_email='', created_by_name='', participant_ids=None):
        """Créer un nouveau salon"""
        room_data = {
            'name': name,
            'slug': slug,
            'room_type': room_type,
            'description': description,
            'created_by_id': created_by_id,
            'created_by_email': created_by_email,
            'created_by_name': created_by_name,
            'created_at': datetime.now(),
            'is_active': True,
            'participant_ids': participant_ids or []
        }
        result = mongodb.rooms.insert_one(room_data)
        room_data['_id'] = result.inserted_id
        return room_data
    
    @staticmethod
    def get_by_slug(slug):
        """Récupérer un salon par son slug"""
        return mongodb.rooms.find_one({'slug': slug, 'is_active': True})
    
    @staticmethod
    def get_by_id(room_id):
        """Récupérer un salon par son ID"""
        if isinstance(room_id, str):
            room_id = ObjectId(room_id)
        return mongodb.rooms.find_one({'_id': room_id})
    
    @staticmethod
    def get_all(room_type=None, is_active=True):
        """Récupérer tous les salons"""
        query = {'is_active': is_active}
        if room_type:
            query['room_type'] = room_type
        return list(mongodb.rooms.find(query).sort('created_at', -1))
    
    @staticmethod
    def get_user_rooms(user_id):
        """Récupérer les salons d'un utilisateur"""
        return list(mongodb.rooms.find({
            'participant_ids': user_id,
            'is_active': True
        }).sort('created_at', -1))
    
    @staticmethod
    def update(room_id, **kwargs):
        """Mettre à jour un salon"""
        if isinstance(room_id, str):
            room_id = ObjectId(room_id)
        return mongodb.rooms.update_one({'_id': room_id}, {'$set': kwargs})
    
    @staticmethod
    def add_participant(room_id, user_id):
        """Ajouter un participant à un salon"""
        if isinstance(room_id, str):
            room_id = ObjectId(room_id)
        return mongodb.rooms.update_one(
            {'_id': room_id},
            {'$addToSet': {'participant_ids': user_id}}
        )


class ChatMessageMongo:
    """Modèle MongoDB pour les messages"""
    
    @staticmethod
    def create(room_id, sender_id, sender_email, sender_name, content):
        """Créer un nouveau message"""
        message_data = {
            'room_id': str(room_id),
            'sender_id': sender_id,
            'sender_email': sender_email,
            'sender_name': sender_name,
            'content': content,
            'timestamp': datetime.now(),
            'is_edited': False,
            'edited_at': None,
            'is_deleted': False,
            'deleted_at': None,
            'deleted_by_id': None,
            'deleted_by_name': ''
        }
        result = mongodb.messages.insert_one(message_data)
        message_data['_id'] = result.inserted_id
        return message_data
    
    @staticmethod
    def get_by_id(message_id):
        """Récupérer un message par son ID"""
        if isinstance(message_id, str):
            message_id = ObjectId(message_id)
        return mongodb.messages.find_one({'_id': message_id})
    
    @staticmethod
    def get_room_messages(room_id, limit=50, skip=0, include_deleted=False):
        """Récupérer les messages d'un salon"""
        query = {'room_id': str(room_id)}
        if not include_deleted:
            query['is_deleted'] = False
        
        return list(mongodb.messages.find(query)
                   .sort('timestamp', -1)
                   .skip(skip)
                   .limit(limit))
    
    @staticmethod
    def update(message_id, **kwargs):
        """Mettre à jour un message"""
        if isinstance(message_id, str):
            message_id = ObjectId(message_id)
        return mongodb.messages.update_one({'_id': message_id}, {'$set': kwargs})
    
    @staticmethod
    def edit_message(message_id, new_content):
        """Modifier un message"""
        if isinstance(message_id, str):
            message_id = ObjectId(message_id)
        return mongodb.messages.update_one(
            {'_id': message_id},
            {'$set': {
                'content': new_content,
                'is_edited': True,
                'edited_at': datetime.now()
            }}
        )
    
    @staticmethod
    def soft_delete(message_id, deleted_by_id, deleted_by_name):
        """Supprimer un message (soft delete)"""
        if isinstance(message_id, str):
            message_id = ObjectId(message_id)
        return mongodb.messages.update_one(
            {'_id': message_id},
            {'$set': {
                'is_deleted': True,
                'deleted_at': datetime.now(),
                'deleted_by_id': deleted_by_id,
                'deleted_by_name': deleted_by_name
            }}
        )


class ChatParticipantMongo:
    """Modèle MongoDB pour les participants"""
    
    @staticmethod
    def create(room_id, user_id, user_email, user_name):
        """Créer un participant"""
        participant_data = {
            'room_id': str(room_id),
            'user_id': user_id,
            'user_email': user_email,
            'user_name': user_name,
            'joined_at': datetime.now(),
            'last_seen': datetime.now(),
            'is_online': False,
            'unread_count': 0
        }
        result = mongodb.participants.insert_one(participant_data)
        participant_data['_id'] = result.inserted_id
        return participant_data
    
    @staticmethod
    def get_or_create(room_id, user_id, user_email, user_name):
        """Récupérer ou créer un participant"""
        participant = mongodb.participants.find_one({
            'room_id': str(room_id),
            'user_id': user_id
        })
        
        if not participant:
            return ChatParticipantMongo.create(room_id, user_id, user_email, user_name)
        return participant
    
    @staticmethod
    def get_room_participants(room_id):
        """Récupérer les participants d'un salon"""
        return list(mongodb.participants.find({'room_id': str(room_id)}))
    
    @staticmethod
    def set_online(room_id, user_id, is_online=True):
        """Définir le statut en ligne d'un participant"""
        return mongodb.participants.update_one(
            {'room_id': str(room_id), 'user_id': user_id},
            {'$set': {
                'is_online': is_online,
                'last_seen': datetime.now()
            }}
        )
    
    @staticmethod
    def update_last_seen(room_id, user_id):
        """Mettre à jour la dernière visite"""
        return mongodb.participants.update_one(
            {'room_id': str(room_id), 'user_id': user_id},
            {'$set': {'last_seen': datetime.now()}}
        )
    
    @staticmethod
    def reset_unread_count(room_id, user_id):
        """Réinitialiser le compteur de messages non lus"""
        return mongodb.participants.update_one(
            {'room_id': str(room_id), 'user_id': user_id},
            {'$set': {'unread_count': 0}}
        )
    
    @staticmethod
    def increment_unread_count(room_id, user_id):
        """Incrémenter le compteur de messages non lus"""
        return mongodb.participants.update_one(
            {'room_id': str(room_id), 'user_id': user_id},
            {'$inc': {'unread_count': 1}}
        )
