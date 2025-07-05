from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check the current sequence value for campaigns_campaignemailattachment'

    def handle(self, *args, **options):
        self.stdout.write("=== Campaign Email Attachment Sequence Check ===")
        
        with connection.cursor() as cursor:
            try:
                # Check if sequence exists
                cursor.execute("""
                    SELECT 1 
                    FROM pg_sequences 
                    WHERE schemaname = 'public' 
                    AND sequencename = 'campaigns_campaignemailattachment_id_seq';
                """)
                if not cursor.fetchone():
                    self.stdout.write(self.style.ERROR("Sequence 'campaigns_campaignemailattachment_id_seq' not found!"))
                    return 1
                
                # Get current sequence value
                cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
                current_seq = cursor.fetchone()[0]
                
                # Get max ID from table
                cursor.execute("SELECT COALESCE(MAX(id), 0) FROM campaigns_campaignemailattachment;")
                max_id = cursor.fetchone()[0]
                
                self.stdout.write(f"Current sequence value: {current_seq}")
                self.stdout.write(f"Max ID in table: {max_id}")
                
                if current_seq <= max_id:
                    self.stdout.write(self.style.WARNING(
                        f"WARNING: Sequence value ({current_seq}) is less than or equal to max ID ({max_id}). "
                        "This could cause duplicate key errors."
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS("Sequence is properly set."))
                
                # Show recent records
                cursor.execute("""
                    SELECT id, original_filename, created_at 
                    FROM campaigns_campaignemailattachment 
                    ORDER BY id DESC 
                    LIMIT 5;
                """)
                
                self.stdout.write("\nMost recent records:")
                for row in cursor.fetchall():
                    self.stdout.write(f"ID: {row[0]}, File: {row[1]}, Created: {row[2]}")
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error checking sequence: {str(e)}"))
                import traceback
                self.stderr.write(traceback.format_exc())
                return 1
