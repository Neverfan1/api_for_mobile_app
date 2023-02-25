from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from .views import *
from api_settings import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
    ),
    url=settings.SWAGGER_PATH,
    public=True,
    permission_classes=[permissions.AllowAny]
)
app_name = "api_mobile"

auth_urls = [
    path("registration/", Register.as_view(), name="registration"),
    path("registration_finish/", CheckCode.as_view(), name="finish"),
    path("auth/", AuthUser.as_view(), name="auth"),
    path("test/", MyView.as_view(), name="test")
]

# Shema-swagger-ui
swagger_urls = [
    re_path('swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema_json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='shema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='shema-redoc'),
]

urlpatterns = [
    *auth_urls,
    *swagger_urls,
]