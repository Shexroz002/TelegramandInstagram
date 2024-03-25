from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from posts.models import Post
from posts.serializers import CommentPostSerializer
from users.serializers import ProfileImageSerializers


class UserFollowingPosts(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
            await self.channel_layer.group_add(
                f'following_post_all',
                self.channel_name
            )
            await self.channel_layer.group_send(
                f'following_post_all', {
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
                "author_image": post.author.get_user_last_image().photo.url if post.author.get_user_last_image() else "",
                "post_image": post.post_image.url,
                "post_text": post.title,
                "post_date": post.time_ago(),
                "likes": post.likes.count(),
                "get_likes_id": [like.id for like in post.likes.all()],
                "comments": post.count_comments(),
                "liked": post.likes.filter(id=user.id).exists(),
                "saved": post.saved_post.filter(user=user).exists(),
                "get_last_three_like_user_image_url": post.get_last_three_like_user_image_url(),
                "last_comment": {
                    "comment": post.get_comments().last().comment if post.get_comments().last() else "",
                    "comment_author": post.get_comments().last().user.username if post.get_comments().last() else "",
                } if post.get_comments().last() else "",

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

