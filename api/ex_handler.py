from typing import List
from functools import wraps

from django.db import IntegrityError, DataError
from django.core.exceptions import EmptyResultSet, ObjectDoesNotExist, MultipleObjectsReturned

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, ParseError

from .custom_loguru import *


# кастомные классы ошибок

class MyException(Exception):
    """Базовый класс ошибки для IwaterAPI."""
    pass


class MissingEmailCode(MyException):
    """Ошибка должна бросаться при пустом поле sms."""
    pass

class DateError(MyException):
    """Ошибка должна бросаться если есть пересечение в датах."""
    pass

class TokenError(MyException):
    """Ошибка должна бросаться передачи неверного токена."""
    pass


class DoesNotExistID(MyException):
    """Ошибка должна бросаться при отсутствии пользователя с указанным ID ."""
    pass


class DifferentCode(MyException):
    """Ошибка должна бросаться при несовпадении отправленного и полученного кода."""
    pass


# обработчик ошибок для основных методов представлений

def ex_handler(error_code: int = 1,
               message: str = 'Неизвестная ошибка.',
               object_name: str = 'Объект',
               class_name: str = 'Класс',
               method_name: str = 'Метод',
               error_dates: List[dict] = [],
               error_fields: List[str] = []) -> dict:
    """Возвращает стандартный ответ на ошибку (код и сообщение).

    :param error_code: код ошибки
    :param message: пользовательское сообщение (только для кодов 1 и 8)
    :param object_name: название объекта, с которым связана ошибка
    :param class_name: название класса, в котором возникла ошибка
    :param method_name: название метода, в котором возникла ошибка
    :param error_dates: даты, при бронировании которых произошла ошибка
    :param error_fields: поля, при валидации которых произошла ошибка
    :return: стандартный ответ на некорректный запрос
    """
    messages = {
        1: message,
        2: 'Данные по запросу не найдены.',
        3: 'Ошибка в формате данных. Проверьте правильность введенных данных.',
        4: f'Поля {error_fields} не указаны, либо указаны неверно. Проверьте правильность введенных данных.',
        5: f'{object_name} с таким id уже присутствует в базе данных.',
        6: f'{object_name} с таким id отсутствует в базе данных.',
        7: 'Возможно отсутствует заголовок запроса или поле данных в теле запроса.',
        8: 'Unauthorized.',
        9: f'Невозможно забронировать жилище в эти даты {error_dates}.',
        10: message,
    }

    error_root = f'Ошибка в {class_name}|{method_name}'

    return {
        'error_code': error_code,
        'message': f'{messages[error_code]} {error_root}'
    }


def exception_handler(object_name: str = 'Объект'):
    """Декоратор для ловли и обработки ошибок в методах представлений."""
    def func_decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                log_request_created(view_logger, *args, **kwargs)

                result = method(self, *args, **kwargs)

                log_request_completed(view_logger, result, *args, **kwargs)
            except Exception as e:
                error_fields = []

                if isinstance(e, EmptyResultSet):
                    error_code = 2
                elif isinstance(e, (ParseError, DataError, ValueError)):
                    error_code = 3
                elif isinstance(e, ValidationError):
                    error_code = 4
                    error_fields = list(e.get_full_details().keys())
                elif isinstance(e, IntegrityError):
                    error_code = 5
                elif isinstance(e, ObjectDoesNotExist):
                    error_code = 6
                elif isinstance(e, KeyError):
                    error_code = 7
                elif isinstance(e, TokenError):
                    error_code = 8
                elif isinstance(e, DateError):
                    error_code = 9
                elif isinstance(e, TypeError):
                    error_code = 10
                else:
                    error_code = 1

                error = ex_handler(
                    error_code=error_code,
                    message=(e.args[0] if e.args else 'Неизвестная ошибка.'),
                    object_name=object_name,
                    class_name=self.__class__.__name__,
                    method_name=method.__name__,
                    error_dates=(e.args[0] if e.args else []),
                    error_fields=error_fields
                )

                log_request_error(view_logger, e, error)

                return Response(error)
            else:
                return result

        return wrapper

    return func_decorator


# обработчик ошибок для методов авторизации

def auth_ex_handler(error_code: int = 1,
                    message: str = 'Неизвестная ошибка.',
                    user_id: id = 'UNKNOWN_ID',
                    user_email: str = 'UNKNOWN_EMAIL',
                    code: str = 'UNKNOWN_CODE',
                    error_fields: List[str] = []) -> dict:
    """Возвращает стандартный ответ на ошибку при авторизации (код и сообщение).

    :param error_code: код ошибки
    :param message: пользовательское сообщение (только для кода 1)
    :param user_id: ID пользователя, на котором возникла ошибка
    :param user_email: EMAIL пользователя, на котором возникла ошибка
    :param code: код, на котором возникла ошибка
    :param error_fields: поля, при валидации которых произошла ошибка
    :return: стандартный ответ на некорректный запрос при авторизации
    """
    messages = {
        1: message,
        2: f'Отсутствует пользователь с user_email={user_email}',
        4: f'Поля {error_fields} не указаны, либо указаны неверно. Проверьте правильность введенных данных.',
        3: f'Отсутствует пользователь с user_id={user_id}',
        5: f' Пользователь с user_email={user_email} уже присутствует в базе данных.',
        9: f'Отправленный код {code} не совпадает с кодом пользователя!',
        10: f'Код не введен.'
    }

    return {
        'error_code': error_code,
        'message': messages[error_code]
    }


def auth_exception_handler(method):
    """Декоратор для ловли и обработки ошибок в методах авторизации."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            log_request_created(auth_logger, *args, **kwargs)

            result = method(self, *args, **kwargs)

            log_request_completed(auth_logger, result, *args, **kwargs)
        except Exception as e:
            error_fields = []

            if isinstance(e, ObjectDoesNotExist):
                error_code = 2
            elif isinstance(e, DoesNotExistID):
                error_code = 3
            elif isinstance(e, ValidationError):
                error_code = 4
                error_fields = list(e.get_full_details().keys())
            elif isinstance(e, MultipleObjectsReturned):
                error_code = 5
            elif isinstance(e, DifferentCode):
                error_code = 9
            elif isinstance(e, MissingEmailCode):
                error_code = 10
            else:
                error_code = 1

            error = auth_ex_handler(
                error_code=error_code,
                message=(e.args[0] if e.args else 'Неизвестная ошибка.'),
                user_id=(e.args[0] if e.args else 'UNKNOWN_ID'),
                user_email=(e.args[0] if e.args else 'UNKNOWN_EMAIL'),
                code=(e.args[0] if e.args else 'UNKNOWN_CODE'),
                error_fields=error_fields
            )

            log_request_error(auth_logger, e, error)

            return Response(error)
        else:
            return result

    return wrapper
