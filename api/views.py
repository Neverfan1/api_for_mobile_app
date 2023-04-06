from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .models import *
from .toolkit import *
from django.db.models import Q
from datetime import datetime
from drf_yasg import openapi

from .ex_handler import exception_handler, DateError


class AccommodationDetail(APIView):
    """Класс для работы с конкретными жилищами."""
    serializer_class = AccommodationDetailSerializer

    @swagger_auto_schema(
        operation_id="AccommodationDetail",
        operation_summary="Метод возвращает информацию о жилье",
        tags=['Жилища']
    )
    @exception_handler('Жилища')
    @require_authentication
    def get(self, request, id):
        """Возвращает информацию о жилье"""
        data = Accommodation.objects.get(accommodation_id=id)
        serializer_data = self.serializer_class(data, many=False)
        information = serializer_data.data

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
        operation_id="AccommodationAll",
        operation_summary="Метод возвращает информацию о всех жилищах",
        tags=['Жилища']

    )
    @exception_handler('Жилища')
    @require_authentication
    def get(self, request):
        """Возвращает информацию о жилье"""
        offset = self.request.query_params.get('offset')
        count = self.request.query_params.get('count')

        data = Accommodation.objects.all().order_by('accommodation_id')
        serializer = self.serializer_class(data, many=True)

        data = paginate_data(serializer.data, offset, count)
        response_data = {
            "data": data,
            "message": 'Информация получена',
        }

        return Response(response_data)


class AccommodationFiltering(APIView):
    """Класс для фильтрации жилищ."""
    serializer_class = AccommodationSerializer

    @swagger_auto_schema(
        operation_id="AccommodationFiltering",
        operation_summary="Метод возвращает отфильтрованные жилища",
        tags=['Жилища']
    )
    @exception_handler('Жилища')
    @require_authentication
    def get(self, request):
        type = self.request.query_params.get('type')
        rooms = self.request.query_params.get('rooms')
        beds = self.request.query_params.get('beds')
        capacity = self.request.query_params.get('capacity')
        price_to = self.request.query_params.get('price_to')
        price_from = self.request.query_params.get('price_from')
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
        if price_from and price_to:
            filters &= Q(pricing__price__gte=price_from, pricing__price__lte=price_to)

        # фильтруем жилища по заданным параметрам
        accommodations = Accommodation.objects.filter(filters).order_by('accommodation_id')

        # сериализуем результат и возвращаем его
        serializer = self.serializer_class(accommodations, many=True)
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
        operation_id="OwnerDetail",
        operation_summary="Метод возвращает информацию о хозяине",
        tags=['Хозяин']
    )
    @exception_handler('Хозяин')
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


class OwnerAccommodation(APIView):
    """Класс для работы с владельцем жилища."""
    serializer_class = AccommodationSerializer

    @swagger_auto_schema(
        operation_id="OwnerAccommodation",
        operation_summary="Метод возвращает информацию о всех жилищах хозяина",
        tags=['Хозяин']
    )
    @exception_handler('Хозяин')
    @require_authentication
    def get(self, request, id):
        data = Accommodation.objects.filter(owner_id=id)
        serializer = self.serializer_class(data, many=True)
        response_data = {
            "data": serializer.data,
            "message": 'Информация получена',
        }
        return Response(response_data)


class CreateBookingDate(APIView):
    serializers_class = CreateBookingSerializer

    @swagger_auto_schema(
        operation_id="CreateBookingDate",
        operation_summary="Метод бронирования дат",
        tags=['Бронь'],
        request_body=CreateBookingSerializer
    )
    @exception_handler('Бронь')
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
                    raise DateError(booking_dates)

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


class CancelBookingDate(APIView):
    serializers_class = CancelBookingSerializer

    @swagger_auto_schema(
        operation_id="CancelBookingDate",
        operation_summary="Метод удаления брони",
        tags=['Бронь'],
        responses={
            200: openapi.Response(
                description='Удаление брони по ID',
                examples={
                    'application/json': {
                        "data": {
                            "booking_id": 5
                        },
                        "message": "Бронь успешно удалена"
                    }
                }
            )
        }
    )
    @exception_handler('Бронь')
    @require_authentication
    def delete(self, request, id):
        """Удаляет бронь по ID"""
        booking = Booking.objects.get(booking_id=id)

        booking.delete()

        return Response({
            'data': {
                'booking_id': id
            },
            'message': 'Бронь успешно удалена'
        })


class UserDetail(APIView):
    """Класс для работы с пользователем."""
    serializer_class = UserSerializer


    @swagger_auto_schema(
        operation_id="UserDetail",
        operation_summary="Метод возвращает информацию о пользователе",
        tags=['Пользователь'],

    )

    @exception_handler('Пользователь')
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


class UserBooking(APIView):
    """Класс для работы с  пользователем."""
    serializer_class = UserBookingSerializer

    @swagger_auto_schema(
        operation_id="UserBooking",
        operation_summary="Метод возвращает информацию о всех бронях пользователя",
        tags=['Пользователь'],
        responses={
            200: openapi.Response(
                description='Список бронирований пользователя',
                examples={
                    'application/json': {
                        "data": [
                            {
                                "accommodation_id": 1,
                                "type": "Комната",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "price": 4000,
                                "booking_dates": [
                                    [
                                        {
                                            "date": [
                                                1,
                                                2,
                                                3,
                                                4,
                                                5,
                                                6,
                                                7,
                                                8,
                                                9,
                                                10
                                            ],
                                            "year": 2023,
                                            "month": "April"
                                        }
                                    ]
                                ]
                            }
                        ],
                        "message": "Информация получена"
                    }
                }
            )
        }
    )
    @exception_handler('Пользователь')
    @require_authentication
    def get(self, request):
        user_id = request.META.get('HTTP_ID')
        bookings = Booking.objects.filter(user_id=user_id)
        accommodation_ids = [booking.accommodation_id_id for booking in bookings]
        data = Accommodation.objects.filter(accommodation_id__in=accommodation_ids)
        serializer = self.serializer_class(data, many=True)
        response_data = {
            "data": serializer.data,
            "message": 'Информация получена',
        }

        return Response(response_data)

# TODO добавить во все методы responses в swagger_auto_schema
