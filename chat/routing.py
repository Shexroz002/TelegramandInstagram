from django.urls import path, include
from .consumers import GetChatMessageAll, GetChatRoomListByUser
websocket_urlpatterns = [
    path('<int:chat_room_id>', GetChatMessageAll.as_asgi()),
    path('list', GetChatRoomListByUser.as_asgi())
]
