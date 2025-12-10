import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import CustomerChallan, CustomerChallanMaster
from django.db import transaction

def delete_test_customer_challans():
    """Delete all test customer challans"""
    
    print("🗑️  Starting deletion of test customer challans...")
    
    try:
        with transaction.atomic():
            # Count before deletion
            challan_count = CustomerChallan.objects.count()
            items_count = CustomerChallanMaster.objects.count()
            
            print(f"📊 Found {challan_count} customer challans and {items_count} items")
            
            # Confirm deletion
            confirm = input(f"\n⚠️  Are you sure you want to delete ALL {challan_count} customer challans? (yes/no): ")
            
            if confirm.lower() != 'yes':
                print("❌ Deletion cancelled")
                return
            
            # Delete all challan items first (due to foreign key)
            deleted_items = CustomerChallanMaster.objects.all().delete()
            print(f"✅ Deleted {deleted_items[0]} customer challan items")
            
            # Delete all challans
            deleted_challans = CustomerChallan.objects.all().delete()
            print(f"✅ Deleted {deleted_challans[0]} customer challans")
            
            print(f"\n🎉 Successfully deleted all test customer challans!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import time
    start = time.time()
    delete_test_customer_challans()
    print(f"⏱️  Time taken: {time.time() - start:.2f} seconds")
