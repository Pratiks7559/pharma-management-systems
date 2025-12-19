import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import ProductInventoryCache, BatchInventoryCache, ProductMaster

print("=" * 60)
print("CACHE STATUS CHECK")
print("=" * 60)

# Product Cache
product_cache_count = ProductInventoryCache.objects.count()
total_products = ProductMaster.objects.count()

print(f"\n📦 ProductInventoryCache:")
print(f"   Entries: {product_cache_count}")
print(f"   Total Products: {total_products}")
print(f"   Coverage: {(product_cache_count/total_products*100):.1f}%")

# Batch Cache
batch_cache_count = BatchInventoryCache.objects.count()
batch_with_stock = BatchInventoryCache.objects.filter(current_stock__gt=0).count()

print(f"\n📊 BatchInventoryCache:")
print(f"   Total Entries: {batch_cache_count}")
print(f"   With Stock > 0: {batch_with_stock}")
print(f"   Empty Batches: {batch_cache_count - batch_with_stock}")

# Sample Data
print(f"\n🔍 Sample Product Cache (First 5):")
for cache in ProductInventoryCache.objects.all()[:5]:
    print(f"   {cache.product.product_name}: Stock={cache.total_stock}, Batches={cache.total_batches}, Value=₹{cache.total_stock_value:.2f}")

print(f"\n🔍 Sample Batch Cache (First 5):")
for batch in BatchInventoryCache.objects.filter(current_stock__gt=0)[:5]:
    print(f"   {batch.product.product_name} | Batch: {batch.batch_no} | Expiry: {batch.expiry_date} | Stock: {batch.current_stock}")

print("\n" + "=" * 60)
