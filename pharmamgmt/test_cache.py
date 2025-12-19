"""
Quick test - Populate cache for first 10 products only
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import ProductMaster
from core.inventory_cache import update_all_batches_for_product

if __name__ == '__main__':
    print("\n" + "="*60)
    print("TESTING CACHE - First 10 Products")
    print("="*60)
    
    products = ProductMaster.objects.all()[:10]
    
    for idx, product in enumerate(products, 1):
        print(f"\n[{idx}/10] Processing: {product.product_name}")
        try:
            update_all_batches_for_product(product.productid)
            print(f"  [OK] Cache updated successfully")
        except Exception as e:
            print(f"  [ERROR] Failed: {e}")
    
    print("\n" + "="*60)
    print("[SUCCESS] Test completed!")
    print("="*60)
    
    # Show results
    from core.models import ProductInventoryCache, BatchInventoryCache
    
    print(f"\nCache Statistics:")
    print(f"  Product Caches: {ProductInventoryCache.objects.count()}")
    print(f"  Batch Caches: {BatchInventoryCache.objects.count()}")
