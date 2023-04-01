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


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = ('price', 'cancellation_policy',)


class AccommodationSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ('accommodation_id', 'type', 'image_preview', 'price')

    def get_price(self, obj):
        pricing = obj.pricing_set.first()
        return pricing.price if pricing else None


class AccommodationDetailSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    cancellation_policy = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ('accommodation_id', 'address', 'description',
                  'image_preview', 'images', 'type', 'rooms', 'beds',
                  'capacity', 'owner_id', 'price', 'cancellation_policy')

    def get_price(self, obj):
        pricing = obj.pricing_set.first()
        return pricing.price if pricing else None

    def get_cancellation_policy(self, obj):
        pricing = obj.pricing_set.first()
        return pricing.cancellation_policy if pricing else None


# class AccommodationFilterSerializer(serializers.Serializer):
#     type = serializers.CharField(max_length=20)
#     rooms = serializers.IntegerField()
#     beds = serializers.IntegerField()
#     capacity = serializers.IntegerField()
#     price_from = serializers.IntegerField()
#     price_to = serializers.IntegerField()


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersApp
        exclude = ('user_id', 'registr', 'sms', 'is_active',
                   'personal_data')


class BookingSerializer(serializers.Serializer):
    booking_dates = serializers.ListField()
    accommodation_id = serializers.IntegerField()
