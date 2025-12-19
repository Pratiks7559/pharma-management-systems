#!/usr/bin/env python3
"""
Delete Unused Database Tables Script
Removes unused tables to optimize database for 600K records
"""

import os
import django
from django.db import connection
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

def delete_unused_tables():
    """Delete unused database tables"""
    
    unused_tables = [
        'core_inventorymaster',
        'core_inventorytransaction', 
        'core_batchstocksummary',
        'sales_challan_invoice',
        'sales_challan_invoice_paid'
    ]
    
    with connection.cursor() as cursor:
        print("🗑️ Starting unused tables cleanup...")
        
        # First check which tables exist (SQLite)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        deleted_count = 0
        for table in unused_tables:
            if table in existing_tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    print(f"✅ Deleted table: {table}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Error deleting {table}: {e}")
            else:
                print(f"ℹ️ Table {table} does not exist")
        
        print(f"\n📊 Summary:")
        print(f"   - Tables deleted: {deleted_count}")
        print(f"   - Tables checked: {len(unused_tables)}")
        
        # Show remaining tables count (SQLite)
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        remaining_tables = cursor.fetchone()[0]
        print(f"   - Remaining tables: {remaining_tables}")

if __name__ == "__main__":
    delete_unused_tables()
    print("\n✅ Database cleanup completed!")