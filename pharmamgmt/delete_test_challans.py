import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import Challan1, SupplierChallanMaster
from django.db import transaction

def delete_test_challans():
    """Delete all test supplier challans"""
    
    print("🗑️  Starting deletion of test challans...")
    
    try:
        with transaction.atomic():
            # Count before deletion
            challan_count = Challan1.objects.count()
            items_count = SupplierChallanMaster.objects.count()
            
            print(f"📊 Found {challan_count} challans and {items_count} items")
            
            # Confirm deletion
            confirm = input(f"\n⚠️  Are you sure you want to delete ALL {challan_count} challans? (yes/no): ")
            
            if confirm.lower() != 'yes':
                print("❌ Deletion cancelled")
                return
            
            # Delete all challan items first (due to foreign key)
            deleted_items = SupplierChallanMaster.objects.all().delete()
            print(f"✅ Deleted {deleted_items[0]} challan items")
            
            # Delete all challans
            deleted_challans = Challan1.objects.all().delete()
            print(f"✅ Deleted {deleted_challans[0]} challans")
            
            print(f"\n🎉 Successfully deleted all test challans!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import time
    start = time.time()
    delete_test_challans()
    print(f"⏱️  Time taken: {time.time() - start:.2f} seconds")
