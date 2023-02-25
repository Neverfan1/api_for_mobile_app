import random
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .models import *
from django.core.mail import send_mail
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .toolkit import *


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
            else:
                raise UsersApp.DoesNotExist

        except UsersApp.DoesNotExist:
            # клиента с переданным номером телефона не существует

            phone_number = serializer.data['phone_number']
            name = serializer.data['name']
            surname = serializer.data['surname']
            email = serializer.data['email']
            sex = serializer.data['sex']

            new_client = UsersApp.objects.create(

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
                'Code: ' + new_client.sms,
                'bookinglookingapp@gmail.com',
                [new_client.email],
                fail_silently=False
            )
            print(new_client.sms)
            return Response({
                'data': new_client.id,
                'message': 'Запись в бд сделана'
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
            user.sms=new_sms
            user.save()
            print(new_sms)
            return Response({
                'data': user.id,
                'message': 'все ок'
            })

        except UsersApp.DoesNotExist:

            return Response({
                'message': 'Ошибка, такого клиента нет.'
            })


class CheckCode(APIView):
    """Класс для проверки смс кода для входа в приложение и установки новой сессии."""

    @swagger_auto_schema(
        operation_id="CheckCode",
        operation_summary=(
                "Метод для проверки смс кода для окончания регистрация пользователя "
                "и выдачи ему токена"
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

        # Compare received and stored sms codes.
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
            'data': user.id,
            'message': 'Все ок.'
        })

    @staticmethod
    def generate_code():
        """Генерирует sms код."""
        return str(random.randint(0, 9999)).rjust(4, '0')


class MyView(APIView):
    def get(self, request):
        # код для обработки запроса
        if process_request(request):
            return Response({'message': 'Вы аутентифицированы и имеете доступ к этому методу.'})
        else:
            return Response({'message': 'нет.'})
