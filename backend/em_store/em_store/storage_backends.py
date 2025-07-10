from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class R2MediaStorage(S3Boto3Storage):
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'email-autoamation')
    location = 'media'
    default_acl = getattr(settings, 'AWS_DEFAULT_ACL', 'public-read')
    file_overwrite = getattr(settings, 'AWS_S3_FILE_OVERWRITE', False)
    custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', f'{bucket_name}.r2.cloudflarestorage.com')
    endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', 'https://r2.cloudflarestorage.com')
    
    def _get_security_token(self):
        return None  # Not needed for R2

class R2StaticStorage(S3Boto3Storage):
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'email-autoamation')
    location = 'static'
    default_acl = getattr(settings, 'AWS_DEFAULT_ACL', 'public-read')
    file_overwrite = getattr(settings, 'AWS_S3_FILE_OVERWRITE', True)
    custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', f'{bucket_name}.r2.cloudflarestorage.com')
    endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', 'https://r2.cloudflarestorage.com')
    
    def _get_security_token(self):
        return None  # Not needed for R2
