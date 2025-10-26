"""
Debug script for invoice functionality
Run this to test the invoice creation process
"""

import json
from datetime import datetime
from core.models import *
from core.forms import InvoiceForm

def debug_invoice_creation():
    """Debug the invoice creation process"""
    
    print("=== Debug Invoice Creation ===")
    
    # Check if we have suppliers
    suppliers = SupplierMaster.objects.all()
    print(f"Available suppliers: {suppliers.count()}")
    
    if suppliers.count() == 0:
        print("Creating test supplier...")
        supplier = SupplierMaster.objects.create(
            supplier_name="Debug Supplier",
            supplier_type="Test",
            supplier_address="Test Address",
            supplier_mobile="1234567890",
            supplier_whatsapp="1234567890",
            supplier_emailid="debug@test.com",
            supplier_spoc="Debug Person",
            supplier_dlno="DL123",
            supplier_gstno="GST123",
            supplier_bank="Test Bank",
            supplier_bankaccountno="123456789",
            supplier_bankifsc="TEST123"
        )
        print(f"Created supplier: {supplier.supplier_name}")
    else:
        supplier = suppliers.first()
        print(f"Using existing supplier: {supplier.supplier_name}")
    
    # Check if we have products
    products = ProductMaster.objects.all()
    print(f"Available products: {products.count()}")
    
    if products.count() == 0:
        print("Creating test product...")
        product = ProductMaster.objects.create(
            product_name="Debug Medicine",
            product_company="Debug Pharma",
            product_packing="10x10",
            product_salt="Debug Salt",
            product_category="tablet",
            product_hsn="30049099",
            product_hsn_percent="12"
        )
        print(f"Created product: {product.product_name}")
    else:
        product = products.first()
        print(f"Using existing product: {product.product_name}")
    
    # Test form data
    form_data = {
        'invoice_no': f'DEBUG{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'invoice_date': datetime.now().date(),
        'supplierid': supplier.supplierid,
        'scroll_no': 'DEBUG_SCROLL',
        'transport_charges': 0,
        'invoice_total': 1000.0
    }
    
    print(f"Form data: {form_data}")
    
    # Test form validation
    form = InvoiceForm(data=form_data)
    if form.is_valid():
        print("✓ Form is valid")
        
        # Test invoice creation
        try:
            invoice = form.save(commit=False)
            invoice.invoice_paid = 0
            invoice.save()
            print(f"✓ Invoice created: {invoice.invoice_no}")
            
            # Test products data
            products_data = [{
                'productid': product.productid,
                'batch_no': 'DEBUG001',
                'expiry': '12-2025',
                'mrp': 100.0,
                'purchase_rate': 80.0,
                'quantity': 10.0,
                'scheme': 0,
                'discount': 0,
                'igst': 12.0,
                'calculation_mode': 'flat',
                'rate_A': 90.0,
                'rate_B': 85.0,
                'rate_C': 80.0
            }]
            
            print(f"Products data: {products_data}")
            
            # Test purchase creation
            for product_data in products_data:
                purchase = PurchaseMaster(
                    product_supplierid=supplier,
                    product_invoiceid=invoice,
                    product_invoice_no=invoice.invoice_no,
                    productid=product,
                    product_name=product.product_name,
                    product_company=product.product_company,
                    product_packing=product.product_packing,
                    product_batch_no=product_data['batch_no'],
                    product_expiry=product_data['expiry'],
                    product_MRP=product_data['mrp'],
                    product_purchase_rate=product_data['purchase_rate'],
                    product_quantity=product_data['quantity'],
                    product_scheme=product_data['scheme'],
                    product_discount_got=product_data['discount'],
                    IGST=product_data['igst'],
                    purchase_calculation_mode=product_data['calculation_mode'],
                    actual_rate_per_qty=product_data['purchase_rate'],
                    product_actual_rate=product_data['purchase_rate'],
                    total_amount=product_data['purchase_rate'] * product_data['quantity'],
                    product_transportation_charges=0
                )
                purchase.save()
                print(f"✓ Purchase created for {product.product_name}")
            
            print(f"✓ Invoice {invoice.invoice_no} created successfully with products!")
            print(f"Invoice ID: {invoice.invoiceid}")
            
            return invoice
            
        except Exception as e:
            print(f"✗ Error creating invoice: {e}")
            import traceback
            traceback.print_exc()
            return None
    else:
        print("✗ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return None

if __name__ == "__main__":
    debug_invoice_creation()