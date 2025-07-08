"""
Django settings for em_store project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment detection
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')

# Security
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is required")

# Validate required environment variables
required_env_vars = ['DJANGO_SECRET_KEY']
if not DEBUG:
    required_env_vars.extend(['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST'])

for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} is not set")

# Hosts configuration
if DEBUG:
    ALLOWED_HOSTS = ['*']
    try:
        from .local_settings import *  # noqa
    except ImportError:
        pass
else:
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        'email-automate-ob1a.onrender.com',
    ]

# Application definition
INSTALLED_APPS = [
    'storages',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_extensions',
    'import_export',
    'drf_yasg',
    'rest_framework_simplejwt.token_blacklist',
    'email_entry',
    'unread_emails',
    'campaigns',
    'api.apps.ApiConfig',
    'auth_app',
]

# Middleware configuration - CORS middleware should be as high as possible
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware should be placed as high as possible
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auth_app.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'em_store.urls'

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'unread_emails', 'templates'),
        ],
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

WSGI_APPLICATION = 'em_store.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'em_store'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# CORS configuration
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://email-automate-ob1a.onrender.com',
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
]

# CSRF configuration for cross-domain
CSRF_TRUSTED_ORIGINS = [
    'https://email-automate-ob1a.onrender.com',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    # Add your frontend domain here
]
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'X-CSRFToken'  # Changed to match frontend
CSRF_COOKIE_HTTPONLY = False  # Must be False to be read by JavaScript
CSRF_COOKIE_SAMESITE = 'None'  # Must be None for cross-domain
CSRF_COOKIE_SECURE = True     # Must be True when SameSite=None
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_AGE = 60 * 60 * 24 * 7 * 52  # 1 year
CSRF_COOKIE_DOMAIN = '.render.com'  # Set to your parent domain

# Session configuration for cross-domain
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'None'  # Must be None for cross-domain
SESSION_COOKIE_SECURE = True     # Must be True when SameSite=None
SESSION_COOKIE_PATH = '/'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_DOMAIN = '.render.com'  # Set to your parent domain

# CORS configuration for cross-domain
CORS_ALLOW_CREDENTIALS = True  # Important for credentials

if DEBUG:
    # Local development settings
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ]

# Allow all methods and headers for preflight requests
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
     'cache-control',  # Add this line
    'pragma',         # Add this line
]

# Expose cookies and other headers to the frontend
CORS_EXPOSE_HEADERS = [
    'Content-Type',
    'X-CSRFToken',
    'Content-Length',
    'X-Requested-With',
    'Set-Cookie',    # Add this line
]

# Important security settings for cross-domain cookies
CORS_ALLOW_PRIVATE_NETWORK = True  # For local development
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'

# AWS S3/Cloudflare R2 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_DEFAULT_ACL = os.getenv('AWS_DEFAULT_ACL', 'public-read')
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_QUERYSTRING_AUTH = False

# If you have a custom domain for your R2 bucket
if os.getenv('AWS_S3_CUSTOM_DOMAIN'):
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    # Use R2 for file storage
    STORAGES['default']['BACKEND'] = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.r2.cloudflarestorage.com/'
    if hasattr(globals(), 'AWS_S3_CUSTOM_DOMAIN'):
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    # Fallback to local file storage
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
# Local development storage settings
if DEBUG:
    # Use local file system for development
    MEDIA_URL = '/media/'
    
# Use local file system for static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   
# Configure storage backends
STORAGES = {
    'default': {
        'BACKEND': (
            'django.core.files.storage.FileSystemStorage' if DEBUG
            else 'storages.backends.s3boto3.S3Boto3Storage'
        ),
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# Media URL configuration
if DEBUG:
    MEDIA_URL = '/media/'
else:
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.r2.cloudflarestorage.com/media/'
    if hasattr(globals(), 'AWS_S3_CUSTOM_DOMAIN'):
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Media files root directory
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure directories exist
os.makedirs(MEDIA_ROOT, exist_ok=True)
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Logging configuration
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
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'errors.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'file_errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security.csrf': {
            'handlers': ['console', 'file', 'file_errors'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
