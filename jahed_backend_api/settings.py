from datetime import timedelta
from pathlib import Path
from os import getenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

ZARINPAL_MERCHANT_ID = getenv("ZARINPAL_MERCHANT_ID")
ZARINPAL_SANDBOX = getenv("ZARINPAL_SANDBOX") == "True"
ZARINPAL_CALLBACK_URL = getenv("ZARINPAL_CALLBACK_URL")
FRONTEND_PAYMENT_RESULT_URL = getenv("FRONTEND_PAYMENT_RESULT_URL")
BOOKING_FEE = getenv("BOOKING_FEE")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("SECRET_KEY")
SMS_USERNAME = getenv("SMS_USERNAME")
SMS_PASSWORD = getenv("SMS_PASSWORD")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = getenv("ALLOWED_HOSTS", "*").split(",")

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "tamin-token",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "account",
)

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.JWTAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
    "user",
    "patient",
    "medical_tests",
    "medical_imaging",
    "medicines",
    "insurance",
    "visit",
    "other_paraclinic_services",
    "referral_services",
    "chat",
    "appointment",
    "paraclinic",
    "stat_clinic",
    "app_messages",
    "ckeditor",
]

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            {
                "name": "basicstyles",
                "items": ["Bold", "Italic", "Underline", "RemoveFormat"],
            },
            {
                "name": "paragraph",
                "items": [
                    "NumberedList",
                    "BulletedList",
                    "-",
                    "Outdent",
                    "Indent",
                    "Blockquote",
                    "JustifyLeft",
                    "JustifyCenter",
                    "JustifyRight",
                ],
            },
            {"name": "links", "items": ["Link", "Unlink"]},
            {"name": "insert", "items": ["Table", "HorizontalRule"]},
            {"name": "styles", "items": ["Format", "Styles"]},
            {"name": "document", "items": ["Source", "Maximize"]},
        ],
        # افزونه‌های کمکی اختیاری
        "extraPlugins": ",".join(
            [
                "autogrow",  # ارتفاع خودکار
                "liststyle",  # استایل برای لیست‌ها
                "justify",  # دکمه‌های ترازبندی
                # "emoji",       # اگر پلاگین emoji را جداگانه اضافه کرده‌ای
            ]
        ),
        "removePlugins": "stylesheetparser",
        "height": 300,
        "width": "auto",
        "allowedContent": True,  # اجازهٔ HTML سفارشی (مانع حذف <ul>/<ol> نمی‌شود)
        "removeDialogTabs": "image:advanced;link:advanced",
    }
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "jahed_backend_api.middleware.DatabaseRouterMiddleware",
]

APPEND_SLASH = False
# CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
# CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = "jahed_backend_api.urls"

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

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "file": {
#             "level": "DEBUG",
#             "class": "logging.FileHandler",
#             "filename": "debug.log",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["file"],
#             "level": "DEBUG",
#             "propagate": True,
#         },
#     },
# }

WSGI_APPLICATION = "jahed_backend_api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# CLINIC_NAMES = getenv("CLINICS").split(",")
# clinics = {}
# for clinic_name in CLINIC_NAMES:
#     clinics[f"clinic_{clinic_name}"] = {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": f"clinic_{clinic_name}",
#         "USER": getenv("DB_USER"),
#         "PASSWORD": getenv("DB_PASS"),
#         "HOST": getenv("DB_HOST"),
#         "PORT": getenv("DB_PORT"),
#     }

DATABASES = {
    "default": {  # for users authentication and shared tables
        "ENGINE": "django.db.backends.mysql",
        # "ENGINE": "django.db.backends.postgresql",
        "NAME": getenv("DB_NAME"),  # Replace with your database name
        "USER": getenv("DB_USER"),  # Replace with your MySQL username
        "PASSWORD": getenv("DB_PASS"),  # Replace with your MySQL password
        "HOST": getenv("DB_HOST"),  # Or replace with your MySQL host if it's different
        "PORT": getenv("DB_PORT"),  # Or replace with your MySQL port if it's different
        "OPTIONS": {
            "charset": "utf8mb4",
            "use_unicode": True,
            "init_command": "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'",
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1")

DEFAULT_CACHE_DEV = {
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "unique-dev-locmem",  # نام‌گذاری یکتا
    "TIMEOUT": 300,  # 5 دقیقه
    "KEY_PREFIX": "myapp_dev",  # جلوگیری از تداخل کلید
}

DEFAULT_CACHE_PROD = {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": REDIS_URL,  # مثلا: redis://127.0.0.1:6379/1
    "OPTIONS": {
        "CLIENT_CLASS": "django_redis.client.DefaultClient",
        "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        "IGNORE_EXCEPTIONS": True,  # مثل Memcached رفتار کند؛ اپ روی خطا متوقف نشود
    },
    "TIMEOUT": 300,  # بسته به نیاز تنظیم کن
    "KEY_PREFIX": "myapp",
}

CACHES = {
    "default": DEFAULT_CACHE_DEV if DEBUG else DEFAULT_CACHE_PROD,
}
# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
# tehran
TIME_ZONE = getenv("TIME_ZONE", "Asia/Tehran")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "user.User"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "SIGNING_KEY": getenv("SIGNING_KEY"),
    # "ACCESS_TOKEN_LIFETIME": timedelta(days=20) if DEBUG else timedelta(minutes=15),
    # "REFRESH_TOKEN_LIFETIME": timedelta(days=20) if DEBUG else timedelta(days=1),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=20),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(hours=int(getenv("JWT_HOURS"))),
    "SLIDING_TOKEN_LIFETIME": timedelta(days=30),
    "SLIDING_TOKEN_REFRESH_LIFETIME_LATE_USER": timedelta(
        hours=int(getenv("JWT_HOURS"))
    ),
    "SLIDING_TOKEN_LIFETIME_LATE_USER": timedelta(days=30),
}

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
    "TITLE": "VClinica API Docs",
    # "DESCRIPTION": "توضیحات مستندات",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


STATIC_ROOT = getenv("STATIC_ROOT", os.path.join(BASE_DIR, "static"))
MEDIA_ROOT = getenv("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))
MEDIA_URL = getenv("MEDIA_URL", "/media/")
MEDIA_ROOT = getenv("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))

# Celery settings
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tehran"

# DATABASE_ROUTERS = ["jahed_backend_api.db_routers.MultiTenantRouter"]
