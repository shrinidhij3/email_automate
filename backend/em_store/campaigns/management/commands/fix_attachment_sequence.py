from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix the sequence for the campaigns_campaignemailattachment table'

    def handle(self, *args, **options):
        self.stdout.write("=== Fixing CampaignEmailAttachment Sequence ===")
        
        with connection.cursor() as cursor:
            try:
                # Get current max ID
                cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
                max_id = cursor.fetchone()[0] or 0
                next_id = max_id + 100  # Add buffer to prevent immediate conflicts
                
                self.stdout.write(f"Current max ID in table: {max_id or 'No records found'}")
                self.stdout.write(f"Setting sequence to start from: {next_id}")
                
                # Set the sequence to a higher value
                cursor.execute(
                    "ALTER SEQUENCE campaigns_campaignemailattachment_id_seq RESTART WITH %s;",
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
                else:
                    self.stderr.write(
                        self.style.ERROR(
                            f'Failed to update sequence. Current value: {new_sequence}'
                        )
                    )
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
                import traceback
                self.stderr.write(traceback.format_exc())
