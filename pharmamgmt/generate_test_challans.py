import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import SupplierMaster, ProductMaster, Challan1, SupplierChallanMaster
from datetime import datetime, timedelta
import random
from django.db import transaction

def generate_test_challans(count=100000):
    """Generate bulk test supplier challans"""
    
    print(f"🚀 Generating {count} test supplier challans...")
    
    suppliers = list(SupplierMaster.objects.all())
    products = list(ProductMaster.objects.all())
    
    if not suppliers or not products:
        print("❌ Need suppliers and products!")
        return
    
    print(f"✅ Using {len(suppliers)} suppliers, {len(products)} products")
    
    start_date = datetime.now() - timedelta(days=730)
    batch_size = 1000
    items_created = 0
    challans_created = 0
    
    for batch_num in range(0, count, batch_size):
        challans_batch = []
        
        batch_end = min(batch_num + batch_size, count)
        
        for i in range(batch_num, batch_end):
            supplier = random.choice(suppliers)
            challan_date = start_date + timedelta(days=random.randint(0, 730))
            challan_no = f"CH{challan_date.strftime('%Y%m%d')}{i:06d}"
            
            challans_batch.append(Challan1(
                challan_no=challan_no,
                challan_date=challan_date.date(),
                supplier=supplier,
                challan_total=0,
                transport_charges=random.uniform(0, 200),
                challan_paid=0,
                is_invoiced=random.choice([True, False])
            ))
        
        # Bulk create challans
        Challan1.objects.bulk_create(challans_batch, ignore_conflicts=True)
        
        # Retrieve saved challans by challan_no
        challan_nos = [c.challan_no for c in challans_batch]
        saved_challans = Challan1.objects.filter(challan_no__in=challan_nos)
        
        # Create items for saved challans
        items_batch = []
        for challan in saved_challans:
            num_items = random.randint(2, 5)
            total = 0
            
            for _ in range(num_items):
                product = random.choice(products)
                qty = random.randint(10, 100)
                rate = random.uniform(50, 1000)
                mrp = rate * random.uniform(1.2, 1.5)
                discount = random.uniform(0, 50)
                actual_rate = rate - discount
                item_total = qty * actual_rate
                total += item_total
                
                items_batch.append(SupplierChallanMaster(
                    product_suppliername=challan.supplier,
                    product_challan_id=challan,
                    product_challan_no=challan.challan_no,
                    product_id=product,
                    product_name=product.product_name,
                    product_company=product.product_company,
                    product_packing=product.product_packing,
                    product_batch_no=f"B{random.randint(1000, 9999)}",
                    product_expiry=f"{random.randint(1, 12):02d}-{random.randint(2025, 2028)}",
                    product_mrp=mrp,
                    product_purchase_rate=rate,
                    product_quantity=qty,
                    product_discount=discount,
                    actual_rate_per_qty=actual_rate,
                    product_actual_rate=actual_rate,
                    total_amount=item_total,
                    cgst=2.5,
                    sgst=2.5
                ))
                items_created += 1
            
            challan.challan_total = total
        
        # Bulk create items
        SupplierChallanMaster.objects.bulk_create(items_batch, batch_size=5000)
        
        # Update challan totals
        Challan1.objects.bulk_update(list(saved_challans), ['challan_total'])
        
        challans_created += len(saved_challans)
        print(f"✅ Progress: {batch_end}/{count} challans created...")
    
    print(f"\n🎉 DONE! Created {count} test challans")

if __name__ == '__main__':
    import time
    start = time.time()
    generate_test_challans(100000)
    print(f"⏱️ Time taken: {time.time() - start:.2f} seconds")
