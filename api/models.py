import binascii
import os
from django.db import models


# модель пользователя
class UsersApp(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    sex = models.SmallIntegerField()
    phone_number = models.CharField(max_length=16)
    registr = models.SmallIntegerField(default=0)
    sms = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    personal_data = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'sex', 'phone_number']

    class Meta:
        db_table = 'users'


# модель токена
class MyToken(models.Model):
    token_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(UsersApp, related_name='auth_token', on_delete=models.CASCADE,  db_column="user_id")
    key = models.CharField(max_length=40, unique=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(MyToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    class Meta:
        db_table = 'tokens'


class Owner(models.Model):
    owner_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    description = models.TextField()
    image = models.TextField()

    class Meta:
        db_table = 'owner'


class Accommodation(models.Model):
    accommodation_id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255)
    description = models.TextField()
    images = models.JSONField()
    type = models.CharField(max_length=20)
    rooms = models.IntegerField()
    beds = models.IntegerField()
    capacity = models.IntegerField()
    owner_id = models.ForeignKey(Owner, on_delete=models.CASCADE,  db_column="owner_id")

    class Meta:
        db_table = 'accommodation'


class Pricing(models.Model):
    price_id = models.AutoField(primary_key=True)
    accommodation_id = models.ForeignKey(Accommodation, on_delete=models.CASCADE, db_column="accommodation_id")
    price = models.IntegerField()
    cancellation_policy = models.TextField()

    class Meta:
        db_table = 'pricing'


class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    accommodation_id = models.ForeignKey(Accommodation, on_delete=models.CASCADE, db_column="accommodation_id")
    user_id = models.ForeignKey(UsersApp, on_delete=models.CASCADE, db_column="user_id")
    booking_dates = models.JSONField()

    class Meta:
        db_table = 'booking'
