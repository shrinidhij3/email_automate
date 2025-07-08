"""
Production settings for em_store project.
"""
import os
from .settings import *

# Override for production
DEBUG = False

# Production hosts
ALLOWED_HOSTS = [
    os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost'),
    'email-automate-ob1a.onrender.com',
    'email-automate-1-1hwv.onrender.com',
]

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

# CORS settings for production - FIXED VERSION
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
if not CORS_ALLOWED_ORIGINS[0]:  # If empty string, use default
    CORS_ALLOWED_ORIGINS = [
        'https://email-automate-1-1hwv.onrender.com',
        'https://email-automate-ob1a.onrender.com',
    ]

# Add regex patterns for Vercel preview deployments
CORS_ORIGIN_REGEX_WHITELIST = [
    r'^https://\w+\.vercel\.app$',
    r'^https://\w+\-\w+\.vercel\.app$',
    r'^https://email-automate-eight-.*\.vercel\.app$',
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
    'expires',  # Adding expires header for cache control
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
    'pragma',
]

CORS_EXPOSE_HEADERS = [
    'Content-Type',
    'X-CSRFToken',
    'Content-Length',
    'X-Requested-With',
    'Set-Cookie',
]

CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# CSRF settings for production - FIXED for cross-origin
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
if not CSRF_TRUSTED_ORIGINS[0]:  # If empty string, use default
    CSRF_TRUSTED_ORIGINS = [
        'https://email-automate-1-1hwv.onrender.com',
        'https://email-automate-ob1a.onrender.com',
    ]

CSRF_COOKIE_SECURE = True  # True for production HTTPS
CSRF_COOKIE_SAMESITE = 'None'  # Required for cross-origin requests
CSRF_COOKIE_DOMAIN = os.getenv('CSRF_COOKIE_DOMAIN', '.onrender.com')
CSRF_COOKIE_HTTPONLY = False  # Must be False for JavaScript access
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_AGE = 60 * 60 * 24 * 7 * 52  # 1 year

# Session settings for production - FIXED for cross-origin
SESSION_COOKIE_SECURE = True  # True for production HTTPS
SESSION_COOKIE_SAMESITE = 'None'  # Required for cross-origin requests
SESSION_COOKIE_DOMAIN = os.getenv('SESSION_COOKIE_DOMAIN', '.onrender.com')
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_PATH = '/'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# HTTPS settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Cloudflare R2 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'email-automation')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_DEFAULT_ACL = None  # R2 doesn't use ACLs
AWS_S3_REGION_NAME = 'auto'  # R2 uses 'auto' region
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_VERIFY = True  # Enable SSL verification for production
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

# R2 object parameters
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Storage settings for production
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files configuration for production - with fallback to local storage
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    # Use S3/R2 for storage if credentials are available
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.r2.dev/'
    if os.getenv('AWS_S3_CUSTOM_DOMAIN'):
        MEDIA_URL = f'https://{os.getenv("AWS_S3_CUSTOM_DOMAIN")}/'
    
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STORAGES['default'] = {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
    }
else:
    # Fallback to local file system storage
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STORAGES['default'] = {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message} {pathname}:{lineno}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django_errors.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'corsheaders': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
