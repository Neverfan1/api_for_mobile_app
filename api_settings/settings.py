
# *************************************** #
#    Инициализация переменные среды       #
# *************************************** #

import json
import os
from pathlib import Path
from dotenv import load_dotenv
import pymysql
pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.abspath(BASE_DIR / 'config' / '.env'))

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

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


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# *************************************** #
#           DATABASE SETTINGS             #
# *************************************** #
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'HOST': os.getenv('DB_HOST'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'PORT': os.getenv('DB_PORT'),
#     }
# }

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