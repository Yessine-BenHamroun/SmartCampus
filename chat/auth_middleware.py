"""
Middleware d'authentification personnalisé pour les WebSockets
"""
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()


@database_sync_to_async
def get_user_from_session(session):
    """
    Récupère l'utilisateur depuis les données de session
    """
    if not session.get('is_authenticated'):
        return AnonymousUser()
    
    user_data = session.get('user')
    if not user_data:
        return AnonymousUser()
    
    # Essayer de récupérer l'utilisateur par email ou username
    email = user_data.get('email')
    username = user_data.get('username')
    
    user = None
    if email:
        user = User.objects.filter(email=email).first()
    if not user and username:
        user = User.objects.filter(username=username).first()
    
    if user:
        return user
    
    # Créer un utilisateur si nécessaire
    try:
        user = User.objects.create_user(
            username=username or email.split('@')[0],
            email=email or '',
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            password=User.objects.make_random_password()
        )
        return user
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return AnonymousUser()


class SessionAuthMiddleware(BaseMiddleware):
    """
    Middleware qui authentifie les utilisateurs pour les WebSockets
    en utilisant les données de session
    """
    
    async def __call__(self, scope, receive, send):
        # Récupérer la session
        session = scope.get('session', {})
        
        # Récupérer l'utilisateur depuis la session
        scope['user'] = await get_user_from_session(session)
        
        return await super().__call__(scope, receive, send)
