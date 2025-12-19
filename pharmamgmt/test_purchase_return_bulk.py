import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import *
from decimal import Decimal
from datetime import datetime, timedelta
import random

def generate_purchase_returns(count=25000):
    print(f"Starting purchase return generation for {count} records...")
    
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
            
            return_no = f"PR{i+j+1:06d}"
            return_date = datetime.now() - timedelta(days=random.randint(1, 180))
            
            # Create return invoice
            return_invoice = ReturnInvoiceMaster.objects.create(
                returninvoiceid=return_no,
                returninvoice_date=return_date,
                returnsupplierid=supplier,
                returninvoice_total=Decimal('0'),
                return_charges=Decimal('0')
            )
            
            # Create return item
            qty = random.randint(5, 30)
            rate = Decimal(str(random.uniform(50, 500)))
            cgst = Decimal('6')
            sgst = Decimal('6')
            
            amount = qty * rate
            cgst_amt = amount * cgst / 100
            sgst_amt = amount * sgst / 100
            total = amount + cgst_amt + sgst_amt
            
            expiry_date = datetime(random.randint(2025, 2027), random.randint(1, 12), 1).date()
            
            ReturnPurchaseMaster.objects.create(
                returninvoiceid=return_invoice,
                returnproduct_supplierid=supplier,
                returnproductid=product,
                returnproduct_batch_no=f"B{random.randint(1000, 9999)}",
                returnproduct_expiry=expiry_date,
                returnproduct_MRP=Decimal(str(random.uniform(100, 1000))),
                returnproduct_quantity=qty,
                returnproduct_purchase_rate=rate,
                returnproduct_cgst=cgst,
                returnproduct_sgst=sgst,
                returntotal_amount=total,
                return_reason='Damaged'
            )
            
            return_invoice.returninvoice_total = total
            return_invoice.save()
        
        print(f"Created {i + batch_size}/{count} purchase returns...")
    
    print(f"✓ Successfully created {count} purchase return records!")

if __name__ == '__main__':
    generate_purchase_returns(25000)
