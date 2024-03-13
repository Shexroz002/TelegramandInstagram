from django.urls import path
from .views import (
    CreatePost,
    GetUpdateDeletePost,
    CreateComment,
    GetUpdateDeleteComment,
    LikePost, SavedPostByUser,
    SavedPostGetAll,

)

urlpatterns = [
    path('create', CreatePost.as_view(), name='create_post'),
    path('<int:post_id>', GetUpdateDeletePost.as_view(), name='get_update_delete_post'),
    path('comment/<int:post_id>', CreateComment.as_view(), name='create_comment'),
    path('comment/<int:comment_id>', GetUpdateDeleteComment.as_view(), name='get_update_delete_comment'),
    path('like/<int:post_id>', LikePost.as_view(), name='like_post'),
    path('saved/<int:post_id>', SavedPostByUser.as_view(), name='saved_post'),
    path('saved/post/all', SavedPostGetAll.as_view(), name='saved_post_get_all')

]
