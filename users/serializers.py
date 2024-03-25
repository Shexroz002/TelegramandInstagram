from rest_framework import serializers
from .models import CustomUser, Story, UserStory, ProfileImage
from .validate_functions import validate_password, validate_image_type


class ProfileImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ['id', 'photo', 'date']


class SelfUserSerializers(serializers.ModelSerializer):
    user_image = ProfileImageSerializers(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'user_image']


class CustomUserSerializers(serializers.ModelSerializer):
    followers = serializers.StringRelatedField(many=True, read_only=True)
    following = serializers.StringRelatedField(many=True, read_only=True)
    user_image = ProfileImageSerializers(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_image', 'user_bio', 'user_birth_date', 'followers', 'following', ]
        extra_kwargs = {
            'user_image': {'required': False},
            'user_bio': {'required': False},
            'user_birth_date': {'required': False},
            'username': {'required': True},
            'email': {'required': False},
        }


class UserForComments(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'user_image', ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user_image'] = instance.get_user_last_image().photo.url if instance.get_user_last_image() else ""
        return ret


class StorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"


class StoryUserSerializer(serializers.ModelSerializer):
    story = StorySerializers(read_only=True)
    user = UserForComments(read_only=True)

    class Meta:
        model = UserStory
        fields = ['id', 'story', 'user', 'created_at']


class SelfStorySerializers(serializers.ModelSerializer):
    story = StorySerializers(read_only=True)
    time_ago = serializers.CharField()

    class Meta:
        model = UserStory
        fields = ['id', 'story', 'likes', 'time_ago']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['story_detail'] = {
            "user_seen": UserForComments(instance.seen_user.all(), many=True).data,
            "likes": instance.likes.count(),
            "user_seen_count": instance.seen_user.count(),
            # "story_created_at": instance.created_at,
        }

        return ret
