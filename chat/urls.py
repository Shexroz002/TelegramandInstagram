from django.urls import path
from .views import (
    CreateChatRoom,
    CreateChatRoomMessage,
    DeleteUpdateChatRoomMessageAndFiles,
    GetChatRoomMessagesByMessageType,
    CreateGroupChat,
    GroupChatList,
    GetGroupChat,
    GetChatRoomMessages,
    ReadChatRoomMessages
)
urlpatterns = [
    path('room/create/<int:user_id>', CreateChatRoom.as_view(), name='create_chat_room'),
    path('room/message/<int:chat_room_id>', CreateChatRoomMessage.as_view(), name='create_chat_room_message'),
    path('room/message/action/<int:chat_message_id>', DeleteUpdateChatRoomMessageAndFiles.as_view(),
         name='delete_update_chat_room_message'),
    path('room/message/type/<int:chat_room_id>', GetChatRoomMessagesByMessageType.as_view(),
         name='get_chat_room_messages_by_message_type'),
    path('group/chat/create', CreateGroupChat.as_view(), name='create_group_chat'),
    path('group/chat/list', GroupChatList.as_view(), name='group_chat_list'),
    path('group/chat/<int:group_chat_id>', GetGroupChat.as_view(), name='get_group_chat'),
    path('room/messages/<int:chat_room_id>', GetChatRoomMessages.as_view(), name='get_chat_room_messages'),
    path('room/messages/read/<int:message_id>', ReadChatRoomMessages.as_view(), name='read_chat_room_messages')
]