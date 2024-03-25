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
    ReadChatRoomMessages,
    CreateGroupChatMessage,
    AddUserToGroupChat,
    MessageByMessageTypeForGroupChat,
    CreateForwardPost
)
urlpatterns = [
    # Chat Room
    path('room/create/<int:user_id>', CreateChatRoom.as_view(), name='create_chat_room'),
    path('room/message/<int:chat_room_id>', CreateChatRoomMessage.as_view(), name='create_chat_room_message'),
    path('room/message/action/<int:chat_message_id>', DeleteUpdateChatRoomMessageAndFiles.as_view(),
         name='delete_update_chat_room_message'),
    path('room/message/type/<int:chat_room_id>', GetChatRoomMessagesByMessageType.as_view(),
         name='get_chat_room_messages_by_message_type'),
    path('room/messages/<int:chat_room_id>', GetChatRoomMessages.as_view(), name='get_chat_room_messages'),
    path('room/messages/read/<int:message_id>', ReadChatRoomMessages.as_view(), name='read_chat_room_messages'),
    # Group Chat
    path('group/chat/create', CreateGroupChat.as_view(), name='create_group_chat'),
    path('group/chat/list', GroupChatList.as_view(), name='group_chat_list'),
    path('group/chat/<int:group_chat_id>', GetGroupChat.as_view(), name='get_group_chat'),
    path('group/chat/message/create/<int:group_chat_id>', CreateGroupChatMessage.as_view(), name="create_chat_message"),
    path('group/chat/add/or/remove/user/<int:group_chat_id>', AddUserToGroupChat.as_view(), name="add_or_remove_user"),
    path('group/message/type/<int:group_chat_id>', MessageByMessageTypeForGroupChat.as_view(),
         name='get_group_chat_messages_by_message_type'),
    path('forward/post', CreateForwardPost.as_view(), name='create_forward_post')


]