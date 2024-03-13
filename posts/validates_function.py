from django.core.exceptions import ValidationError


def validate_title_length(value):
    max_length = 100
    if len(value) > max_length:
        raise ValidationError("Title length should be below 100 characters.")


def validate_image_size(value):
    max_size = 5 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError("Image size should be below 5 MB.")


def validate_comment_length(value):
    max_length = 500
    if len(value) > max_length:
        raise ValidationError("Comment length should be below 500 characters.")
