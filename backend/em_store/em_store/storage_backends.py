from storages.backends.s3boto3 import S3Boto3Storage

class R2MediaStorage(S3Boto3Storage):
    bucket_name = 'email-autoamation'  # Your R2 bucket name
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
    custom_domain = f'{bucket_name}.r2.cloudflarestorage.com'
    endpoint_url = 'https://r2.cloudflarestorage.com'  # Cloudflare R2 endpoint
    
    def _get_security_token(self):
        return None  # Not needed for R2

class R2StaticStorage(S3Boto3Storage):
    bucket_name = 'email-autoamation'  # Your R2 bucket name
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True
    custom_domain = f'{bucket_name}.r2.cloudflarestorage.com'
    endpoint_url = 'https://r2.cloudflarestorage.com'  # Cloudflare R2 endpoint
    
    def _get_security_token(self):
        return None  # Not needed for R2
