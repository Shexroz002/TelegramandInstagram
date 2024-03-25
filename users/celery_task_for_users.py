from celery import shared_task
from PIL import Image
from io import BytesIO
import base64
import os
from notifications.models import NotificationModel
from chat.models import ChatRoom, ChatMessage, Message
from users.models import CustomUser, Story, UserStory
from notifications.models import NotificationModel


@shared_task
def create_user_task(file_info, **kwargs):
    try:
        content = base64.b64decode(file_info['base64_content'])
        file_content = BytesIO(content)
        file_content.name = file_info['name']
        file_content.content_type = file_info['content_type']
        file_content.size = file_info['size']
        image = Image.open(file_content)
        resized_image = image.resize((640, 640))
        current_path = f"/my_future/media/user_images/{file_info['name']}"
        if os.path.exists(current_path):
            current_path = (f"/my_future/media/user_images/"
                            f"{file_info['name'].split('.')[0]}_{file_info['size']}"
                            f".{file_info['name'].split('.')[1]}")
        if file_info['size'] > 1024 * 1024:
            resized_image.save(current_path, quality=50)
        else:
            resized_image.save(current_path, )
        CustomUser.objects.create(user_image=current_path, **kwargs)
        return "User created successfully"
    except Exception as e:
        return "Error occurred {}".format(e)


# This task is for creating a notification for the following user
@shared_task
def create_following_notification_task(following_user, notification_visible_to_user):
    try:
        notification = NotificationModel.objects.filter(following_user=following_user,
                                                        notification_visible_to_user=notification_visible_to_user,
                                                        type_notification=1)
        if not notification.exists():
            NotificationModel.objects.create(following_user=following_user,
                                             notification_visible_to_user=notification_visible_to_user,
                                             type_notification=1)
            return "Notification created successfully"
        else:
            return "Notification already exists"
    except Exception as e:
        return "Error occurred {}".format(e)


# This task is for sending notification to mentioned users in story
@shared_task
def mentioned_user_for_story(story_id, creator, mentioned_users_id, user_story_id):
    # Get the story and user story
    story = Story.objects.get(id=story_id)
    user_story = UserStory.objects.get(id=user_story_id)
    # Get the mentioned users
    mentioned_users = CustomUser.objects.filter(id__in=mentioned_users_id)
    # Check if the mentioned users are in the chat room
    for receiver in mentioned_users:
        check_chat_room = ChatRoom.objects.filter(first_user=receiver, second_user=creator)
        second_check_chat_room = ChatRoom.objects.filter(first_user=creator, second_user=receiver)
        # If the mentioned users are not in the chat room, create a chat room and send the story
        if creator != receiver and not check_chat_room.exists() and not second_check_chat_room.exists():
            chat_room = ChatRoom.objects.create(first_user=creator, second_user=receiver)
            message = Message.objects.create(message_type='story', story=story)
            ChatMessage.objects.create(chat_room=chat_room, message=message, from_user=creator)
            # Create a notification for the mentioned user
            NotificationModel.objects.create(
                notification_story=user_story,
                notification_visible_to_user=receiver,
                type_notification=4)

        else:
            # If the mentioned users are in the chat room, send the story
            if check_chat_room.exists():
                message = Message.objects.create(message_type='story', story=story)
                ChatMessage.objects.create(chat_room=check_chat_room.last(), message=message, from_user=creator)
                NotificationModel.objects.create(
                    notification_story=user_story,
                    notification_visible_to_user=receiver,
                    type_notification=4)
            # If the mentioned users are in the chat room, send the story
            elif second_check_chat_room.exists():
                message = Message.objects.create(message_type='story', story=story)
                ChatMessage.objects.create(chat_room=second_check_chat_room.last(), message=message, from_user=creator)
                NotificationModel.objects.create(
                    notification_story=user_story,
                    notification_visible_to_user=receiver,
                    type_notification=4)
            else:
                pass
