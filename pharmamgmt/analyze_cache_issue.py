import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import (
    ProductInventoryCache, BatchInventoryCache, ProductMaster,
    PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster,
    SupplierChallanMaster, CustomerChallanMaster
)

print("=" * 70)
print("CACHE ISSUE ANALYSIS - Why only 8 entries?")
print("=" * 70)

# 1. Check total products
total_products = ProductMaster.objects.count()
print(f"\n1️⃣ Total Products in DB: {total_products}")

# 2. Check cache entries
product_cache = ProductInventoryCache.objects.count()
batch_cache = BatchInventoryCache.objects.count()
print(f"\n2️⃣ Cache Entries:")
print(f"   ProductInventoryCache: {product_cache}")
print(f"   BatchInventoryCache: {batch_cache}")

# 3. Check which products have transactions
products_with_purchases = PurchaseMaster.objects.values('productid').distinct().count()
products_with_sales = SalesMaster.objects.values('productid').distinct().count()
products_with_pr = ReturnPurchaseMaster.objects.values('returnproductid').distinct().count()
products_with_sr = ReturnSalesMaster.objects.values('return_productid').distinct().count()
products_with_sc = SupplierChallanMaster.objects.values('product_id').distinct().count()
products_with_cc = CustomerChallanMaster.objects.values('product_id').distinct().count()

print(f"\n3️⃣ Products with Transactions:")
print(f"   With Purchases: {products_with_purchases}")
print(f"   With Sales: {products_with_sales}")
print(f"   With Purchase Returns: {products_with_pr}")
print(f"   With Sales Returns: {products_with_sr}")
print(f"   With Supplier Challans: {products_with_sc}")
print(f"   With Customer Challans: {products_with_cc}")

# 4. Check if signals are working
print(f"\n4️⃣ Checking Signal Status:")
print(f"   Signals should auto-create cache entries on transactions")
print(f"   If cache = 8 but transactions exist for 50 products,")
print(f"   then signals are NOT working properly!")

# 5. Sample products without cache
products_without_cache = ProductMaster.objects.exclude(
    productid__in=ProductInventoryCache.objects.values('product_id')
)[:10]

print(f"\n5️⃣ Sample Products WITHOUT Cache (First 10):")
for p in products_without_cache:
    purchases = PurchaseMaster.objects.filter(productid=p.productid).count()
    sales = SalesMaster.objects.filter(productid=p.productid).count()
    print(f"   {p.product_name} (ID: {p.productid})")
    print(f"      Purchases: {purchases}, Sales: {sales}")

# 6. Products WITH cache
print(f"\n6️⃣ Products WITH Cache:")
for cache in ProductInventoryCache.objects.all():
    print(f"   {cache.product.product_name}: Stock={cache.total_stock}, Batches={cache.total_batches}")

print("\n" + "=" * 70)
print("DIAGNOSIS:")
print("=" * 70)
if product_cache < products_with_purchases:
    print("❌ PROBLEM: Signals are NOT creating cache automatically!")
    print("   Solution: Run 'python rebuild_cache.py' to populate all cache")
else:
    print("✅ Cache is working correctly")
print("=" * 70)
