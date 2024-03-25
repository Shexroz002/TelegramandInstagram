from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import AbstractUser
from django.db import models
from .validate_functions import validate_image_size, validate_bio_length, validate_image_type


class ProfileImage(models.Model):
    photo = models.ImageField(null=True, blank=True, upload_to='user_images/', default='user_image/user_images.jpg',
                              validators=[
                                  validate_image_size,
                              ]
                              )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        db_table = 'profile_image'
        verbose_name = 'Profile Image'

    def __str__(self):
        name = self.photo.name.split('/')[-1].split('.')[0]
        return name


class CustomUser(AbstractUser):
    user_image = models.ManyToManyField(ProfileImage, related_name='user_image', blank=True)
    user_bio = models.TextField(max_length=500, blank=True, validators=[validate_bio_length], default='')
    user_birth_date = models.DateField(null=True, blank=True)
    followers = models.ManyToManyField('self', related_name='user_followers', symmetrical=False, blank=True)
    following = models.ManyToManyField('self', related_name='chat_following', symmetrical=False, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now_add=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-create_at']
        db_table = 'custom_user'
        verbose_name = 'Web site User'
        indexes = [
            models.Index(fields=['username']),
        ]

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

    def get_user_image(self):
        return self.user_image.all()

    def get_user_last_image(self):
        return self.user_image.last()


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

    class Meta:
        ordering = ['-created_at']
        db_table = 'story'
        verbose_name = 'Story'
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title


class UserStory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_story")
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    likes = models.ManyToManyField(CustomUser, related_name="likes")
    mentioned = models.ManyToManyField(CustomUser, related_name="mentioned_user")
    created_at = models.DateTimeField(auto_now_add=True)
    seen_user = models.ManyToManyField(CustomUser, related_name="seen_user")

    class Meta:
        ordering = ['-created_at']
        db_table = 'user_story'
        verbose_name = 'User Story'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return self.user.username

    def seen_user_count(self):
        return self.seen_user.count()

    def time_ago(self):
        from django.utils.timesince import timesince
        return timesince(self.created_at) + " ago"

    def save(self, *args, **kwargs):
        super(UserStory, self).save(*args, **kwargs)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'get_all_stories', {
                "type": "send_stories_all",
            }
        )
        async_to_sync(channel_layer.group_send)(
            f'get_self_stories_{self.user.id}', {
                "type": "send_self_stories",
            }
        )
