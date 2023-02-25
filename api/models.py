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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'sex', 'phone_number']

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

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
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'

# import binascii
# import os
#
# from django.db import models
#
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
#
#
# class MyUserManager(BaseUserManager):
#     def create_user(self, email, name, surname, sex, phone_number, registr, sms, password=None):
#         if not email:
#             raise ValueError('Users must have an email address')
#
#         user = self.model(
#             email=self.normalize_email(email),
#             name=name,
#             surname=surname,
#             sex=sex,
#             phone_number=phone_number,
#             registr=registr,
#             sms=sms
#         )
#
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, email, name, surname, sex, phone_number, registr, sms, password):
#         user = self.create_user(
#             email=self.normalize_email(email),
#             name=name,
#             surname=surname,
#             sex=sex,
#             phone_number=phone_number,
#             registr=registr,
#             sms=sms,
#             password=password
#         )
#         user.is_admin = True
#         user.save(using=self._db)
#         return user
#
#
# class UsersApp(AbstractBaseUser):
#     email = models.CharField(max_length=255, unique=True)
#     name = models.CharField(max_length=255)
#     surname = models.CharField(max_length=255)
#     sex = models.SmallIntegerField()
#     phone_number = models.CharField(max_length=16)
#     registr = models.SmallIntegerField(default=0)
#     sms = models.CharField(max_length=255, blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     is_admin = models.BooleanField(default=False)
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['name', 'surname', 'sex', 'phone_number', 'registr', 'sms']
#
#     objects = MyUserManager()
#
#     def __str__(self):
#         return self.email
#
#     def has_perm(self, perm, obj=None):
#         return True
#
#     def has_module_perms(self, app_label):
#         return True
#
#     @property
#     def is_staff(self):
#         return self.is_admin
#
#
# class MyToken(models.Model):
#     user = models.ForeignKey(UsersApp, related_name='my_tokens', on_delete=models.CASCADE)
#     key = models.CharField(max_length=40, unique=True, blank=True)
#     created = models.DateTimeField(auto_now_add=True)
#
#     def save(self, *args, **kwargs):
#         if not self.key:
#             self.key = self.generate_key()
#         return super(MyToken, self).save(*args, **kwargs)
#
#     def generate_key(self):
#         return binascii.hexlify(os.urandom(20)).decode()
#
#     class Meta:
#         verbose_name = 'Token'
#         verbose_name_plural = 'Tokens'
