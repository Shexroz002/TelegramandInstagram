import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from core_settings.main_routing import websocket_urlpatterns as main_websocket_urlpatterns
from users.middleware import TokenAuthMiddlewareStack
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_settings.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'https': get_asgi_application(),
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            main_websocket_urlpatterns
        )
    )
})
