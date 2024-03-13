from django.shortcuts import get_object_or_404
from rest_framework import response, status, views
from posts.models import Post
from users.models import CustomUser
from .models import ChatRoom, ChatMessage, GroupChat, Message, FileModel
from users.models import Story
from .celery_task_for_chat import create_message_pdf_image, create_message_excel_image
from .serializers import GroupChatSerializers, ChatMessageSerializers, MessageSerializers, FileModelSerializers, \
    ChatMessageSerializersForMessageType


class CreateChatRoom(views.APIView):
    @staticmethod
    def post(request, user_id):
        receiver = get_object_or_404(CustomUser, id=user_id)
        creator = request.user
        check_chat_room = ChatRoom.objects.filter(first_user=creator, second_user=receiver)
        second_check_chat_room = ChatRoom.objects.filter(first_user=receiver, second_user=creator)
        if creator != receiver and not check_chat_room.exists() and not second_check_chat_room.exists():
            chat_room = ChatRoom.objects.create(first_user=creator, second_user=receiver)
            return response.Response({"chat_room_id": chat_room.id}, status=status.HTTP_201_CREATED)
        else:
            if check_chat_room.exists():
                return response.Response(
                    {"chat_room_id": check_chat_room.first().id},
                    status=status.HTTP_200_OK
                )
            elif second_check_chat_room.exists():
                return response.Response(
                    {"chat_room_id": second_check_chat_room.first().id},
                    status=status.HTTP_200_OK)
            else:
                return response.Response({"error": "You are not allowed to create chat room with this user"},
                                         status=status.HTTP_403_FORBIDDEN)


