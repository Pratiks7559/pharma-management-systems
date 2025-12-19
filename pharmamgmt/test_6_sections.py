import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import *
from datetime import datetime, timedelta
import random
import time

def create_base_data():
    """Create base suppliers, customers, products"""
    print("Creating base data...")
    
    suppliers = []
    for i in range(50):
        s, _ = SupplierMaster.objects.get_or_create(
            supplier_name=f"TestSupp_{i+1}",
            defaults={'supplier_mobile': f"98{i+1:08d}"}
        )
        suppliers.append(s)
    
    customers = []
    for i in range(100):
        c, _ = CustomerMaster.objects.get_or_create(
            customer_name=f"TestCust_{i+1}",
            defaults={'customer_mobile': f"87{i+1:08d}"}
        )
        customers.append(c)
    
    products = []
    for i in range(200):
        p, _ = ProductMaster.objects.get_or_create(
            product_name=f"TestProd_{i+1}",
            defaults={
                'product_company': f"Co_{i%20}",
                'product_packing': "10",
                'product_salt': f"Salt_{i+1}",
                'product_category': "General",
                'product_hsn': f"HSN{i+1:06d}",
                'product_hsn_percent': "12"
            }
        )
        products.append(p)
    
    print(f"✓ Base data: {len(suppliers)} suppliers, {len(customers)} customers, {len(products)} products")
    return suppliers, customers, products

