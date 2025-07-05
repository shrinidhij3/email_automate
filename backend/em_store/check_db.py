import os
import django

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
    django.setup()

def check_sequence():
    from django.db import connection
    
    print("=== Checking Database Sequence ===\n")
    
    # Test connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return
    
    # Check sequence
    try:
        with connection.cursor() as cursor:
            # Check if sequence exists
            cursor.execute("""
                SELECT 1 
                FROM pg_sequences 
                WHERE schemaname = 'public' 
                AND sequencename = 'campaigns_campaignemailattachment_id_seq';
            """)
            
            if not cursor.fetchone():
                print("✗ Sequence 'campaigns_campaignemailattachment_id_seq' does not exist")
                return
                
            # Get current sequence value
            cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
            seq_value = cursor.fetchone()[0]
            print(f"Current sequence value: {seq_value}")
            
            # Get max ID from table
            cursor.execute("SELECT COALESCE(MAX(id), 0) FROM campaigns_campaignemailattachment;")
            max_id = cursor.fetchone()[0]
            print(f"Max ID in table: {max_id}")
            
            if seq_value <= max_id:
                print(f"⚠ WARNING: Sequence value ({seq_value}) is less than or equal to max ID ({max_id})")
                print("  This will cause duplicate key errors on new inserts.")
                
                # Calculate next sequence value
                next_val = max_id + 1
                print(f"\nTo fix, run this SQL command:")
                print(f"ALTER SEQUENCE campaigns_campaignemailattachment_id_seq RESTART WITH {next_val};")
            else:
                print("✓ Sequence is properly configured")
                
    except Exception as e:
        print(f"Error checking sequence: {e}")

if __name__ == "__main__":
    setup_django()
    check_sequence()
