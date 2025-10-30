"""
ASGI config for smartcampus project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings')

# Initialiser Django ASGI application tôt pour s'assurer que AppRegistry est populated
# avant d'importer le code qui peut importer des ORM models.
django_asgi_app = get_asgi_application()

# Importer le routing WebSocket et le middleware d'auth après l'initialisation Django
from chat.routing import websocket_urlpatterns
from chat.auth_middleware import SessionAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        SessionMiddlewareStack(
            SessionAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            )
        )
    ),
})
