"""
Backup Verification Script
Run this to check if backup has data
"""
import sqlite3
import sys

def verify_backup(backup_file):
    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n✅ Backup file: {backup_file}")
        print(f"📊 Total tables: {len(tables)}\n")
        
        total_rows = 0
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_rows += count
            if count > 0:
                print(f"  ✓ {table_name}: {count} rows")
        
        print(f"\n📈 Total data rows: {total_rows}")
        
        if total_rows == 0:
            print("\n❌ WARNING: Backup has NO DATA!")
        else:
            print("\n✅ Backup is VALID with data!")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        verify_backup(sys.argv[1])
    else:
        print("Usage: python verify_backup.py <backup_file>")
        print("Example: python verify_backup.py backups/backup_20250115.sqlite3")
