from rest_framework import serializers
from .models import CommentPost, Post, SavedPost
from users.serializers import CustomUserSerializers, UserForComments


class PostSerializer(serializers.ModelSerializer):
    author = CustomUserSerializers(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'post_image']
        extra_kwargs = {
            'title': {'required': False},
            'post_image': {'required': False}
        }


class CommentPostSerializer(serializers.ModelSerializer):
    user = UserForComments(read_only=True)

    class Meta:
        model = CommentPost
        fields = ['user', 'comment', 'date_commented', 'id']
        extra_kwargs = {
            'comment': {'required': True},
            'user': {'required': False},
            'date_commented': {'required': False}

        }


class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    user = CustomUserSerializers()

    class Meta:
        model = SavedPost
        fields = '__all__'
