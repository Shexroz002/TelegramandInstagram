from django.urls import path
from .views import UserRegister, UserUpdate, GetFollowers, GetFollowing

urlpatterns = [
    path('register/', UserRegister.as_view(), name='register'),
    path('update/<int:user_id>/', UserUpdate.as_view(), name='update'),
    path('followers/', GetFollowers.as_view(), name='followers'),
    path('following/', GetFollowing.as_view(), name='following'),
]