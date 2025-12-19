"""
Script to populate inventory cache
Run this after creating cache tables
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.inventory_cache import rebuild_all_cache

if __name__ == '__main__':
    print("\n" + "="*60)
    print("POPULATING INVENTORY CACHE")
    print("="*60)
    
    result = rebuild_all_cache()
    
    if result:
        print("\n" + "="*60)
        print("[SUCCESS] Cache populated successfully!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("[ERROR] Cache population failed!")
        print("="*60)
