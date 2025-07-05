import os
import psycopg2
from dotenv import load_dotenv

def get_db_connection():
    """Create a direct database connection using environment variables"""
    load_dotenv()
    
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def check_sequence():
    """Check the campaigns_campaignemailattachment sequence status"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return

    try:
        with conn.cursor() as cur:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'campaigns_campaignemailattachment'
                );
            """)
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                print("Table 'campaigns_campaignemailattachment' does not exist")
                return
                
            print("✓ Table 'campaigns_campaignemailattachment' exists")
            
            # Get max ID
            cur.execute("SELECT COALESCE(MAX(id), 0) FROM campaigns_campaignemailattachment;")
            max_id = cur.fetchone()[0]
            print(f"Max ID in table: {max_id}")
            
            # Check if sequence exists
            cur.execute("""
                SELECT 1 
                FROM pg_sequences 
                WHERE schemaname = 'public' 
                AND sequencename = 'campaigns_campaignemailattachment_id_seq';
            """)
            
            if not cur.fetchone():
                print("✗ Sequence 'campaigns_campaignemailattachment_id_seq' does not exist")
                print("\nTo create the sequence, run these SQL commands:")
                print(f"CREATE SEQUENCE campaigns_campaignemailattachment_id_seq START WITH {max_id + 1};")
                print("ALTER TABLE campaigns_campaignemailattachment ALTER COLUMN id SET DEFAULT nextval('campaigns_campaignemailattachment_id_seq');")
                return
                
            # Get current sequence value
            cur.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
            current_seq = cur.fetchone()[0]
            print(f"Current sequence value: {current_seq}")
            
            if current_seq <= max_id:
                print(f"⚠ WARNING: Sequence value ({current_seq}) is less than or equal to max ID ({max_id})")
                print("  This will cause duplicate key errors on new inserts.")
                
                # Calculate next sequence value
                next_val = max_id + 1
                print("\nTo fix, run this SQL command:")
                print(f"ALTER SEQUENCE campaigns_campaignemailattachment_id_seq RESTART WITH {next_val};")
            else:
                print("✓ Sequence is properly configured")
                
    except Exception as e:
        print(f"Error checking sequence: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Campaign Email Attachment Sequence Check ===\n")
    check_sequence()
