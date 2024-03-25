from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models

from chat.models import ChatMessage
from posts.models import Post, CommentPost
from users.models import CustomUser, UserStory


class NotificationType(models.IntegerChoices):
    LIKE = 0, 'LIKE'
    FOLLOWING = 1, 'FOLLOWING'
    CHAT = 2, 'CHAT'
    COMMENT = 3, 'COMMENT'
    STORY = 4, 'STORY'
    GROUP = 5, 'GROUP'
    FORWARD = 6, 'FORWARD'


class NotificationModel(models.Model):
    notification_visible_to_user = models.ForeignKey(CustomUser,
                                                     related_name='notification_visible_to_user',
                                                     on_delete=models.CASCADE,
                                                     null=False
                                                     )
    following_user = models.ForeignKey(CustomUser,
                                       related_name='notification_following_user',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       blank=True
                                       )
    post_like = models.ForeignKey(Post,
                                  related_name='notification_post_like',
                                  on_delete=models.CASCADE,
                                  null=True,
                                  blank=True
                                  )
    notification_chat = models.ForeignKey(ChatMessage,
                                          related_name='notification_chat',
                                          on_delete=models.CASCADE,
                                          null=True,
                                          blank=True
                                          )
    notification_comment = models.ForeignKey(CommentPost,
                                             related_name='notification_comment',
                                             on_delete=models.CASCADE,
                                             null=True,
                                             blank=True
                                             )
    notification_story = models.ForeignKey(UserStory,
                                           related_name='notification_story',
                                           on_delete=models.CASCADE,
                                           null=True,
                                           blank=True
                                           )
    notification_group = models.ForeignKey('chat.GroupChat',
                                           related_name='notification_group',
                                           on_delete=models.CASCADE,
                                           null=True,
                                           blank=True
                                           )
    forward_post = models.ForeignKey(Post,
                                     related_name='notification_forward_post',
                                     on_delete=models.CASCADE,
                                     null=True,
                                     blank=True
                                     )
    type_notification = models.IntegerField(choices=NotificationType.choices, default=NotificationType.LIKE)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    # This method is used to get the type of the notification
    def notification_type_int_to_str(self):
        if self.type_notification == 0:
            return 'LIKE'
        elif self.type_notification == 1:
            return 'FOLLOWING'
        elif self.type_notification == 2:
            return 'CHAT'
        elif self.type_notification == 3:
            return 'COMMENT'
        elif self.type_notification == 4:
            return 'STORY'
        elif self.type_notification == 5:
            return 'GROUP'
        else:
            return 'UNKNOWN'

    # This method is used to get the type of the notification
    def get_type_notification_display(self):
        return self.get_type_notification_display

    def __str__(self):
        return self.notification_type_int_to_str()

    # This method is used to get the time ago of the notification
    def time_ago(self):
        from django.utils.timesince import timesince
        return timesince(self.created_at) + " ago"

    # This method is used to send notification when the notification is saved
    def save(self, *args, **kwargs):
        super(NotificationModel, self).save(*args, **kwargs)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_user_{self.notification_visible_to_user.id}', {
                "type": "send_notification_user",
            })

        async_to_sync(channel_layer.group_send)(
            f'unread_notification_user_{self.notification_visible_to_user.id}', {
                "type": "send_unread_notification_user",
            })

        async_to_sync(channel_layer.group_send)(
            f'get_last_thirty_notification_user_{self.notification_visible_to_user.id}', {
                "type": "send_last_thirty_notification_user",
            })
        async_to_sync(channel_layer.group_send)(
            f'notification_count_user_{self.notification_visible_to_user.id}', {
                "type": "send_notification_count_user",
            })
