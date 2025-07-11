import os
import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from urllib.parse import urljoin, urlparse
from django.conf import settings

logger = logging.getLogger(__name__)

def upload_file_to_r2(file_obj, file_name, content_type=None, folder='attachments'):
    """
    Upload a file to Cloudflare R2 storage and fetch the actual public URL.
    
    Args:
        file_obj: File object or content to upload
        file_name: Name to save the file as
        content_type: MIME type of the file
        folder: Folder within the bucket to store the file
    
    Returns:
        dict: {'success': bool, 'url': str, 'key': str, 'error': str}
    """
    try:
        # Ensure the folder path ends with a slash
        if folder and not folder.endswith('/'):
            folder = f"{folder}/"
            
        # Create the full path
        file_path = f"{folder}{file_name}"
        
        # Handle both file objects and raw content
        if hasattr(file_obj, 'read'):
            # It's a file-like object
            file_content = file_obj.read()
        else:
            # It's raw content
            file_content = file_obj
        
        # Upload the file using R2 storage
        saved_path = default_storage.save(file_path, ContentFile(file_content))
        
        # Fetch the actual public URL from R2
        file_url = fetch_r2_public_url(saved_path)
        
        logger.info(f"Successfully uploaded file to R2: {saved_path}")
        logger.info(f"Fetched public URL: {file_url}")
        
        return {
            'success': True,
            'url': file_url,
            'key': saved_path,
            'error': None
        }
        
    except Exception as e:
        logger.error(f"Error uploading file to R2: {str(e)}", exc_info=True)
        return {
            'success': False,
            'url': None,
            'key': None,
            'error': str(e)
        }

def fetch_r2_public_url(file_key):
    """
    Fetch the actual public URL for a file from R2 storage using the public domain.
    
    Args:
        file_key: The key of the file in R2
        
    Returns:
        str: Actual public URL for the file from R2
    """
    try:
        # Use the R2 public domain approach with /media/ prefix
        # This constructs the public URL directly using the R2 public domain
        public_domain = "pub-cbcbce585d8246e0bdf0edecb1542e99.r2.dev"
        url = f"https://{public_domain}/media/{file_key}"
        logger.debug(f"Generated R2 public URL: {url}")
        return url
        
    except Exception as e:
        logger.error(f"Error generating R2 public URL: {str(e)}", exc_info=True)
        # Fallback to storage backend URL method
        try:
            url = default_storage.url(file_key)
            logger.debug(f"Fallback R2 public URL: {url}")
            return url
        except Exception as fallback_error:
            logger.error(f"Fallback URL generation failed: {str(fallback_error)}", exc_info=True)
            return generate_public_url(file_key)

def generate_public_url(file_key):
    """
    Generate a public URL for a file in R2 using Cloudflare's public URL format.
    
    Args:
        file_key: The key of the file in R2
        
    Returns:
        str: Public URL for the file
    """
    try:
        # Use Cloudflare R2 public URL format directly
        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'email-autoamation')
        account_id = extract_account_id_from_endpoint()
        
        if account_id:
            # Cloudflare R2 public URL format: https://{account_id}.r2.cloudflarestorage.com/{bucket_name}/{file_key}
            url = f"https://{account_id}.r2.cloudflarestorage.com/{bucket_name}/{file_key}"
            logger.debug(f"Generated Cloudflare R2 public URL: {url}")
            return url
        
        # Fallback: Use bucket name as subdomain
        url = f"https://{bucket_name}.r2.cloudflarestorage.com/{file_key}"
        logger.debug(f"Generated fallback R2 URL: {url}")
        return url
        
    except Exception as e:
        logger.error(f"Error generating public URL: {str(e)}", exc_info=True)
        # Final fallback
        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'email-autoamation')
        return f"https://{bucket_name}.r2.cloudflarestorage.com/{file_key}"

def extract_account_id_from_endpoint():
    """
    Extract account ID from R2 endpoint URL.
    
    Returns:
        str: Account ID or None if not found
    """
    try:
        endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', '')
        if endpoint_url:
            # Parse the endpoint URL to extract account ID
            parsed = urlparse(endpoint_url)
            # R2 endpoint format: https://{account_id}.r2.cloudflarestorage.com
            if '.r2.cloudflarestorage.com' in parsed.netloc:
                account_id = parsed.netloc.split('.')[0]
                return account_id
    except Exception as e:
        logger.error(f"Error extracting account ID: {str(e)}")
    
    return None

def delete_file_from_r2(file_key):
    """
    Delete a file from Cloudflare R2 storage.
    
    Args:
        file_key: The key of the file to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        if not file_key:
            return False
            
        default_storage.delete(file_key)
        logger.info(f"Successfully deleted file from R2: {file_key}")
        return True
    except Exception as e:
        logger.error(f"Error deleting file from R2: {str(e)}", exc_info=True)
        return False

def generate_presigned_url(file_key, expiration=3600):
    """
    Generate a pre-signed URL for a file in R2.
    
    Args:
        file_key: The key of the file
        expiration: Time in seconds until the URL expires (default: 1 hour)
        
    Returns:
        str: Pre-signed URL or None if there was an error
    """
    try:
        if not file_key:
            return None
            
        url = default_storage.url(file_key)
        return url
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}", exc_info=True)
        return None

def validate_r2_configuration():
    """
    Validate that R2 configuration is properly set up.
    
    Returns:
        dict: Configuration status and any issues found
    """
    issues = []
    config = {}
    
    # Check required settings
    required_settings = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_ENDPOINT_URL'
    ]
    
    for setting in required_settings:
        value = getattr(settings, setting, None)
        config[setting] = 'Set' if value else 'Not set'
        if not value:
            issues.append(f"Missing required setting: {setting}")
    
    # Check optional settings
    optional_settings = [
        'AWS_S3_CUSTOM_DOMAIN',
        'AWS_S3_VERIFY',
        'AWS_S3_REGION_NAME'
    ]
    
    for setting in optional_settings:
        value = getattr(settings, setting, None)
        config[setting] = str(value) if value else 'Not set'
    
    # Test storage connection
    try:
        from django.core.files.storage import default_storage
        # Get the actual storage class (not the proxy wrapper)
        storage_class = default_storage.__class__
        storage_type = storage_class.__name__
        config['storage_backend'] = storage_type
        
        # Check if it's R2 storage by checking the class name or module
        if 'R2' not in storage_type and 'R2' not in str(storage_class):
            issues.append(f"Storage backend is not R2: {storage_type}")
            
    except Exception as e:
        issues.append(f"Storage backend error: {str(e)}")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'config': config
    }
