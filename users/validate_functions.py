from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_password(value):
    if len(value) < 8:
        raise serializers.ValidationError('Password must be at least 8 characters long')
    return value


def validate_image_type(value):
    if value.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
        raise ValidationError("Image type should be either jpeg, jpg or png.")
    return value


def validate_image_size(value):
    max_size = 5 * 1024 * 1024  # 5 MB
    if value.size > max_size:
        raise ValidationError("Image size should be below 5 MB.")


def validate_bio_length(value):
    max_length = 500
    if len(value) > max_length:
        raise ValidationError("Bio length should be below 500 characters.")


def validate_list_for_item_int(value):
    if not all(isinstance(item, int) for item in value):
        return False
    return True
