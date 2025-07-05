from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check database connection and sequence status'

    def handle(self, *args, **options):
        self.stdout.write("=== Database Connection Check ===")
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS("✓ Database connection successful"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Database connection failed: {e}"))
            return
        
        # Check if table exists
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'campaigns_campaignemailattachment'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                self.stdout.write(self.style.ERROR("✗ Table 'campaigns_campaignemailattachment' does not exist"))
                return
                
            self.stdout.write(self.style.SUCCESS("✓ Table 'campaigns_campaignemailattachment' exists"))
            
            # Get max ID
            cursor.execute("SELECT COALESCE(MAX(id), 0) FROM campaigns_campaignemailattachment;")
            max_id = cursor.fetchone()[0]
            self.stdout.write(f"Max ID in table: {max_id}")
            
            # Check sequence
            try:
                cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
                current_seq = cursor.fetchone()[0]
                self.stdout.write(f"Current sequence value: {current_seq}")
                
                if current_seq <= max_id:
                    self.stdout.write(self.style.WARNING(
                        f"⚠ WARNING: Sequence value ({current_seq}) is less than or equal to max ID ({max_id})"
                    ))
                    self.stdout.write(self.style.WARNING(
                        "  This will cause duplicate key errors on new inserts."
                    ))
                    
                    # Calculate next sequence value
                    next_val = max_id + 1
                    self.stdout.write("\nTo fix, run this SQL command:")
                    self.stdout.write(self.style.SQL_KEYWORD(
                        f"ALTER SEQUENCE campaigns_campaignemailattachment_id_seq RESTART WITH {next_val};"
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS("✓ Sequence is properly configured"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error checking sequence: {e}"))
                self.stdout.write("\nTo create the sequence, run these SQL commands:")
                self.stdout.write(self.style.SQL_KEYWORD(
                    f"CREATE SEQUENCE IF NOT EXISTS campaigns_campaignemailattachment_id_seq \n"
                    f"  START WITH {max_id + 1} \n"
                    f"  OWNED BY campaigns_campaignemailattachment.id;"
                ))
                self.stdout.write(self.style.SQL_KEYWORD(
                    "ALTER TABLE campaigns_campaignemailattachment \n"
                    "  ALTER COLUMN id SET DEFAULT nextval('campaigns_campaignemailattachment_id_seq'::regclass);"
                ))
        
        self.stdout.write("\n=== Database Check Complete ===")
