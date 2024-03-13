from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError


# Create your models here.
def validate_image_size(value):
    max_size = 5 * 1024 * 1024  # 5 MB
    if value.size > max_size:
        raise ValidationError("Image size should be below 5 MB.")


def validate_bio_length(value):
    max_length = 500
    if len(value) > max_length:
        raise ValidationError("Bio length should be below 500 characters.")


class CustomUser(AbstractUser):
    user_image = models.ImageField(upload_to='user_images/', default='user_images/user_images.jpg',
                                   validators=[
                                       validate_image_size,
                                   ]
                                   )
    user_bio = models.TextField(max_length=500, blank=True, validators=[validate_bio_length], default='')
    user_birth_date = models.DateField(null=True, blank=True)
    followers = models.ManyToManyField('self', related_name='user_followers', symmetrical=False, blank=True)
    following = models.ManyToManyField('self', related_name='chat_following', symmetrical=False, blank=True)
    is_online = models.BooleanField(default=False)

    def join_followers(self, user):
        self.followers.add(user)
        self.save()

    def leave_followers(self, user):
        self.followers.remove(user)
        self.save()

    def join_following(self, user):
        self.following.add(user)
        self.save()

    def leave_following(self, user):
        self.following.remove(user)
        self.save()

    def count_followers(self):
        return self.followers.count()

    def count_following(self):
        return self.following.count()

    def get_followers(self):
        return self.followers.all()

    def get_following(self):
        return self.following.all()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'information_about_user_{self.id}', {
                "type": "send_user_information",

            })


class Story(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='users/story', null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserStory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_story")
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    likes = models.ManyToManyField(CustomUser, related_name="likes")
    mentioned = models.ManyToManyField(CustomUser, related_name="mentioned_user")
    created_at = models.DateTimeField(auto_now_add=True)
    seen_user = models.ManyToManyField(CustomUser, related_name="seen_user")

    def __str__(self):
        return self.user.username

    def seen_user_count(self):
        return self.seen_user.count()
