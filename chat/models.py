from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models

from posts.models import Post
from users.models import CustomUser, UserStory, Story
from .validate_function_for_chat import validate_file


class FileModel(models.Model):
    file = models.FileField(upload_to='message/', null=False, blank=False, validators=[validate_file, ])
    name = models.CharField(max_length=100, null=False, blank=False)
    size = models.CharField(max_length=100, blank=False, null=False)
    content_type = models.CharField(max_length=100, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_image = models.ImageField(upload_to='message_image/', null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        db_table = 'file_model'
        verbose_name = 'Message File Model'

    def __str__(self):
        return self.name


class ChatRoom(models.Model):
    first_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="first_user")
    second_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="second_user")
    first_user_is_writing = models.BooleanField(default=False)
    second_user_is_writing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'chat_room'
        verbose_name = 'Chat Room'
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.first_user} and {self.second_user}"

    def count_unread_messages(self):
        return self.chat_room.filter(is_read=False).count()

    def count_messages(self):
        return self.chat_room.count()

    def count_documents(self):
        return self.chat_room.filter(message__message_type__in=["word", "pdf", "excel"]).count()

    def count_images(self):
        return self.chat_room.filter(message__message_type="image").count()

    def count_videos(self):
        return self.chat_room.filter(message__message_type="video").count()

    def count_voices(self):
        return self.chat_room.filter(message__message_type="voice").count()

    def get_document_messages(self):
        return self.chat_room.filter(message__message_type__in=["word", "pdf", "excel"])

    def get_image_messages(self):
        return self.chat_room.filter(message__message_type="image")

    def get_voice_messages(self):
        return self.chat_room.filter(message__message_type="voice")

    def get_video_messages(self):
        return self.chat_room.filter(message__message_type="video"
                                     )

    def get_last_message(self):
        return self.chat_room.last()


class Message(models.Model):
    message_type_choice = (
        ("word", "word"),
        ("pdf", "pdf"),
        ("excel", "excel"),
        ("image", "image"),
        ("video", "video"),
        ("voice", "voice"),
        ("text", "text"),
        ("story", "story"),
        ("forward_message", "forward_message"),
        ("forward_post", "forward_post")
    )
    message = models.CharField(max_length=250, null=True, blank=True)
    message_file = models.ForeignKey(FileModel, on_delete=models.SET_NULL, null=True, blank=True)
    message_type = models.CharField(choices=message_type_choice, max_length=15, null=False, blank=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="chat_story_message", null=True,
                              blank=True)
    forward_message = models.ForeignKey('self', on_delete=models.CASCADE, related_name="forward_chat_message",
                                        null=True, )
    forward_post = models.ForeignKey(Post, on_delete=models.SET_NULL, related_name="forward_post_message", null=True, )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'message'
        verbose_name = 'Message'
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.message_type


class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="chat_room")
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="from_user",
                                  null=False, blank=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="chat_message")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'chat_message'
        verbose_name = 'Chat Message'
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.from_user.username


class GroupChat(models.Model):
    group_name = models.CharField(max_length=100, null=False, blank=False, unique=True, db_index=True)
    group_image = models.ImageField(upload_to='group/image', null=True, blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="group_owner")
    users = models.ManyToManyField(CustomUser, related_name="group_users")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'group_chat'
        verbose_name = 'Group Chat'
        indexes = [
            models.Index(fields=['group_name']),
        ]

    def __str__(self):
        return self.group_name

    def count_online_users(self):
        return self.users.filter(is_online=True).count()

    def count_offline_users(self):
        return self.users.filter(is_online=False).count()

    def count_users(self):
        return self.users.count()

    def count_messages(self):
        return self.group_chat.count()

    def unread_message_count(self, user):
        return self.group_chat.exclude(read_users=user).count()

    def count_documents(self):
        return self.group_chat.filter(message__message_type="document").count()

    def count_images(self):
        return self.group_chat.filter(message__message_type="image").count()

    def count_videos(self):
        return self.group_chat.filter(message__message_type="video").count()

    def count_voices(self):
        return self.group_chat.filter(message__message_type="voice").count()

    def get_document_messages(self):
        return self.group_chat.filter(message__message_type="document")

    def get_image_messages(self):
        return self.group_chat.filter(message__message_type="ïmage")

    def get_voice_messages(self):
        return self.group_chat.filter(message__message_type="voice")

    def get_video_messages(self):
        return self.group_chat.filter(message__message_type="video")

    def add_user(self, user):
        self.users.add(user)
        self.save()

    def remove_user(self, user):
        self.users.remove(user)
        self.save()

    def get_users(self):
        return self.users.all()

    def get_messages(self):
        return self.group_chat.all().order_by('created_at')

    def get_last_added_user(self):
        return self.users.last()

    def get_last_message(self):
        return self.group_chat.last()


class GroupChatMessage(models.Model):
    group_chat = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name="group_chat")
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="group_from_user",
                                  null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="group_message")
    is_read = models.BooleanField(default=False)
    read_users = models.ManyToManyField(CustomUser, related_name="group_message_read_users", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'group_chat_message'
        verbose_name = 'Group Chat Message'
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        super(GroupChatMessage, self).save(*args, **kwargs)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'group_chat_list', {
                "type": "send_group_chat_list",
            })
        async_to_sync(channel_layer.group_send)(
            f'group_chat_message_all_{self.group_chat.id}', {
                "type": "send_group_chat_message_all",
            })
