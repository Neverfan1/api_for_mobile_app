# *************************************** #
#    Инициализация переменные среды       #
# *************************************** #

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

if (BASE_DIR / 'config' / '.env').exists():
    load_dotenv(os.path.abspath(BASE_DIR / 'config' / '.env'))

if (BASE_DIR / '.env').exists():
    load_dotenv(os.path.abspath(BASE_DIR / '.env'))

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('PRODUCTION')

ALLOWED_HOSTS = json.loads(os.getenv('ALLOWED_HOSTS', '[]'))

PATH_LOG = Path(str(os.getenv('PATH_LOG')))
PATH_LOG_DIR = Path(os.path.join(BASE_DIR, 'log'))
if not PATH_LOG.exists():
    if not PATH_LOG_DIR.exists():
        PATH_LOG_DIR.mkdir(parents=True)
    PATH_LOG = PATH_LOG_DIR

# *************************************** #
#       Application definition            #
# *************************************** #

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'rest_framework',
    'drf_yasg',
    # 'rest_framework.authtoken',
    "corsheaders",
]

# *************************************** #
#          MIDDLEWARE SETTINGS            #
# *************************************** #

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = 'api_settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api_settings.wsgi.application'

# *************************************** #
#           DATABASE SETTINGS             #
# *************************************** #
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'HOST': os.getenv('DB_HOST'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# *************************************** #
#         VALIDATION SETTINGS             #
# *************************************** #

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# *************************************** #
#     Internationalization settings       #
# *************************************** #

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# *************************************** #
#       Static files settings             #
# *************************************** #

# STATIC_ROOT = 'static'

# STATICFILES_DIRS = [
# os.path.join(BASE_DIR, "static")
# ]

# *************************************** #
#       Default primary key settings      #
#               field type                 #
# *************************************** #
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'

# ******************************************** #
# *              SWAGGER SETTINGS            * #
# ******************************************** #
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        },
        'ID': {
            'type': 'apiKey',
            'name': 'ID',
            'in': 'header'
        }
    },
    'SECURITY_REQUIREMENTS': [
        {
            'Bearer': [],
            'ID': []
        }
    ]
}

SWAGGER_PATH = os.getenv('SWAGGER_URL')

# ******************************************** #
# *               CORS SETTINGS              * #
# ******************************************** #

CORS_ALLOWED_ORIGINS = json.loads(os.getenv('CORS_ALLOWED_ORIGINS', '[]'))

CORS_ALLOW_HEADERS = list(default_headers) + [
    "ID",
    "Authorization",
]
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "DELETE"
]
# *************************************** #
#            Email settings               #
# *************************************** #
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

TOKEN_AUTHENTICATION_KEY = 'Authorization'
