import re

from rest_framework import serializers
from django.core.validators import EmailValidator

from .models import *


class RegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    surname = serializers.CharField(max_length=255)
    sex = serializers.IntegerField()
    email = serializers.EmailField(max_length=255, default="", allow_blank=True,
                                   validators=[EmailValidator])

    def validate_phone(self, value):
        if not re.fullmatch(r'^(\+7\((\d{3})\)\s((\d{3})-(\d{4})))$', value):
            raise serializers.ValidationError('Телефон не совпадает с маской')

        return value


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, default="", allow_blank=True,
                                   validators=[EmailValidator])


class CheckCodeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField()


class AccommodationSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    images = serializers.JSONField()
    type = serializers.CharField(max_length=20)
    rooms = serializers.IntegerField()
    beds = serializers.IntegerField()
    capacity = serializers.IntegerField()

class AccommodationFilterSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=20)
    rooms = serializers.IntegerField()
    beds = serializers.IntegerField()
    capacity = serializers.IntegerField()
    price_from = serializers.IntegerField()
    price_to = serializers.IntegerField()

class OwnerSerializer (serializers.Serializer):
    name = serializers.CharField(max_length=255)
    contact = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    image = serializers.CharField(max_length=1000)
