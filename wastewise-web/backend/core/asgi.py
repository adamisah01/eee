"""
ASGI config for WasteWise backend.
Combines Django HTTP, Django Admin, and Channels WebSocket routing.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from realtime.routing import websocket_urlpatterns

# Mount FastAPI alongside Django
from api.main import app as fastapi_app

django_asgi = get_asgi_application()


class ASGIRouter:
    """
    Custom ASGI router that sends /api/ requests to FastAPI
    and everything else to Django (including /admin/, /ws/).
    """

    def __init__(self):
        self.fastapi = fastapi_app
        self.django = ProtocolTypeRouter({
            'http': django_asgi,
            'websocket': AllowedHostsOriginValidator(
                URLRouter(websocket_urlpatterns)
            ),
        })

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            path = scope.get('path', '')
            if path.startswith('/api/'):
                await self.fastapi(scope, receive, send)
                return
        await self.django(scope, receive, send)


application = ASGIRouter()
