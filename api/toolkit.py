from .models import MyToken


def process_request(request):
    if not request.user.is_authenticated:
        try:
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            request.user = MyToken.objects.get(key=token).user
            return True
        except MyToken.DoesNotExist:
            return False
