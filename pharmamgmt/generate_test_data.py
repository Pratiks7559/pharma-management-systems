import os
import django
import sys
from datetime import datetime, timedelta
import random

# Django setup
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import (
    ProductMaster, SupplierMaster, CustomerMaster, InvoiceMaster, 
    PurchaseMaster, SalesInvoiceMaster, SalesMaster, ReturnInvoiceMaster,
    ReturnPurchaseMaster, ReturnSalesInvoiceMaster, ReturnSalesMaster,
    Challan1, SupplierChallanMaster, CustomerChallan, CustomerChallanMaster
)

def generate_test_data():
    print("Starting test data generation...")
    
    # Create 100 Suppliers
    print("Creating 100 Suppliers...")
    suppliers = []
    for i in range(1, 101):
        supplier = SupplierMaster.objects.create(
            supplier_name=f"Test Supplier {i}",
            supplier_type="Distributor",
            supplier_address=f"Address {i}",
            supplier_mobile=f"98765{i:05d}",
            supplier_whatsapp=f"98765{i:05d}",
            supplier_emailid=f"supplier{i}@test.com",
            supplier_gstno=f"27AABCT{i:04d}Z1Z5"
        )
        suppliers.append(supplier)
    print(f"Created {len(suppliers)} suppliers")
    
    # Create 100 Customers
    print("Creating 100 Customers...")
    customers = []
    for i in range(1, 101):
        customer = CustomerMaster.objects.create(
            customer_name=f"Test Customer {i}",
            customer_type="TYPE-A",
            customer_address=f"Customer Address {i}",
            customer_mobile=f"87654{i:05d}",
            customer_whatsapp=f"87654{i:05d}",
            customer_emailid=f"customer{i}@test.com",
            customer_gstno=f"27AABCC{i:04d}Z1Z5"
        )
        customers.append(customer)
    print(f"Created {len(customers)} customers")
    
    # Get existing products or create some
    products = list(ProductMaster.objects.all()[:50])
    if len(products) < 10:
        print("Creating test products...")
        for i in range(1, 51):
            product = ProductMaster.objects.create(
                product_name=f"Test Medicine {i}",
                product_company=f"Company {i%10}",
                product_packing="10x10",
                product_salt=f"Salt {i}",
                product_category="Tablet",
                product_hsn="30049099",
                product_hsn_percent="12"
            )
            products.append(product)
    
    print(f"Using {len(products)} products")
    
    # Generate 25000 Purchase records
    print("Creating 25000 Purchase records...")
    batch_size = 1000
    for batch_num in range(25):
        purchases = []
        invoices = []
        
        for i in range(batch_size):
            supplier = random.choice(suppliers)
            product = random.choice(products)
            
            invoice_no = f"TINV{batch_num*batch_size + i + 1:08d}"
            invoice_date = datetime.now().date() - timedelta(days=random.randint(1, 365))
            
            invoice = InvoiceMaster(
                invoice_no=invoice_no,
                invoice_date=invoice_date,
                supplierid=supplier,
                transport_charges=random.uniform(0, 500),
                invoice_total=random.uniform(1000, 50000),
                invoice_paid=0,
                payment_status='pending'
            )
            invoices.append(invoice)
        
        InvoiceMaster.objects.bulk_create(invoices, ignore_conflicts=True)
        created_invoices = InvoiceMaster.objects.filter(invoice_no__in=[inv.invoice_no for inv in invoices])
        
        for invoice in created_invoices:
            product = random.choice(products)
            qty = random.uniform(10, 500)
            rate = random.uniform(10, 500)
            
            purchase = PurchaseMaster(
                product_supplierid=invoice.supplierid,
                product_invoiceid=invoice,
                product_invoice_no=invoice.invoice_no,
                productid=product,
                product_name=product.product_name,
                product_company=product.product_company,
                product_packing=product.product_packing,
                product_batch_no=f"BATCH{random.randint(1000, 9999)}",
                product_expiry=f"{random.randint(1,12):02d}-{random.randint(2024,2027)}",
                product_MRP=rate * 1.5,
                product_purchase_rate=rate,
                product_quantity=qty,
                product_scheme=0,
                product_discount_got=random.uniform(0, 10),
                product_transportation_charges=0,
                product_actual_rate=rate,
                total_amount=qty * rate,
                CGST=2.5,
                SGST=2.5
            )
            purchases.append(purchase)
        
        PurchaseMaster.objects.bulk_create(purchases, batch_size=500)
        print(f"Created batch {batch_num + 1}/25 - {len(purchases)} purchases")
    
    # Generate 25000 Sales records
    print("Creating 25000 Sales records...")
    for batch_num in range(25):
        sales_invoices = []
        sales = []
        
        for i in range(batch_size):
            customer = random.choice(customers)
            invoice_no = f"TSINV{batch_num*batch_size + i + 1:08d}"
            invoice_date = datetime.now().date() - timedelta(days=random.randint(1, 180))
            
            sales_invoice = SalesInvoiceMaster(
                sales_invoice_no=invoice_no,
                sales_invoice_date=invoice_date,
                customerid=customer,
                sales_transport_charges=random.uniform(0, 200),
                sales_invoice_paid=0
            )
            sales_invoices.append(sales_invoice)
        
        SalesInvoiceMaster.objects.bulk_create(sales_invoices, ignore_conflicts=True)
        created_sales_invoices = SalesInvoiceMaster.objects.filter(sales_invoice_no__in=[si.sales_invoice_no for si in sales_invoices])
        
        for sales_invoice in created_sales_invoices:
            product = random.choice(products)
            qty = random.uniform(5, 100)
            rate = random.uniform(20, 600)
            
            sale = SalesMaster(
                sales_invoice_no=sales_invoice,
                customerid=sales_invoice.customerid,
                productid=product,
                product_name=product.product_name,
                product_company=product.product_company,
                product_packing=product.product_packing,
                product_batch_no=f"BATCH{random.randint(1000, 9999)}",
                product_expiry=f"{random.randint(1,12):02d}-{random.randint(2024,2027)}",
                product_MRP=rate * 1.2,
                sale_rate=rate,
                sale_quantity=qty,
                sale_scheme=0,
                sale_discount=random.uniform(0, 5),
                sale_cgst=2.5,
                sale_sgst=2.5,
                sale_total_amount=qty * rate
            )
            sales.append(sale)
        
        SalesMaster.objects.bulk_create(sales, batch_size=500)
        print(f"Created batch {batch_num + 1}/25 - {len(sales)} sales")
    
    # Generate 25000 Sales Return records
    print("Creating 25000 Sales Return records...")
    for batch_num in range(25):
        return_invoices = []
        returns = []
        
        for i in range(batch_size):
            customer = random.choice(customers)
            invoice_no = f"TSRINV{batch_num*batch_size + i + 1:08d}"
            invoice_date = datetime.now().date() - timedelta(days=random.randint(1, 90))
            
            return_invoice = ReturnSalesInvoiceMaster(
                return_sales_invoice_no=invoice_no,
                return_sales_invoice_date=invoice_date,
                return_sales_customerid=customer,
                return_sales_charges=0,
                transport_charges=0,
                return_sales_invoice_total=random.uniform(500, 5000),
                return_sales_invoice_paid=0
            )
            return_invoices.append(return_invoice)
        
        ReturnSalesInvoiceMaster.objects.bulk_create(return_invoices, ignore_conflicts=True)
        created_return_invoices = ReturnSalesInvoiceMaster.objects.filter(return_sales_invoice_no__in=[ri.return_sales_invoice_no for ri in return_invoices])
        
        for return_invoice in created_return_invoices:
            product = random.choice(products)
            qty = random.uniform(1, 20)
            rate = random.uniform(20, 600)
            
            return_sale = ReturnSalesMaster(
                return_sales_invoice_no=return_invoice,
                return_customerid=return_invoice.return_sales_customerid,
                return_productid=product,
                return_product_name=product.product_name,
                return_product_company=product.product_company,
                return_product_packing=product.product_packing,
                return_product_batch_no=f"BATCH{random.randint(1000, 9999)}",
                return_product_expiry=f"{random.randint(1,12):02d}-{random.randint(2024,2027)}",
                return_product_MRP=rate * 1.2,
                return_sale_rate=rate,
                return_sale_quantity=qty,
                return_sale_scheme=0,
                return_sale_discount=0,
                return_sale_cgst=2.5,
                return_sale_sgst=2.5,
                return_sale_total_amount=qty * rate,
                return_reason='expiry'
            )
            returns.append(return_sale)
        
        ReturnSalesMaster.objects.bulk_create(returns, batch_size=500)
        print(f"Created batch {batch_num + 1}/25 - {len(returns)} sales returns")
    
    # Generate 25000 Purchase Return records
    print("Creating 25000 Purchase Return records...")
    for batch_num in range(25):
        return_invoices = []
        returns = []
        
        for i in range(batch_size):
            supplier = random.choice(suppliers)
            invoice_no = f"TPRINV{batch_num*batch_size + i + 1:08d}"
            invoice_date = datetime.now().date() - timedelta(days=random.randint(1, 90))
            
            return_invoice = ReturnInvoiceMaster(
                returninvoiceid=invoice_no,
                returninvoice_date=invoice_date,
                returnsupplierid=supplier,
                return_charges=0,
                returninvoice_total=random.uniform(500, 5000),
                returninvoice_paid=0
            )
            return_invoices.append(return_invoice)
        
        ReturnInvoiceMaster.objects.bulk_create(return_invoices, ignore_conflicts=True)
        created_return_invoices = ReturnInvoiceMaster.objects.filter(returninvoiceid__in=[ri.returninvoiceid for ri in return_invoices])
        
        for return_invoice in created_return_invoices:
            product = random.choice(products)
            qty = random.uniform(1, 50)
            rate = random.uniform(10, 500)
            expiry_date = datetime.now().date() + timedelta(days=random.randint(30, 730))
            
            return_purchase = ReturnPurchaseMaster(
                returninvoiceid=return_invoice,
                returnproduct_supplierid=return_invoice.returnsupplierid,
                returnproductid=product,
                returnproduct_batch_no=f"BATCH{random.randint(1000, 9999)}",
                returnproduct_expiry=expiry_date,
                returnproduct_MRP=rate * 1.5,
                returnproduct_purchase_rate=rate,
                returnproduct_quantity=qty,
                returnproduct_cgst=2.5,
                returnproduct_sgst=2.5,
                returntotal_amount=qty * rate,
                return_reason='Damaged'
            )
            returns.append(return_purchase)
        
        ReturnPurchaseMaster.objects.bulk_create(returns, batch_size=500)
        print(f"Created batch {batch_num + 1}/25 - {len(returns)} purchase returns")
    
    # Generate 25000 Supplier Challan records
    print("Creating 25000 Supplier Challan records...")
    for batch_num in range(25):
        challans = []
        challan_details = []
        
        for i in range(batch_size):
            supplier = random.choice(suppliers)
            challan_no = f"TSCHAL{batch_num*batch_size + i + 1:08d}"
            challan_date = datetime.now().date() - timedelta(days=random.randint(1, 180))
            
            challan = Challan1(
                challan_no=challan_no,
                challan_date=challan_date,
                supplier=supplier,
                challan_total=random.uniform(1000, 20000),
                transport_charges=random.uniform(0, 300),
                challan_paid=0,
                is_invoiced=False
            )
            challans.append(challan)
        
        Challan1.objects.bulk_create(challans, ignore_conflicts=True)
        created_challans = Challan1.objects.filter(challan_no__in=[ch.challan_no for ch in challans])
        
        for challan in created_challans:
            product = random.choice(products)
            qty = random.uniform(10, 200)
            rate = random.uniform(10, 500)
            
            challan_detail = SupplierChallanMaster(
                product_suppliername=challan.supplier,
                product_challan_id=challan,
                product_challan_no=challan.challan_no,
                product_id=product,
                product_name=product.product_name,
                product_company=product.product_company,
                product_packing=product.product_packing,
                product_batch_no=f"BATCH{random.randint(1000, 9999)}",
                product_expiry=f"{random.randint(1,12):02d}-{random.randint(2024,2027)}",
                product_mrp=rate * 1.5,
                product_purchase_rate=rate,
                product_quantity=qty,
                product_scheme=0,
                product_discount=0,
                product_transportation_charges=0,
                product_actual_rate=rate,
                total_amount=qty * rate,
                cgst=2.5,
                sgst=2.5
            )
            challan_details.append(challan_detail)
        
        SupplierChallanMaster.objects.bulk_create(challan_details, batch_size=500)
        print(f"Created batch {batch_num + 1}/25 - {len(challan_details)} supplier challans")
    
    # Generate 25000 Customer Challan records
    print("Creating 25000 Customer Challan records...")
    for batch_num in range(25):
        challans = []
        challan_details = []
        
        for i in range(batch_size):
            customer = random.choice(customers)
            challan_no = f"TCCHAL{batch_num*batch_size + i + 1:08d}"
            challan_date = datetime.now().date() - timedelta(days=random.randint(1, 180))
            
            challan = CustomerChallan(
                customer_challan_no=challan_no,
                customer_challan_date=challan_date,
                customer_name=customer,
                customer_transport_charges=random.uniform(0, 200),
                challan_total=random.uniform(1000, 15000),
                challan_invoice_paid=0,
                is_invoiced=False
            )
            challans.append(challan)
        
        CustomerChallan.objects.bulk_create(challans, ignore_conflicts=True)
        created_challans = CustomerChallan.objects.filter(customer_challan_no__in=[ch.customer_challan_no for ch in challans])
        
        for challan in created_challans:
            product = random.choice(products)
            qty = random.uniform(5, 100)
            rate = random.uniform(20, 600)
            
            challan_detail = CustomerChallanMaster(
                customer_challan_id=challan,
                customer_challan_no=challan.customer_challan_no,
                customer_name=challan.customer_name,
                product_id=product,
                product_name=product.product_name,
                product_company=product.product_company,
                product_packing=product.product_packing,
                product_batch_no=f"BATCH{random.randint(1000, 9999)}",
                product_expiry=f"{random.randint(1,12):02d}-{random.randint(2024,2027)}",
                product_mrp=rate * 1.2,
                sale_rate=rate,
                sale_quantity=qty,
                sale_discount=0,
                sale_cgst=2.5,
                sale_sgst=2.5,
                sale_total_amount=qty * rate
            )
            challan_details.append(challan_detail)
        
        CustomerChallanMaster.objects.bulk_create(challan_details, batch_size=500)
        print(f"Created batch {batch_num + 1}/25 - {len(challan_details)} customer challans")
    
    print("\n" + "="*60)
    print("TEST DATA GENERATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"Suppliers: 100")
    print(f"Customers: 100")
    print(f"Purchase Records: 25000")
    print(f"Sales Records: 25000")
    print(f"Sales Return Records: 25000")
    print(f"Purchase Return Records: 25000")
    print(f"Supplier Challan Records: 25000")
    print(f"Customer Challan Records: 25000")
    print("="*60)

if __name__ == "__main__":
    try:
        generate_test_data()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
