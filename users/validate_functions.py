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
