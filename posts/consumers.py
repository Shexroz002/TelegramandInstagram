from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from posts.models import Post
from posts.serializers import CommentPostSerializer


class UserFollowingPosts(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            await self.channel_layer.group_add(
                f'following_posts_{self.scope["user"].id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'following_posts_{self.scope["user"].id}', {
                    "type": "send_following_posts",
                })

    async def disconnect(self, close_code):
        await self.close()

    async def send_following_posts(self, event):
        user = self.scope['user']
        data = await self.get_following_posts(user)
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_following_posts(self, user):
        following = user.following.all()
        posts = Post.objects.filter(author__in=following)
        data = []
        for post in posts:
            data.append({
                "id": post.id,
                "author": post.author.username,
                "author_id": post.author.id,
                "author_image": post.author.user_image.url if post.author.user_image else "",
                "post_image": post.post_image.url if post.post_image else "",
                "post_text": post.post_text,
                "post_date": post.post_date,
                "likes": post.likes.count(),
                "comments": post.comments.count()
            })

        return data


class PostGetAllComment(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            post_id = self.scope['url_route']['kwargs']['post_id']
            await self.channel_layer.group_add(
                f'post_comments_all{post_id}',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'post_comments_all{post_id}', {
                    "type": "send_comments_all",
                }
            )

    async def disconnect(self, code):
        await self.close()

    async def send_comments_all(self, event):
        post_id = self.scope['url_route']['kwargs']['post_id']
        data = await self.get_comments_all(post_id)
        await self.send_json({
            "data": data
        })

    @database_sync_to_async
    def get_comments_all(self, post_id):
        try:
            comments = Post.objects.get(id=post_id).get_comments()
            data = CommentPostSerializer(comments, many=True).data

        except Post.DoesNotExist:
            data = {"error": "comments not found"}
        return data
