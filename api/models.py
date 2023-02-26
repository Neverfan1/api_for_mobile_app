import binascii
import os

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UsersApp(models.Model):
    email = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    sex = models.SmallIntegerField()
    phone_number = models.CharField(max_length=16)
    registr = models.SmallIntegerField(default=0)
    sms = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'sex', 'phone_number']

    class Meta:
        db_table = 'users'


class MyToken(models.Model):
    user = models.ForeignKey(UsersApp, related_name='auth_token', on_delete=models.CASCADE)
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
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'
