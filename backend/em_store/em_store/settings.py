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
else:
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        'email-automate-ob1a.onrender.com',
        'email-automate-frontend.onrender.com',
    ]

# Application definition
INSTALLED_APPS = [
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

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
    'https://email-automate-frontend.onrender.com',
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

# CSRF configuration - FIXED
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'  # ✅ CORRECTED - This was the main issue!
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_AGE = 60 * 60 * 24 * 7 * 52
CSRF_COOKIE_DOMAIN = '.onrender.com' if not DEBUG else None

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_PATH = '/'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_DOMAIN = '.onrender.com' if not DEBUG else None

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

# Static and Media files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
