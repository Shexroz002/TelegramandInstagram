from django.contrib import admin
from .models import ChatRoom, ChatMessage, GroupChat, GroupChatMessage,FileModel,Message
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(GroupChat)
admin.site.register(GroupChatMessage)
admin.site.register(FileModel)
admin.site.register(Message)
# Register your models here.
