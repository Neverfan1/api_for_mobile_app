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
from django.db.models import Q
from datetime import datetime


class Register(APIView):
    """Класс для регистрации пользователей."""

    @swagger_auto_schema(
        operation_id="Registration",
        operation_summary="Метод для регистрации пользователей",
        tags=['Регистрация и аутентификации'],
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
                    'data': user.user_id,
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
                'data': {
                    'user id': new_user.user_id
                },
                'message': 'Запись в бд сделана, код на почту отправлен'
            })


class AuthUser(APIView):
    @swagger_auto_schema(
        operation_id="Authenticationuth",
        operation_summary="Метод для аутенфикации пользователей",
        tags=['Регистрация и аутентификации'],
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
                'data': {
                    'User id': user.user_id
                },
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
                "Метод для проверки кода и выдачи токена пользователю"
        ),
        tags=['Регистрация и аутентификации'],
        request_body=CheckCodeSerializer
    )
    def post(self, request):
        serializer = CheckCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.data['user_id']
        sms_code = serializer.data['code']
        try:
            user = UsersApp.objects.get(user_id=user_id)
        except UsersApp.DoesNotExist:
            raise UsersApp.DoesNotExist(user_id)
        # except MultipleObjectsReturned:
        #     raise MultipleObjectsReturned(user_id)

        # if user.sms is None:
        #     raise MissingSMSCode

        if user.sms != sms_code:
            # raise DifferentSMSCode(received_sms_code)
            return Response({
                'data': user.user_id,
                'message': 'Ошибка. Неверный код'
            })

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


class AccommodationDetail(APIView):
    """Класс для работы с конкретными жилищами."""
    serializer_class = AccommodationSerializer

    @swagger_auto_schema(
        operation_id="Accommodation",
        operation_summary="Метод возвращает информацию о жилье",
        tags=['Жилища']
    )
    @require_authentication
    def get(self, request, id):
        """Возвращает информацию о жилье"""
        data = Accommodation.objects.get(accommodation_id=id)
        pricing = Pricing.objects.get(accommodation_id=id)
        serializer_pricing = PricingSerializer(pricing, many=False)
        serializer_data = self.serializer_class(data, many=False)
        information = serializer_data.data
        information.update(serializer_pricing.data)

        all_dates = to_representation()

        bookings = Booking.objects.filter(accommodation_id=id)

        # Составляем список уже забронированных дат
        reserved_dates = []
        for booking in bookings:
            for booking_day in booking.booking_dates:
                reserved_dates.append(
                    {"month": booking_day["month"], "year": booking_day["year"], "date": booking_day["date"]})

        # Удаляем из all_dates все забронированные даты
        for booked in reserved_dates:
            for date in all_dates:
                if date["month"] == booked["month"] and date["year"] == booked["year"]:
                    date["date"] = list(set(date["date"]) - set(booked["date"]))

        information['free_dates'] = all_dates
        response_data = {
            "data": information,
            "message": 'Информация получена',
        }

        return Response(response_data)


class AccommodationAll(APIView):
    """Класс для работы с жилищами."""
    serializer_class = AccommodationSerializer

    @swagger_auto_schema(
        operation_id="Accommodation",
        operation_summary="Метод возвращает информацию о всех жилищах",
        tags=['Жилища']

    )
    @require_authentication
    def get(self, request):
        """Возвращает информацию о жилье"""
        offset = self.request.query_params.get('offset')
        count = self.request.query_params.get('count')

        data = Accommodation.objects.all().order_by('accommodation_id')
        pricing = Pricing.objects.all().order_by('accommodation_id')
        serializer = self.serializer_class(data, many=True)
        serializer_pricing = PricingSerializer(pricing, many=True)
        data_with_pricing = []
        for i, item in enumerate(serializer.data):
            item.update(serializer_pricing.data[i])
            data_with_pricing.append(item)

        data = paginate_data(data_with_pricing, offset, count)
        response_data = {
            "data": data,
            "message": 'Информация получена',
        }

        return Response(response_data)


