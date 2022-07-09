from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS += [
    'django_extensions',
]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = config('CORS_ORIGIN_WHITELIST_DEV', cast=lambda v: [s.strip() for s in v.split(',')])

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

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }

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

CRISPY_FAIL_SILENTLY = not DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 'django.core.mail.backends.console.EmailBackend'
EMAIL_USE_TLS = config('EMAIL_USE_TLS_DEV', cast=bool)
EMAIL_HOST = config('EMAIL_HOST_DEV')
EMAIL_HOST_USER = config('EMAIL_HOST_USER_DEV')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD_DEV')
EMAIL_PORT = config('EMAIL_PORT_DEV', cast=int)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL_DEV')
SERVER_EMAIL = config('SERVER_EMAIL')
EMAIL_SUBJECT_PREFIX = config('EMAIL_SUBJECT_PREFIX_DEV', cast=lambda v: v + " ")
MANAGERS = [('dev', config('MANAGERS_DEV'))]
ADMINS = [('admin', config('ADMINS_DEV'))]
