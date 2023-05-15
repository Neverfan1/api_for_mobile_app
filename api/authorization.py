import random

from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .models import *
from django.core.mail import send_mail
from .toolkit import *

from .ex_handler import auth_exception_handler, MissingEmailCode, DifferentCode, DoesNotExistID
from .custom_loguru import auth_logger


class Register(APIView):
    """Класс для регистрации пользователей."""

    @swagger_auto_schema(
        operation_id="Registration",
        operation_summary="Метод для регистрации пользователей",
        tags=['Регистрация и аутентификации'],
        request_body=RegistrationSerializer,
        responses={
            200: openapi.Response(
                description='Регистрация',
                examples={
                    'application/json': {
                        "data": {
                            "user id": 4
                        },
                        "message": "Код для регистрации отправлен на почту test2@mail.ru"
                    }
                }
            )
        }
    )
    @auth_exception_handler
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data['email']
        try:
            user = UsersApp.objects.get(email=email)
            registr = user.registr

            if registr == 1:
                raise UsersApp.MultipleObjectsReturned(email)
            elif registr == 0:
                user.phone_number = serializer.data['phone_number']
                user.name = serializer.data['name']
                user.surname = serializer.data['surname']
                user.sex = serializer.data['sex']
                user.sms = CheckCode.generate_code()
                user.save()

                send_mail(
                    'Code for registration',
                    'Code: ' + user.sms,
                    'bookinglookingapp@gmail.com',
                    [user.email],
                    fail_silently=False
                )
                print(user.sms)

                return Response({
                    'data': {
                        'user id': user.user_id
                    },
                    'message': f'Код для регистрации отправлен на почту {user.email}'
                })

        except UsersApp.DoesNotExist:
            # пользователя с переданной почтой не существует

            phone_number = serializer.data['phone_number']
            name = serializer.data['name']
            surname = serializer.data['surname']
            email = serializer.data['email']
            sex = serializer.data['sex']

            new_user = UsersApp.objects.create(

                name=name,
                surname=surname,
                phone_number=phone_number,
                email=email,
                sex=sex,
                registr=0,
                sms=CheckCode.generate_code()
            )
            send_mail(
                'Code for registration',
                'Code: ' + new_user.sms,
                'bookinglookingapp@gmail.com',
                [new_user.email],
                fail_silently=False
            )
            print(new_user.sms)
            return Response({
                'data': {
                    'user id': new_user.user_id
                },
                'message': f'Код для регистрации отправлен на почту {new_user.email}'
            })


class AuthUser(APIView):
    @swagger_auto_schema(
        operation_id="Authenticationuth",
        operation_summary="Метод для аутентификации пользователей",
        tags=['Регистрация и аутентификации'],
        request_body=AuthSerializer,
        responses={
            200: openapi.Response(
                description='Аутентификация',
                examples={
                    'application/json': {
                        "data": {
                            "user id": 4
                        },
                        "message": "Код для входа отправлен на почту test2@mail.ru"
                    }
                }
            )
        }
    )
    @auth_exception_handler
    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data['email']
        try:
            user = UsersApp.objects.get(email=email)
            new_sms = CheckCode.generate_code()
            send_mail(
                'Code for authenticationuth',
                'Code: ' + new_sms,
                'bookinglookingapp@gmail.com',
                [user.email],
                fail_silently=False
            )
            user.sms = new_sms
            user.save()

            auth_logger.debug(f'Отправлен код {new_sms} на почту {email}')

            return Response({
                'data': {
                    'user id': user.user_id
                },
                'message': f'Код для входа отправлен на почту {user.email}'
            })

        except UsersApp.DoesNotExist:
            raise UsersApp.DoesNotExist(email)


class CheckCode(APIView):
    """Класс для проверки  кода для входа в приложение и выдачи токена."""

    @swagger_auto_schema(
        operation_id="CheckCode",
        operation_summary=(
                "Метод для проверки кода и выдачи токена пользователю"
        ),
        tags=['Регистрация и аутентификации'],
        request_body=CheckCodeSerializer,
        responses={
            200: openapi.Response(
                description='Проверка кода и выдача токена',
                examples={
                    'application/json': {
                        "data": {
                            "token": "****************************************",
                            "user id": 4
                        },
                        "message": "Токен выдан"
                    }
                }
            )
        }
    )
    @auth_exception_handler
    def post(self, request):
        serializer = CheckCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.data['user_id']
        sms_code = serializer.data['code']
        try:
            user = UsersApp.objects.get(user_id=user_id)
        except UsersApp.DoesNotExist:
            raise DoesNotExistID(user_id)

        if user.sms is None:
            raise MissingEmailCode

        if user.sms != sms_code:
            raise DifferentCode(sms_code)

        user.registr = 1
        token, created = MyToken.objects.get_or_create(user_id=user)
        user.save()

        return Response({
            'data': {
                'token': token.key,
                'user id': user.user_id
            },
            'message': 'Токен выдан'
        })

    @staticmethod
    def generate_code():
        """Генерирует sms код."""
        return str(random.randint(0, 9999)).rjust(4, '0')
