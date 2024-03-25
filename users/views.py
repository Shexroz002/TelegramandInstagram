from django.shortcuts import get_object_or_404
from rest_framework import response, status, views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
import json
from notifications.models import NotificationModel
from notifications.serializers import NotificationFollowingUser
from .models import CustomUser, UserStory, Story
from .serializers import CustomUserSerializers, SelfUserSerializers, StorySerializers
import base64
from .celery_task_for_users import create_user_task, create_following_notification_task, mentioned_user_for_story
from .validate_functions import validate_list_for_item_int


# Create your views here.
class UserRegister(views.APIView):
    @staticmethod
    def post(request):
        serializer_data = CustomUserSerializers(data=request.data)
        if serializer_data.is_valid():
            if 'user_image' in request.FILES:
                user_image = request.FILES['user_image']
                file_content_base64 = base64.b64encode(user_image.read()).decode('utf-8')
                file_info = {
                    'name': user_image.name,
                    'content_type': user_image.content_type,
                    'size': user_image.size,
                    'base64_content': file_content_base64,

                }
                del serializer_data.validated_data['user_image']
                create_user_task.delay(file_info, **serializer_data.validated_data)
                return response.Response(status=status.HTTP_201_CREATED)
            else:
                serializer_data.save()
                return response.Response(status=status.HTTP_201_CREATED)
            # return response.Response(status=status.HTTP_201_CREATED)
        else:
            return response.Response({"error": serializer_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdate(views.APIView):
    @staticmethod
    def get(request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer_data = CustomUserSerializers(user)
        return response.Response(serializer_data.data)

    @staticmethod
    def put(request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer_data = CustomUserSerializers(user, data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return response.Response(status=status.HTTP_200_OK)
        else:
            return response.Response({"error": serializer_data.errors}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class GetFollowers(views.APIView):
    @staticmethod
    def get(request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        followers = user.followers.all()
        serializer_data = CustomUserSerializers(followers, many=True)
        return response.Response(serializer_data.data)


class GetFollowing(views.APIView):
    @staticmethod
    def get(request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        following = user.following.all()
        serializer_data = CustomUserSerializers(following, many=True)
        return response.Response(serializer_data.data)


class Login(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return response.Response({'token': token.key, 'user_id': user.id})


class UserFollowingAddOrDelete(views.APIView):
    @staticmethod
    def get(request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        if request.user in user.followers.all():
            user.leave_followers(request.user)
            request.user.leave_following(request.user)
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            user.join_followers(request.user)
            request.user.join_following(request.user)
            create_following_notification_task.delay(request.user, user)
            return response.Response(status=status.HTTP_200_OK)


class UserDetail(views.APIView):
    @staticmethod
    def get(request):
        user = request.user
        data = {
            "user_id": user.id,
            "username": user.username,
            "user_image": user.get_user_last_image().photo.url if user.get_user_last_image() else "",
        }
        return response.Response(data)


class UserList(views.APIView):
    @staticmethod
    def get(request):
        users = CustomUser.objects.all()
        serializer_data = NotificationFollowingUser(users, many=True)
        return response.Response(serializer_data.data, status=status.HTTP_200_OK)


class CreateStory(views.APIView):
    @staticmethod
    def post(request):
        print(request.data)
        serializer_data = StorySerializers(data=request.data)
        users = request.data.get('users', None)

        # Check if the users are a list of integers
        if users is not None:
            users = users.split(',')
            users = [int(user) for user in users]
            if not validate_list_for_item_int(users):
                return response.Response({"error": "The users must be a list of integers"},
                                         status=status.HTTP_400_BAD_REQUEST)
        # Check if the serializer is valid
        if serializer_data.is_valid():
            story = serializer_data.save()
            creator = request.user
            user_story = UserStory.objects.create(user=creator, story=story)
            # if there are users, mentioned story for all users
            if users is not None:
                mentioned_user_for_story.delay(story.id, creator, users, user_story.id)
            return response.Response(serializer_data.data, status=status.HTTP_201_CREATED)
        else:
            return response.Response({"error": serializer_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class UpdateStory(views.APIView):
    @staticmethod
    def put(request, story_id):
        story = get_object_or_404(Story, id=story_id)
        serializer_data = StorySerializers(story, data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return response.Response(serializer_data.data, status=status.HTTP_200_OK)
        else:
            return response.Response({"error": serializer_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class DeleteStory(views.APIView):
    @staticmethod
    def delete(request, story_id):
        story = get_object_or_404(UserStory, id=story_id)
        story.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class StoryLikeByUsers(views.APIView):
    @staticmethod
    def get(request, user_story_id):
        user = request.user
        user_story = get_object_or_404(UserStory, id=user_story_id)
        if user in user_story.likes.all():
            user_story.likes.add(user)
            return response.Response(status=status.HTTP_200_OK)
        else:
            user_story.likes.remove(user)
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class StorySeenByUsers(views.APIView):
    @staticmethod
    def get(request, user_story_id):
        user = request.user
        user_story = get_object_or_404(UserStory, id=user_story_id)
        for story in user_story.seen_user.all():
            story.seen_by.add(user)
        return response.Response(status=status.HTTP_200_OK)
