from django.urls import path
from .consumers import UserFollowingPosts, PostGetAllComment

websocket_urlpatterns = [
    path('following/post', UserFollowingPosts.as_asgi()),
    path('comments/<int:post_id>', PostGetAllComment.as_asgi())

]
