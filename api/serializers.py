import re

from rest_framework import serializers
from django.core.validators import EmailValidator
import json
from datetime import datetime
import datetime

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


class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = '__all__'


class PricingSerializer(serializers.Serializer):
    price = serializers.IntegerField()
    cancellation_policy = serializers.CharField(max_length=1000)


class AccommodationFilterSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=20)
    rooms = serializers.IntegerField()
    beds = serializers.IntegerField()
    capacity = serializers.IntegerField()
    price_from = serializers.IntegerField()
    price_to = serializers.IntegerField()


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = '__all__'


class BookingSerializer(serializers.Serializer):
    booking_dates = serializers.ListField()
    accommodation_id = serializers.IntegerField()
