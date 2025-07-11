from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class R2MediaStorage(S3Boto3Storage):
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'email-autoamation')
    location = 'media'
    default_acl = getattr(settings, 'AWS_DEFAULT_ACL', 'public-read')
    file_overwrite = getattr(settings, 'AWS_S3_FILE_OVERWRITE', False)
    custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', f'{bucket_name}.r2.cloudflarestorage.com')
    endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', 'https://4d4c294f4e40b9cb08edf870ed60b046.r2.cloudflarestorage.com')
    region_name = getattr(settings, 'AWS_S3_REGION_NAME', 'auto')
    verify = getattr(settings, 'AWS_S3_VERIFY', True)
    querystring_auth = getattr(settings, 'AWS_QUERYSTRING_AUTH', False)
    
    # Ensure files are uploaded as single pieces
    max_memory_size = 0  # Disable memory-based uploads, force file-based
    multipart_threshold = 0  # Disable multipart uploads
    
    def _get_security_token(self):
        return None  # Not needed for R2
    
    def url(self, name, parameters=None, expire=None, http_method=None):
        """
        Generate a public URL for the file using the R2 public domain.
        """
        try:
            # Use the R2 public domain approach with /media/ prefix
            public_domain = "pub-cbcbce585d8246e0bdf0edecb1542e99.r2.dev"
            return f"https://{public_domain}/media/{name}"
        except Exception:
            # Fallback to parent method
            return super().url(name, parameters, expire, http_method)
    
    def _extract_account_id(self):
        """Extract account ID from endpoint URL."""
        try:
            if self.endpoint_url:
                from urllib.parse import urlparse
                parsed = urlparse(self.endpoint_url)
                if '.r2.cloudflarestorage.com' in parsed.netloc:
                    return parsed.netloc.split('.')[0]
        except Exception:
            pass
        return None

class R2StaticStorage(S3Boto3Storage):
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'email-autoamation')
    location = 'static'
    default_acl = getattr(settings, 'AWS_DEFAULT_ACL', 'public-read')
    file_overwrite = getattr(settings, 'AWS_S3_FILE_OVERWRITE', True)
    custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', f'{bucket_name}.r2.cloudflarestorage.com')
    endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', 'https://4d4c294f4e40b9cb08edf870ed60b046.r2.cloudflarestorage.com')
    region_name = getattr(settings, 'AWS_S3_REGION_NAME', 'auto')
    verify = getattr(settings, 'AWS_S3_VERIFY', True)
    
    def _get_security_token(self):
        return None  # Not needed for R2
