from django.core.management.base import BaseCommand
from unread_emails.models import UnreadEmailAttachment
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate download URLs for existing UnreadEmailAttachment records'

    def handle(self, *args, **options):
        # Get all attachments without a download URL
        attachments = UnreadEmailAttachment.objects.filter(download_url__isnull=True)
        total = attachments.count()
        
        self.stdout.write(f'Found {total} attachments without download URLs')
        
        updated_count = 0
        for attachment in attachments:
            try:
                # Try to generate a Cloudflare URL first
                attachment.download_url = attachment._generate_cloudflare_url()
                
                # If Cloudflare URL generation failed, try the fallback
                if not attachment.download_url:
                    attachment.download_url = attachment._generate_download_url()
                
                if attachment.download_url:
                    attachment.save(update_fields=['download_url'])
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Generated URL for {attachment.original_filename}: {attachment.download_url}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Could not generate URL for {attachment.original_filename}'))
                    
            except Exception as e:
                logger.error(f'Error processing attachment {attachment.id}: {str(e)}')
                self.stdout.write(self.style.ERROR(f'Error processing {attachment.original_filename}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} out of {total} attachments'))