class AccommodationFiltering(APIView):  # TODO сделать фильтрацию по цене, и чтобы выводилась цена
    """Класс для фильтрации жилищ."""
    serializer_class = AccommodationFilterSerializer

    @swagger_auto_schema(
        operation_id="Accommodation",
        operation_summary="Метод возвращает отфильтрованные жилища",
        tags=['Жилища']
    )
    @require_authentication
    def get(self, request):
        type = self.request.query_params.get('type')
        rooms = self.request.query_params.get('rooms')
        beds = self.request.query_params.get('beds')
        capacity = self.request.query_params.get('capacity')
        # price_to = self.request.query_params.get('price_to')
        # price_from = self.request.query_params.get('price_from')
        offset = self.request.query_params.get('offset')
        count = self.request.query_params.get('count')

        # создаем пустой объект фильтра
        filters = Q()

        # добавляем условия фильтрации, если параметры заданы
        if type:
            filters &= Q(type=type)
        if rooms:
            filters &= Q(rooms=rooms)
        if beds:
            filters &= Q(beds=beds)
        if capacity:
            filters &= Q(capacity=capacity)
        # if price_from and price_to:
        #     filters &= Q(pricing__price__gte=price_from, pricing__price__lte=price_to)

        # фильтруем жилища по заданным параметрам
        accommodations = Accommodation.objects.filter(filters).order_by('accommodation_id')

        # сериализуем результат и возвращаем его
        serializer = AccommodationSerializer(accommodations, many=True)
        data = paginate_data(serializer.data, offset, count)
        response_data = {
            "data": data,
            "message": 'Информация получена',
        }

        return Response(response_data)


class OwnerDetail(APIView):
    """Класс для работы с владельцем жилища."""
    serializer_class = OwnerSerializer

    @swagger_auto_schema(
        operation_id="Owner",
        operation_summary="Метод возвращает информацию о хозяине",
        tags=['Хозяин']
    )
    @require_authentication
    def get(self, request, id):
        """Возвращает информацию о хозяине"""
        data = Owner.objects.get(owner_id=id)
        serializer = self.serializer_class(data, many=False)
        response_data = {
            "data": serializer.data,
            "message": 'Информация получена',
        }

        return Response(response_data)


class BookingDate(APIView):
    serializers_class = BookingSerializer

    @swagger_auto_schema(
        operation_id="BookingDate",
        operation_summary="Метод бронирования дат",
        tags=['Бронь'],
        request_body=BookingSerializer
    )
    @require_authentication
    def post(self, request):
        """Делает бронь на определенное жилье для определенного пользователя"""

        serializer = self.serializers_class(data=request.data)
        serializer.is_valid()

        # Получаем жилище и даты бронирования
        accommodation = Accommodation.objects.get(accommodation_id=serializer.data['accommodation_id'])
        booking_dates = serializer.data['booking_dates']

        # Проверяем наличие пересечения дат бронирования
        for dates in booking_dates:
            year = dates['year']
            month = datetime.strptime(dates['month'], '%B').month
            for day in dates['date']:
                overlapping_bookings = Booking.objects.filter(
                    accommodation_id=accommodation,
                    booking_dates__contains=[{"date": [day], "year": year, "month": dates['month']}]
                ).exclude(
                    Q(booking_dates__contains=[{"date": [day], "year": year, "month": dates['month']}]) &
                    Q(booking_dates__contains=[{"date": [day - 1], "year": year, "month": dates['month']}]) &
                    Q(booking_dates__contains=[{"date": [day + 1], "year": year, "month": dates['month']}])
                )
                if overlapping_bookings.exists():
                    # Если есть пересечение, выдаем ошибку
                    return Response({'message': 'Невозможно забронировать жилище в эти даты'})

        # Если пересечений нет, создаем новую запись в Booking
        new_booking = Booking.objects.create(
            booking_dates=booking_dates,
            accommodation_id=accommodation,
            user_id=UsersApp.objects.get(user_id=request.META.get('HTTP_ID')),
        )
        new_booking.save()

        return Response({
            'data': {
                'booking_id': new_booking.booking_id
            },
            'message': 'Жилье забронированно'
        })


class UserDetail(APIView):
    """Класс для работы с владельцем."""
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_id="User",
        operation_summary="Метод возвращает информацию о пользователе",
        tags=['Пользователь']
    )
    @require_authentication
    def get(self, request, id):
        """Возвращает информацию о хозяине"""
        data = UsersApp.objects.get(user_id=id)
        serializer = self.serializer_class(data, many=False)
        response_data = {
            "data": serializer.data,
            "message": 'Информация получена',
        }

        return Response(response_data)

class MyView(APIView):
    @require_authentication
    def get(self, request):
        return HttpResponse('OK')
