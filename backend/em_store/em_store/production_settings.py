"""
Production settings for em_store project.
"""
import os
from .settings import *

# Override for production
DEBUG = False

# AWS S3 and R2 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'email-autoamation')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL', 'https://r2.cloudflarestorage.com')
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
AWS_S3_VERIFY = False  # Set to False only for testing without SSL verification

# Storage settings
STORAGES = {
    'default': {
        'BACKEND': 'em_store.storage_backends.R2MediaStorage',
    },
    'staticfiles': {
        'BACKEND': 'em_store.storage_backends.R2StaticStorage',
    },
}

# Media files
MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.r2.cloudflarestorage.com/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files
STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.r2.cloudflarestorage.com/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Boto3 configuration
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# SSL Configuration
import ssl
import certifi

# Create a custom SSL context
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Configure boto3 to use the custom SSL context
import boto3
from botocore.config import Config

s3_config = Config(
    region_name='auto',
    signature_version='s3v4',
    s3={
        'addressing_style': 'virtual',
        'use_ssl': True,
        'verify': True,
    }
)

# Override the default S3 client configuration
boto3.setup_default_session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='auto'
)

ALLOWED_HOSTS = [
    os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost'),
    'email-automate-ob1a.onrender.com',
    'email-automate-frontend.onrender.com',
    'email-automate-eight.vercel.app',
]

# HTTPS settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Production database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
    }
}

COOKIE_DOMAIN = os.getenv('COOKIE_DOMAIN', None)  # Will be None in development
CSRF_COOKIE_DOMAIN = COOKIE_DOMAIN
SESSION_COOKIE_DOMAIN = COOKIE_DOMAIN

# CORS settings for production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'https://email-automate-ob1a.onrender.com',
    'https://email-automate-eight.vercel.app',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS_ORIGIN_WHITELIST = CORS_ALLOWED_ORIGINS
CORS_ORIGIN_REGEX_WHITELIST = [
    r'^https://\w+\.vercel\.app$',
    r'^https://\w+\-\w+\.vercel\.app$',
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
    'pragma',
]
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']

# CSRF settings - Critical for CORS
CSRF_TRUSTED_ORIGINS = [
    'https://email-automate-ob1a.onrender.com',
    'https://email-automate-eight.vercel.app',
]
CSRF_COOKIE_HTTPONLY = False  # Required for JavaScript to read CSRF token
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'  # Required for cross-site requests
CSRF_COOKIE_DOMAIN = 'email-automate-ob1a.onrender.com'  # Match with cookie domain
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_AGE = 60 * 60 * 24 * 7 * 52  # 1 year

# Session settings for CORS
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'None'  # Required for cross-site requests
SESSION_COOKIE_DOMAIN = 'email-automate-ob1a.onrender.com'  # Match with CSRF domain
SESSION_COOKIE_PATH = '/'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 weeks

# CORS credentials and cookie settings
CORS_ALLOW_CREDENTIALS = True

# Add CORS middleware configuration
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

def cors_headers_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        if request.method == 'OPTIONS':
            response['Access-Control-Allow-Headers'] = ', '.join(CORS_ALLOW_HEADERS)
            response['Access-Control-Allow-Methods'] = ', '.join(CORS_ALLOW_METHODS)
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Max-Age'] = str(86400)
        return response
    return middleware

MIDDLEWARE.append('em_store.production_settings.cors_headers_middleware')

# Set cookie domain in production
if not DEBUG:
    CSRF_COOKIE_DOMAIN = 'email-automate-ob1a.onrender.com'
    SESSION_COOKIE_DOMAIN = 'email-automate-ob1a.onrender.com'

# Static files with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Ensure Cloudflare R2 is used for media files in production
if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY') and os.getenv('AWS_STORAGE_BUCKET_NAME'):
    # Configure file storage
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    AWS_DEFAULT_ACL = os.getenv('AWS_DEFAULT_ACL', 'public-read')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    if os.getenv('AWS_S3_CUSTOM_DOMAIN'):
        AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    else:
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.r2.cloudflarestorage.com/'
