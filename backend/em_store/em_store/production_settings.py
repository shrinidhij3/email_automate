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

# CORS settings for production
CORS_ALLOW_CREDENTIALS = True

# Allowed origins for CORS - specifically for your frontend domain
CORS_ALLOWED_ORIGINS = [
    'https://email-automate-1-1hwv.onrender.com',
]

# Also allow environment variable override
env_origins = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
if env_origins and env_origins[0]:
    CORS_ALLOWED_ORIGINS.extend([origin.strip() for origin in env_origins if origin.strip()])

# Add regex patterns for Render preview deployments
CORS_ORIGIN_REGEX_WHITELIST = [
    r'^https:\/\/email-automate-\w+\-\w+\.onrender\.com$',
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
    'expires',
    'origin',
    'user-agent',
    'x-requested-with',
    'cache-control',
    'pragma',
    'x-csrftoken',
]

CORS_EXPOSE_HEADERS = [
    'Content-Type',
    'Content-Length',
    'X-Requested-With',
    'Authorization',
    'Set-Cookie',
]

CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# CSRF settings for production
CSRF_TRUSTED_ORIGINS = [
    'https://email-automate-1-1hwv.onrender.com',
    'https://email-automate-ob1a.onrender.com',
]

# Add environment variable override for CSRF trusted origins
env_csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
if env_csrf_origins and env_csrf_origins[0]:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in env_csrf_origins if origin.strip()])

# JWT Settings for production
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Shorter for security
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
    # Cookie settings for JWT if using cookies
    'ACCESS_TOKEN_COOKIE_NAME': 'access_token',
    'REFRESH_TOKEN_COOKIE_NAME': 'refresh_token',
    'ACCESS_TOKEN_COOKIE_SECURE': True,
    'REFRESH_TOKEN_COOKIE_SECURE': True,
    'ACCESS_TOKEN_COOKIE_HTTPONLY': True,
    'REFRESH_TOKEN_COOKIE_HTTPONLY': True,
    'ACCESS_TOKEN_COOKIE_SAMESITE': 'None',
    'REFRESH_TOKEN_COOKIE_SAMESITE': 'None',
    'ACCESS_TOKEN_COOKIE_DOMAIN': '.onrender.com',
    'REFRESH_TOKEN_COOKIE_DOMAIN': '.onrender.com',
}

# Session settings for production - simplified for JWT
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
        'BACKEND': 'em_store.storage_backends.R2MediaStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files configuration for production - with fallback to local storage
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    # Use R2 for storage if credentials are available
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.r2.cloudflarestorage.com/'
    if os.getenv('AWS_S3_CUSTOM_DOMAIN'):
        MEDIA_URL = f'https://{os.getenv("AWS_S3_CUSTOM_DOMAIN")}/'
    
    DEFAULT_FILE_STORAGE = 'em_store.storage_backends.R2MediaStorage'
    STORAGES['default'] = {
        'BACKEND': 'em_store.storage_backends.R2MediaStorage',
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
        'auth_app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
