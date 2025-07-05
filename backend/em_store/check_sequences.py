import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.db import connection

def check_sequences():
    print("=== Checking Database Sequences ===\n")
    
    with connection.cursor() as cursor:
        # Get all sequences
        cursor.execute("""
            SELECT 
                t.relname as table_name,
                s.relname as sequence_name,
                pg_get_serial_sequence(t.relname, 'id') as sequence_used,
                c.column_name,
                c.data_type,
                pg_sequence_last_value(s.oid) as last_value,
                (SELECT MAX(id) FROM """ + t.relname + """) as max_id
            FROM 
                pg_class s
                JOIN pg_depend d ON d.objid = s.oid
                JOIN pg_class t ON d.objid = s.oid AND d.refobjid = t.oid
                JOIN information_schema.columns c ON c.table_name = t.relname
            WHERE 
                s.relkind = 'S' 
                AND c.column_default LIKE 'nextval%'
            ORDER BY 
                t.relname;
        """)
        
        sequences = cursor.fetchall()
        
        if not sequences:
            print("No sequences found.")
            return
        
        # Print header
        print(f"{'Table':<40} {'Sequence':<40} {'Last Value':>15} {'Max ID':>15} {'Status'}")
        print("-" * 120)
        
        for seq in sequences:
            table_name, seq_name, seq_used, col_name, data_type, last_val, max_id = seq
            max_id = max_id or 0
            last_val = last_val or 0
            
            status = "✅ OK"
            if last_val <= max_id:
                status = f"❌ Needs update (next: {last_val} <= max: {max_id})"
            
            print(f"{table_name:<40} {seq_name:<40} {last_val:>15} {max_id:>15} {status}")

if __name__ == "__main__":
    check_sequences()
    input("\nPress Enter to exit...")
