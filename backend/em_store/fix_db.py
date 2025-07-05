"""
Database diagnostic and fix script for CampaignEmailAttachment sequence issue.
This script will:
1. Check database connection
2. Check if the table exists
3. Check current sequence value
4. Fix the sequence if needed
"""
import os
import sys
import django

def setup_django():
    """Set up Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
    django.setup()

def check_database():
    """Check database connection and table status"""
    from django.db import connection
    
    print("=== Database Check ===")
    
    # Test connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
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
            print("✗ Table 'campaigns_campaignemailattachment' does not exist")
            return False
            
        print("✓ Table 'campaigns_campaignemailattachment' exists")
        
        # Get current sequence value
        try:
            cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
            current_seq = cursor.fetchone()[0]
            print(f"Current sequence value: {current_seq}")
        except Exception as e:
            print(f"✗ Could not get sequence value: {e}")
            return False
            
        # Get max ID from table
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM campaigns_campaignemailattachment;")
        max_id = cursor.fetchone()[0]
        print(f"Max ID in table: {max_id}")
        
        if current_seq <= max_id:
            print(f"⚠ WARNING: Sequence value ({current_seq}) is less than or equal to max ID ({max_id})")
            return True
            
        print("✓ Sequence is properly set")
        return True

def fix_sequence():
    """Fix the sequence for the campaigns_campaignemailattachment table"""
    from django.db import connection
    
    print("\n=== Fixing Sequence ===")
    
    with connection.cursor() as cursor:
        # Get max ID
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM campaigns_campaignemailattachment;")
        next_id = cursor.fetchone()[0]
        
        print(f"Setting sequence to start from: {next_id}")
        
        try:
            # Set the sequence
            cursor.execute(
                "ALTER SEQUENCE campaigns_campaignemailattachment_id_seq RESTART WITH %s;",
                [next_id]
            )
            print("✓ Sequence updated successfully")
            
            # Verify
            cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
            new_seq = cursor.fetchone()[0]
            print(f"New sequence value: {new_seq}")
            
            if new_seq < next_id:
                print("⚠ WARNING: Sequence was not updated correctly")
                return False
                
            return True
            
        except Exception as e:
            print(f"✗ Error updating sequence: {e}")
            return False

if __name__ == "__main__":
    print("=== Campaign Email Attachment Sequence Fix ===\n")
    
    try:
        setup_django()
        
        if not check_database():
            print("\n✗ Database check failed. Please fix the issues above.")
            sys.exit(1)
            
        if fix_sequence():
            print("\n✓ Sequence fixed successfully!")
        else:
            print("\n✗ Failed to fix sequence. Please check the error messages above.")
            
    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
