import os
import django
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.db.models import Sum, Count, Q
from core.models import (
    ProductMaster, ProductInventoryCache, BatchInventoryCache,
    PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster,
    SupplierChallanMaster, CustomerChallanMaster
)

print("🚀 FAST Cache Rebuild - Bulk Processing")
print("=" * 60)

# Clear old cache
print("🗑️  Clearing old cache...")
ProductInventoryCache.objects.all().delete()
BatchInventoryCache.objects.all().delete()

# Get all unique batches in ONE query
print("📊 Collecting batch data...")
batches_data = {}

# Purchases
for p in PurchaseMaster.objects.values('productid', 'product_batch_no', 'product_expiry', 'product_MRP', 'product_purchase_rate', 'rate_a', 'rate_b', 'rate_c').distinct():
    key = (p['productid'], p['product_batch_no'], p['product_expiry'])
    if key not in batches_data:
        batches_data[key] = {'mrp': p['product_MRP'], 'rate': p['product_purchase_rate'], 'a': p['rate_a'], 'b': p['rate_b'], 'c': p['rate_c']}

# Supplier Challans
for c in SupplierChallanMaster.objects.values('product_id', 'product_batch_no', 'product_expiry', 'product_mrp', 'product_purchase_rate', 'rate_a', 'rate_b', 'rate_c').distinct():
    key = (c['product_id'], c['product_batch_no'], c['product_expiry'])
    if key not in batches_data:
        batches_data[key] = {'mrp': c['product_mrp'], 'rate': c['product_purchase_rate'], 'a': c['rate_a'], 'b': c['rate_b'], 'c': c['rate_c']}

print(f"✅ Found {len(batches_data)} unique batches")

# Calculate stock for each batch
print("💾 Creating batch cache entries...")
batch_caches = []
for (pid, batch, expiry), info in batches_data.items():
    # Calculate stock
    purchased = PurchaseMaster.objects.filter(productid=pid, product_batch_no=batch, product_expiry=expiry).aggregate(s=Sum('product_quantity'))['s'] or 0
    sc = SupplierChallanMaster.objects.filter(product_id=pid, product_batch_no=batch, product_expiry=expiry).aggregate(s=Sum('product_quantity'))['s'] or 0
    sr = ReturnSalesMaster.objects.filter(return_productid=pid, return_product_batch_no=batch, return_product_expiry=expiry).aggregate(s=Sum('return_sale_quantity'))['s'] or 0
    
    sold = SalesMaster.objects.filter(productid=pid, product_batch_no=batch, product_expiry=expiry).aggregate(s=Sum('sale_quantity'))['s'] or 0
    cc = CustomerChallanMaster.objects.filter(product_id=pid, product_batch_no=batch, product_expiry=expiry).aggregate(s=Sum('sale_quantity'))['s'] or 0
    pr = ReturnPurchaseMaster.objects.filter(returnproductid=pid, returnproduct_batch_no=batch).aggregate(s=Sum('returnproduct_quantity'))['s'] or 0
    
    stock = (purchased + sc + sr) - (sold + cc + pr)
    
    if stock > 0:
        batch_caches.append(BatchInventoryCache(
            product_id=pid,
            batch_no=batch,
            expiry_date=expiry,
            current_stock=stock,
            mrp=info['mrp'],
            purchase_rate=info['rate'],
            rate_a=info['a'],
            rate_b=info['b'],
            rate_c=info['c'],
            is_expired=False,
            expiry_status='valid'
        ))

# Bulk create batches
with transaction.atomic():
    BatchInventoryCache.objects.bulk_create(batch_caches, batch_size=1000)
print(f"✅ Created {len(batch_caches)} batch cache entries")

# Create product cache
print("📦 Creating product cache entries...")
product_caches = []
for pid in set(b.product_id for b in batch_caches):
    batches = [b for b in batch_caches if b.product_id == pid]
    total_stock = sum(b.current_stock for b in batches)
    total_value = sum(b.current_stock * b.mrp for b in batches)
    
    product_caches.append(ProductInventoryCache(
        product_id=pid,
        total_stock=total_stock,
        total_batches=len(batches),
        avg_mrp=sum(b.mrp for b in batches) / len(batches),
        avg_purchase_rate=sum(b.purchase_rate for b in batches) / len(batches),
        total_stock_value=total_value,
        stock_status='in_stock' if total_stock > 10 else 'low_stock' if total_stock > 0 else 'out_of_stock',
        has_expired_batches=False
    ))

with transaction.atomic():
    ProductInventoryCache.objects.bulk_create(product_caches, batch_size=1000)
print(f"✅ Created {len(product_caches)} product cache entries")

print("=" * 60)
print("✅ DONE! Cache rebuilt successfully!")
