from django.urls import path

from .views import (
    UserRegister,
    UserUpdate,
    GetFollowers,
    GetFollowing,
    Login,
    UserFollowingAddOrDelete,
    UserDetail,
    UserList,
    CreateStory,
    UpdateStory,
    DeleteStory,
    StoryLikeByUsers,
    StorySeenByUsers
)

urlpatterns = [
    path('register/', UserRegister.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('update/<int:user_id>/', UserUpdate.as_view(), name='update'),
    path('followers/', GetFollowers.as_view(), name='followers'),
    path('following/', GetFollowing.as_view(), name='following'),
    path('following/add/or/delete/<int:user_id>', UserFollowingAddOrDelete.as_view(), name='add_or_delete'),
    path('detail', UserDetail.as_view(), name='user'),
    path('list/', UserList.as_view(), name='user_list'),
    path('story/create/', CreateStory.as_view(), name='create_story'),
    path('story/update/<int:story_id>', UpdateStory.as_view(), name='update_story'),
    path('story/delete/<int:story_id>', DeleteStory.as_view(), name='delete_story'),
    path('story/like/<int:user_story_id>', StoryLikeByUsers.as_view(), name='story_like'),
    path('story/seen/<int:user_story_id>', StorySeenByUsers.as_view(), name='story_seen'),
]
