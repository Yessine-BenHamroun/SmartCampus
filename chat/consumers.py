import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime
from .mongo_models import ChatRoomMongo, ChatMessageMongo, ChatParticipantMongo
from bson import ObjectId


class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer WebSocket pour gérer les messages en temps réel"""
    
    @database_sync_to_async
    def get_user(self, user_id):
        """Récupérer l'objet User réel depuis la DB"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    async def connect(self):
        """Appelé quand le WebSocket se connecte"""
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        
        # Récupérer l'utilisateur réel (pas le LazyObject)
        user = self.scope['user']
        
        # Vérifier que l'utilisateur est authentifié
        if not user.is_authenticated:
            await self.close()
            return
        
        # Convertir le UserLazyObject en vrai User pour les requêtes DB
        self.user = await self.get_user(user.id if hasattr(user, 'id') else user.pk)
        if not self.user:
            await self.close()
            return
        
        # Rejoindre le groupe de chat
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Marquer l'utilisateur comme en ligne
        await self.set_user_online(True)
        
        # Notifier les autres utilisateurs
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.user.username,
                'user_id': self.user.id,
                'status': 'online'
            }
        )
        
        print(f"✅ {self.user.username} connected to room {self.room_slug}")
    
    async def disconnect(self, close_code):
        """Appelé quand le WebSocket se déconnecte"""
        # Vérifier que self.user existe (peut ne pas exister si connexion a échoué)
        if not hasattr(self, 'user') or not self.user:
            return
        
        # Marquer l'utilisateur comme hors ligne
        await self.set_user_online(False)
        
        # Notifier les autres utilisateurs
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.user.username,
                'user_id': self.user.id,
                'status': 'offline'
            }
        )
        
        # Quitter le groupe de chat
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        print(f"❌ {self.user.username} disconnected from room {self.room_slug}")
    
    async def receive(self, text_data):
        """Appelé quand un message est reçu du WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                message_content = data.get('message', '').strip()
                
                if not message_content:
                    return
                
                # Sauvegarder le message dans la DB
                message = await self.save_message(message_content)
                
                # Construire le nom d'affichage (prénom + nom ou username)
                display_name = f"{self.user.first_name} {self.user.last_name}".strip()
                if not display_name:
                    display_name = self.user.username
                
                # Envoyer le message à tout le groupe
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message_content,
                        'username': self.user.username,
                        'display_name': display_name,
                        'user_id': self.user.id,
                        'timestamp': message['timestamp'],
                        'message_id': message['id']
                    }
                )
            
            elif message_type == 'typing':
                # Indicateur "en train d'écrire..."
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'username': self.user.username,
                        'user_id': self.user.id,
                        'is_typing': data.get('is_typing', False)
                    }
                )
            
            elif message_type == 'delete_message':
                # Suppression de message
                message_id = data.get('message_id')
                if message_id:
                    success = await self.delete_message(message_id)
                    if success:
                        # Construire le texte de suppression
                        display_name = f"{self.user.first_name} {self.user.last_name}".strip()
                        if not display_name:
                            display_name = self.user.username
                        
                        # Notifier tout le groupe
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'message_deleted',
                                'message_id': message_id,
                                'deleted_text': f"{display_name} a supprimé ce message",
                                'user_id': self.user.id
                            }
                        )
            
            elif message_type == 'edit_message':
                # Modification de message
                message_id = data.get('message_id')
                new_content = data.get('content', '').strip()
                
                if message_id and new_content:
                    result = await self.edit_message(message_id, new_content)
                    if result['success']:
                        # Notifier tout le groupe
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'message_edited',
                                'message_id': message_id,
                                'content': new_content,
                                'edited_at': result['edited_at'],
                                'user_id': self.user.id
                            }
                        )
        
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON received: {text_data}")
        except Exception as e:
            print(f"❌ Error in receive: {e}")
    
    async def chat_message(self, event):
        """Envoyer le message au WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'display_name': event.get('display_name', event['username']),
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))
    
    async def user_status(self, event):
        """Envoyer le statut utilisateur au WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'username': event['username'],
            'user_id': event['user_id'],
            'status': event['status']
        }))
    
    async def typing_indicator(self, event):
        """Envoyer l'indicateur de frappe"""
        # Ne pas envoyer à soi-même
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'username': event['username'],
                'user_id': event['user_id'],
                'is_typing': event['is_typing']
            }))
    
    async def message_deleted(self, event):
        """Envoyer la notification de suppression de message"""
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
            'deleted_text': event['deleted_text'],
            'user_id': event['user_id']
        }))
    
    async def message_edited(self, event):
        """Envoyer la notification de modification de message"""
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'message_id': event['message_id'],
            'content': event['content'],
            'edited_at': event['edited_at'],
            'user_id': event['user_id']
        }))
    
    @database_sync_to_async
    def save_message(self, content):
        """Sauvegarder le message dans MongoDB"""
        try:
            room = ChatRoomMongo.get_by_slug(self.room_slug)
            if not room:
                print(f"❌ Room {self.room_slug} does not exist")
                return {'id': None, 'timestamp': datetime.utcnow().isoformat()}
            
            room_id = str(room['_id'])
            display_name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
            
            message = ChatMessageMongo.create(
                room_id=room_id,
                sender_id=self.user.id,
                sender_email=self.user.email,
                sender_name=display_name,
                content=content
            )
            
            return {
                'id': str(message['_id']),
                'timestamp': message['timestamp'].isoformat() if message.get('timestamp') else datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"❌ Error saving message: {e}")
            return {'id': None, 'timestamp': datetime.utcnow().isoformat()}
    
    @database_sync_to_async
    def set_user_online(self, is_online):
        """Mettre à jour le statut en ligne de l'utilisateur - MongoDB"""
        try:
            room = ChatRoomMongo.get_by_slug(self.room_slug)
            if not room:
                print(f"❌ Room {self.room_slug} does not exist")
                return
            
            room_id = str(room['_id'])
            display_name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
            
            # Créer ou récupérer le participant
            ChatParticipantMongo.get_or_create(
                room_id=room_id,
                user_id=self.user.id,
                user_email=self.user.email,
                user_name=display_name
            )
            
            # Mettre à jour le statut en ligne
            ChatParticipantMongo.set_online(room_id, self.user.id, is_online)
            
            # Mettre à jour last_seen
            ChatParticipantMongo.update_last_seen(room_id, self.user.id)
            
            # Réinitialiser le compteur si hors ligne
            if not is_online:
                ChatParticipantMongo.reset_unread_count(room_id, self.user.id)
        except Exception as e:
            print(f"❌ Error setting user online status: {e}")
    
    @database_sync_to_async
    def delete_message(self, message_id):
        """Supprimer un message (soft delete) - MongoDB"""
        try:
            obj_id = ObjectId(message_id)
            message = ChatMessageMongo.get_by_id(obj_id)
            
            if not message:
                print(f"❌ Message {message_id} does not exist")
                return False
            
            # Vérifier que l'utilisateur est l'expéditeur
            if message.get('sender_id') != self.user.id:
                print(f"❌ User {self.user.id} is not the sender of message {message_id}")
                return False
            
            # Vérifier que le message n'est pas déjà supprimé
            if message.get('is_deleted', False):
                return False
            
            display_name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
            ChatMessageMongo.soft_delete(obj_id, self.user.id, display_name)
            return True
        except Exception as e:
            print(f"❌ Error deleting message: {e}")
            return False
    
    @database_sync_to_async
    def edit_message(self, message_id, new_content):
        """Modifier un message - MongoDB"""
        try:
            obj_id = ObjectId(message_id)
            message = ChatMessageMongo.get_by_id(obj_id)
            
            if not message:
                print(f"❌ Message {message_id} does not exist")
                return {'success': False, 'error': 'Message introuvable'}
            
            # Vérifier que l'utilisateur est l'expéditeur
            if message.get('sender_id') != self.user.id:
                print(f"❌ User {self.user.id} is not the sender of message {message_id}")
                return {'success': False, 'error': 'Non autorisé'}
            
            if message.get('is_deleted', False):
                return {'success': False, 'error': 'Message supprimé'}
            
            # Mettre à jour le message
            ChatMessageMongo.edit_message(obj_id, new_content)
            
            return {
                'success': True,
                'edited_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"❌ Error editing message: {e}")
            return {'success': False, 'error': str(e)}
