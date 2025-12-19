import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import *
from decimal import Decimal
from datetime import datetime, timedelta
import random
import time

def create_base_data():
    """Create suppliers, customers, products"""
    print("Creating base data...")
    
    suppliers = []
    for i in range(50):
        s, _ = SupplierMaster.objects.get_or_create(
            supplier_name=f"TestSupplier_{i+1}",
            defaults={
                'supplier_mobile': f"98765{i+1:05d}",
                'supplier_gstno': f"GST{i+1:010d}"
            }
        )
        suppliers.append(s)
    
    customers = []
    for i in range(100):
        c, _ = CustomerMaster.objects.get_or_create(
            customer_name=f"TestCustomer_{i+1}",
            defaults={
                'customer_mobile': f"87654{i+1:05d}",
                'customer_gstno': f"CUST{i+1:010d}"
            }
        )
        customers.append(c)
    
    products = []
    for i in range(200):
        p, _ = ProductMaster.objects.get_or_create(
            product_name=f"TestProduct_{i+1}",
            defaults={
                'product_company': f"Company_{i%20}",
                'product_packing': "10",
                'product_salt': f"Salt_{i%50}",
                'product_category': "General",
                'product_hsn': "3004",
                'product_hsn_percent': "12"
            }
        )
        products.append(p)
    
    print(f"[OK] Created {len(suppliers)} suppliers, {len(customers)} customers, {len(products)} products")
    return suppliers, customers, products

