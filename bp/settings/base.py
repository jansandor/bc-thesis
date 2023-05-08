from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SITE_ID = 1

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
    'accounts',
    'sportdiag',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = 'accounts.User'

ROOT_URLCONF = 'bp.urls'

WSGI_APPLICATION = 'bp.wsgi.application'

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = config('CORS_ORIGIN_WHITELIST', cast=lambda v: [s.strip() for s in v.split(',')])

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
STATIC_ROOT = BASE_DIR / 'collected_static'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'sportdiag:home'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap5", "custom_crispy")
CRISPY_TEMPLATE_PACK = "custom_crispy"  # "bootstrap5"

MANAGERS = [('dev', config('MANAGERS'))]
ADMINS = [('admin', config('ADMINS'))]
