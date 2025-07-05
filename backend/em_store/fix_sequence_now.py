import os
import django
import logging

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.db import connection

def fix_sequence():
    print("=== Fixing Campaign Email Attachment Sequence ===")
    
    with connection.cursor() as cursor:
        try:
            # Get current max ID
            cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
            max_id = cursor.fetchone()[0] or 0
            next_id = max_id + 1  # Set to next available ID
            
            print(f"Current max ID in table: {max_id or 'No records found'}")
            print(f"Setting sequence to: {next_id}")
            
            # Set the sequence
            cursor.execute(
                "ALTER SEQUENCE campaigns_campaignemailattachment_id_seq RESTART WITH %s;",
                [next_id]
            )
            
            # Verify
            cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
            new_val = cursor.fetchone()[0]
            
            if new_val == next_id:
                print(f"✅ Success! Sequence is now at: {new_val}")
                return True
            else:
                print(f"❌ Failed to update sequence. Current value: {new_val}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    fix_sequence()
    input("\nPress Enter to exit...")
