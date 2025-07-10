# model
import os
import uuid
import base64
import logging
from django.db import models

# Set up logger
logger = logging.getLogger(__name__)
from django.core.validators import EmailValidator
from django.utils import timezone
from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Generate a key from Django's SECRET_KEY
def get_fernet_key():
    salt = settings.SECRET_KEY[:16].encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
    return key

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'unread_emails/user_{instance.id}/{filename}'

class UnreadEmail(models.Model):
    """
    Model to store unread email form submissions with email provider configuration
    """
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('other', 'Other'),
    ]
    
    # User information
    name = models.CharField(max_length=255, help_text="Full name of the submitter")
    email = models.EmailField(
        max_length=255,
        validators=[EmailValidator()],
        help_text="Email address of the submitter"
    )
    # Password field - stores encrypted password in the database
    _password = None
    password = models.CharField(
        max_length=1024,  # Increased to store encrypted data
        null=True,
        blank=True,
        help_text="Email account password (encrypted in database)"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original password on init to detect changes
        self._password = self.password
    
    def save(self, *args, **kwargs):
        # Always encrypt the password if it's set and not already encrypted
        if self.password and not self.password.startswith('gAA'):  # Simple check if not encrypted
            try:
                f = Fernet(get_fernet_key())
                self.password = f.encrypt(self.password.encode()).decode()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error encrypting password: {e}")
                raise
        super().save(*args, **kwargs)
    
    def get_decrypted_password(self):
        """Get the decrypted password"""
        if not self.password:
            return None
        try:
            f = Fernet(get_fernet_key())
            return f.decrypt(self.password.encode()).decode()
        except Exception as e:
            logger.error(f"Error decrypting password: {e}")
            return None
    
    # Processing status
    is_processed = models.BooleanField(
        default=False,
        help_text="Whether this submission has been processed"
    )
    
    # Provider information
    provider = models.CharField(
        max_length=100,  # Increased max_length to accommodate custom providers
        default='gmail',
        help_text="Email service provider (can be any value)"
    )
    
    # IMAP Configuration
    imap_host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="IMAP server hostname"
    )
    imap_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="IMAP server port"
    )
    
    # SMTP Configuration
    smtp_host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="SMTP server hostname"
    )
    smtp_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="SMTP server port"
    )
    
    # Security
    secure = models.BooleanField(
        default=True,
        help_text="Whether to use SSL/TLS for the connection (legacy field)"
    )
    use_ssl = models.BooleanField(
        default=True,
        help_text="Whether to use SSL/TLS for the connection (new field)"
    )
    
    # Timestamps and status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(
        default=False,
        help_text="Whether this submission has been processed"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Any additional notes or comments"
    )

    def __str__(self):
        return f"{self.name} <{self.email}>"

    class Meta:
        db_table = 'credentials_email'
        ordering = ['-created_at']
        verbose_name = 'Unread Email Submission'
        verbose_name_plural = 'Unread Email Submissions'


class UnreadEmailAttachment(models.Model):
    """
    Model to store file attachments for unread email submissions
    Files are stored in Cloudflare R2 storage
    """
    def unread_email_attachment_path(instance, filename):
        """Generate file path for unread email attachments"""
        ext = os.path.splitext(filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        return os.path.join('unread_email_attachments', filename)

    unread_email = models.ForeignKey(
        UnreadEmail,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text="The unread email submission this file belongs to"
    )
    file = models.FileField(
        upload_to=unread_email_attachment_path,
        null=True,
        blank=True,
        help_text="The actual file"
    )
    original_filename = models.CharField(
        max_length=255,
        help_text="Original name of the uploaded file"
    )
    content_type = models.CharField(
        max_length=100,
        help_text="MIME type of the file"
    )
    file_size = models.PositiveIntegerField(default=0, help_text="Size of the file in bytes")
    download_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct download URL for the file")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Unread Email Attachment'
        verbose_name_plural = 'Unread Email Attachments'

    def __str__(self):
        return f"{self.original_filename} ({self.unread_email.email})"

    def save(self, *args, **kwargs):
        """Save the file to Cloudflare R2 and update file metadata."""
        is_new = not self.pk
        file_changed = False
        
        # Handle file upload to R2 for new attachments
        if is_new and self.file:
            self.original_filename = os.path.basename(str(self.file))
            
            # Get content type from file if not set
            if not hasattr(self, 'content_type') or not self.content_type:
                try:
                    import mimetypes
                    content_type, _ = mimetypes.guess_type(self.original_filename)
                    self.content_type = content_type or 'application/octet-stream'
                except Exception as e:
                    logger.error(f"Error detecting content type: {e}")
                    self.content_type = 'application/octet-stream'
            
            # Read the file content
            try:
                file_content = self.file.read()
                self.file_size = len(file_content)
                
                # Upload to R2
                from em_store.storage_utils import upload_file_to_r2
                upload_result = upload_file_to_r2(
                    file_content,
                    file_name=os.path.basename(self.file.name),
                    content_type=self.content_type,
                    folder=f'unread_emails/{self.unread_email_id}/attachments'
                )
                
                if upload_result['success']:
                    # Store the R2 key and URL
                    self.file.name = upload_result['key']
                    self.download_url = upload_result['url']
                    file_changed = True
                else:
                    logger.error(f"Failed to upload file to R2: {upload_result.get('error')}")
                    raise Exception(f"Failed to upload file to storage: {upload_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error processing file upload: {e}", exc_info=True)
                raise
        
        # Save the model
        super().save(*args, **kwargs)
        
        # If file was changed, update the URL in the database
        if file_changed and self.pk:
            UnreadEmailAttachment.objects.filter(pk=self.pk).update(
                file=self.file.name,
                download_url=self.download_url
            )
    
    def get_download_url(self):
        """Return the stored download URL."""
        if not self.download_url and self.pk:
            self.download_url = self._generate_download_url()
            self.save(update_fields=['download_url'])
        return self.download_url
    
    def _generate_download_url(self):
        """Generate a download URL for this attachment from R2."""
        if not self.file:
            return ""
            
        try:
            # If we already have a download URL, use it
            if self.download_url:
                return self.download_url
                
            # Otherwise, generate a new URL from the file field
            if hasattr(self.file, 'url'):
                return self.file.url
                
            # Fallback to constructing the URL from settings
            if hasattr(settings, 'AWS_S3_CUSTOM_DOMAIN'):
                return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{self.file.name}"
                
            return ""
            
        except Exception as e:
            logger.error(f"Error generating download URL: {e}", exc_info=True)
            return ""
    
    def delete(self, *args, **kwargs):
        """Delete the file from R2 when the model instance is deleted"""
        # Delete the file from R2 storage
        if self.file:
            try:
                from em_store.storage_utils import delete_file_from_r2
                delete_file_from_r2(self.file.name)
            except Exception as e:
                logger.error(f"Error deleting file from R2: {e}", exc_info=True)
                
        # Delete the model instance
        super().delete(*args, **kwargs)

