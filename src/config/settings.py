"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from decouple import config
from decouple import config
from datetime import timedelta
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG')

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',

    # Local
    'authentication',
    'main',
    'customer_support',
    'orders',
    'products',
    'users',
    'config',
    'admin_dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('NAME'),
        "USER": config('USER'),
        "PASSWORD": config('PASSWORD'),
        "HOST": config('HOST'),
        "PORT": config('PORT')
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "authentication.User"

FRONTEND_HOST = config('FRONTEND_HOST')
FRONTEND_PROTOCOL = config('FRONTENT_PROTOCOL')

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

ACCESS_TOKEN_VALID_DURATION = int(config("ACCESS_TOKEN_VALID_DURATION"))
REFRESH_TOKEN_VALID_DURATION = int(config("REFRESH_TOKEN_VALID_DURATION"))
ALLOW_NEW_REFRESH_TOKENS_FOR_UNVERIFIED_USERS = bool(config('ALLOW_NEW_REFRESH_TOKENS_FOR_UNVERIFIED_USERS'))

import os

AUTHORIZATION_DIR = os.path.join(Path(BASE_DIR), "authorization")
JWT_PRIVATE_KEY_PATH = os.path.join(AUTHORIZATION_DIR, "jwt_key")
JWT_PUBLIC_KEY_PATH = os.path.join(AUTHORIZATION_DIR, "jwt_key.pub")

# If the above directory does not exist when we run the sever
if (not os.path.exists(JWT_PRIVATE_KEY_PATH)) or (not os.path.exists(JWT_PUBLIC_KEY_PATH)):
    if not os.path.exists(AUTHORIZATION_DIR):
        os.makedirs(AUTHORIZATION_DIR)
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=4096, backend=default_backend()
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(JWT_PRIVATE_KEY_PATH, "w") as pk:
        pk.write(pem.decode())
    
    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(JWT_PUBLIC_KEY_PATH, "w") as pk:
        pk.write(pem_public.decode())
    print("PRIVATE/PUBLIC keys generated!")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        days=ACCESS_TOKEN_VALID_DURATION,
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        weeks=REFRESH_TOKEN_VALID_DURATION
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "RS256",
    "SIGNING_KEY": open(JWT_PRIVATE_KEY_PATH).read(),
    "VERIFYING_KEY": open(JWT_PUBLIC_KEY_PATH).read(),
    "AUDIENCE": None,
    "ISSUER": None, # In case of multiple auth service
    "USER_ID_CLAIM": "user_id",
    "USER_ID_FIELD": "id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "JTI_CLAIM": "jti", # Token unique identifier
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "AUTH_HEADER_TYPES": ("Bearer",),
}