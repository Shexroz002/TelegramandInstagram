from celery import shared_task
from PIL import Image
from io import BytesIO
import base64
import os
from .models import Post
from users.models import CustomUser


@shared_task
def create_post_task(file_info, title, user_id):
    try:

        content = base64.b64decode(file_info['base64_content'])
        file_content = BytesIO(content)
        file_content.name = file_info['name']
        file_content.content_type = file_info['content_type']
        file_content.size = file_info['size']
        image = Image.open(file_content)
        resized_imagee = image.resize((640, 640))
        current_path = f"/my_future/media/post_images/{file_info['name']}"
        if os.path.exists(current_path):
            current_path = f"/my_future/media/post_images/{file_info['name'].split('.')[0]}_{file_info['size']}.{file_info['name'].split('.')[1]}"
        if file_info['size'] > 1024 * 1024:
            resized_imagee.save(current_path, quality=50)
        else:
            resized_imagee.save(current_path)
        user = CustomUser.objects.get(id=user_id)
        post = Post.objects.create(title=title, post_image=current_path, author=user)
        post.save()
        return post.id

    except Exception as e:
        return "Error occurred {}".format(e)


@shared_task
def update_post_task(file_info, title, post_id):
    try:
        image_content = base64.b64decode(file_info['base64_content'])
        file_content = BytesIO(image_content)
        file_content.name = file_info['name']
        file_content.content_type = file_info['content_type']
        file_content.size = file_info['size']
        image = Image.open(file_content)
        image.resize((640, 640))
        current_path = os.path.join(os.getcwd(), 'media', 'post_images', file_info['name'])
        if os.path.exists(current_path):
            current_path = os.path.join(os.getcwd(), 'media', 'post_images',
                                        f"{file_info['name'].split('.')[0]}_{file_info['size']}.{file_info['name'].split('.')[1]}")
        if file_info['size'] > 1024 * 1024:
            image.save(current_path, "PNG", quality=50)
        else:
            image.save(current_path, "PNG")

        post = Post.objects.get(id=post_id)
        old_image = post.post_image.url
        if post.title != title and title:
            post.title = title
        post.post_image = current_path
        post.save()
        if os.path.exists(old_image):
            os.remove(old_image)
        return post.id

    except Exception as e:
        return "Error occurred {}".format(e)
