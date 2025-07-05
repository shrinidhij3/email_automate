import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.db import connection

def check_sequence():
    print("=== Current Sequence Status ===")
    
    with connection.cursor() as cursor:
        try:
            # Get current max ID
            cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
            max_id = cursor.fetchone()[0] or 0
            
            # Get current sequence value
            cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
            current_sequence = cursor.fetchone()[0]
            
            print(f"Current max ID in table: {max_id or 'No records found'}")
            print(f"Current sequence value: {current_sequence}")
            
            if max_id >= current_sequence:
                print("⚠️  WARNING: Sequence needs to be updated!")
                print(f"   Run: ALTER SEQUENCE campaigns_campaignemailattachment_id_seq RESTART WITH {max_id + 1};")
            else:
                print("✅ Sequence is in sync")
                
            return True
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    check_sequence()
    input("\nPress Enter to exit...")
