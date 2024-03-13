from rest_framework import serializers
from .models import CustomUser, Story, UserStory
from .validate_functions import validate_password, validate_image_type


class CustomUserSerializers(serializers.ModelSerializer):
    followers = serializers.StringRelatedField(many=True, read_only=True)
    following = serializers.StringRelatedField(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    user_image = serializers.ImageField(required=False, validators=[validate_image_type])

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'email', 'user_image', 'user_bio', 'user_birth_date', 'followers',
                  'following', ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
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


class StorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"


class StoryUserSerializer(serializers.ModelSerializer):
    story = StorySerializers(read_only=True)

    class Meta:
        model = UserStory
        fields = "__all__"
