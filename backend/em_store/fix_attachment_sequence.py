import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    exit(1)

from django.db import connection

def check_and_fix_sequence():
    try:
        with connection.cursor() as cursor:
            # Get current max ID
            cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
            max_id = cursor.fetchone()[0] or 0
            
            # Get current sequence value
            cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
            current_sequence = cursor.fetchone()[0]
            
            print(f"Current max ID: {max_id}, Current sequence: {current_sequence}")
            
            if max_id >= current_sequence:
                new_sequence = max_id + 1
                print(f"Sequence needs update. Setting sequence to {new_sequence}")
                
                # Set the sequence to max_id + 1
                cursor.execute(
                    "SELECT setval('campaigns_campaignemailattachment_id_seq', %s, false);",
                    [new_sequence]
                )
                
                # Verify the update
                cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
                updated_sequence = cursor.fetchone()[0]
                
                if updated_sequence == new_sequence:
                    print(f"✓ Successfully updated sequence to {new_sequence}")
                    return True
                else:
                    print(f"✗ Failed to update sequence. Current value: {updated_sequence}")
                    return False
            else:
                print("✓ Sequence is already up to date")
                return True
                
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Campaign Email Attachment Sequence Fixer ===\n")
    success = check_and_fix_sequence()
    
    if success:
        print("\n✓ Sequence check completed successfully")
    else:
        print("\n✗ There were issues updating the sequence")
    
    input("\nPress Enter to exit...")
