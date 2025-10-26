#!/usr/bin/env python
"""
Test script to debug dashboard functionality
Run this from Django shell: python manage.py shell < test_dashboard.py
"""

import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebsiteHostingService.settings')
django.setup()

from core.models import ProductMaster, PurchaseMaster, SalesMaster
from core.utils import get_stock_status, get_batch_stock_status

def test_dashboard_data():
    print("=== DASHBOARD DATA TEST ===")
    
    # Test 1: Check total products
    total_products = ProductMaster.objects.count()
    print(f"Total products in database: {total_products}")
    
    # Test 2: Check products with purchases
    products_with_purchases = ProductMaster.objects.filter(
        purchasemaster__isnull=False
    ).distinct().count()
    print(f"Products with purchases: {products_with_purchases}")
    
    # Test 3: Check purchases with expiry dates
    purchases_with_expiry = PurchaseMaster.objects.filter(
        product_expiry__isnull=False
    ).exclude(product_expiry='').count()
    print(f"Purchases with expiry dates: {purchases_with_expiry}")
    
    # Test 4: Sample expiry dates
    sample_expiries = PurchaseMaster.objects.filter(
        product_expiry__isnull=False
    ).exclude(product_expiry='').values_list('product_expiry', flat=True)[:10]
    print(f"Sample expiry dates: {list(sample_expiries)}")
    
    # Test 5: Check stock calculation for first few products
    print("\n=== STOCK CALCULATION TEST ===")
    products = ProductMaster.objects.all()[:5]
    
    for product in products:
        try:
            stock_info = get_stock_status(product.productid)
            print(f"Product: {product.product_name}")
            print(f"  Stock: {stock_info.get('current_stock', 0)}")
            print(f"  Purchased: {stock_info.get('purchased', 0)}")
            print(f"  Sold: {stock_info.get('sold', 0)}")
            print()
        except Exception as e:
            print(f"Error with {product.product_name}: {e}")
    
    # Test 6: Check for expiring products
    print("\n=== EXPIRING PRODUCTS TEST ===")
    current_date = datetime.now().date()
    warning_date = current_date + timedelta(days=30)
    
    purchases_with_expiry = PurchaseMaster.objects.filter(
        product_expiry__isnull=False
    ).exclude(product_expiry='').select_related('productid')[:10]
    
    expiring_count = 0
    for purchase in purchases_with_expiry:
        try:
            expiry_str = str(purchase.product_expiry)
            expiry_date = None
            
            # Handle different date formats
            if len(expiry_str) == 10 and '-' in expiry_str:  # YYYY-MM-DD
                expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
            elif len(expiry_str) == 7 and '-' in expiry_str:  # MM-YYYY
                month, year = expiry_str.split('-')
                import calendar
                last_day = calendar.monthrange(int(year), int(month))[1]
                expiry_date = datetime(int(year), int(month), last_day).date()
            
            if expiry_date and expiry_date <= warning_date:
                stock_info = get_batch_stock_status(purchase.productid.productid, purchase.product_batch_no)
                if stock_info[1] and stock_info[0] > 0:
                    days_to_expiry = (expiry_date - current_date).days
                    print(f"Expiring: {purchase.productid.product_name} - Batch: {purchase.product_batch_no}")
                    print(f"  Expiry: {expiry_date} ({days_to_expiry} days)")
                    print(f"  Stock: {stock_info[0]}")
                    expiring_count += 1
                    
        except Exception as e:
            print(f"Error processing expiry for {purchase.productid.product_name}: {e}")
    
    print(f"\nTotal expiring products found: {expiring_count}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_dashboard_data()