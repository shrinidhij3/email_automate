import os
import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from django.conf import settings

logger = logging.getLogger(__name__)

def upload_file_to_r2(file_obj, file_name, content_type=None, folder='attachments'):
    """
    Upload a file to Cloudflare R2 storage.
    
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
        
        # Upload the file
        saved_path = default_storage.save(file_path, ContentFile(file_content))
        
        # Generate the public URL
        file_url = urljoin(f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/", saved_path)
        
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
