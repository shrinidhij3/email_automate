import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.db import connection

def check_attachment_sequence():
    print("=== Checking Campaign Email Attachment Sequence ===\n")
    
    with connection.cursor() as cursor:
        # Get current max ID
        cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
        max_id = cursor.fetchone()[0] or 0
        
        # Get current sequence value
        cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
        last_value = cursor.fetchone()[0] or 0
        
        # Get next sequence value
        cursor.execute("SELECT nextval('campaigns_campaignemailattachment_id_seq');")
        next_value = cursor.fetchone()[0]
        
        # Rollback the nextval so we don't consume the sequence
        cursor.execute("SELECT setval('campaigns_campaignemailattachment_id_seq', %s, false);", [last_value])
        
        print(f"Current max ID in table: {max_id}")
        print(f"Current sequence last value: {last_value}")
        print(f"Next sequence value would be: {next_value}")
        
        if last_value <= max_id:
            print("\n⚠️  WARNING: Sequence is behind or equal to max ID. This will cause duplicate key errors!")
            print(f"   Current max ID: {max_id}")
            print(f"   Next sequence value: {next_value}")
        else:
            print("\n✅ Sequence is properly set (last_value > max_id)")

if __name__ == "__main__":
    check_attachment_sequence()
    input("\nPress Enter to exit...")
