"""
Django settings for wtnt project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import environ
import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
MY_DOMAIN = "https://api.whatmeow.shop"
SITE_ID = 1

ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + ["x-from", "x-admin", "x-debug"]
CSRF_TRUSTED_ORIGINS = ["https://api.whatmeow.shop"]
AUTH_USER_MODEL = "user.CustomUser"

REST_AUTH = {
    "TOKEN_MODEL": None,
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "access_token",
    "JWT_AUTH_REFRESH_COOKIE": "refresh_token",
    "JWT_AUTH_HTTPONLY": False,
    "SESSION_LOGIN": False,
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("core.authenticator.CustomJWTAuthentication",),
}


ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework_simplejwt",
    "user",
    "team",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "drf_yasg",
    "corsheaders",
    "celery",
    "django_celery_beat",
    "django_celery_results",
    "debug_toolbar",
    "django_seed",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.AttachJWTFromCookieToHeaderMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "core.middleware.CustomLoginMiddleware",
    "core.middleware.CustomRegisterMiddleware",
    "core.middleware.CustomRefreshMiddleware",
    "core.middleware.CustomLogoutMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "wtnt.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wtnt.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("MYSQLDB_NAME"),
        "USER": env("MYSQLDB_USERNAME"),
        "PASSWORD": env("MYSQLDB_PW"),
        "HOST": env("MYSQLDB_HOST"),
        "PORT": env("MYSQLDB_PORT"),
    }
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "file": {
            "level": "INFO",
            "filters": ["require_debug_false"],
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "D",
            "filename": BASE_DIR / "logs/wtnt.log",
            "backupCount": 10,
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins", "file"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": True,
        },
    },
}


# S3
AWS_CLIENT_ID = env("AWS_CLIENT_ID")
AWS_CLIENT_SECRET = env("AWS_CLIENT_SECRET")
BUCKET_NAME = env("AWS_BUCKET_NAME")
AWS_REGION = env("AWS_S3_REGION_NAME")

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "ko"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = env("STATIC_ROOT")
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery Settings

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "django-db"
CELERY_TIMEZONE = "Asia/Seoul"

# Email Settings

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_ID")
EMAIL_HOST_PASSWORD = env("EMAIL_PW")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
