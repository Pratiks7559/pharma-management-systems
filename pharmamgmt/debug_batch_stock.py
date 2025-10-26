#!/usr/bin/env python
"""
Debug Batch Stock Calculation
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
from django.db.models import Sum

def debug_paracetamol_batches():
    """Debug paracetamol batch calculations"""
    
    print("=== Debugging Paracetamol Batch Stock ===\n")
    
    # Get paracetamol product with ID 3371
    try:
        product = ProductMaster.objects.get(productid=3371)
    except ProductMaster.DoesNotExist:
        print("Product ID 3371 not found!")
        return
    
    print(f"Product: {product.product_name} (ID: {product.productid})")
    
    # Get all unique batches
    all_batches = set()
    
    # From purchases
    purchase_batches = PurchaseMaster.objects.filter(
        productid=product
    ).values_list('product_batch_no', flat=True)
    all_batches.update(purchase_batches)
    
    # From sales
    sales_batches = SalesMaster.objects.filter(
        productid=product
    ).values_list('product_batch_no', flat=True)
    all_batches.update(sales_batches)
    
    # From purchase returns
    pr_batches = ReturnPurchaseMaster.objects.filter(
        returnproductid=product
    ).values_list('returnproduct_batch_no', flat=True)
    all_batches.update(pr_batches)
    
    # From sales returns
    sr_batches = ReturnSalesMaster.objects.filter(
        return_productid=product
    ).values_list('return_product_batch_no', flat=True)
    all_batches.update(sr_batches)
    
    print(f"All Batches Found: {sorted(all_batches)}")
    print()
    
    total_stock_check = 0
    
    for batch_no in sorted(all_batches):
        print(f"Batch: {batch_no}")
        print("-" * 30)
        
        # Purchases
        purchases = PurchaseMaster.objects.filter(
            productid=product,
            product_batch_no=batch_no
        )
        purchased_qty = purchases.aggregate(total=Sum('product_quantity'))['total'] or 0
        print(f"Purchases: {purchased_qty}")
        for p in purchases:
            print(f"  - {p.product_quantity} units on {p.purchase_entry_date}")
        
        # Sales
        sales = SalesMaster.objects.filter(
            productid=product,
            product_batch_no=batch_no
        )
        sold_qty = sales.aggregate(total=Sum('sale_quantity'))['total'] or 0
        print(f"Sales: {sold_qty}")
        for s in sales:
            print(f"  - {s.sale_quantity} units on {s.sale_entry_date}")
        
        # Purchase Returns
        purchase_returns = ReturnPurchaseMaster.objects.filter(
            returnproductid=product,
            returnproduct_batch_no=batch_no
        )
        pr_qty = purchase_returns.aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        print(f"Purchase Returns: {pr_qty}")
        for pr in purchase_returns:
            print(f"  - {pr.returnproduct_quantity} units on {pr.returnpurchase_entry_date}")
        
        # Sales Returns
        sales_returns = ReturnSalesMaster.objects.filter(
            return_productid=product,
            return_product_batch_no=batch_no
        )
        sr_qty = sales_returns.aggregate(total=Sum('return_sale_quantity'))['total'] or 0
        print(f"Sales Returns: {sr_qty}")
        for sr in sales_returns:
            print(f"  - {sr.return_sale_quantity} units on {sr.return_sale_entry_date}")
        
        # Calculate batch stock
        batch_stock = purchased_qty - sold_qty - pr_qty + sr_qty
        print(f"Batch Stock: {purchased_qty} - {sold_qty} - {pr_qty} + {sr_qty} = {batch_stock}")
        
        total_stock_check += batch_stock
        print()
    
    print(f"Total Stock (sum of all batches): {total_stock_check}")
    
    # Compare with StockManager
    stock_summary = StockManager.get_stock_summary(product.productid)
    print(f"StockManager Total Stock: {stock_summary['total_stock']}")
    
    if total_stock_check == stock_summary['total_stock']:
        print("SUCCESS: Batch sum matches total stock!")
    else:
        print("ERROR: Batch sum does not match total stock!")

if __name__ == "__main__":
    debug_paracetamol_batches()