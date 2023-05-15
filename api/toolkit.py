import os

from .models import MyToken
from django.http import HttpResponseBadRequest
from datetime import datetime
import datetime
from functools import wraps
from django.http import HttpResponse
from .ex_handler import exception_handler, TokenError
import jwt


def require_authentication(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            user = MyToken.objects.get(key=token).user_id
            if user:
                request.user = user
                return view_func(self, request, *args, **kwargs)
        except MyToken.DoesNotExist:
            raise TokenError()

    return wrapper


def paginate_data(data, offset, count=None):
    """
    Возвращает список элементов данных согласно параметрам offset и count.
    """
    if offset and offset.isdigit():
        offset = int(offset)
    else:
        offset = 0

    if count and count.isdigit():
        count = int(count)
    else:
        count = None

    if count is not None:
        paginated_data = data[offset:offset + count]
    else:
        paginated_data = data[offset:]

    return paginated_data


all_dates = {
    "January": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                29, 30, 31],
    "February": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
    "March": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
              30, 31],
    "April": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
              30],
    "May": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
            30, 31],
    "June": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30],
    "July": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31],
    "August": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
               29, 30, 31],
    "September": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                  29, 30],
    "October": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                29, 30, 31],
    "November": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                 29, 30],
    "December": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                 29, 30, 31]
}


def to_representation():
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month

    # Get dates for current month and next two months
    dates = []
    for month in range(current_month, current_month + 3):
        if month > 12:
            # If we've gone past December, wrap around to January
            year = current_year + 1
            month -= 12
        else:
            year = current_year

        month_name = datetime.datetime.strptime(str(month), "%m").strftime("%B")

        if month_name in all_dates:
            date_list = []
            for date in all_dates[month_name]:
                if date >= now.day and month_name == now.strftime("%B"):
                    date_list.append(date)
                elif month_name != now.strftime("%B"):
                    date_list.append(date)
            dates.append({
                'month': month_name,
                'year': year,
                'date': date_list
            })
    return dates


def create_booking_dict():
    now = datetime.datetime.now()
    current_year = now.year
    dict_booking = [
        {
            current_year: {
                "January": [],
                "February": [],
                "March": [],
                "April": [],
                "May": [],
                "June": [],
                "July": [],
                "August": [],
                "September": [],
                "October": [],
                "November": [],
                "December": []

            }}]
    return dict_booking


def get_user_id_from_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]  # Получаем токен из заголовка Authorization

    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'),
                             algorithms=['HS256'])  # Раскодируем токен с использованием секретного ключа
        user_id = payload.get('user_id')  # Получаем значение user_id из раскодированной полезной нагрузки
        return user_id
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired.")  # Обработка исключения, если токен истек срок действия
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token.")  # Обработка исключения, если токен недействительный или поврежден
