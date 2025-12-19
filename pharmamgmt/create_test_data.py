"""
Create 100,000 Test Entries
Creates: Invoices, Sales, Challans, Returns
"""

import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import (
    ProductMaster, SupplierMaster, CustomerMaster,
    InvoiceMaster, PurchaseMaster,
    SalesInvoiceMaster, SalesMaster,
    Challan1, CustomerChallan,
    ReturnInvoiceMaster, ReturnPurchaseMaster,
    ReturnSalesInvoiceMaster, ReturnSalesMaster
)

def create_test_data():
    print("Creating 100,000 test entries...")
    print("=" * 50)
    
    # Get or create test data
    supplier = SupplierMaster.objects.first() or SupplierMaster.objects.create(
        supplier_name="Test Supplier", supplier_mobile="9999999999"
    )
    customer = CustomerMaster.objects.first() or CustomerMaster.objects.create(
        customer_name="Test Customer", customer_mobile="8888888888"
    )
    product = ProductMaster.objects.first() or ProductMaster.objects.create(
        product_name="Test Medicine", product_company="Test Co", product_packing="10"
    )
    
    start_date = datetime.now() - timedelta(days=365)
    
    # 1. Purchase Invoices (25,000)
    print("\n1. Creating 25,000 Purchase Invoices...")
    for i in range(25000):
        invoice = InvoiceMaster.objects.create(
            supplierid=supplier,
            invoice_no=f"PI{datetime.now().strftime('%Y%m%d')}{i+1:06d}",
            invoice_date=start_date + timedelta(days=random.randint(0, 365)),
            transport_charges=0,
            invoice_total=random.randint(1000, 50000)
        )
        
        # Add purchase items
        PurchaseMaster.objects.create(
            product_invoiceid=invoice,
            product_supplierid=supplier,
            product_invoice_no=invoice.invoice_no,
            productid=product,
            product_name=product.product_name,
            product_company=product.product_company,
            product_packing=product.product_packing,
            product_batch_no=f"BATCH{i+1}",
            product_expiry="12-2025",
            product_MRP=random.randint(50, 200),
            product_purchase_rate=random.randint(10, 100),
            product_quantity=random.randint(10, 100),
            product_discount_got=0,
            product_transportation_charges=0
        )
        
        if (i + 1) % 5000 == 0:
            print(f"   Created {i+1} purchase invoices...")
    
    # 2. Sales Invoices (25,000)
    print("\n2. Creating 25,000 Sales Invoices...")
    for i in range(25000):
        invoice = SalesInvoiceMaster.objects.create(
            sales_invoice_no=f"SI{datetime.now().strftime('%Y%m%d')}{i+1:06d}",
            sales_invoice_date=start_date + timedelta(days=random.randint(0, 365)),
            customerid=customer
        )
        
        # Add sale items
        SalesMaster.objects.create(
            sales_invoice_no=invoice,
            customerid=customer,
            productid=product,
            product_name=product.product_name,
            product_company=product.product_company,
            product_packing=product.product_packing,
            product_batch_no=f"BATCH{i+1}",
            product_expiry="12-2025",
            product_MRP=random.randint(50, 200),
            sale_rate=random.randint(20, 150),
            sale_quantity=random.randint(5, 50),
            sale_total_amount=random.randint(500, 5000)
        )
        
        if (i + 1) % 5000 == 0:
            print(f"   Created {i+1} sales invoices...")
    
    # 3. Supplier Challans (15,000)
    print("\n3. Creating 15,000 Supplier Challans...")
    for i in range(15000):
        Challan1.objects.create(
            supplier=supplier,
            challan_no=f"SC{datetime.now().strftime('%Y%m%d')}{i+1:06d}",
            challan_date=start_date + timedelta(days=random.randint(0, 365)),
            challan_total=random.randint(1000, 30000)
        )
        
        if (i + 1) % 3000 == 0:
            print(f"   Created {i+1} supplier challans...")
    
    # 4. Customer Challans (15,000)
    print("\n4. Creating 15,000 Customer Challans...")
    for i in range(15000):
        CustomerChallan.objects.create(
            customer_name=customer,
            customer_challan_no=f"CC{datetime.now().strftime('%Y%m%d')}{i+1:06d}",
            customer_challan_date=start_date + timedelta(days=random.randint(0, 365)),
            challan_total=random.randint(500, 15000)
        )
        
        if (i + 1) % 3000 == 0:
            print(f"   Created {i+1} customer challans...")
    
    # 5. Purchase Returns (10,000)
    print("\n5. Creating 10,000 Purchase Returns...")
    for i in range(10000):
        ret = ReturnInvoiceMaster.objects.create(
            returninvoiceid=f"PR{datetime.now().strftime('%Y%m%d')}{i+1:06d}",
            returnsupplierid=supplier,
            returninvoice_date=start_date + timedelta(days=random.randint(0, 365)),
            returninvoice_total=random.randint(500, 10000)
        )
        
        ReturnPurchaseMaster.objects.create(
            returninvoiceid=ret,
            returnproduct_supplierid=supplier,
            returnproductid=product,
            returnproduct_batch_no=f"BATCH{i+1}",
            returnproduct_expiry=start_date + timedelta(days=365),
            returnproduct_purchase_rate=random.randint(10, 100),
            returnproduct_quantity=random.randint(5, 20),
            returntotal_amount=random.randint(500, 2000)
        )
        
        if (i + 1) % 2000 == 0:
            print(f"   Created {i+1} purchase returns...")
    
    # 6. Sales Returns (10,000)
    print("\n6. Creating 10,000 Sales Returns...")
    for i in range(10000):
        ret = ReturnSalesInvoiceMaster.objects.create(
            return_sales_invoice_no=f"SR{datetime.now().strftime('%Y%m%d')}{i+1:06d}",
            return_sales_invoice_date=start_date + timedelta(days=random.randint(0, 365)),
            return_sales_customerid=customer,
            return_sales_invoice_total=random.randint(200, 5000)
        )
        
        ReturnSalesMaster.objects.create(
            return_sales_invoice_no=ret,
            return_customerid=customer,
            return_productid=product,
            return_product_name=product.product_name,
            return_product_company=product.product_company,
            return_product_packing=product.product_packing,
            return_product_batch_no=f"BATCH{i+1}",
            return_product_expiry="12-2025",
            return_sale_rate=random.randint(20, 150),
            return_sale_quantity=random.randint(2, 10),
            return_sale_total_amount=random.randint(200, 1000)
        )
        
        if (i + 1) % 2000 == 0:
            print(f"   Created {i+1} sales returns...")
    
    print("\n" + "=" * 50)
    print("✓ Successfully created 100,000 entries!")
    print("=" * 50)
    print("\nBreakdown:")
    print(f"  Purchase Invoices:  {InvoiceMaster.objects.count():,}")
    print(f"  Sales Invoices:     {SalesInvoiceMaster.objects.count():,}")
    print(f"  Supplier Challans:  {Challan1.objects.count():,}")
    print(f"  Customer Challans:  {CustomerChallan.objects.count():,}")
    print(f"  Purchase Returns:   {ReturnInvoiceMaster.objects.count():,}")
    print(f"  Sales Returns:      {ReturnSalesInvoiceMaster.objects.count():,}")
    print(f"\n  TOTAL:              100,000")

if __name__ == '__main__':
    try:
        create_test_data()
    except Exception as e:
        print(f"\nError: {e}")
