#!/usr/bin/env python
"""
Final Stock System Validation
Validates that all stock calculations are working correctly
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import ProductMaster, PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster
from core.stock_manager import StockManager
from core.utils import get_batch_stock_status, get_stock_status
from django.db.models import Sum

def validate_stock_formula():
    """Validate the stock calculation formula for all products"""
    
    print("=== Stock Formula Validation ===\n")
    
    # Test with all products that have transactions
    products = ProductMaster.objects.filter(
        purchasemaster__isnull=False
    ).distinct()
    
    all_passed = True
    
    for product in products:
        print(f"Validating Product: {product.product_name} (ID: {product.productid})")
        
        # Manual calculation
        purchased = PurchaseMaster.objects.filter(
            productid=product
        ).aggregate(total=Sum('product_quantity'))['total'] or 0
        
        sold = SalesMaster.objects.filter(
            productid=product
        ).aggregate(total=Sum('sale_quantity'))['total'] or 0
        
        purchase_returns = ReturnPurchaseMaster.objects.filter(
            returnproductid=product
        ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        
        sales_returns = ReturnSalesMaster.objects.filter(
            return_productid=product
        ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
        
        # Formula: Stock = Purchased - Sold - Purchase Returns + Sales Returns
        expected_stock = purchased - sold - purchase_returns + sales_returns
        
        # StockManager calculation
        stock_summary = StockManager.get_stock_summary(product.productid)
        manager_stock = stock_summary['total_stock']
        
        # Batch sum validation
        batch_sum = sum(batch['stock'] for batch in stock_summary['batches'])
        
        print(f"  Expected: {expected_stock}, Manager: {manager_stock}, Batch Sum: {batch_sum}")
        
        if expected_stock == manager_stock == batch_sum:
            print("  SUCCESS: All calculations match")
        else:
            print("  ERROR: Calculations don't match")
            all_passed = False
        
        print()
    
    if all_passed:
        print("SUCCESS: All products passed stock validation!")
    else:
        print("ERROR: Some products failed validation!")
    
    return all_passed

def test_transaction_scenarios():
    """Test different transaction scenarios"""
    
    print("=== Transaction Scenarios Test ===\n")
    
    # Test purchase return validation
    print("1. Testing Purchase Return Validation:")
    
    # Find a purchase return
    pr = ReturnPurchaseMaster.objects.first()
    if pr:
        result = StockManager.process_purchase_return(pr)
        print(f"   Purchase Return Processing: {result['success']}")
        print(f"   Message: {result['message']}")
    else:
        print("   No purchase returns found to test")
    
    print()
    
    # Test sales return validation
    print("2. Testing Sales Return Validation:")
    
    # Find a sales return
    sr = ReturnSalesMaster.objects.first()
    if sr:
        result = StockManager.process_sales_return(sr)
        print(f"   Sales Return Processing: {result['success']}")
        print(f"   Message: {result['message']}")
    else:
        print("   No sales returns found to test")
    
    print()

def test_stock_reports():
    """Test stock reporting functions"""
    
    print("=== Stock Reports Test ===\n")
    
    # Test low stock products
    print("1. Testing Low Stock Detection:")
    low_stock = StockManager.get_low_stock_products(threshold=50)
    print(f"   Found {len(low_stock)} products with low stock")
    for item in low_stock[:3]:  # Show first 3
        print(f"     {item['product'].product_name}: {item['current_stock']} units")
    
    print()
    
    # Test out of stock products
    print("2. Testing Out of Stock Detection:")
    out_of_stock = StockManager.get_out_of_stock_products()
    print(f"   Found {len(out_of_stock)} products out of stock")
    for item in out_of_stock[:3]:  # Show first 3
        print(f"     {item['product'].product_name}: {item['current_stock']} units")
    
    print()
    
    # Test stock value summary
    print("3. Testing Stock Value Summary:")
    value_summary = StockManager.get_stock_value_summary()
    print(f"   Total Stock Value: Rs.{value_summary['total_value']:.2f}")
    print(f"   Products in Stock: {value_summary['total_products_in_stock']}")
    
    print()

def summary_report():
    """Generate a summary report"""
    
    print("=== Stock System Summary ===\n")
    
    # Count transactions
    total_purchases = PurchaseMaster.objects.count()
    total_sales = SalesMaster.objects.count()
    total_purchase_returns = ReturnPurchaseMaster.objects.count()
    total_sales_returns = ReturnSalesMaster.objects.count()
    
    print(f"Transaction Counts:")
    print(f"  Purchases: {total_purchases}")
    print(f"  Sales: {total_sales}")
    print(f"  Purchase Returns: {total_purchase_returns}")
    print(f"  Sales Returns: {total_sales_returns}")
    print()
    
    # Stock status
    products_with_stock = 0
    products_out_of_stock = 0
    products_negative_stock = 0
    
    all_products = ProductMaster.objects.filter(purchasemaster__isnull=False).distinct()
    
    for product in all_products:
        stock_summary = StockManager.get_stock_summary(product.productid)
        stock = stock_summary['total_stock']
        
        if stock > 0:
            products_with_stock += 1
        elif stock == 0:
            products_out_of_stock += 1
        else:
            products_negative_stock += 1
    
    print(f"Stock Status:")
    print(f"  Products with Stock: {products_with_stock}")
    print(f"  Products Out of Stock: {products_out_of_stock}")
    print(f"  Products with Negative Stock: {products_negative_stock}")
    print()
    
    print("Stock Calculation Formula:")
    print("  Current Stock = Purchased - Sold - Purchase Returns + Sales Returns")
    print()
    
    print("Key Features Implemented:")
    print("  ✓ Batch-wise stock tracking")
    print("  ✓ Purchase returns reduce stock")
    print("  ✓ Sales returns increase stock")
    print("  ✓ Negative stock detection")
    print("  ✓ Stock validation for sales")
    print("  ✓ Comprehensive reporting")
    print()

if __name__ == "__main__":
    print("Starting Stock System Validation...\n")
    
    # Validate stock formula
    formula_valid = validate_stock_formula()
    
    # Test transaction scenarios
    test_transaction_scenarios()
    
    # Test stock reports
    test_stock_reports()
    
    # Generate summary
    summary_report()
    
    if formula_valid:
        print("FINAL RESULT: Stock system is working correctly!")
    else:
        print("FINAL RESULT: Stock system needs attention!")
    
    print("\nValidation completed!")