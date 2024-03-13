from django.urls import path,include
from channels.routing import URLRouter
from users.routing import websocket_urlpatterns as user_websocket_urlpatterns
from posts.routing import websocket_urlpatterns as post_websocket_urlpatterns
from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
websocket_urlpatterns = [
    path('chat/', URLRouter(chat_websocket_urlpatterns)),
    path('users/', URLRouter(user_websocket_urlpatterns)),
    path('posts/', URLRouter(post_websocket_urlpatterns)),
]