class CreateChatRoomMessage(views.APIView):
    @staticmethod
    def post(request, chat_room_id):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        if request.user == chat_room.first_user or request.user == chat_room.second_user:
            message_type = request.data.get("message_type")
            if message_type == "word":
                word_file = request.FILES.get("word_file", None)
                if word_file:
                    file_type = word_file.name.split('.')[1]
                    if word_file and file_type in ['docx', 'doc'] and word_file.size < 10 * 1024 * 1024:
                        file_info = {
                            "name": word_file.name,
                            "size": word_file.size,
                            "content_type": word_file.content_type,
                            "file": word_file
                        }
                        file_data = FileModel.objects.create(**file_info)
                        message = Message.objects.create(
                            message_type="word",
                            message_file=file_data
                        )
                        ChatMessage.objects.create(
                            from_user=request.user,
                            chat_room=chat_room,
                            message=message
                        )
                        return response.Response(status=status.HTTP_201_CREATED)
                    else:
                        error = "Word file is required and it should be less than 10MB. You only can upload doc files."
                        return response.Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return response.Response({"error": "Word file required"})
            elif message_type == "pdf":
                pdf_file = request.FILES.get("pdf_file", None)
                if pdf_file:
                    file_type = pdf_file.name.split('.')[1]
                    if pdf_file and file_type in ['pdf'] and pdf_file.size < 10 * 1024 * 1024:
                        file_info = {
                            "name": pdf_file.name,
                            "size": pdf_file.size,
                            "content_type": pdf_file.content_type,
                            "file": pdf_file
                        }
                        file_data = FileModel.objects.create(**file_info)
                        message = Message.objects.create(
                            message_type="pdf",
                            message_file=file_data
                        )
                        chat_message = ChatMessage.objects.create(
                            from_user=request.user,
                            chat_room=chat_room,
                            message=message
                        )
                        pdf_path = file_data.file.path
                        create_message_pdf_image.delay(pdf_path, file_data.id, chat_message.id)
                        return response.Response(status=status.HTTP_201_CREATED)
                    else:
                        error = "PDF file is required and it should be less than 10MB. You only can upload doc files."
                        return response.Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return response.Response({"error": "PDF file required"})
            elif message_type == "excel":
                excel_file = request.FILES.get("excel_file", None)
                if excel_file:
                    file_type = excel_file.name.split('.')[1]
                    print(file_type)
                    if excel_file and file_type in ['xlsx'] and excel_file.size < 10 * 1024 * 1024:
                        file_info = {
                            "name": excel_file.name,
                            "size": excel_file.size,
                            "content_type": excel_file.content_type,
                            "file": excel_file
                        }
                        file_data = FileModel.objects.create(**file_info)
                        message = Message.objects.create(
                            message_type="excel",
                            message_file=file_data
                        )
                        chat_message = ChatMessage.objects.create(
                            from_user=request.user,
                            chat_room=chat_room,
                            message=message
                        )
                        create_message_excel_image.delay(file_data.file.path, file_data.id, chat_message.id)
                        return response.Response(status=status.HTTP_201_CREATED)
                    else:
                        error = "Excel file is required and it should be less than 10MB. You only can upload doc files."
                        return response.Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return response.Response({"error": "Excel file required"}, status=status.HTTP_400_BAD_REQUEST)
            elif message_type == "image":
                image_file = request.FILES.get("image_file", None)
                if image_file:
                    file_info = {
                        "name": image_file.name,
                        "size": image_file.size,
                        "content_type": image_file.content_type,
                        "file": image_file
                    }
                    file_data = FileModel.objects.create(**file_info)
                    message = Message.objects.create(
                        message_type="image",
                        image=file_data
                    )
                    ChatMessage.objects.create(
                        from_user=request.user,
                        chat_room=chat_room,
                        message=message
                    )
                    return response.Response(status=status.HTTP_201_CREATED)
            elif message_type == "voice":
                voice_file = request.FILES.get("voice_file", None)
                if voice_file:
                    if voice_file and voice_file.size < 10 * 1024 * 1024:
                        file_info = {
                            "name": voice_file.name,
                            "size": voice_file.size,
                            "content_type": voice_file.content_type,
                            "file": voice_file
                        }
                        file_data = FileModel.objects.create(**file_info)
                        message = Message.objects.create(
                            message_type="voice",
                            voice=file_data
                        )
                        ChatMessage.objects.create(
                            from_user=request.user,
                            chat_room=chat_room,
                            message=message
                        )
                        return response.Response(status=status.HTTP_201_CREATED)
                else:
                    return response.Response({"error": "Vocie file required!"})
            elif message_type == "video":
                video_file = request.FILES.get("video_file", None)
                if video_file and video_file.content_type == "video/mp4" and video_file.size < 10 * 1024 * 1024:
                    file_info = {
                        "name": video_file.name,
                        "size": video_file.size / (1024 * 1024),
                        "content_type": video_file.content_type,
                        "file": video_file
                    }
                    file_data = FileModel.objects.create(**file_info)

                    message = Message.objects.create(
                        message_type="video",
                        message_file=file_data
                    )
                    ChatMessage.objects.create(
                        from_user=request.user,
                        chat_room=chat_room,
                        message=message
                    )
                    return response.Response(status=status.HTTP_201_CREATED)
                else:
                    error = "Video file is required and it should be less than 10MB. You only can upload mp4 files."
                    return response.Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
            elif message_type == "text":
                message_text = request.data.get("message_text", None)
                if message_text and len(message_text) > 0:
                    message = Message.objects.create(
                        message_type="text",
                        message=message_text
                    )
                    ChatMessage.objects.create(
                        from_user=request.user,
                        chat_room=chat_room,
                        message=message
                    )
                    return response.Response(status=status.HTTP_201_CREATED)
                else:
                    return response.Response({"error": "Message text is required"}, status=status.HTTP_400_BAD_REQUEST)
            elif message_type == "story":
                story_id = request.data.get("story_id", None)
                if story_id:
                    get_story = get_object_or_404(Story, id=story_id)
                    message = Message.objects.create(
                        message_type="story",
                        story=get_story
                    )
                    ChatMessage.objects.create(
                        from_user=request.user,
                        chat_room=chat_room,
                        message=message
                    )
                    return response.Response(status=status.HTTP_201_CREATED)
                else:
                    return response.Response({"error": "Story id is required"}, status=status.HTTP_400_BAD_REQUEST)
            elif message_type == "forward_message":
                forward_message_id = request.data.get("forward_message_id", None)
                if forward_message_id:
                    forward_message = get_object_or_404(Message, id=forward_message_id)
                    message = Message.objects.create(
                        message_type="forward_message",
                        forward_message=forward_message
                    )
                    ChatMessage.objects.create(
                        from_user=request.user,
                        chat_room=chat_room,
                        message=message
                    )
                    return response.Response(status=status.HTTP_201_CREATED)
                else:
                    return response.Response({"error": "Forward message id is required"},
                                             status=status.HTTP_400_BAD_REQUEST)
            elif message_type == "forward_post":
                forward_post_id = request.data.get("forward_post_id", None)
                if forward_post_id:
                    forward_post = get_object_or_404(Post, id=forward_post_id)
                    message = Message.objects.create(
                        message_type="forward_post",
                        forward_post=forward_post
                    )
                    ChatMessage.objects.create(
                        from_user=request.user,
                        chat_room=chat_room,
                        message=message
                    )
                    return response.Response(status=status.HTTP_201_CREATED)
                else:
                    return response.Response({"error": "Forward post id is required"},
                                             status=status.HTTP_400_BAD_REQUEST)
            else:
                return response.Response({"error": "Invalid message type"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({"error": "You are not allowed to send message to this chat room"},
                                     status=status.HTTP_403_FORBIDDEN)


class GetChatRoomMessages(views.APIView):
    @staticmethod
    def get(request, chat_room_id):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        if request.user == chat_room.first_user or request.user == chat_room.second_user:
            messages = chat_room.chat_room.all()
            serializer_data = ChatMessageSerializers(messages, many=True)
            return response.Response(serializer_data.data, status=status.HTTP_200_OK)
        else:
            return response.Response({"error": "You are not allowed to see this chat room messages"},
                                     status=status.HTTP_403_FORBIDDEN)


class DeleteUpdateChatRoomMessageAndFiles(views.APIView):
    @staticmethod
    def put(request, chat_message_id):
        chat_message = get_object_or_404(ChatMessage, id=chat_message_id)
        if request.user == chat_message.from_user:
            if chat_message.message.message_type == "text":
                message_text = request.data.get("message_text")
                if message_text and len(message_text) > 0:
                    chat_message.message.message = message_text
                    chat_message.message.save()
                    return response.Response(status=status.HTTP_200_OK)
                else:
                    return response.Response({"error": "Message text is required"},
                                             status=status.HTTP_400_BAD_REQUEST)
            else:
                return response.Response({"error": "You can only update text message"},
                                         status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({"error": "You are not allowed to update this message"},
                                     status=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def delete(request, chat_message_id):
        chat_message = get_object_or_404(ChatMessage, id=chat_message_id)
        if request.user == chat_message.from_user:
            chat_message.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return response.Response({"error": "You are not allowed to delete this message"},
                                     status=status.HTTP_403_FORBIDDEN)


class GetChatRoomMessagesByMessageType(views.APIView):
    @staticmethod
    def get(request, chat_room_id):
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        if request.user == chat_room.first_user or request.user == chat_room.second_user:
            message_type = request.query_params.get("message_type")
            if message_type == "document":
                messages = chat_room.get_document_messages()
                message_count = chat_room.count_documents()
            elif message_type == "image":
                messages = chat_room.get_image_messages()
                message_count = chat_room.count_images()
            elif message_type == "voice":
                messages = chat_room.get_voice_messages()
                message_count = chat_room.count_voices()
            elif message_type == "video":
                messages = chat_room.get_video_messages()
                message_count = chat_room.count_videos()
            else:
                return response.Response({"error": "Invalid message type"}, status=status.HTTP_400_BAD_REQUEST)
            data = {
                "messages": ChatMessageSerializersForMessageType(messages, many=True).data,
                "message_count": message_count
            }
            return response.Response(data, status=status.HTTP_200_OK)

        else:
            return response.Response({"error": "You are not allowed to see this chat room messages"},
                                     status=status.HTTP_403_FORBIDDEN)


class ReadChatRoomMessages(views.APIView):
    @staticmethod
    def get(request, message_id):
        message = get_object_or_404(ChatMessage, id=message_id)
        if request.user == message.chat_room.first_user or request.user == message.chat_room.second_user:
            message.is_read = True
            message.save()
            return response.Response(status=status.HTTP_200_OK)
        else:
            return response.Response({"error": "You are not allowed to read this message"},
                                     status=status.HTTP_403_FORBIDDEN)


class CreateGroupChat(views.APIView):
    @staticmethod
    def post(request):
        serializer_data = GroupChatSerializers(data=request.data)
        if serializer_data.is_valid():
            group_data = serializer_data.save(owner=request.user)
            users = request.data.get("users")
            get_all_user = CustomUser.objects.filter(id__in=users)
            group_data.users.set(get_all_user)
            group_data.save()
            return response.Response({"group_chat_id": group_data.id}, status=status.HTTP_201_CREATED)
        else:
            return response.Response({"error": serializer_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class UpdateGroupChat(views.APIView):
    @staticmethod
    def put(request, group_id):
        group_chat = get_object_or_404(GroupChat, id=group_id)
        if request.user == group_chat.owner:
            serializer_data = GroupChatSerializers(group_chat, data=request.data)
            if serializer_data.is_valid():
                serializer_data.save()
                return response.Response(status=status.HTTP_200_OK)
            else:
                return response.Response({"error": serializer_data.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({"error": "You are not allowed to update this group chat"},
                                     status=status.HTTP_403_FORBIDDEN)


class GroupChatList(views.APIView):
    @staticmethod
    def get(request):
        group_chat = GroupChat.objects.filter(users=request.user)
        serializer_data = GroupChatSerializers(group_chat, many=True)
        return response.Response(serializer_data.data)


class GetGroupChat(views.APIView):
    @staticmethod
    def get(request, group_id):
        group_chat = get_object_or_404(GroupChat, id=group_id)
        serializer_data = GroupChatSerializers(group_chat)
        return response.Response(serializer_data.data)


class GetGroupChatMessagesByMessageType(views.APIView):
    @staticmethod
    def get(request, group_id):
        group_chat = get_object_or_404(GroupChat, id=group_id)
        if request.user in group_chat.users.all():
            message_type = request.query_params.get("message_type")
            if message_type == "document":
                messages = group_chat.get_document_messages()
                message_count = group_chat.count_documents()
            elif message_type == "image":
                messages = group_chat.get_image_messages()
                message_count = group_chat.count_images()
            elif message_type == "voice":
                messages = group_chat.get_voice_messages()
                message_count = group_chat.count_voices()
            elif message_type == "video":
                messages = group_chat.get_video_messages()
                message_count = group_chat.count_videos()
            else:
                return response.Response({"error": "Invalid message type"}, status=status.HTTP_400_BAD_REQUEST)
            data = {
                "messages": MessageSerializers(messages, many=True).data,
                "message_count": message_count
            }
            return response.Response(data, status=status.HTTP_200_OK)
        else:
            return response.Response({"error": "You are not allowed to see this group chat messages"},
                                     status=status.HTTP_403_FORBIDDEN)
