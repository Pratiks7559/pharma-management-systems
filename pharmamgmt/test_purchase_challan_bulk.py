import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import *
from decimal import Decimal
from datetime import datetime, timedelta
import random

def generate_purchase_challans(count=25000):
    print(f"Starting purchase challan generation for {count} records...")
    
    suppliers = list(SupplierMaster.objects.all()[:10])
    products = list(ProductMaster.objects.all()[:100])
    
    if not suppliers or not products:
        print("Error: Need suppliers and products first!")
        return
    
    batch_size = 1000
    for i in range(0, count, batch_size):
        for j in range(min(batch_size, count - i)):
            supplier = random.choice(suppliers)
            product = random.choice(products)
            
            challan_no = f"PC{i+j+1:06d}"
            challan_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            # Create challan
            challan = SupplierChallanMaster2.objects.create(
                challan_no=challan_no,
                challan_date=challan_date,
                supplier=supplier,
                challan_total=Decimal('0'),
                transaction_type='INWARD'
            )
            
            # Create challan item
            qty = random.randint(10, 100)
            rate = Decimal(str(random.uniform(50, 500)))
            
            total = qty * rate
            
            PurchaseMaster.objects.create(
                supplier_challan=challan,
                product_name=product.product_name,
                product_company=product.product_company,
                product_batch_no=f"B{random.randint(1000, 9999)}",
                product_expiry=f"{random.randint(1,12):02d}/{random.randint(2025,2027)}",
                product_quantity=qty,
                product_purchase_rate=rate,
                product_discount_got=Decimal('0'),
                purchase_calculation_mode='percentage',
                CGST=Decimal('6'),
                SGST=Decimal('6'),
                total_amount=total
            )
            
            challan.challan_total = total
            challan.save()
        
        print(f"Created {i + batch_size}/{count} purchase challans...")
    
    print(f"✓ Successfully created {count} purchase challan records!")

if __name__ == '__main__':
    generate_purchase_challans(25000)
