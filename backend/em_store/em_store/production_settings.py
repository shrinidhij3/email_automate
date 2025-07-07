"""
Production settings for em_store project.
"""
import os
from .settings import *

# Override for production
DEBUG = False

ALLOWED_HOSTS = [
    os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost'),
    'email-automate-ob1a.onrender.com',
    'email-automate-frontend.onrender.com'
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

# Production CORS settings
CORS_ALLOWED_ORIGINS = [
    'https://email-automate-ob1a.onrender.com',
    'https://email-automate-frontend.onrender.com'
]

# Production CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://email-automate-ob1a.onrender.com',
    'https://email-automate-frontend.onrender.com'
]

# Static files with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
