import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import CustomerMaster, ProductMaster, CustomerChallan, CustomerChallanMaster
from datetime import datetime, timedelta
import random
from django.db import transaction

def generate_test_customer_challans(count=100000):
    """Generate bulk test customer challans"""
    
    print(f"🚀 Generating {count} test customer challans...")
    
    customers = list(CustomerMaster.objects.all())
    products = list(ProductMaster.objects.all())
    
    if not customers or not products:
        print("❌ Need customers and products!")
        return
    
    print(f"✅ Using {len(customers)} customers, {len(products)} products")
    
    start_date = datetime.now() - timedelta(days=730)
    batch_size = 1000
    items_created = 0
    challans_created = 0
    
    for batch_num in range(0, count, batch_size):
        challans_batch = []
        
        batch_end = min(batch_num + batch_size, count)
        
        for i in range(batch_num, batch_end):
            customer = random.choice(customers)
            challan_date = start_date + timedelta(days=random.randint(0, 730))
            challan_no = f"SCH{challan_date.strftime('%Y%m%d')}{i:06d}"
            
            challans_batch.append(CustomerChallan(
                customer_challan_no=challan_no,
                customer_challan_date=challan_date.date(),
                customer_name=customer,
                challan_total=0,
                customer_transport_charges=random.uniform(0, 200),
                challan_invoice_paid=0,
                is_invoiced=random.choice([True, False])
            ))
        
        # Bulk create challans
        CustomerChallan.objects.bulk_create(challans_batch, ignore_conflicts=True)
        
        # Retrieve saved challans by challan_no
        challan_nos = [c.customer_challan_no for c in challans_batch]
        saved_challans = CustomerChallan.objects.filter(customer_challan_no__in=challan_nos)
        
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
                
                items_batch.append(CustomerChallanMaster(
                    customer_name=challan.customer_name,
                    customer_challan_id=challan,
                    customer_challan_no=challan.customer_challan_no,
                    product_id=product,
                    product_name=product.product_name,
                    product_company=product.product_company,
                    product_packing=product.product_packing,
                    product_batch_no=f"B{random.randint(1000, 9999)}",
                    product_expiry=f"{random.randint(1, 12):02d}-{random.randint(2025, 2028)}",
                    product_mrp=mrp,
                    sale_rate=rate,
                    sale_quantity=qty,
                    sale_discount=discount,
                    sale_total_amount=item_total,
                    sale_cgst=2.5,
                    sale_sgst=2.5,
                    rate_applied='A'
                ))
                items_created += 1
            
            challan.challan_total = total
        
        # Bulk create items
        CustomerChallanMaster.objects.bulk_create(items_batch, batch_size=5000)
        
        # Update challan totals
        CustomerChallan.objects.bulk_update(list(saved_challans), ['challan_total'])
        
        challans_created += len(saved_challans)
        print(f"✅ Progress: {batch_end}/{count} challans created...")
    
    print(f"\n🎉 DONE! Created {count} test customer challans")

if __name__ == '__main__':
    import time
    start = time.time()
    generate_test_customer_challans(100000)
    print(f"⏱️ Time taken: {time.time() - start:.2f} seconds")
