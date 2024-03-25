from rest_framework import serializers
from .models import ChatMessage, GroupChat, Message, FileModel
from users.serializers import CustomUserSerializers


class FileModelSerializers(serializers.ModelSerializer):
    class Meta:
        model = FileModel
        fields = ["id", "file", "content_type", "file_image", "size", "name"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {key: value for key, value in ret.items() if value is not None}


class MessageSerializers(serializers.ModelSerializer):
    message_file = FileModelSerializers(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "message", "message_type", "message_file", "created_at"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {key: value for key, value in ret.items() if value is not None}


class ChatMessageSerializers(serializers.ModelSerializer):
    from_user = CustomUserSerializers(read_only=True)
    message = MessageSerializers(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "from_user", "message", "is_read", "created_at"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {key: value for key, value in ret.items() if value is not None}


class ChatMessageSerializersForMessageType(serializers.ModelSerializer):
    message = MessageSerializers(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "message", "created_at"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {key: value for key, value in ret.items() if value is not None}


class GroupChatSerializers(serializers.ModelSerializer):
    users = CustomUserSerializers(many=True, read_only=True)

    class Meta:
        model = GroupChat
        fields = ["id", "group_name", "group_image", "created_at", "owner", "users"]
        extra_kwargs = {
            "owner": {"read_only": True},
            "group_name": {"required": True},
            "group_image": {"required": False},
            "users": {"required": True},
        }


class GroupMessageSerializers(serializers.ModelSerializer):
    from_user = CustomUserSerializers(read_only=True)
    message = MessageSerializers(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "from_user", "message", "is_read", "created_at"]


class GroupChatMessageSerializersForMessageType(serializers.ModelSerializer):
    message = MessageSerializers(read_only=True)

    class Meta:
        model = GroupChat
        fields = ["id", "message"]
