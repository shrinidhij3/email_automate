"""
Django settings for em_store project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Determine the environment
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')

# Load environment variables from the appropriate .env file
if ENVIRONMENT == 'production':
    env_file = '.env.production'
else:
    env_file = '.env.development'

env_path = Path(__file__).resolve().parent.parent / env_file
load_dotenv(env_path)

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment detection
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Security
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is required")

# Hosts configuration
ALLOWED_HOSTS = ['*'] if DEBUG else [
    'localhost',
    '127.0.0.1',
    'email-automate-ob1a.onrender.com',
]

# Application definition
INSTALLED_APPS = [
    'storages',
    'corsheaders',  # CORS headers package - REQUIRED
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

# Middleware configuration - CORS middleware MUST be first
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # <-- Added for CORS
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'em_store.middleware.CustomCSRFMiddleware',  # Custom CSRF middleware for API
    # 'django.middleware.csrf.CsrfViewMiddleware',  # Disabled for JWT-based auth
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

# --- HARDCODED SETTINGS FOR DEV/PROD ---

# Set this to True for local dev, False for production
IS_DEV = os.getenv('DJANGO_ENV', 'development') == 'development'

if IS_DEV:
    DEBUG = True
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
    SESSION_COOKIE_DOMAIN = None  # Use None for localhost to avoid domain mismatch
    CSRF_COOKIE_DOMAIN = None
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    FRONTEND_URL = 'http://localhost:5173'
    BACKEND_URL = 'http://localhost:8000'
else:
    DEBUG = False
    ALLOWED_HOSTS = [
        'email-automate-ob1a.onrender.com',
        'localhost',
        '127.0.0.1',
    ]
    CORS_ALLOWED_ORIGINS = [
        'https://email-automate-1-1hwv.onrender.com',
        'https://email-automate-ob1a.onrender.com',
    ]
    CSRF_TRUSTED_ORIGINS = [
        'https://email-automate-1-1hwv.onrender.com',
        'https://email-automate-ob1a.onrender.com',
    ]
    SESSION_COOKIE_DOMAIN = '.onrender.com'
    CSRF_COOKIE_DOMAIN = '.onrender.com'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    FRONTEND_URL = 'https://email-automate-1-1hwv.onrender.com'
    BACKEND_URL = 'https://email-automate-ob1a.onrender.com'

# --- END HARDCODED SETTINGS ---

# Cloudflare R2 Configuration (keep secrets in env)
AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'email-autoamation')
AWS_S3_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL', 'https://4d4c294f4e40b9cb08edf870ed60b046.r2.cloudflarestorage.com')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.r2.cloudflarestorage.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Storage configuration - Use R2 for media files, keep static files local
STORAGES = {
    'default': {
        'BACKEND': 'em_store.storage_backends.R2MediaStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# Frontend/Backend URLs for CORS, CSRF, and download URLs
# FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
# BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', FRONTEND_URL).split(',')
# CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', FRONTEND_URL).split(',')

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
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://email-automate-1-1hwv.onrender.com',
]
CORS_ALLOW_CREDENTIALS = True
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
    'x-xsrf-token',
    'x-api-key',
    'x-client-id',
    'x-access-token',
    'x-refresh-token',
    'x-auth-token',
    'x-csrf-token',
    'x-session-id',
    'x-xsrf-token',
    'x-frame-options',
    'x-content-type-options',
    'x-xss-protection',
    'x-forwarded-for',
    'x-forwarded-proto',
    'x-forwarded-host',
    'x-forwarded-port',
    'x-real-ip',
    'x-request-id',
    'x-correlation-id',
    'x-forwarded-prefix',
    'x-forwarded-path',
    'x-forwarded-slash',
    'x-forwarded-url',
    'x-forwarded-server',
    'x-forwarded-client-cert',
    'x-forwarded-client-cert-chain',
    'x-forwarded-client-cert-issuer',
    'x-forwarded-client-cert-subject',
    'x-forwarded-client-cert-valid-from',
    'x-forwarded-client-cert-valid-to',
    'x-forwarded-client-cert-serial',
    'x-forwarded-client-cert-fingerprint',
    'x-forwarded-client-cert-public-key',
    'x-forwarded-client-cert-signature',
    'x-forwarded-client-cert-algorithm',
    'x-forwarded-client-cert-key-usage',
    'x-forwarded-client-cert-ext-key-usage',
    'x-forwarded-client-cert-basic-constraints',
    'x-forwarded-client-cert-subject-alt-name',
    'x-forwarded-client-cert-issuer-alt-name',
    'x-forwarded-client-cert-crl-distribution-points',
    'x-forwarded-client-cert-ocsp',
    'x-forwarded-client-cert-ocsp-responder',
    'x-forwarded-client-cert-ocsp-response',
    'x-forwarded-client-cert-ocsp-status',
    'x-forwarded-client-cert-ocsp-this-update',
    'x-forwarded-client-cert-ocsp-next-update',
    'x-forwarded-client-cert-ocsp-revocation-time',
    'x-forwarded-client-cert-ocsp-revocation-reason',
    'x-forwarded-client-cert-ocsp-issuer',
    'x-forwarded-client-cert-ocsp-serial',
    'x-forwarded-client-cert-ocsp-fingerprint',
    'x-forwarded-client-cert-ocsp-signature',
    'x-forwarded-client-cert-ocsp-algorithm',
    'x-forwarded-client-cert-ocsp-key-usage',
    'x-forwarded-client-cert-ocsp-ext-key-usage',
    'x-forwarded-client-cert-ocsp-basic-constraints',
    'x-forwarded-client-cert-ocsp-subject-alt-name',
    'x-forwarded-client-cert-ocsp-issuer-alt-name',
    'x-forwarded-client-cert-ocsp-crl-distribution-points',
    'x-forwarded-client-cert-ocsp-ocsp',
    'x-forwarded-client-cert-ocsp-ocsp-responder',
    'x-forwarded-client-cert-ocsp-ocsp-response',
    'x-forwarded-client-cert-ocsp-ocsp-status',
    'x-forwarded-client-cert-ocsp-ocsp-this-update',
    'x-forwarded-client-cert-ocsp-ocsp-next-update',
    'x-forwarded-client-cert-ocsp-ocsp-revocation-time',
    'x-forwarded-client-cert-ocsp-ocsp-revocation-reason',
    'x-forwarded-client-cert-ocsp-ocsp-issuer',
    'x-forwarded-client-cert-ocsp-ocsp-serial',
    'x-forwarded-client-cert-ocsp-ocsp-fingerprint',
    'x-forwarded-client-cert-ocsp-ocsp-signature',
    'x-forwarded-client-cert-ocsp-ocsp-algorithm',
    'x-forwarded-client-cert-ocsp-ocsp-key-usage',
    'x-forwarded-client-cert-ocsp-ocsp-ext-key-usage',
    'x-forwarded-client-cert-ocsp-ocsp-basic-constraints',
    'x-forwarded-client-cert-ocsp-ocsp-subject-alt-name',
    'x-forwarded-client-cert-ocsp-ocsp-issuer-alt-name',
    'x-forwarded-client-cert-ocsp-ocsp-crl-distribution-points',
]
CORS_EXPOSE_HEADERS = [
    'Content-Disposition',
    'Content-Length',
    'X-Requested-With',
    'X-CSRFToken',
    'X-Frame-Options',
]
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
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
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=24),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# Session configuration (simplified - no CSRF needed)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_PATH = '/'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = 'sessionid'
# SESSION_COOKIE_DOMAIN = None # This line is now handled by the new_code

# Handle cookie settings for different environments
if DEBUG:
    # Development: Allow cross-origin cookies without Secure flag
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'None'
else:
    # Production: Require Secure flag for cross-origin cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
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

# CSRF settings - exclude API endpoints
CSRF_EXEMPT_URLS = [
    r'^/api/.*$',  # All API endpoints
]

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files configuration for development
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed file types for uploads
ALLOWED_FILE_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'text/csv',
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp',
    'image/gif',
    'application/zip',
    'application/x-zip-compressed',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

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
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'corsheaders': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'auth_app': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
