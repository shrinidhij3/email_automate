from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check database connection and table status'

    def handle(self, *args, **options):
        self.stdout.write("=== Database Connection Check ===")
        
        try:
            with connection.cursor() as cursor:
                # Check if we can connect to the database
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS("✓ Successfully connected to database"))
                
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'campaigns_campaignemailattachment'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    self.stdout.write(self.style.SUCCESS("✓ Table 'campaigns_campaignemailattachment' exists"))
                    
                    # Get row count
                    cursor.execute("SELECT COUNT(*) FROM campaigns_campaignemailattachment;")
                    row_count = cursor.fetchone()[0]
                    self.stdout.write(f"✓ Table has {row_count} rows")
                    
                    # Get max ID
                    cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
                    max_id = cursor.fetchone()[0] or 0
                    self.stdout.write(f"✓ Max ID in table: {max_id}")
                    
                    # Check sequence
                    cursor.execute("""
                        SELECT last_value 
                        FROM campaigns_campaignemailattachment_id_seq;
                    """)
                    sequence_value = cursor.fetchone()[0]
                    self.stdout.write(f"✓ Current sequence value: {sequence_value}")
                    
                    if sequence_value <= max_id:
                        self.stdout.write(self.style.WARNING(
                            "⚠ WARNING: Sequence value is less than or equal to max ID. "
                            "This will cause duplicate key errors on new inserts."
                        ))
                    
                    # Show recent records
                    if row_count > 0:
                        self.stdout.write("\nMost recent records:")
                        cursor.execute("""
                            SELECT id, original_filename, created_at 
                            FROM campaigns_campaignemailattachment 
                            ORDER BY id DESC 
                            LIMIT 3;
                        """)
                        for row in cursor.fetchall():
                            self.stdout.write(f"  - ID: {row[0]}, File: {row[1]}, Created: {row[2]}")
                else:
                    self.stdout.write(self.style.WARNING("Table 'campaigns_campaignemailattachment' does not exist"))
                    
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Database error: {str(e)}"))
            import traceback
            self.stderr.write(traceback.format_exc())
