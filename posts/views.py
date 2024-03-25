from django.shortcuts import get_object_or_404
from rest_framework import response, status, views
from .models import Post, CommentPost, SavedPost
from .serializers import PostSerializer, CommentPostSerializer, SavedPostSerializer, UpdatePostSerializer
from .celery_task import create_post_task, update_post_task
import base64
import os


class CreatePost(views.APIView):
    @staticmethod
    def get(request):
        following_post = Post.objects.filter(author__in=request.user.following.all())
        most_liked_commented = Post.objects.all().order_by('-likes', '-comment_post')[20]
        all_posts = following_post | most_liked_commented
        serializer_data = PostSerializer(all_posts, many=True)
        return response.Response(serializer_data.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        serializer_data = PostSerializer(data=request.data)
        if serializer_data.is_valid():
            image_file = request.FILES['post_image']
            title = request.data['title']
            file_content_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            file_info = {
                'name': image_file.name,
                'content_type': image_file.content_type,
                'size': image_file.size,
                'base64_content': file_content_base64,

            }
            create_post_task.delay(file_info, title, request.user.id)
            return response.Response(status=status.HTTP_201_CREATED)
        else:
            return response.Response({"error": serializer_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeletePost(views.APIView):
    @staticmethod
    def get(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer_data = PostSerializer(post)
        return response.Response(serializer_data.data)

    @staticmethod
    def put(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer_update = UpdatePostSerializer(post, data=request.data)
        if serializer_update.is_valid():
            if 'post_image' in request.FILES:
                image_file = request.FILES['post_image']
                title = serializer_update.data['title']
                file_content_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                file_info = {
                    'name': image_file.name,
                    'content_type': image_file.content_type,
                    'size': image_file.size,
                    'base64_content': file_content_base64,

                }
                update_post_task.delay(file_info, title, post_id)
                return response.Response(status=status.HTTP_200_OK)
            else:
                serializer_update.save()
                return response.Response(status=status.HTTP_200_OK)
        else:
            return response.Response({"error": serializer_update.errors}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class AllCommentGetFotPost(views.APIView):
    @staticmethod
    def get(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.get_comments()
        serializer_data = CommentPostSerializer(comments, many=True)
        data = {
            "post": post.title,
            "post_image": post.post_image.url,
            "author": post.author.username,
            "comments": serializer_data.data
        }
        return response.Response(data, status=status.HTTP_200_OK)


class CreateComment(views.APIView):
    @staticmethod
    def post(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer_data = CommentPostSerializer(data=request.data)
        if serializer_data.is_valid():
            serializer_data.save(user=request.user, post=post)
            return response.Response(serializer_data.data,status=status.HTTP_201_CREATED)
        else:
            return response.Response({"error": serializer_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteComment(views.APIView):
    @staticmethod
    def get(request, comment_id):
        comment = get_object_or_404(CommentPost, id=comment_id)
        serializer_data = CommentPostSerializer(comment)
        return response.Response(serializer_data.data)

    @staticmethod
    def put(request, comment_id):
        comment = get_object_or_404(CommentPost, id=comment_id)
        serializer_data = CommentPostSerializer(comment, data=request.data)
        if serializer_data.is_valid():
            serializer_data.save()
            return response.Response(serializer_data.data,status=status.HTTP_200_OK)
        else:
            return response.Response({"error": serializer_data.errors}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, comment_id):
        comment = get_object_or_404(CommentPost, id=comment_id)
        comment.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class LikePost(views.APIView):
    @staticmethod
    def get(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            post.likes.add(request.user)
            return response.Response(status=status.HTTP_200_OK)


class SavedPostByUser(views.APIView):
    @staticmethod
    def get(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        saved_post = SavedPost.objects.filter(user=request.user, post=post)
        if saved_post:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            SavedPost.objects.create(user=request.user, post=post)
            return response.Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        saved_post = SavedPost.objects.filter(user=request.user, post=post)
        saved_post.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class SavedPostGetAll(views.APIView):
    @staticmethod
    def get(request):
        saved_post = SavedPost.objects.filter(user=request.user)
        serializer_data = SavedPostSerializer(saved_post, many=True)
        return response.Response(serializer_data.data)


