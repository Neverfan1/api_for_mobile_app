import random
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .models import *
from django.core.mail import send_mail
from .toolkit import *
from django.http import HttpResponseBadRequest, HttpResponse


class Register(APIView):
    """Класс для регистрации пользователей."""

    @swagger_auto_schema(
        operation_id="Register",
        operation_summary="Метод для регистрации пользователей в мобильных приложениях",
        tags=['Регистрация и аутентификации в мобильных приложениях'],
        request_body=RegistrationSerializer
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data['email']
        try:
            user = UsersApp.objects.get(email=email)
            registr = user.registr

            if registr == 1:
                return Response({
                    'message': 'Ошибка. Данный польователем зареган'
                })
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
                    'data': user.id,
                    'message': 'Запись в бд изменена, код на почту отправлен'
                })
            else:
                raise UsersApp.DoesNotExist

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
                'User id': new_user.id,
                'message': 'Запись в бд сделана, код на почту отправлен'
            })


class AuthUser(APIView):
    @swagger_auto_schema(
        operation_id="Auth",
        operation_summary="Метод для аутенфикации пользователей в мобильных приложениях",
        tags=['Регистрация и аутентификации в мобильных приложениях'],
        request_body=AuthSerializer
    )
    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data['email']
        try:
            user = UsersApp.objects.get(email=email)
            new_sms = CheckCode.generate_code()
            send_mail(
                'Code for registration',
                'Code: ' + new_sms,
                'bookinglookingapp@gmail.com',
                [user.email],
                fail_silently=False
            )
            user.sms = new_sms
            user.save()
            print(new_sms)
            return Response({
                'User id': user.id,
                'message': 'Код отправлен на почту'
            })

        except UsersApp.DoesNotExist:

            return Response({
                'message': 'Ошибка, такого пользователя нет.'
            })


class CheckCode(APIView):
    """Класс для проверки  кода для входа в приложение и выдачи токена."""

    @swagger_auto_schema(
        operation_id="CheckCode",
        operation_summary=(
                "Метод для проверки кода для окончания регистрация/авторизации"
                " ользователя и выдачи ему токена"
        ),
        tags=['Регистрация и аутентификации в мобильных приложениях'],
        request_body=CheckCodeSerializer
    )
    def post(self, request):
        serializer = CheckCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.data['user_id']
        sms_code = serializer.data['code']
        try:
            user = UsersApp.objects.get(id=user_id)
        except UsersApp.DoesNotExist:
            raise UsersApp.DoesNotExist(user_id)
        # except MultipleObjectsReturned:
        #     raise MultipleObjectsReturned(user_id)

        # if user.sms is None:
        #     raise MissingSMSCode

        if user.sms != sms_code:
            # raise DifferentSMSCode(received_sms_code)
            return Response({
                'data': user.id,
                'message': 'Ошибка. Неверный код'
            })

        user.registr = 1
        token, created = MyToken.objects.get_or_create(user=user)
        user.save()

        return Response({
            'token': token.key,
            'User id': user.id,
            'message': 'Токен выдан'
        })

    @staticmethod
    def generate_code():
        """Генерирует sms код."""
        return str(random.randint(0, 9999)).rjust(4, '0')


class AuthenticatedAPIView(APIView):
    """Класс для доступа к другим методам.
    Только аутентифицированный пользователь имеет доступ"""
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return api_auth_required(view)


class MyView(AuthenticatedAPIView):
    """Тестовый класс"""
    def get(self, request):
        return HttpResponse('OK')