def test_purchases(suppliers, products, count=25000):
    """Test Purchase Invoices"""
    print(f"\n{'='*60}")
    print(f"TEST 1: PURCHASES ({count} records)")
    print(f"{'='*60}")
    start = time.time()
    
    last = InvoiceMaster.objects.all().order_by('-invoiceid').first()
    num = last.invoiceid + 1 if last else 1
    
    for i in range(count):
        supplier = random.choice(suppliers)
        product = random.choice(products)
        
        inv_no = f"TPI{num+i:08d}"
        inv = InvoiceMaster.objects.create(
            invoice_no=inv_no,
            invoice_date=datetime.now() - timedelta(days=random.randint(1,365)),
            supplierid=supplier,
            invoice_total=0,
            transport_charges=0
        )
        
        qty = random.randint(10,100)
        rate = random.uniform(50,500)
        total = qty * rate
        
        PurchaseMaster.objects.create(
            product_invoiceid=inv,
            product_supplierid=supplier,
            productid=product,
            product_invoice_no=inv_no,
            product_name=product.product_name,
            product_company=product.product_company,
            product_packing=product.product_packing,
            product_batch_no=f"B{random.randint(10,999)}",
            product_expiry=f"{random.randint(1,12):02d}/{random.randint(25,27)}",
            product_MRP=random.uniform(100,1000),
            product_purchase_rate=rate,
            product_quantity=qty,
            product_discount_got=0,
            product_transportation_charges=0,
            CGST=6,
            SGST=6,
            total_amount=total
        )
        
        inv.invoice_total = total
        inv.save()
        
        if (i+1) % 1000 == 0:
            print(f"Progress: {i+1}/{count}")
    
    elapsed = time.time() - start
    print(f"[PASSED] {count} purchases in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def test_sales(customers, products, count=25000):
    """Test Sales Invoices"""
    print(f"\n{'='*60}")
    print(f"TEST 2: SALES ({count} records)")
    print(f"{'='*60}")
    start = time.time()
    
    import uuid
    timestamp = int(time.time())
    
    for i in range(count):
        customer = random.choice(customers)
        product = random.choice(products)
        
        inv_no = f"TSI{timestamp}{i:04d}"
        inv = SalesInvoiceMaster.objects.create(
            sales_invoice_no=inv_no,
            sales_invoice_date=datetime.now() - timedelta(days=random.randint(1,180)),
            customerid=customer
        )
        
        qty = random.randint(1,50)
        rate = random.uniform(100,1000)
        total = qty * rate
        
        SalesMaster.objects.create(
            sales_invoice_no=inv,
            customerid=customer,
            productid=product,
            product_name=product.product_name,
            product_company=product.product_company,
            product_packing=product.product_packing,
            product_batch_no=f"B{random.randint(10,999)}",
            product_expiry=f"{random.randint(1,12):02d}/{random.randint(25,27)}",
            product_MRP=random.uniform(100,1000),
            sale_rate=rate,
            sale_quantity=qty,
            sale_discount=0,
            sale_cgst=6,
            sale_sgst=6,
            sale_total_amount=total
        )
        
        if (i+1) % 1000 == 0:
            print(f"Progress: {i+1}/{count}")
    
    elapsed = time.time() - start
    print(f"[PASSED] {count} sales in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def test_payments(count=25000):
    """Test Payments"""
    print(f"\n{'='*60}")
    print(f"TEST 3: PAYMENTS ({count} records)")
    print(f"{'='*60}")
    start = time.time()
    
    invoices = list(InvoiceMaster.objects.all()[:5000])
    if not invoices:
        print("[WARN] Skipped: No invoices")
        return False
    
    for i in range(count):
        inv = random.choice(invoices)
        InvoicePaid.objects.create(
            ip_invoiceid=inv,
            payment_date=datetime.now() - timedelta(days=random.randint(1,180)),
            payment_amount=random.uniform(1000,50000),
            payment_mode=random.choice(['cash','cheque','bank','upi'])
        )
        
        if (i+1) % 1000 == 0:
            print(f"Progress: {i+1}/{count}")
    
    elapsed = time.time() - start
    print(f"[PASSED] {count} payments in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def test_receipts(count=25000):
    """Test Receipts"""
    print(f"\n{'='*60}")
    print(f"TEST 4: RECEIPTS ({count} records)")
    print(f"{'='*60}")
    start = time.time()
    
    invoices = list(SalesInvoiceMaster.objects.all()[:5000])
    if not invoices:
        print("[WARN] Skipped: No sales invoices")
        return False
    
    for i in range(count):
        inv = random.choice(invoices)
        SalesInvoicePaid.objects.create(
            sales_ip_invoice_no=inv,
            sales_payment_date=datetime.now() - timedelta(days=random.randint(1,180)),
            sales_payment_amount=random.uniform(1000,50000),
            sales_payment_mode=random.choice(['cash','cheque','bank','upi'])
        )
        
        if (i+1) % 1000 == 0:
            print(f"Progress: {i+1}/{count}")
    
    elapsed = time.time() - start
    print(f"[PASSED] {count} receipts in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def test_contra(count=25000):
    """Test Contra Entries"""
    print(f"\n{'='*60}")
    print(f"TEST 5: CONTRA ({count} records)")
    print(f"{'='*60}")
    start = time.time()
    
    for i in range(count):
        contra_type = random.choice(['BANK_TO_CASH','CASH_TO_BANK'])
        ContraEntry.objects.create(
            contra_date=datetime.now() - timedelta(days=random.randint(1,365)),
            contra_type=contra_type,
            amount=random.uniform(1000,100000),
            from_account='Bank ABC' if contra_type == 'BANK_TO_CASH' else 'Cash',
            to_account='Cash' if contra_type == 'BANK_TO_CASH' else 'Bank XYZ'
        )
        
        if (i+1) % 1000 == 0:
            print(f"Progress: {i+1}/{count}")
    
    elapsed = time.time() - start
    print(f"[PASSED] {count} contra in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def run_full_test():
    print("\n" + "="*60)
    print("FULL TEST - 25,000 records per section")
    print("="*60)
    
    total_start = time.time()
    suppliers, customers, products = create_base_data()
    
    results = []
    results.append(("Purchases", test_purchases(suppliers, products, 25000)))
    results.append(("Sales", test_sales(customers, products, 25000)))
    results.append(("Payments", test_payments(25000)))
    results.append(("Receipts", test_receipts(25000)))
    results.append(("Contra", test_contra(25000)))
    
    total_time = time.time() - total_start
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, passed in results:
        print(f"{name:20s}: {'[PASSED]' if passed else '[FAILED]'}")
    
    total_records = sum([1 for _, p in results if p]) * 25000
    print(f"\nTotal Records: {total_records:,}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Speed: {total_records/total_time:.0f} records/sec")
    print("="*60)

def run_quick_test():
    print("\n" + "="*60)
    print("QUICK TEST - 1,000 records per section")
    print("="*60)
    
    suppliers, customers, products = create_base_data()
    
    test_purchases(suppliers, products, 1000)
    test_sales(customers, products, 1000)
    test_payments(1000)
    test_receipts(1000)
    test_contra(1000)
    
    print("\n[OK] Quick test completed!")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        run_quick_test()
    else:
        run_full_test()
