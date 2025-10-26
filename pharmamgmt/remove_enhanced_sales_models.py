#!/usr/bin/env python3
"""
Script to remove Enhanced Sales Return models from the database
Run this script to clean up the database after removing enhanced sales return models
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.db import connection

def remove_enhanced_sales_tables():
    """Remove enhanced sales return tables from database"""
    
    tables_to_remove = [
        'core_enhancedsalesreturn',
        'core_enhancedsalesreturnitem', 
        'core_salesreturnapproval'
    ]
    
    with connection.cursor() as cursor:
        for table in tables_to_remove:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table};")
                print(f"✓ Removed table: {table}")
            except Exception as e:
                print(f"✗ Error removing table {table}: {e}")
    
    print("\n✓ Enhanced sales return tables cleanup completed!")

if __name__ == "__main__":
    print("Removing Enhanced Sales Return tables...")
    remove_enhanced_sales_tables()