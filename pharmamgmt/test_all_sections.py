import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import *
from decimal import Decimal
from datetime import datetime, timedelta
import random
import time

class TestDataGenerator:
    def __init__(self):
        self.suppliers = []
        self.customers = []
        self.products = []
        
    def setup_base_data(self):
        """Create base suppliers, customers, and products"""
        print("Setting up base data...")
        
        # Create 50 suppliers
        for i in range(50):
            supplier, _ = SupplierMaster.objects.get_or_create(
                supplier_name=f"Supplier_{i+1}",
                defaults={
                    'supplier_address': f"Address {i+1}",
                    'supplier_mobile': f"98765{i+1:05d}",
                    'supplier_gstno': f"GST{i+1:010d}"
                }
            )
            self.suppliers.append(supplier)
        
        # Create 100 customers
        for i in range(100):
            customer, _ = CustomerMaster.objects.get_or_create(
                customer_name=f"Customer_{i+1}",
                defaults={
                    'customer_address': f"Address {i+1}",
                    'customer_mobile': f"87654{i+1:05d}",
                    'customer_gstno': f"CUST{i+1:010d}"
                }
            )
            self.customers.append(customer)
        
        # Create 200 products
        for i in range(200):
            product, _ = ProductMaster.objects.get_or_create(
                product_name=f"Product_{i+1}",
                defaults={
                    'product_company': f"Company_{i%20}",
                    'product_packing': f"{random.choice([10, 20, 50, 100])}",
                    'product_hsn': f"HSN{i+1:06d}"
                }
            )
            self.products.append(product)
        
        print(f"✓ Created {len(self.suppliers)} suppliers, {len(self.customers)} customers, {len(self.products)} products")
    
    def test_purchases(self, count=25000):
        """Test 1: Purchase Invoices"""
        print(f"\n{'='*60}")
        print(f"TEST 1: PURCHASE INVOICES ({count} records)")
        print(f"{'='*60}")
        start_time = time.time()
        
        last_invoice = InvoiceMaster.objects.filter(invoice_no__startswith='PI').order_by('-invoice_no').first()
        start_num = int(last_invoice.invoice_no[2:]) + 1 if last_invoice else 1
        
        batch_size = 1000
        for i in range(0, count, batch_size):
            for j in range(min(batch_size, count - i)):
                supplier = random.choice(self.suppliers)
                product = random.choice(self.products)
                
                invoice_no = f"PI{start_num + i + j:06d}"
                invoice_date = datetime.now() - timedelta(days=random.randint(1, 365))
                
                invoice = InvoiceMaster.objects.create(
                    invoice_no=invoice_no,
                    invoice_date=invoice_date,
                    supplierid=supplier,
                    invoice_total=Decimal('0'),
                    transport_charges=Decimal('0')
                )
                
                qty = random.randint(10, 100)
                rate = Decimal(str(random.uniform(50, 500)))
                total = qty * rate
                
                PurchaseMaster.objects.create(
                    product_invoiceid=invoice,
                    product_supplierid=supplier,
                    productid=product,
                    product_invoice_no=invoice_no,
                    product_packing=product.product_packing,
                    product_MRP=Decimal(str(random.uniform(100, 1000))),
                    product_name=product.product_name,
                    product_company=product.product_company,
                    product_batch_no=f"B{random.randint(100, 999)}",
                    product_expiry=f"{random.randint(1,12):02d}/{random.randint(2025,2027)}",
                    product_quantity=qty,
                    product_purchase_rate=rate,
                    product_discount_got=Decimal('0'),
                    CGST=Decimal('6'),
                    SGST=Decimal('6'),
                    total_amount=total
                )
                
                invoice.invoice_total = total
                invoice.save()
            
            print(f"Progress: {i + batch_size}/{count} purchases created...")
        
        elapsed = time.time() - start_time
        print(f"✓ TEST 1 PASSED: {count} purchases in {elapsed:.2f}s ({count/elapsed:.0f} records/sec)")
        return True
    
    def test_sales(self, count=25000):
        """Test 2: Sales Invoices"""
        print(f"\n{'='*60}")
        print(f"TEST 2: SALES INVOICES ({count} records)")
        print(f"{'='*60}")
        start_time = time.time()
        
        last_invoice = SalesInvoice.objects.filter(invoice_no__startswith='SI').order_by('-invoice_no').first()
        start_num = int(last_invoice.invoice_no[2:]) + 1 if last_invoice else 1
        
        batch_size = 1000
        for i in range(0, count, batch_size):
            for j in range(min(batch_size, count - i)):
                customer = random.choice(self.customers)
                product = random.choice(self.products)
                
                invoice_no = f"SI{start_num + i + j:06d}"
                invoice_date = datetime.now() - timedelta(days=random.randint(1, 180))
                
                invoice = SalesInvoice.objects.create(
                    invoice_no=invoice_no,
                    invoice_date=invoice_date,
                    customer=customer,
                    total_amount=Decimal('0')
                )
                
                qty = random.randint(1, 50)
                rate = Decimal(str(random.uniform(100, 1000)))
                total = qty * rate
                
                Sale.objects.create(
                    sales_invoice=invoice,
                    customer=customer,
                    product=product,
                    invoice_no=invoice_no,
                    batch_no=f"B{random.randint(100, 999)}",
                    expiry_date=f"{random.randint(1,12):02d}/{random.randint(2025,2027)}",
                    quantity=qty,
                    rate=rate,
                    discount_percentage=Decimal('0'),
                    cgst=Decimal('6'),
                    sgst=Decimal('6'),
                    total_amount=total
                )
                
                invoice.total_amount = total
                invoice.save()
            
            print(f"Progress: {i + batch_size}/{count} sales created...")
        
        elapsed = time.time() - start_time
        print(f"✓ TEST 2 PASSED: {count} sales in {elapsed:.2f}s ({count/elapsed:.0f} records/sec)")
        return True
    
    def test_inventory(self, count=25000):
        """Test 3: Inventory Records"""
        print(f"\n{'='*60}")
        print(f"TEST 3: INVENTORY ({count} records)")
        print(f"{'='*60}")
        start_time = time.time()
        
        batch_size = 1000
        for i in range(0, count, batch_size):
            inventories = []
            for j in range(min(batch_size, count - i)):
                product = random.choice(self.products)
                
                inventories.append(Inventory(
                    product=product,
                    batch_no=f"INV{i+j+1:06d}",
                    expiry_date=f"{random.randint(1,12):02d}/{random.randint(2025,2027)}",
                    quantity=random.randint(10, 500),
                    purchase_rate=Decimal(str(random.uniform(50, 500))),
                    mrp=Decimal(str(random.uniform(100, 1000)))
                ))
            
            Inventory.objects.bulk_create(inventories, ignore_conflicts=True)
            print(f"Progress: {i + batch_size}/{count} inventory records created...")
        
        elapsed = time.time() - start_time
        print(f"✓ TEST 3 PASSED: {count} inventory in {elapsed:.2f}s ({count/elapsed:.0f} records/sec)")
        return True
    
    def test_payments(self, count=25000):
        """Test 4: Payments"""
        print(f"\n{'='*60}")
        print(f"TEST 4: PAYMENTS ({count} records)")
        print(f"{'='*60}")
        start_time = time.time()
        
        invoices = list(InvoiceMaster.objects.all()[:5000])
        if not invoices:
            print("⚠ Skipping: No purchase invoices found")
            return False
        
        batch_size = 1000
        for i in range(0, count, batch_size):
            payments = []
            for j in range(min(batch_size, count - i)):
                invoice = random.choice(invoices)
                
                payments.append(Payment(
                    invoice=invoice,
                    supplier=invoice.supplierid,
                    payment_date=datetime.now() - timedelta(days=random.randint(1, 180)),
                    amount=Decimal(str(random.uniform(1000, 50000))),
                    payment_mode=random.choice(['cash', 'cheque', 'bank', 'upi']),
                    reference_no=f"REF{i+j+1:08d}"
                ))
            
            Payment.objects.bulk_create(payments)
            print(f"Progress: {i + batch_size}/{count} payments created...")
        
        elapsed = time.time() - start_time
        print(f"✓ TEST 4 PASSED: {count} payments in {elapsed:.2f}s ({count/elapsed:.0f} records/sec)")
        return True
    
    def test_receipts(self, count=25000):
        """Test 5: Receipts"""
        print(f"\n{'='*60}")
        print(f"TEST 5: RECEIPTS ({count} records)")
        print(f"{'='*60}")
        start_time = time.time()
        
        sales_invoices = list(SalesInvoice.objects.all()[:5000])
        if not sales_invoices:
            print("⚠ Skipping: No sales invoices found")
            return False
        
        batch_size = 1000
        for i in range(0, count, batch_size):
            receipts = []
            for j in range(min(batch_size, count - i)):
                invoice = random.choice(sales_invoices)
                
                receipts.append(Receipt(
                    sales_invoice=invoice,
                    customer=invoice.customer,
                    receipt_date=datetime.now() - timedelta(days=random.randint(1, 180)),
                    amount=Decimal(str(random.uniform(1000, 50000))),
                    payment_mode=random.choice(['cash', 'cheque', 'bank', 'upi']),
                    reference_no=f"REC{i+j+1:08d}"
                ))
            
            Receipt.objects.bulk_create(receipts)
            print(f"Progress: {i + batch_size}/{count} receipts created...")
        
        elapsed = time.time() - start_time
        print(f"✓ TEST 5 PASSED: {count} receipts in {elapsed:.2f}s ({count/elapsed:.0f} records/sec)")
        return True
    
    def test_contra(self, count=25000):
        """Test 6: Contra Entries"""
        print(f"\n{'='*60}")
        print(f"TEST 6: CONTRA ENTRIES ({count} records)")
        print(f"{'='*60}")
        start_time = time.time()
        
        batch_size = 1000
        for i in range(0, count, batch_size):
            contras = []
            for j in range(min(batch_size, count - i)):
                contra_type = random.choice(['BANK_TO_CASH', 'CASH_TO_BANK'])
                
                contras.append(ContraEntry(
                    contra_date=datetime.now() - timedelta(days=random.randint(1, 365)),
                    contra_type=contra_type,
                    amount=Decimal(str(random.uniform(1000, 100000))),
                    from_account='Bank ABC' if contra_type == 'BANK_TO_CASH' else 'Cash',
                    to_account='Cash' if contra_type == 'BANK_TO_CASH' else 'Bank XYZ',
                    reference_no=f"CONTRA{i+j+1:08d}",
                    narration=f"Test contra entry {i+j+1}"
                ))
            
            ContraEntry.objects.bulk_create(contras)
            print(f"Progress: {i + batch_size}/{count} contra entries created...")
        
        elapsed = time.time() - start_time
        print(f"✓ TEST 6 PASSED: {count} contra entries in {elapsed:.2f}s ({count/elapsed:.0f} records/sec)")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("PHARMA MANAGEMENT SYSTEM - SCALABILITY TEST")
        print("Testing 25,000 records per section")
        print("="*60)
        
        total_start = time.time()
        results = []
        
        # Setup
        self.setup_base_data()
        
        # Run tests
        results.append(("Purchases", self.test_purchases(25000)))
        results.append(("Sales", self.test_sales(25000)))
        results.append(("Inventory", self.test_inventory(25000)))
        results.append(("Payments", self.test_payments(25000)))
        results.append(("Receipts", self.test_receipts(25000)))
        results.append(("Contra", self.test_contra(25000)))
        
        # Summary
        total_elapsed = time.time() - total_start
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for test_name, passed in results:
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{test_name:20s}: {status}")
        
        total_records = sum([1 for _, passed in results if passed]) * 25000
        print(f"\nTotal Records Created: {total_records:,}")
        print(f"Total Time: {total_elapsed:.2f}s")
        print(f"Average Speed: {total_records/total_elapsed:.0f} records/sec")
        print("="*60)

if __name__ == '__main__':
    generator = TestDataGenerator()
    generator.run_all_tests()
