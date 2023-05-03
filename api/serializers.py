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

    def validate_phone_number(self, value):
        if not re.fullmatch(r'^(8(\d{10}))$', value):
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
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ('accommodation_id', 'type', 'owner_id',
                  'owner_name', 'image_preview', 'address', 'price')

    def get_price(self, obj):
        pricing = obj.pricing_set.first()
        return pricing.price if pricing else None

    def get_owner_name(self, obj):
        return obj.owner_id.name if obj.owner_id else None


class UserBookingSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ('accommodation_id', 'type', 'owner_id',
                  'owner_name', 'image_preview', 'price', 'address')

    def get_price(self, obj):
        pricing = obj.pricing_set.first()
        return pricing.price if pricing else None

    def get_owner_name(self, obj):
        return obj.owner_id.name if obj.owner_id else None


class BookingWithAccommodationSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='accommodation_id.type')
    owner_id = serializers.IntegerField(source='accommodation_id.owner_id_id')
    owner_name = serializers.CharField(source='accommodation_id.owner_id.name')
    image_preview = serializers.CharField(source='accommodation_id.image_preview')
    images = serializers.CharField(source='accommodation_id.images')
    price = serializers.DecimalField(source='accommodation_id.pricing_set.first.price', max_digits=10, decimal_places=2)
    address = serializers.CharField(source='accommodation_id.address')

    class Meta:
        model = Booking
        fields = ('booking_id', 'accommodation_id', 'type', 'owner_id',
                  'owner_name', 'image_preview', 'images', 'price',
                  'booking_dates', 'address')

class AccommodationDetailSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    cancellation_policy = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ('accommodation_id', 'address', 'description',
                  'image_preview', 'images', 'type', 'rooms', 'beds',
                  'capacity', 'owner_id', 'owner_name', 'price', 'cancellation_policy')

    def get_price(self, obj):
        pricing = obj.pricing_set.first()
        return pricing.price if pricing else None

    def get_cancellation_policy(self, obj):
        pricing = obj.pricing_set.first()
        return pricing.cancellation_policy if pricing else None

    def get_owner_name(self, obj):
        return obj.owner_id.name if obj.owner_id else None


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersApp
        exclude = ('user_id', 'registr', 'sms', 'is_active',
                   'personal_data')


class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('booking_dates', 'accommodation_id')


class CancelBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = 'booking_id'
