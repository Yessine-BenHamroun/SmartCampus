"""
Middleware pour synchroniser l'authentification session avec Django auth
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class SessionAuthMiddleware:
    """
    Middleware qui synchronise l'authentification basée sur session
    avec le système d'authentification Django standard.
    
    Cela permet d'utiliser @login_required et request.user.is_authenticated
    même avec une authentification personnalisée basée sur JWT.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier si l'utilisateur est authentifié via session
        if request.session.get('is_authenticated'):
            user_data = request.session.get('user')
            
            if user_data:
                # Créer un objet User "virtuel" basé sur les données de session
                # Cela permet à @login_required et request.user de fonctionner
                try:
                    # Essayer de récupérer l'utilisateur réel de la DB
                    email = user_data.get('email')
                    username = user_data.get('username')
                    
                    # Chercher par email ou username
                    user = None
                    if email:
                        user = User.objects.filter(email=email).first()
                    if not user and username:
                        user = User.objects.filter(username=username).first()
                    
                    if user:
                        # Utilisateur trouvé dans la DB - mettre à jour ses infos
                        updated = False
                        if user_data.get('first_name') and user.first_name != user_data.get('first_name'):
                            user.first_name = user_data.get('first_name', '')
                            updated = True
                        if user_data.get('last_name') and user.last_name != user_data.get('last_name'):
                            user.last_name = user_data.get('last_name', '')
                            updated = True
                        if updated:
                            user.save()
                        request.user = user
                    else:
                        # Créer un utilisateur dans la DB Django locale
                        # Cela permet à @login_required de fonctionner correctement
                        user = User.objects.create_user(
                            username=username or email.split('@')[0],
                            email=email or '',
                            first_name=user_data.get('first_name', ''),
                            last_name=user_data.get('last_name', ''),
                            password=User.objects.make_random_password()  # Mot de passe aléatoire
                        )
                        request.user = user
                    
                    # Ajouter les données supplémentaires comme attributs
                    request.user.session_data = user_data
                    
                except Exception as e:
                    print(f"SessionAuthMiddleware error: {e}")
                    request.user = AnonymousUser()
            else:
                request.user = AnonymousUser()
        else:
            # Pas authentifié - laisser Django gérer
            if not hasattr(request, 'user'):
                request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response
