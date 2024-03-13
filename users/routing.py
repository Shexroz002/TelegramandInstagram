from .consumers import (
    UserInformationAboutSelf,
    UserInformationByID,
    FollowingUserStories,
    UserStoryByID,
    GetStoryByID
)
from django.urls import path

websocket_urlpatterns = [
    path('self/information', UserInformationAboutSelf.as_asgi()),
    path('information/<int:user_id>', UserInformationByID.as_asgi()),
    path('stories', FollowingUserStories.as_asgi()),
    path('stories/<int:user_id>', UserStoryByID.as_asgi()),
    path('story/<int:story_id>', GetStoryByID.as_asgi())
]
