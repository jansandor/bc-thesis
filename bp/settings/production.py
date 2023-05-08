from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

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

CRISPY_FAIL_SILENTLY = not DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = config('EMAIL_USE_TLS_PROD', cast=bool)
EMAIL_HOST = config('EMAIL_HOST_PROD')
EMAIL_HOST_USER = config('EMAIL_HOST_USER_PROD')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD_PROD')
EMAIL_PORT = config('EMAIL_PORT_PROD', cast=int)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL_PROD')
SERVER_EMAIL = config('SERVER_EMAIL')
EMAIL_SUBJECT_PREFIX = config('EMAIL_SUBJECT_PREFIX_PROD', cast=lambda v: v + " ")

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# X-FORWARDED-PROTOCOL = 'ssl'
# X-FORWARDED-PROTO = 'https'
# X-FORWARDED-SSL = 'on'
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
