#!/usr/bin/env python3
import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

def delete_unused_tables():
    unused_tables = [
        'core_inventorymaster',
        'core_inventorytransaction', 
        'core_batchstocksummary',
        'sales_challan_invoice',
        'sales_challan_invoice_paid'
    ]
    
    with connection.cursor() as cursor:
        print("Starting unused tables cleanup...")
        
        # Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        deleted_count = 0
        for table in unused_tables:
            if table in existing_tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    print(f"Deleted table: {table}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {table}: {e}")
            else:
                print(f"Table {table} does not exist")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        remaining_tables = cursor.fetchone()[0]
        
        print(f"\nSummary:")
        print(f"- Tables deleted: {deleted_count}")
        print(f"- Remaining tables: {remaining_tables}")

if __name__ == "__main__":
    delete_unused_tables()
    print("\nDatabase cleanup completed!")