def test_purchases(suppliers, products, count):
    """Section 1: Purchase Invoices"""
    print(f"\n{'='*60}")
    print(f"SECTION 1: PURCHASES ({count:,} records)")
    print(f"{'='*60}")
    start = time.time()
    
    last = InvoiceMaster.objects.filter(invoice_no__startswith='TPI').order_by('-invoice_no').first()
    num = int(last.invoice_no[3:]) + 1 if last else 1
    
    for i in range(count):
        supplier = random.choice(suppliers)
        product = random.choice(products)
        
        inv_no = f"TPI{num+i:07d}"
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
            product_expiry=f"{random.randint(1,12):02d}/25",
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
            print(f"  Progress: {i+1:,}/{count:,}")
    
    elapsed = time.time() - start
    print(f"✓ COMPLETED: {count:,} purchases in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def test_sales(customers, products, count):
    """Section 2: Sales Invoices"""
    print(f"\n{'='*60}")
    print(f"SECTION 2: SALES ({count:,} records)")
    print(f"{'='*60}")
    start = time.time()
    
    last = SalesInvoiceMaster.objects.filter(sales_invoice_no__startswith='TSI').order_by('-sales_invoice_no').first()
    num = int(last.sales_invoice_no[3:]) + 1 if last else 1
    
    for i in range(count):
        customer = random.choice(customers)
        product = random.choice(products)
        
        inv_no = f"TSI{num+i:07d}"
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
            product_expiry=f"{random.randint(1,12):02d}/25",
            product_MRP=random.uniform(100,1000),
            sale_rate=rate,
            sale_quantity=qty,
            sale_discount=0,
            sale_cgst=6,
            sale_sgst=6,
            sale_total_amount=total
        )
        
        if (i+1) % 1000 == 0:
            print(f"  Progress: {i+1:,}/{count:,}")
    
    elapsed = time.time() - start
    print(f"✓ COMPLETED: {count:,} sales in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def test_purchase_returns(suppliers, products, count):
    """Section 3: Purchase Returns"""
    print(f"\n{'='*60}")
    print(f"SECTION 3: PURCHASE RETURNS ({count:,} records)")
    print(f"{'='*60}")
    start = time.time()
    
    last = ReturnInvoiceMaster.objects.filter(returninvoiceid__startswith='TPR').order_by('-returninvoiceid').first()
    num = int(last.returninvoiceid[3:]) + 1 if last else 1
    
    for i in range(count):
        supplier = random.choice(suppliers)
        product = random.choice(products)
        
        ret_no = f"TPR{num+i:07d}"
        ret_inv = ReturnInvoiceMaster.objects.create(
            returninvoiceid=ret_no,
            returninvoice_date=datetime.now() - timedelta(days=random.randint(1,180)),
            returnsupplierid=supplier,
            returninvoice_total=0,
            return_charges=0
        )
        
        qty = random.randint(1,20)
        rate = random.uniform(50,500)
        total = qty * rate
        
        ReturnPurchaseMaster.objects.create(
            returninvoiceid=ret_inv,
            returnproduct_supplierid=supplier,
            returnproductid=product,
            returnproduct_batch_no=f"B{random.randint(10,999)}",
            returnproduct_expiry=datetime.now() + timedelta(days=365),
            returnproduct_MRP=random.uniform(100,1000),
            returnproduct_purchase_rate=rate,
            returnproduct_quantity=qty,
            returnproduct_cgst=6,
            returnproduct_sgst=6,
            returntotal_amount=total
        )
        
        ret_inv.returninvoice_total = total
        ret_inv.save()
        
        if (i+1) % 1000 == 0:
            print(f"  Progress: {i+1:,}/{count:,}")
    
    elapsed = time.time() - start
    print(f"✓ COMPLETED: {count:,} purchase returns in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def test_sales_returns(customers, products, count):
    """Section 4: Sales Returns"""
    print(f"\n{'='*60}")
    print(f"SECTION 4: SALES RETURNS ({count:,} records)")
    print(f"{'='*60}")
    start = time.time()
    
    last = ReturnSalesInvoiceMaster.objects.filter(return_sales_invoice_no__startswith='TSR').order_by('-return_sales_invoice_no').first()
    num = int(last.return_sales_invoice_no[3:]) + 1 if last else 1
    
    for i in range(count):
        customer = random.choice(customers)
        product = random.choice(products)
        
        ret_no = f"TSR{num+i:07d}"
        ret_inv = ReturnSalesInvoiceMaster.objects.create(
            return_sales_invoice_no=ret_no,
            return_sales_invoice_date=datetime.now() - timedelta(days=random.randint(1,180)),
            return_sales_customerid=customer,
            return_sales_invoice_total=0,
            return_sales_charges=0,
            transport_charges=0
        )
        
        qty = random.randint(1,20)
        rate = random.uniform(100,1000)
        total = qty * rate
        
        ReturnSalesMaster.objects.create(
            return_sales_invoice_no=ret_inv,
            return_customerid=customer,
            return_productid=product,
            return_product_name=product.product_name,
            return_product_company=product.product_company,
            return_product_packing=product.product_packing,
            return_product_batch_no=f"B{random.randint(10,999)}",
            return_product_expiry=f"{random.randint(1,12):02d}/25",
            return_product_MRP=random.uniform(100,1000),
            return_sale_rate=rate,
            return_sale_quantity=qty,
            return_sale_discount=0,
            return_sale_cgst=6,
            return_sale_sgst=6,
            return_sale_total_amount=total
        )
        
        ret_inv.return_sales_invoice_total = total
        ret_inv.save()
        
        if (i+1) % 1000 == 0:
            print(f"  Progress: {i+1:,}/{count:,}")
    
    elapsed = time.time() - start
    print(f"✓ COMPLETED: {count:,} sales returns in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def test_supplier_challans(suppliers, products, count):
    """Section 5: Supplier Challans"""
    print(f"\n{'='*60}")
    print(f"SECTION 5: SUPPLIER CHALLANS ({count:,} records)")
    print(f"{'='*60}")
    start = time.time()
    
    last = Challan1.objects.filter(challan_no__startswith='TSC').order_by('-challan_no').first()
    num = int(last.challan_no[3:]) + 1 if last else 1
    
    for i in range(count):
        supplier = random.choice(suppliers)
        product = random.choice(products)
        
        ch_no = f"TSC{num+i:07d}"
        challan = Challan1.objects.create(
            challan_no=ch_no,
            challan_date=datetime.now() - timedelta(days=random.randint(1,180)),
            supplier=supplier,
            challan_total=0,
            transport_charges=0
        )
        
        qty = random.randint(10,100)
        rate = random.uniform(50,500)
        total = qty * rate
        
        SupplierChallanMaster.objects.create(
            product_suppliername=supplier,
            product_challan_id=challan,
            product_challan_no=ch_no,
            product_id=product,
            product_name=product.product_name,
            product_company=product.product_company,
            product_packing=product.product_packing,
            product_batch_no=f"B{random.randint(10,999)}",
            product_expiry=f"{random.randint(1,12):02d}/25",
            product_mrp=random.uniform(100,1000),
            product_purchase_rate=rate,
            product_quantity=qty,
            product_discount=0,
            cgst=6,
            sgst=6,
            total_amount=total
        )
        
        challan.challan_total = total
        challan.save()
        
        if (i+1) % 1000 == 0:
            print(f"  Progress: {i+1:,}/{count:,}")
    
    elapsed = time.time() - start
    print(f"✓ COMPLETED: {count:,} supplier challans in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def test_customer_challans(customers, products, count):
    """Section 6: Customer Challans"""
    print(f"\n{'='*60}")
    print(f"SECTION 6: CUSTOMER CHALLANS ({count:,} records)")
    print(f"{'='*60}")
    start = time.time()
    
    last = CustomerChallan.objects.filter(customer_challan_no__startswith='TCC').order_by('-customer_challan_no').first()
    num = int(last.customer_challan_no[3:]) + 1 if last else 1
    
    for i in range(count):
        customer = random.choice(customers)
        product = random.choice(products)
        
        ch_no = f"TCC{num+i:07d}"
        challan = CustomerChallan.objects.create(
            customer_challan_no=ch_no,
            customer_challan_date=datetime.now() - timedelta(days=random.randint(1,180)),
            customer_name=customer,
            challan_total=0
        )
        
        qty = random.randint(1,50)
        rate = random.uniform(100,1000)
        total = qty * rate
        
        CustomerChallanMaster.objects.create(
            customer_challan_id=challan,
            customer_challan_no=ch_no,
            customer_name=customer,
            product_id=product,
            product_name=product.product_name,
            product_company=product.product_company,
            product_packing=product.product_packing,
            product_batch_no=f"B{random.randint(10,999)}",
            product_expiry=f"{random.randint(1,12):02d}/25",
            product_mrp=random.uniform(100,1000),
            sale_rate=rate,
            sale_quantity=qty,
            sale_discount=0,
            sale_cgst=6,
            sale_sgst=6,
            sale_total_amount=total
        )
        
        challan.challan_total = total
        challan.save()
        
        if (i+1) % 1000 == 0:
            print(f"  Progress: {i+1:,}/{count:,}")
    
    elapsed = time.time() - start
    print(f"✓ COMPLETED: {count:,} customer challans in {elapsed:.2f}s ({count/elapsed:.0f}/sec)")
    return True

def run_full_test():
    """Run full test with 25,000 records per section"""
    print("\n" + "="*60)
    print("FULL TEST - 25,000 RECORDS PER SECTION")
    print("="*60)
    
    total_start = time.time()
    suppliers, customers, products = create_base_data()
    
    results = []
    results.append(("Purchases", test_purchases(suppliers, products, 25000)))
    results.append(("Sales", test_sales(customers, products, 25000)))
    results.append(("Purchase Returns", test_purchase_returns(suppliers, products, 25000)))
    results.append(("Sales Returns", test_sales_returns(customers, products, 25000)))
    results.append(("Supplier Challans", test_supplier_challans(suppliers, products, 25000)))
    results.append(("Customer Challans", test_customer_challans(customers, products, 25000)))
    
    total_time = time.time() - total_start
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:25s}: {status}")
    
    total_records = sum([1 for _, p in results if p]) * 25000
    print(f"\n{'Total Records Created':25s}: {total_records:,}")
    print(f"{'Total Time':25s}: {total_time:.2f}s")
    print(f"{'Average Speed':25s}: {total_records/total_time:.0f} records/sec")
    print("="*60)

def run_quick_test():
    """Run quick test with 1,000 records per section"""
    print("\n" + "="*60)
    print("QUICK TEST - 1,000 RECORDS PER SECTION")
    print("="*60)
    
    suppliers, customers, products = create_base_data()
    
    test_purchases(suppliers, products, 1000)
    test_sales(customers, products, 1000)
    test_purchase_returns(suppliers, products, 1000)
    test_sales_returns(customers, products, 1000)
    test_supplier_challans(suppliers, products, 1000)
    test_customer_challans(customers, products, 1000)
    
    print("\n✓ Quick test completed!")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        run_quick_test()
    else:
        run_full_test()
