from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from posts.models import Post
from users.models import CustomUser, UserStory
from users.serializers import StoryUserSerializer, UserForComments, SelfStorySerializers


class UserInformationAboutSelf(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            await self.channel_layer.group_add(
                f'information_about_user_{self.scope["user"].id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'information_about_user_{self.scope["user"].id}', {
                    "type": "send_user_information",

                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_user_information(self, event):
        data = await self.get_user(self.scope['user'])
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_user(self, user):
        data = {
            "username": user.username,
            "email": user.email,
            "followers": user.count_followers(),
            "following": user.count_following(),
            "user_image": user.user_image.url if user.user_image else "",
            "user_bio": user.user_bio,
            "user_birth_date": user.user_birth_date,
            "post_count": Post.objects.filter(author=user).count()
        }
        return data


class UserInformationByID(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            user_id = self.scope['url_route']['kwargs']['user_id']
            await self.channel_layer.group_add(
                f'information_about_user_{user_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'information_about_user_{user_id}', {
                    "type": "send_user_information_by_id",

                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_user_information_by_id(self, event):
        user_id = self.scope['url_route']['kwargs']['user_id']
        data = await self.get_user_by_id(user_id)

        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            data = {
                "username": user.username,
                "email": user.email,
                "followers": user.count_followers(),
                "following": user.count_following(),
                "user_image": user.user_image.url if user.user_image else "",
                "user_bio": user.user_bio,
                "user_birth_date": user.user_birth_date,
                "post_count": Post.objects.filter(author=user).count()
            }
        except CustomUser.DoesNotExist:
            data = {"error": "User not found"}
        return data


class FollowingUserStories(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            await self.channel_layer.group_add(
                f'get_all_stories',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'get_all_stories', {
                    "type": "send_stories_all",
                }
            )

    async def disconnect(self, code):
        await self.close()

    async def send_stories_all(self, event):
        data = await self.get_stories_all()
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_stories_all(self):
        stories = UserStory.objects.filter(user__in=self.scope['user'].get_following())
        data = StoryUserSerializer(stories, many=True).data
        return data


class UserStoryByID(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            user_id = self.scope['url_route']['kwargs']['user_id']
            await self.channel_layer.group_add(
                f'get_stories_by_id_{user_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'get_stories_by_id_{user_id}', {
                    "type": "send_stories_by_id",
                }
            )

    async def disconnect(self, code):
        await self.close()

    async def send_stories_by_id(self, event):
        user_id = self.scope['url_route']['kwargs']['user_id']
        data = await self.get_stories_by_id(user_id)
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_stories_by_id(self, user_id):
        try:
            # self_user = self.scope['user']
            following_users = CustomUser.objects.get(id=user_id).following.all()
            stories = UserStory.objects.filter(user=following_users).order_by('-created_at')[:5]
            # user_notifications = list(chain(user_notifications_first, user_notifications_second))
            data = StoryUserSerializer(stories, many=True).data
        except CustomUser.DoesNotExist:
            data = {"error": "User not found"}
        return data


class GetStoryByID(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            story_id = self.scope['url_route']['kwargs']['story_id']
            await self.channel_layer.group_add(
                f'get_story_by_id_{story_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'get_story_by_id_{story_id}', {
                    "type": "send_story_by_id",
                }
            )

    async def disconnect(self, code):
        await self.close()

    async def send_story_by_id(self, event):
        story_id = self.scope['url_route']['kwargs']['story_id']
        data = await self.get_story_by_id(story_id)
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_story_by_id(self, story_id):
        try:
            story = UserStory.objects.get(id=story_id)
            data = {
                "story_id": story.id,
                "story_title": story.story.title,
                "story_image": story.story.image.url,
                "story_created_at": story.created_at,
                "likes": story.likes.count(),
            }
        except UserStory.DoesNotExist:
            data = {"error": "Story not found"}
        return data


class SelfUserStory(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            await self.channel_layer.group_add(
                f'get_self_stories_{self.scope["user"].id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'get_self_stories_{self.scope["user"].id}', {
                    "type": "send_self_stories",
                }
            )

    async def disconnect(self, code):
        await self.close()

    async def send_self_stories(self, event):
        data = await self.get_self_stories()
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_self_stories(self):
        stories = UserStory.objects.filter(user=self.scope['user']).order_by('-created_at').last()
        if stories:
            data = SelfStorySerializers(stories).data
            return data
        else:
            data = {"error": "Story not found"}
        return data
