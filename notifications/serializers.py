from rest_framework import serializers

from chat.serializers import MessageSerializers
from .models import NotificationModel
from users.models import CustomUser
from posts.models import Post, CommentPost
from chat.models import ChatMessage, GroupChat
from users.models import UserStory
from users.serializers import StorySerializers, ProfileImageSerializers


# This serializer is used to get the user who is following the user
class NotificationFollowingUser(serializers.ModelSerializer):
    user_image = ProfileImageSerializers(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'user_image']
        read_only_fields = ['id', 'username', 'user_image']

    # This method is used to take the first photo of the user
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        user_image = ret.pop('user_image')
        if user_image:
            ret['user_image'] = user_image[0]['photo']
        return ret


# This serializer is used to get the post that the user liked


class NotificationPost(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'post_image']
        read_only_fields = ['id', 'title', 'post_image']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        data = {}
        if instance.get_last_like_user():
            data = {
                'id': instance.get_last_like_user().id,
                'username': instance.get_last_like_user().username,
                'user_image': instance.get_last_like_user().get_user_last_image().photo.url
            }
        ret['get_last_like_user'] = data if instance.get_last_like_user() else None
        return ret


# This serializer is used to get the chat message that the user received
class NotificationChatMessage(serializers.ModelSerializer):
    from_user = NotificationFollowingUser(read_only=True)
    message = MessageSerializers(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'created_at', 'from_user']
        read_only_fields = ['id', 'message', 'created_at']

    # This method is used to remove the None values from the response
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {key: value for key, value in ret.items() if value is not None}


class PostCommentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_image']


# This serializer is used to get the comment that the user received
class NotificationCommentPost(serializers.ModelSerializer):
    user = NotificationFollowingUser(read_only=True)
    post = PostCommentSerializers(read_only=True)

    class Meta:
        model = CommentPost
        fields = ['id', 'comment', 'date_commented', 'user', 'post']
        read_only_fields = ['id', 'comment', 'date_commented', 'user']

    # This method is used to remove the None values from the response
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {key: value for key, value in ret.items() if value is not None}


# This serializer is used to get the story that the user received
class NotificationUserStory(serializers.ModelSerializer):
    story = StorySerializers(read_only=True)
    user = NotificationFollowingUser(read_only=True)

    class Meta:
        model = UserStory
        fields = ['id', 'user', 'story', 'created_at']
        read_only_fields = ['id', 'user', 'story', 'created_at']

    # This method is used to remove the None values from the response
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {key: value for key, value in ret.items() if value is not None}


class GroupChatNotification(serializers.ModelSerializer):
    class Meta:
        model = GroupChat
        fields = ['id', 'group_name', ]
        read_only_fields = ['id', 'group_name']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        data = {}
        if instance.get_last_added_user():
            data = {
                'id': instance.get_last_added_user().id,
                'username': instance.get_last_added_user().username,
                'user_image': instance.get_last_added_user().get_user_last_image().photo.url
            }
        ret['get_last_added_user'] = data if instance.get_last_added_user() else None
        return ret


# This serializer is used to get the notification of the user
class NotificationModelSerializers(serializers.ModelSerializer):
    following_user = NotificationFollowingUser(read_only=True)
    post_like = NotificationPost(read_only=True)
    notification_chat = NotificationChatMessage(read_only=True)
    notification_comment = NotificationCommentPost(read_only=True)
    notification_story = NotificationUserStory(read_only=True)
    notification_type_int_to_str = serializers.CharField()
    notification_group = GroupChatNotification(read_only=True)
    time_ago = serializers.CharField()

    class Meta:
        model = NotificationModel
        fields = [
            'id',
            'following_user',
            'post_like',
            'notification_chat',
            'notification_comment',
            'notification_story',
            'notification_group',
            'notification_type_int_to_str',
            'is_seen',
            'time_ago'
        ]

    # This method is used to remove the None values from the response
    def to_representation(self, instance):
        print(instance.notification_chat)
        ret = super().to_representation(instance)
        return {key: value for key, value in ret.items() if value is not None}
