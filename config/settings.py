import os
import pathlib

import environ
from django.contrib import messages
from phonenumber_field.phonenumber import PhoneNumber

DEBUG = True

env = environ.Env()

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PROJECT_DIR = pathlib.Path(__file__).resolve().parent

# Read django project settings
if DEBUG is True:
    environ.Env.read_env(PROJECT_DIR / "development.env")
else:
    environ.Env.read_env(PROJECT_DIR / "production.env")

# Read StonPower(Meter Vendor) settings
environ.Env.read_env(BASE_DIR / "vendor_api" / "vendors" / "stron_power" / ".env")
# Read PayLeo settings
environ.Env.read_env(BASE_DIR / "core" / "services" / "payment" / "backends" / "payleo" / ".env")
# Read TrueAfrican SMS settings
environ.Env.read_env(BASE_DIR / "core" / "services" / "notification" / "backends" / "trueafrican" / ".env")

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL")
FROM_EMAIL = env("FROM_EMAIL")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize'
]

THIRD_PARTY_APPS = [
    'django_user_agents',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'phonenumber_field',
    'rest_framework',
]

LOCAL_APPS = [
    'core',  # Should come first before any other local app
    'meters',
    'users',
    'payments',
    'vendor_api',
    'meter_vendors',
    'recharge_tokens',
]

INSTALLED_APPS += THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'string_if_invalid': 'Invalid Variable: %s',
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': env.db()
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = env.str("STATIC_ROOT", BASE_DIR / "static")
STATIC_URL = '/static/'

AUTH_USER_MODEL = "users.User"
LOGIN_URL = "/users/login"
LOGIN_REDIRECT_URL = "/users/dashboard"
LOGOUT_REDIRECT_URL = LOGIN_URL

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRISPY_TEMPLATE_PACK = "bootstrap5"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname}: {asctime}: Module:{name} - {message}",
            "style": "{"
        }
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue"
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "general_file": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "filename": BASE_DIR / "errors.log",
            "filters": ["require_debug_false"],
            "formatter": "verbose"
        },
        "vendor_api_file": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "filename": BASE_DIR / "vendor_api" / "errors.log",
            "filters": ["require_debug_false"],
            "formatter": "verbose"
        },
        "vendor_api_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "verbose",
            "filters": ["require_debug_true"]
        }
    },
    "loggers": {
        "vendor_api": {
            "handlers": ["vendor_api_file", "vendor_api_console"]
        },
        "": {
            "handlers": ["general_file"]
        }
    }
}


HASHIDS_SALT = env("HASHIDS_SALT")

MESSAGE_TAGS = {
    messages.constants.ERROR: "danger",
}

PHONENUMBER_DEFAULT_REGION = "UG"

# LEGIT SYSTEMS SETTINGS - CUSTOM PROJECT SETTINGS

LEGIT_SYSTEMS_MAX_ITEMS_PER_PAGE = 20

LEGIT_SYSTEMS_DEFAULT_MANAGER = {
    "MANAGER": {
        "lookup_field": "phone_no",
        "lookup_value": PhoneNumber.from_string(env("LEGIT_SYSTEMS_DEFAULT_MANAGER_PHONE_NO")),
        "defaults": {
            "first_name": env("LEGIT_SYSTEMS_DEFAULT_MANAGER_FIRST_NAME"),
            "last_name": env("LEGIT_SYSTEMS_DEFAULT_MANAGER_LAST_NAME"),
            "address": env("LEGIT_SYSTEMS_DEFAULT_MANAGER_ADDRESS")
        }
    }
}
LEGIT_SYSTEMS_DEFAULT_UNIT_PRICE = 1000  # UGX

LEGIT_SYSTEMS_PAYMENT_BACKEND = "core.services.payment.backends.payleo.PayLeoPaymentBackend"
LEGIT_SYSTEMS_EMAIL_NOTIFICATION_BACKEND = "core.services.notification.backends.email.EmailNotificationBackend"
LEGIT_SYSTEMS_SMS_NOTIFICATION_BACKEND = "core.services.notification.backends.trueafrican.TrueAfricanSMSBackend"

LEGIT_SYSTEMS_METER_MONTHLY_FLAT_FEE = 1000  # UGX

PROXIES = {
    "http": f"http://{env('LEGIT_SYSTEMS_PROXY_USERNAME')}:{env('LEGIT_SYSTEMS_PROXY_PASSWORD')}@{env('LEGIT_SYSTEMS_PROXY_IP')}:{env('LEGIT_SYSTEMS_PROXY_PORT')}",
    "https": f"http://{env('LEGIT_SYSTEMS_PROXY_USERNAME')}:{env('LEGIT_SYSTEMS_PROXY_PASSWORD')}@{env('LEGIT_SYSTEMS_PROXY_IP')}:{env('LEGIT_SYSTEMS_PROXY_PORT')}"
}
