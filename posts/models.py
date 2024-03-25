from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from users.models import CustomUser
from posts.validates_function import validate_title_length, validate_image_size, validate_comment_length


class Post(models.Model):
    title = models.CharField(max_length=100, validators=[validate_title_length])
    date_posted = models.DateTimeField(auto_now_add=True)
    post_image = models.ImageField(upload_to='post_images/', null=False, blank=False, validators=[validate_image_size])
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    likes = models.ManyToManyField(CustomUser, related_name='post_likes', blank=True)

    class Meta:
        ordering = ['-date_posted']
        db_table = 'post'
        verbose_name = 'Post'
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

    def count_likes(self):
        return self.likes.count()

    def count_comments(self):
        return self.comment_post.count()

    def count_saved(self):
        return self.saved_post.count()

    def get_comments(self):
        return self.comment_post.all()

    def get_likes(self):
        return self.likes.all()[:3]

    def get_last_like_user(self):
        return self.likes.last()

    def get_last_three_like_user_image_url(self):
        return [
            user.get_user_last_image().photo.url
            if user.get_user_last_image() else ""
            for user in self.likes.all()[:3]
        ]



    def time_ago(self):
        from django.utils.timesince import timesince
        return timesince(self.date_posted)

    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'following_post_all', {
                "type": "send_following_posts",
            })


class SavedPost(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_post')
    date_saved = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_post'
        verbose_name = 'Saved Post'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return self.user.username + " saved " + self.post.title


# Path: users/models.py
# Compare this snippet from core_settings/settings.py:

class CommentPost(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_post')
    comment = models.TextField(max_length=500, blank=False, null=False, validators=[validate_comment_length])
    date_commented = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment_post'
        verbose_name = 'Comment Post'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return self.user.username + " commented on " + self.post.title
