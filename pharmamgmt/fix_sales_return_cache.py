"""
Fix Sales Return Cache - Manually rebuild cache for affected products
Run this after sales return to update inventory
"""
import os
import sys
import django

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebsiteHostingService.settings')
django.setup()

from core.inventory_cache import update_all_batches_for_product, rebuild_all_cache
from core.models import ReturnSalesMaster

def fix_recent_sales_returns():
    """Fix cache for recent sales returns"""
    print("🔧 Fixing sales return cache...")
    
    # Get all unique products from sales returns
    returns = ReturnSalesMaster.objects.values('return_productid').distinct()
    
    fixed_count = 0
    for ret in returns:
        product_id = ret['return_productid']
        try:
            update_all_batches_for_product(product_id)
            fixed_count += 1
            print(f"✅ Fixed product {product_id}")
        except Exception as e:
            print(f"❌ Error fixing product {product_id}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} products")
    return fixed_count

if __name__ == "__main__":
    print("=" * 60)
    print("SALES RETURN CACHE FIX")
    print("=" * 60)
    
    choice = input("\n1. Fix recent sales returns only\n2. Rebuild entire cache\n\nChoice (1/2): ")
    
    if choice == "1":
        fix_recent_sales_returns()
    elif choice == "2":
        rebuild_all_cache()
    else:
        print("Invalid choice")
    
    print("\n✅ Done! Check All Product Inventory now.")
