import os

from django.contrib import messages

import environ

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Read django project settings
environ.Env.read_env(os.path.join(PROJECT_DIR, ".env"))

# Read Stron Power settings
environ.Env.read_env(os.path.join(BASE_DIR, "external_api", "vendor", "stron_power", ".env"))

DEBUG = env("DEBUG")

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
    'django_filters'
]

LOCAL_APPS = [
    'meters.apps.MeterConfig',
    'users.apps.UserConfig',
    'manufacturers.apps.MeterManufacturerConfig',
    'meter_categories.apps.MeterCategoryConfig',
    'payments.apps.PaymentConfig',
    'recharge_tokens.apps.RechargeTokensConfig',
    'external_api.apps.ExternalApiConfig',
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
        'DIRS': ["%s/templates" % BASE_DIR],
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
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    "%s/static/" % BASE_DIR,
]

AUTH_USER_MODEL = "users.User"
LOGIN_URL = "/users/login"
LOGIN_REDIRECT_URL = "/users/profile"
LOGOUT_REDIRECT_URL = LOGIN_URL

TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NO = env("TWILIO_PHONE_NO")

HASHIDS_SALT = env("HASHIDS_SALT")

MESSAGE_TAGS = {
    messages.constants.ERROR: "danger",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRISPY_TEMPLATE_PACK = "bootstrap4"

MAX_ITEMS_PER_PAGE = 5

DEFAULT_MANAGER_PHONE_NO = env("DEFAULT_MANAGER_PHONE_NO")
DEFAULT_MANAGER_FIRST_NAME = env("DEFAULT_MANAGER_FIRST_NAME")
DEFAULT_MANAGER_LAST_NAME = env("DEFAULT_MANAGER_LAST_NAME")
DEFAULT_MANAGER_ADDRESS = env("DEFAULT_MANAGER_ADDRESS")

DEFAULT_METER_CATEGORY_LABEL = env("DEFAULT_METER_CATEGORY_LABEL")
DEFAULT_METER_CATEGORY_FIXED_CHARGE = env.int("DEFAULT_METER_CATEGORY_FIXED_CHARGE")
DEFAULT_METER_CATEGORY_PERCENTAGE_CHARGE = env.int("DEFAULT_METER_CATEGORY_PERCENTAGE_CHARGE")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
           "format": "{levelname}: {asctime}: Module:{module} - {message}",
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
            "filename": os.path.join(BASE_DIR, "errors.log"),
            "filters": ["require_debug_false"],
            "formatter": "verbose"
        },
        "external_api_file": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "filename": os.path.join(BASE_DIR, "external_api", "errors.log"),
            "filters": ["require_debug_false"],
            "formatter": "verbose"
        },
        "external_api_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "verbose",
            "filters": ["require_debug_true"]
        }
    },
    "loggers": {
        "external_api": {
            "handlers": ["external_api_file", "external_api_console"]
        },
        "": {
            "handlers": ["general_file"]
        }
    }
}
