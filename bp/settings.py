"""
Django settings for bp project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

# from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^fciw131&-mq!4$um$m2fq%mzk0t+5#4$-k2+z$r5oqe45spls'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    'accounts',
    'sportdiag',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bp.urls'

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    'http://localhost:8000',
    # 'https://localhost:8000',
)

# MESSAGE_TAGS = {
#    messages.DEBUG: 'alert-info',
#    messages.INFO: 'alert-info',
#    messages.SUCCESS: 'alert-success',
#    messages.WARNING: 'alert-warning',
#    messages.ERROR: 'alert-danger',
# }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #    'ENGINE': 'django.db.backends.postgresql',
    #    'NAME': 'postgres',
    #    'USER': 'postgres',
    #    'PASSWORD': '1234',
    #    'HOST': '127.0.0.1',
    #    'PORT': '5432'
    #    ,
    # }
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # some default password validators were removed to make password creation simpler for users
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'cs'

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'accounts/static/accounts',
    BASE_DIR / 'sportdiag/static/sportdiag',
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# todo login url, logout url, redirect url
LOGIN_REDIRECT_URL = 'sportdiag:home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# TODO posilani emailu v develop verzi do konzole, zmenit
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap5", "custom_crispy")

CRISPY_TEMPLATE_PACK = "custom_crispy"  # "bootstrap5"

CRISPY_FAIL_SILENTLY = not DEBUG

AUTH_USER_MODEL = 'accounts.User'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'sandor.jan9@gmail.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = 'info@sportdiag.cz'
