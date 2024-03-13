from django.core.exceptions import ValidationError


def validate_file(value):
    if value.content_type in ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']:
        if value.size > 5 * 1024 * 1024:
            raise ValidationError("Image size should be below 5 MB.")
    elif value.content_type in ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/3gp',
                                'video/webm', ]:
        if value.size > 20 * 1024 * 1024:
            raise ValidationError("Video size should be below 20 MB.")
    elif value.content_type in ['audio/webm', 'audio/wav', 'audio/ogg', 'audio/midi', 'audio/x-ms-wma',
                                'audio/x-ms-wav', 'audio/mp4', 'audio/mpeg']:
        if value.size > 10 * 1024 * 1024:
            raise ValidationError("Audio size should be below 10 MB.")
    elif value.content_type in [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/zip'
    ]:
        if value.size > 10 * 1024 * 1024:
            raise ValidationError("Document size should be below 10 MB.")
    else:
        raise ValidationError("File type not supported.")
