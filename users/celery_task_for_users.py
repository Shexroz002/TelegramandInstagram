from celery import shared_task
from PIL import Image
from io import BytesIO
import base64
import os
from users.models import CustomUser


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
