from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import ChatMessage, ChatRoom, GroupChatMessage, GroupChat
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


class GetGroupChatListByUser(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            user_id = self.scope['user'].id
            await self.channel_layer.group_add(
                f'group_chat_list',
                self.channel_name
            )
            await self.channel_layer.group_send(
                'group_chat_list', {
                    "type": "send_group_chat_list",
                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_group_chat_list(self, event):
        data = await self.get_group_chat_list()
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_group_chat_list(self):
        user_id = self.scope['user'].id
        group_chats = GroupChat.objects.filter(users=user_id).order_by('created_at')
        data = []
        for group_chat in group_chats:
            print(group_chat.get_last_message().message.message_type)
            if group_chat.get_last_message().message.message_type == 'text':
                last_message = group_chat.get_last_message().message.message
                last_message_time = group_chat.get_last_message().message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif group_chat.get_last_message().message.message_type == 'image':
                last_message = 'You have Image'
                last_message_time = group_chat.get_last_message().message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif group_chat.get_last_message().message.message_type == 'video':
                last_message = 'You have Video'
                last_message_time = group_chat.get_last_message().message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif group_chat.get_last_message().message.message_type == 'voice':
                last_message = 'You have Voice'
                last_message_time = group_chat.get_last_message().message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif group_chat.get_last_message().message.message_type in ['word', 'pdf', 'excel']:
                last_message = 'You have Document'
                last_message_time = group_chat.get_last_message().message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif group_chat.get_last_message().message.message_type == 'forward_post':
                last_message = 'You have forward post'
                last_message_time = group_chat.get_last_message().message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif group_chat.get_last_message().message.message_type == 'forward_message':
                last_message = 'You have forward message'
                last_message_time = group_chat.get_last_message().message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_message = 'You have Message'
                last_message_time = group_chat.get_last_message().message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            info = {
                "group_chat_id": group_chat.id,
                "group_name": group_chat.group_name,
                "group_image": group_chat.group_image.url if group_chat.group_image else "",
                "last_message": last_message,
                "unread_message": group_chat.unread_message_count(self.scope['user']),
                "last_message_time": last_message_time
            }
            data.append(info)
        return data


class GetGroupChatMessageAll(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            group_chat_room_id = self.scope['url_route']['kwargs']['group_chat_room_id']
            check_user = await self.check_user(group_chat_room_id)
            if check_user:
                await self.channel_layer.group_add(
                    f'group_chat_message_all_{group_chat_room_id}',
                    self.channel_name
                )
                await self.channel_layer.group_send(
                    f'group_chat_message_all_{group_chat_room_id}', {
                        "type": "send_group_chat_message_all",
                    })
            else:
                await self.close()

    async def disconnect(self, close_code):
        await self.close()

    async def send_group_chat_message_all(self, event):
        data = await self.get_group_chat_message_all()
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_group_chat_message_all(self):
        chat_room_id = self.scope['url_route']['kwargs']['group_chat_room_id']
        chat_messages = GroupChatMessage.objects.filter(group_chat_id=chat_room_id).order_by('message__created_at')
        return ChatMessageSerializers(chat_messages, many=True).data

    @database_sync_to_async
    def check_user(self, group_chat_room_id):
        try:
            group_chat = GroupChat.objects.get(id=group_chat_room_id)
            return self.scope["user"] in group_chat.users.all()
        except GroupChat.DoesNotExist:
            return False
