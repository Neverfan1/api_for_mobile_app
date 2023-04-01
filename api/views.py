from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .models import *
from .toolkit import *
from django.db.models import Q
from datetime import datetime

from .ex_handler import exception_handler, DateError


class AccommodationDetail(APIView):
    """Класс для работы с конкретными жилищами."""
    serializer_class = AccommodationDetailSerializer

    @swagger_auto_schema(
        operation_id="Accommodation",
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
        operation_id="Accommodation",
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


class AccommodationFiltering(APIView):  # TODO сделать фильтрацию по цене, и чтобы выводилась цена
    """Класс для фильтрации жилищ."""
    serializer_class = AccommodationSerializer

    @swagger_auto_schema(
        operation_id="Accommodation",
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
        operation_id="Owner",
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


class BookingDate(APIView):
    serializers_class = BookingSerializer

    @swagger_auto_schema(
        operation_id="BookingDate",
        operation_summary="Метод бронирования дат",
        tags=['Бронь'],
        request_body=BookingSerializer
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


class UserDetail(APIView):
    """Класс для работы с владельцем."""
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_id="User",
        operation_summary="Метод возвращает информацию о пользователе",
        tags=['Пользователь']
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

#TODO написать get метод, который показывает текущие брони пользователя
#TODO написать del метод, который удаляет бронь
