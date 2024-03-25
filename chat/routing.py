from django.urls import path, include
from .consumers import GetChatMessageAll, GetChatRoomListByUser, GetGroupChatListByUser, GetGroupChatMessageAll

websocket_urlpatterns = [
    # Chat
    path('<int:chat_room_id>', GetChatMessageAll.as_asgi()),
    path('list', GetChatRoomListByUser.as_asgi()),
    # Group
    path('group/list', GetGroupChatListByUser.as_asgi()),
    path('group/message/all/<int:group_chat_room_id>', GetGroupChatMessageAll.as_asgi(), )
]
