from django.shortcuts import get_object_or_404
from rest_framework import response, status, views
from .models import CustomUser
from .serializers import CustomUserSerializers
import base64
from .celery_task_for_users import create_user_task


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
