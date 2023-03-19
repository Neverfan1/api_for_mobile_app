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


class AccommodationSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    images = serializers.JSONField()
    type = serializers.CharField(max_length=20)
    rooms = serializers.IntegerField()
    beds = serializers.IntegerField()
    capacity = serializers.IntegerField()

class PricingSerializer(serializers.Serializer):
    price = serializers.IntegerField()
    cancellation_policy = serializers.CharField(max_length=1000),
    availability = serializers.JSONField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert availability string to dictionary
        availability_dict = json.loads(representation['availability'])
        # Remove past days for each month
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month

        # Get dates for current month and next two months
        dates = []
        for month in range(current_month, current_month + 3):
            if month > 12:
                # If we've gone past December, wrap around to January
                year = current_year + 1
                month -= 12
            else:
                year = current_year

            month_name = datetime.datetime.strptime(str(month), "%m").strftime("%B")

            if month_name in availability_dict:
                for date in availability_dict[month_name]:
                    if date >= now.day and month_name == now.strftime("%B"):
                        dates.append({'month': month_name, 'date': date, 'year': year})
                    elif month_name != now.strftime("%B"):
                        dates.append({'month': month_name, 'date': date, 'year': year})

        representation['availability'] = dates
        return representation


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
