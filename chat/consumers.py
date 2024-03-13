from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import ChatMessage, ChatRoom
from .serializers import ChatMessageSerializers
from django.db.models import Q
import json


class GetChatMessageAll(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            chat_room_id = self.scope['url_route']['kwargs']['chat_room_id']
            await self.channel_layer.group_add(
                f'chat_message_all_{chat_room_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'chat_message_all_{chat_room_id}', {
                    "type": "send_chat_message_all",
                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_chat_message_all(self, event):
        data = await self.get_chat_message_all()
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_chat_message_all(self):
        chat_room_id = self.scope['url_route']['kwargs']['chat_room_id']
        chat_messages = ChatMessage.objects.filter(chat_room_id=chat_room_id).order_by('created_at')
        return ChatMessageSerializers(chat_messages, many=True).data


class GetChatRoomListByUser(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            user_id = self.scope['user'].id
            await self.channel_layer.group_add(
                f'chat_room_list_{user_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'chat_room_list_{user_id}', {
                    "type": "send_chat_room_list",
                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_chat_room_list(self, event):
        data = await self.get_chat_room_list()
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_chat_room_list(self):
        user_id = self.scope['user'].id
        chat_rooms = ChatRoom.objects.filter(Q(first_user=user_id) | Q(second_user=user_id)).order_by('created_at')
        data = []
        for chat_room in chat_rooms:
            if chat_room.get_last_message().message.message_type == 'text':
                last_message = chat_room.get_last_message().message.message
                last_message_time = chat_room.get_last_message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif chat_room.get_last_message().message.message_type == 'image':
                last_message = 'You have Image'
                last_message_time = chat_room.get_last_message().created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif chat_room.get_last_message().message.message_type == 'video':
                last_message = 'You have Video'
                last_message_time = chat_room.get_last_message().created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif chat_room.get_last_message().message.message_type == 'voice':
                last_message = 'You have Voice'
                last_message_time = chat_room.get_last_message().created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif chat_room.get_last_message().message.message_type in ['word', 'pdf', 'excel']:
                last_message = 'You have Document'
                last_message_time = chat_room.get_last_message().created_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_message = 'You have Message'
                last_message_time = chat_room.get_last_message().created_at.strftime("%Y-%m-%d %H:%M:%S")
            info = {
                "chat_room_id": chat_room.id,
                "last_message": last_message,
                "unread_message": chat_room.count_unread_messages(),
                "last_message_time": last_message_time
            }
            if chat_room.first_user == self.scope['user']:
                info['user_id'] = chat_room.second_user.id
                info['username'] = chat_room.second_user.username
                info['user_image'] = chat_room.second_user.user_image.url if chat_room.second_user.user_image else ""

            else:
                info['user_id'] = chat_room.first_user.id
                info['username'] = chat_room.first_user.username
                info['user_image'] = chat_room.first_user.user_image.url if chat_room.first_user.user_image else ""
            data.append(info)
        return data
