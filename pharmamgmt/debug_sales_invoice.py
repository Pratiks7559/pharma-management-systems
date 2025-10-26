#!/usr/bin/env python
"""
Debug script for sales invoice issues
Run this to check database connections and form validation
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import *
from core.forms import SalesInvoiceForm
from core.utils import generate_sales_invoice_number
from datetime import datetime

def test_database_connection():
    """Test if database is accessible"""
    try:
        count = ProductMaster.objects.count()
        print(f"✓ Database connection OK - {count} products found")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_models():
    """Test model creation"""
    try:
        # Test customer creation
        customers = CustomerMaster.objects.all()[:5]
        print(f"✓ Found {len(customers)} customers")
        
        # Test product creation
        products = ProductMaster.objects.all()[:5]
        print(f"✓ Found {len(products)} products")
        
        return True
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False

def test_form_validation():
    """Test form validation"""
    try:
        # Test with valid data
        form_data = {
            'sales_invoice_date': '1512',  # DDMM format
            'customerid': CustomerMaster.objects.first().customerid if CustomerMaster.objects.exists() else 1,
            'sales_transport_charges': 0
        }
        
        form = SalesInvoiceForm(data=form_data)
        is_valid = form.is_valid()
        
        print(f"Form validation result: {is_valid}")
        if not is_valid:
            print(f"Form errors: {form.errors}")
        else:
            print("✓ Form validation passed")
            
        return is_valid
    except Exception as e:
        print(f"✗ Form validation test failed: {e}")
        return False

def test_invoice_number_generation():
    """Test invoice number generation"""
    try:
        invoice_no = generate_sales_invoice_number()
        print(f"✓ Generated invoice number: {invoice_no}")
        return True
    except Exception as e:
        print(f"✗ Invoice number generation failed: {e}")
        return False

def test_stock_functions():
    """Test stock calculation functions"""
    try:
        from core.utils import get_batch_stock_status
        
        # Test with first product if exists
        product = ProductMaster.objects.first()
        if product:
            # Get a batch from purchases
            purchase = PurchaseMaster.objects.filter(productid=product).first()
            if purchase:
                stock, available = get_batch_stock_status(product.productid, purchase.product_batch_no)
                print(f"✓ Stock check for {product.product_name} batch {purchase.product_batch_no}: {stock} (Available: {available})")
            else:
                print("! No purchase records found for testing stock")
        else:
            print("! No products found for testing stock")
        return True
    except Exception as e:
        print(f"✗ Stock function test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Sales Invoice Debug Script ===")
    print()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Models", test_models),
        ("Form Validation", test_form_validation),
        ("Invoice Number Generation", test_invoice_number_generation),
        ("Stock Functions", test_stock_functions)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
        print()
    
    print("=== Test Results ===")
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\nTroubleshooting tips:")
        print("1. Check database connection")
        print("2. Run migrations: python manage.py migrate")
        print("3. Check if customers and products exist in database")
        print("4. Verify form field names match model fields")

if __name__ == "__main__":
    main()