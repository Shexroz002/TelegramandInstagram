from itertools import chain

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import NotificationModel
from .serializers import NotificationModelSerializers


class NotificationForUser(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            user_id = self.scope['user'].id
            await self.channel_layer.group_add(
                f'notification_user_{user_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'notification_user_{user_id}', {
                    "type": "send_notification_user",
                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_notification_user(self, event):
        data = await self.get_notification_user()
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_notification_user(self):
        user = self.scope['user']
        user_notifications = (NotificationModel.objects.filter(notification_visible_to_user=user)
                              .order_by('created_at').last())
        if user_notifications:
            serializer_data = NotificationModelSerializers(user_notifications)
            return serializer_data.data
        else:
            return {}


class UnReadNotificationCount(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            user_id = self.scope['user'].id
            await self.channel_layer.group_add(
                f'unread_notification_user_{user_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'unread_notification_user_{user_id}', {
                    "type": "send_unread_notification_user",
                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_unread_notification_user(self, event):
        data = await self.get_unread_notification_user()
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_unread_notification_user(self):
        user = self.scope['user']
        user_notifications = NotificationModel.objects.filter(notification_visible_to_user=user, is_seen=False).count()
        if user_notifications:
            return user_notifications
        else:
            return 0


class GetLastThirtyNotification(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            user_id = self.scope['user'].id
            await self.channel_layer.group_add(
                f'get_last_thirty_notification_user_{user_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'get_last_thirty_notification_user_{user_id}', {
                    "type": "send_last_thirty_notification_user",
                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_last_thirty_notification_user(self, event):
        data = await self.get_last_thirty_notification_user()
        await self.send_json({
            "data": data
        })

    # This method is used to get the last thirty notification of the user
    @database_sync_to_async
    def get_last_thirty_notification_user(self):
        user = self.scope['user']
        user_notifications_first = (NotificationModel.objects.filter(
            notification_visible_to_user=user, is_seen=False).order_by('-created_at'))
        user_notifications_second = (NotificationModel.objects.filter(
            notification_visible_to_user=user, is_seen=True).order_by('-created_at'))
        user_notifications = list(chain(user_notifications_first, user_notifications_second))
        for notification in user_notifications:
            print(notification.created_at)
        if user_notifications:
            serializer_data = NotificationModelSerializers(user_notifications, many=True)
            return serializer_data.data
        else:
            return []


class NotificationCount(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            user_id = self.scope['user'].id
            await self.channel_layer.group_add(
                f'notification_count_user_{user_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'notification_count_user_{user_id}', {
                    "type": "send_notification_count_user",
                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_notification_count_user(self, event):
        data = await self.get_notification_count_user()
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_notification_count_user(self):
        user = self.scope['user']
        user_notifications = NotificationModel.objects.filter(notification_visible_to_user=user, is_seen=False).count()
        if user_notifications:
            return user_notifications
        else:
            return 0
