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
        tags=['Жилища'],
        responses={
            200: openapi.Response(
                description='Подробная информация о жилище',
                examples={
                    'application/json': {
                        "data": {
                            "accommodation_id": 1,
                            "address": "Пушкина 7а",
                            "description": "Тестовое жилище 1",
                            "image_preview": "img.ru",
                            "images": {
                                "1": "image1",
                                "2": "image2"
                            },
                            "type": "Комната",
                            "rooms": 2,
                            "beds": 2,
                            "capacity": 2,
                            "owner_id": 1,
                            "owner_name": "Test Owner 1",
                            "price": 4000,
                            "cancellation_policy": "за день до въезда",
                            "free_dates": [
                                {
                                    "month": "April",
                                    "year": 2023,
                                    "date": [
                                        11,
                                        12,
                                        30
                                    ]
                                },
                                {
                                    "month": "May",
                                    "year": 2023,
                                    "date": [
                                        1,
                                        29,
                                        30,
                                        31
                                    ]
                                },
                                {
                                    "month": "June",
                                    "year": 2023,
                                    "date": [
                                        1,
                                        2,
                                        3,

                                    ]
                                }
                            ]
                        },
                        "message": "Информация получена"
                    }
                }
            )
        }
    )
    # @exception_handler('Жилища')
    # @require_authentication
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
        tags=['Жилища'],
        manual_parameters=[
            openapi.Parameter(name='offset', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Смещение'),
            openapi.Parameter(name='count', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Количество записей'),
        ],
        responses={
            200: openapi.Response(
                description='Все жилища',
                examples={
                    'application/json': {
                        "data": [
                            {
                                "accommodation_id": 1,
                                "type": "Комната",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "address": "Test",
                                "price": 4000
                            },
                            {
                                "accommodation_id": 2,
                                "type": "Отель",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "Image.com",
                                "address": "Test",
                                "price": 2500
                            },
                            {
                                "accommodation_id": 3,
                                "type": "Дом",
                                "owner_id": 2,
                                "owner_name": "Test Owner 2",
                                "image_preview": "image.com",
                                "address": "Test",
                                "price": 7000
                            }
                        ],
                        "message": "Информация получена"
                    }
                }
            )
        }

    )
    # @exception_handler('Жилища')
    # @require_authentication
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
        tags=['Жилища'],
        manual_parameters=[
            openapi.Parameter(name='type', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Тип жилища'),
            openapi.Parameter(name='rooms', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Количество комнат'),
            openapi.Parameter(name='beds', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Количество кроватей'),
            openapi.Parameter(name='capacity', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Вместимость'),
            openapi.Parameter(name='price_to', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Максимальная цена'),
            openapi.Parameter(name='price_from', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Минимальная цена'),
            openapi.Parameter(name='offset', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Смещение'),
            openapi.Parameter(name='count', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Количество записей'),
        ],
        responses={
            200: openapi.Response(
                description='Поиск жилищ по параметрам',
                examples={
                    'application/json': {
                        "data": [
                            {
                                "accommodation_id": 1,
                                "type": "Комната",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "address": "Пушкина 7а",
                                "price": 4000
                            },
                            {
                                "accommodation_id": 2,
                                "type": "Отель",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "address": "Кирова 41",
                                "price": 2500
                            },
                            {
                                "accommodation_id": 3,
                                "type": "Дом",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "address": "Антонова 1",
                                "price": 7000
                            },
                            {
                                "accommodation_id": 4,
                                "type": "Комната",
                                "owner_id": 2,
                                "owner_name": "Test Owner 2",
                                "image_preview": "none",
                                "address": "Вишневый проезд 1",
                                "price": 2315
                            }
                        ],
                        "message": "Информация получена"
                    }
                }
            )
        }
    )
    # @exception_handler('Жилища')
    # @require_authentication
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
        elif price_from:
            filters &= Q(pricing__price__gte=price_from)
        elif price_to:
            filters &= Q(pricing__price__lte=price_to)
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
        tags=['Хозяин'],
        responses={
            200: openapi.Response(
                description='Информация о хозяине',
                examples={
                    'application/json': {
                        "data": {
                            "owner_id": 1,
                            "name": "Test Owner 1",
                            "contact": "+79999999999",
                            "description": "Тестовый овнер 1",
                            "image": "https://test-image.com"
                        },
                        "message": "Информация получена"
                    }
                }
            )
        }
    )
    # @exception_handler('Хозяин')
    # @require_authentication
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
        tags=['Хозяин'],
        responses={
            200: openapi.Response(
                description='Все жилища хозяина',
                examples={
                    'application/json': {
                        "data": [
                            {
                                "accommodation_id": 1,
                                "type": "Комната",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "price": 4000
                            },
                            {
                                "accommodation_id": 2,
                                "type": "Отель",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "Image.com",
                                "price": 2500
                            }
                        ],
                        "message": "Информация получена"
                    }
                }
            )
        }
    )
    # @exception_handler('Хозяин')
    # @require_authentication
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
        request_body=CreateBookingSerializer,
        responses={
            200: openapi.Response(
                description='Бронирование жилища',
                examples={
                    'application/json': {
                        "data": {
                            "booking_id": 1
                        },
                        "message": "Жилье забронированно"
                    }
                }
            )
        }
    )
    # @exception_handler('Бронь')
    # @require_authentication
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
            user_id=UsersApp.objects.get(user_id=get_user_id_from_token(request)),
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
    # @exception_handler('Бронь')
    # @require_authentication
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
        responses={
            200: openapi.Response(
                description='Подробная информация о пользователе',
                examples={
                    'application/json': {
                        "data": {
                            "email": "test@gmail.com",
                            "name": "TestUser1",
                            "surname": "Tester1",
                            "sex": 1,
                            "phone_number": "+79279180444"
                        },
                        "message": "Информация получена"
                    }
                }
            )
        }
    )
    # @exception_handler('Пользователь')
    # @require_authentication
    def get(self, request):
        """Возвращает информацию о пользователе"""
        data = UsersApp.objects.get(user_id=get_user_id_from_token(request))
        serializer = self.serializer_class(data, many=False)
        response_data = {
            "data": serializer.data,
            "message": 'Информация получена',
        }

        return Response(response_data)


class UserBooking(APIView):
    """Класс для работы с  пользователем."""
    serializer_class = BookingWithAccommodationSerializer

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
                                "booking_id": 5,
                                "accommodation_id": 1,
                                "type": "Комната",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "images": [
                                    "image.com",
                                    "image2.com"
                                ],
                                "price": 4000,
                                "booking_dates": [
                                    {
                                        "date": [
                                            17,
                                            18,
                                            19
                                        ],
                                        "year": 2023,
                                        "month": "August"
                                    }
                                ],
                                "address": "Пушкина 7а"
                            },
                            {
                                "booking_id": 6,
                                "accommodation_id": 2,
                                "type": "Отель",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "images": [
                                    "image.com",
                                    "image2.com"
                                ],
                                "price": 2500,
                                "booking_dates": [
                                    {
                                        "date": [
                                            20,
                                            21,
                                            22
                                        ],
                                        "year": 2023,
                                        "month": "August"
                                    }
                                ],
                                "address": "Кирова 41"
                            },
                            {
                                "booking_id": 4,
                                "accommodation_id": 2,
                                "type": "Отель",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "images": [
                                    "image.com",
                                    "image2.com"
                                ],
                                "price": 2500,
                                "booking_dates": [
                                    {
                                        "date": [
                                            17,
                                            18,
                                            19
                                        ],
                                        "year": 2023,
                                        "month": "August"
                                    }
                                ],
                                "address": "Кирова 41"
                            },
                            {
                                "booking_id": 7,
                                "accommodation_id": 3,
                                "type": "Дом",
                                "owner_id": 1,
                                "owner_name": "Test Owner 1",
                                "image_preview": "img.ru",
                                "images": [
                                    "image.com",
                                    "image2.com"
                                ],
                                "price": 7000,
                                "booking_dates": [
                                    {
                                        "date": [
                                            1,
                                            2,
                                            3,
                                            4,
                                            5
                                        ],
                                        "year": 2023,
                                        "month": "September"
                                    }
                                ],
                                "address": "Антонова 1"
                            }
                        ],
                        "message": "Информация получена"
                    }
                }
            )
        }
    )
    # @exception_handler('Пользователь')
    # @require_authentication
    def get(self, request):
        user_id = get_user_id_from_token(request)
        bookings = Booking.objects.filter(user_id=user_id).select_related('accommodation_id')
        serializer = self.serializer_class(bookings, many=True)

        response_data = {
            "data": serializer.data,
            "message": 'Информация получена',
        }

        return Response(response_data)
