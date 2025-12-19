"""
Test Sales Return and Inventory Display
Run: python manage.py shell < test_sales_return_inventory.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebsiteHostingService.settings')
django.setup()

from core.models import (
    ProductMaster, ProductInventoryCache, BatchInventoryCache,
    ReturnSalesMaster, SalesMaster, PurchaseMaster
)

print("=" * 80)
print("SALES RETURN & INVENTORY TEST")
print("=" * 80)

# Test Product ID 2 (1ST AID TRANSPORE TAPE)
product_id = 2
batch_no = "1234"

print(f"\n📦 Testing Product ID: {product_id}")
print(f"📦 Batch: {batch_no}")

# 1. Check Product Details
try:
    product = ProductMaster.objects.get(productid=product_id)
    print(f"\n✅ Product Found: {product.product_name}")
except ProductMaster.DoesNotExist:
    print(f"\n❌ Product {product_id} not found!")
    sys.exit(1)

# 2. Check Database Transactions
print("\n" + "=" * 80)
print("DATABASE TRANSACTIONS:")
print("=" * 80)

purchases = PurchaseMaster.objects.filter(
    productid=product_id,
    product_batch_no=batch_no
).aggregate(total=Sum('product_quantity'))['total'] or 0

sales = SalesMaster.objects.filter(
    productid=product_id,
    product_batch_no=batch_no
).aggregate(total=Sum('sale_quantity'))['total'] or 0

sales_returns = ReturnSalesMaster.objects.filter(
    return_productid=product_id,
    return_product_batch_no=batch_no
).aggregate(total=Sum('return_sale_quantity'))['total'] or 0

calculated_stock = purchases - sales + sales_returns

print(f"  Purchases: {purchases}")
print(f"  Sales: {sales}")
print(f"  Sales Returns: {sales_returns}")
print(f"  Calculated Stock: {calculated_stock}")

# 3. Check Batch Cache
print("\n" + "=" * 80)
print("BATCH CACHE:")
print("=" * 80)

try:
    batch_cache = BatchInventoryCache.objects.get(
        product_id=product_id,
        batch_no=batch_no
    )
    print(f"  ✅ Batch Cache Found")
    print(f"  Current Stock: {batch_cache.current_stock}")
    print(f"  MRP: ₹{batch_cache.mrp}")
    print(f"  Rate A: ₹{batch_cache.rate_a}")
    print(f"  Rate B: ₹{batch_cache.rate_b}")
    print(f"  Rate C: ₹{batch_cache.rate_c}")
    print(f"  Expiry: {batch_cache.expiry_date}")
except BatchInventoryCache.DoesNotExist:
    print(f"  ❌ Batch Cache NOT FOUND!")
    batch_cache = None

# 4. Check Product Cache
print("\n" + "=" * 80)
print("PRODUCT CACHE:")
print("=" * 80)

try:
    product_cache = ProductInventoryCache.objects.get(product_id=product_id)
    print(f"  ✅ Product Cache Found")
    print(f"  Total Stock: {product_cache.total_stock}")
    print(f"  Total Batches: {product_cache.total_batches}")
    print(f"  Stock Value: ₹{product_cache.total_stock_value}")
    print(f"  Status: {product_cache.stock_status}")
except ProductInventoryCache.DoesNotExist:
    print(f"  ❌ Product Cache NOT FOUND!")
    product_cache = None

# 5. Simulate Inventory List View Query
print("\n" + "=" * 80)
print("INVENTORY LIST VIEW QUERY (What UI Shows):")
print("=" * 80)

if product_cache:
    print(f"  Product: {product.product_name}")
    print(f"  Current Stock: {product_cache.total_stock}")
    print(f"  Stock Value: ₹{product_cache.total_stock_value}")
    print(f"  Status: {product_cache.stock_status}")
    
    # Get batches
    batch_caches = BatchInventoryCache.objects.filter(
        product_id=product_id,
        current_stock__gt=0
    )
    
    print(f"\n  Batches ({batch_caches.count()}):")
    for bc in batch_caches:
        print(f"    - {bc.batch_no} ({bc.current_stock} units)")
        print(f"      Exp: {bc.expiry_date}, MRP: ₹{bc.mrp}")
else:
    print("  ❌ No cache data - UI will show 0 stock")

# 6. Comparison
print("\n" + "=" * 80)
print("COMPARISON:")
print("=" * 80)

if batch_cache and product_cache:
    if batch_cache.current_stock == calculated_stock:
        print(f"  ✅ Cache matches calculation: {batch_cache.current_stock} = {calculated_stock}")
    else:
        print(f"  ❌ MISMATCH!")
        print(f"     Cache: {batch_cache.current_stock}")
        print(f"     Calculated: {calculated_stock}")
        print(f"     Difference: {abs(batch_cache.current_stock - calculated_stock)}")
else:
    print(f"  ❌ Cache missing - needs rebuild")

# 7. Recent Sales Returns
print("\n" + "=" * 80)
print("RECENT SALES RETURNS:")
print("=" * 80)

recent_returns = ReturnSalesMaster.objects.filter(
    return_productid=product_id,
    return_product_batch_no=batch_no
).order_by('-return_sales_invoiceid')[:5]

if recent_returns.exists():
    for ret in recent_returns:
        print(f"  Return ID: {ret.return_sales_invoiceid}")
        print(f"  Quantity: {ret.return_sale_quantity}")
        print(f"  Date: {ret.return_sale_entry_date}")
        print()
else:
    print("  No sales returns found")

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

# Summary
print("\n📊 SUMMARY:")
if batch_cache and product_cache and batch_cache.current_stock == calculated_stock:
    print("  ✅ Everything is working correctly!")
    print("  ✅ Cache is up to date")
    print("  ✅ UI should show correct stock")
    print("\n  If UI still shows wrong value:")
    print("     1. Hard refresh browser (Ctrl+Shift+R)")
    print("     2. Clear browser cache")
    print("     3. Check browser console for errors")
else:
    print("  ❌ Issues found!")
    if not batch_cache:
        print("     - Batch cache missing")
    if not product_cache:
        print("     - Product cache missing")
    if batch_cache and batch_cache.current_stock != calculated_stock:
        print(f"     - Cache mismatch: {batch_cache.current_stock} vs {calculated_stock}")
    print("\n  Run: python manage.py fix_sales_return_cache")
