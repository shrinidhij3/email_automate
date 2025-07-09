import os
import uuid
import logging
import base64
from django.db import models, connection
from django.conf import settings
from django.core.validators import EmailValidator
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.utils import timezone
from em_store.storage_utils import upload_file_to_r2, delete_file_from_r2

# Set up logging
logger = logging.getLogger(__name__)

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


def campaign_attachment_path(instance, filename):
    """Generate file path for campaign attachments"""
    ext = filename.split('.')[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    return f'campaigns/{instance.email_campaign_id}/attachments/{filename}'

class EmailCampaign(models.Model):
    """
    Model representing an email campaign with provider configuration.
    """
    
    # Campaign Information
    name = models.CharField(max_length=255, help_text="Name of the campaign")
    subject = models.CharField(max_length=255, help_text="Email subject line")
    body = models.TextField(help_text="HTML content of the email")
 
    
    # User and Authentication
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_campaigns',
        help_text="User who created this campaign (optional)"
    )
    email = models.EmailField(
        max_length=255,
        validators=[EmailValidator()],
        help_text="Email address used to send the campaign"
    )
    _password = None
    password = models.CharField(
        max_length=1024,  # Increased to store encrypted data
        null=True,
        blank=True,
        help_text="Email account password (encrypted in database)"
    )
    
    # Provider Configuration
    provider = models.CharField(
        max_length=100,
        default='gmail',
        help_text="Email service provider (e.g., gmail, yahoo, cpanel, etc.)"
    )
    
    # IMAP Configuration
    imap_host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="IMAP server hostname (leave blank to use provider defaults)"
    )
    imap_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="IMAP server port (leave blank to use provider defaults)"
    )
    
    # SMTP Configuration
    smtp_host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="SMTP server hostname (leave blank to use provider defaults)"
    )
    smtp_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="SMTP server port (leave blank to use provider defaults)"
    )
    
    # Security Settings
    use_ssl = models.BooleanField(
        default=True,
        help_text="Whether to use SSL/TLS for the connection"
    )
    

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Any additional notes or comments"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Campaign'
        verbose_name_plural = 'Email Campaigns'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original password on init to detect changes
        self._password = self.password
    
    def __str__(self):
        return f"{self.name} - {self.email} ({self.provider})"
    
    def save(self, *args, **kwargs):
        # Encrypt password if it's new or changed
        if self.password and (not self.pk or self.password != self._password):
            try:
                f = Fernet(get_fernet_key())
                self.password = f.encrypt(self.password.encode()).decode()
            except Exception as e:
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
    
    def get_decrypted_password_display(self):
        return self.get_decrypted_password()
    get_decrypted_password_display.short_description = 'Password (decrypted)'
    


class CampaignEmailAttachment(models.Model):
    """
    Model for files attached to email campaigns.
    Uses FileField for better performance with large files.
    """
    id = models.BigAutoField(primary_key=True, auto_created=True)
    email_campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text="The email campaign this file is attached to"
    )
    file = models.FileField(
        upload_to=campaign_attachment_path,
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
    file_size = models.PositiveIntegerField(
        help_text="Size of the file in bytes"
    )
    download_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Direct download URL for the file"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Campaign Attachment'
        verbose_name_plural = 'Campaign Attachments'
    
    def __str__(self):
        return f"{self.original_filename} (Campaign: {self.email_campaign.name})"
    
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
                upload_result = upload_file_to_r2(
                    file_content,
                    file_name=os.path.basename(self.file.name),
                    content_type=self.content_type,
                    folder=f'campaigns/{self.email_campaign_id}/attachments'
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
        
        # Ensure sequence is in sync after saving
        if is_new and self.pk:
            self._ensure_sequence_sync()
            
        # If file was changed, update the URL in the database
        if file_changed and self.pk:
            CampaignEmailAttachment.objects.filter(pk=self.pk).update(
                file=self.file.name,
                download_url=self.download_url
            )
    
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
        
    def get_download_url(self):
        """Return the stored download URL."""
        if not self.download_url and self.pk:
            self.download_url = self._generate_download_url()
            self.save(update_fields=['download_url'])
        return self.download_url
    
    def _ensure_sequence_sync(self):
        """Ensure the sequence is in sync with the max ID"""
        try:
            with connection.cursor() as cursor:
                # Get current max ID
                cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
                max_id = cursor.fetchone()[0] or 0
                
                # Get current sequence value
                cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
                current_sequence = cursor.fetchone()[0]
                
                if max_id > current_sequence:
                    new_sequence = max_id + 1
                    logger.info(f"Updating sequence from {current_sequence} to {new_sequence}")
                    
                    # Set the sequence to max_id + 1
                    cursor.execute(
                        "SELECT setval('campaigns_campaignemailattachment_id_seq', %s, false);",
                        [new_sequence]
                    )
                    return True
                return False
                    
        except Exception as e:
            logger.error(f"Error syncing sequence: {e}", exc_info=True)
            return False
    
    def delete(self, *args, **kwargs):
        """Delete the file from R2 when the model instance is deleted"""
        # Delete the file from R2 storage
        if self.file:
            try:
                # Delete using our storage utility
                delete_file_from_r2(self.file.name)
            except Exception as e:
                logger.error(f"Error deleting file from R2: {e}", exc_info=True)
                
        # Delete the model instance
        super().delete(*args, **kwargs)
        
        # Ensure sequence is still in sync after deletion
        self._ensure_sequence_sync()
