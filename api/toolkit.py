from .models import MyToken
from django.http import HttpResponseBadRequest


def api_auth_required(func):
    """Декоратор для аутентификации пользователя"""
    def wrapper(request, *args, **kwargs):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            user_id = request.META.get('HTTP_ID')
            request.user = MyToken.objects.get(key=token, user_id=user_id).user
            if request.user:
                return func(request, *args, **kwargs)
        except MyToken.DoesNotExist:
            return HttpResponseBadRequest('Invalid token')
    return wrapper
