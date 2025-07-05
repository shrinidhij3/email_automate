from django.core.management.base import BaseCommand
from django.db import connection, models
from campaigns.models import CampaignEmailAttachment
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix the sequence for the campaigns_campaignemailattachment table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force the sequence update even if it appears to be in sync',
        )

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        force = options.get('force', False)
        
        if verbosity > 1:
            logger.setLevel(logging.DEBUG)
        
        self.stdout.write("=== Campaign Email Attachment Sequence Fix ===")
        
        with connection.cursor() as cursor:
            try:
                # Get current max ID
                cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
                max_id = cursor.fetchone()[0] or 0
                next_id = max_id + 1 if max_id > 0 else 1
                
                # Get current sequence value
                cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
                current_sequence = cursor.fetchone()[0]
                
                self.stdout.write(f"Current max ID in table: {max_id or 'No records found'}")
                self.stdout.write(f"Current sequence value: {current_sequence}")
                
                if max_id >= current_sequence or force:
                    if not force:
                        self.stdout.write(f"Sequence needs update. Will set to: {next_id}")
                    else:
                        self.stdout.write(f"Forcing sequence update to: {next_id}")
                    
                    # Set new sequence value
                    cursor.execute(
                        "SELECT setval('campaigns_campaignemailattachment_id_seq', %s, false);",
                        [next_id]
                    )
                    
                    # Verify the update
                    cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
                    new_sequence = cursor.fetchone()[0]
                    
                    if new_sequence == next_id:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Successfully updated sequence to {new_sequence}'
                            )
                        )
                        return
                    else:
                        self.stderr.write(
                            self.style.ERROR(
                                f'Failed to update sequence. Current value: {new_sequence}'
                            )
                        )
                        return 1
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            'Sequence is already in sync. No changes needed.'
                        )
                    )
                    return
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
                if verbosity > 1:
                    import traceback
                    self.stderr.write(traceback.format_exc())
                return 1
