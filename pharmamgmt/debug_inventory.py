#!/usr/bin/env python
"""
Debug Inventory Script
Quick check of inventory status and recent transactions
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import (
    ProductMaster, InventoryMaster, StockIssueMaster, 
    StockIssueDetail, InventoryTransaction
)

def debug_paracetamol_inventory():
    """Debug Paracetamol inventory specifically"""
    print("DEBUGGING PARACETAMOL INVENTORY")
    print("=" * 50)
    
    # Find Paracetamol products
    paracetamol_products = ProductMaster.objects.filter(
        product_name__icontains='paracetamol'
    )
    
    print(f"Found {paracetamol_products.count()} Paracetamol products:")
    
    for product in paracetamol_products:
        print(f"\nProduct: {product.product_name} (ID: {product.productid})")
        print(f"   Company: {product.product_company}")
        
        # Get inventory for this product
        inventories = InventoryMaster.objects.filter(product=product)
        print(f"   Batches: {inventories.count()}")
        
        for inv in inventories:
            print(f"      Batch: {inv.batch_no} | Stock: {inv.current_stock} | Expiry: {inv.expiry_date}")
        
        # Get recent stock issues for this product
        recent_issues = StockIssueDetail.objects.filter(
            product=product
        ).order_by('-issue__created_at')[:5]
        
        print(f"   Recent Stock Issues: {recent_issues.count()}")
        for issue in recent_issues:
            print(f"      Issue: {issue.issue.issue_no} | Qty: {issue.quantity_issued} | Date: {issue.issue.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Get recent inventory transactions
        for inv in inventories:
            transactions = InventoryTransaction.objects.filter(
                inventory=inv
            ).order_by('-transaction_date')[:3]
            
            if transactions:
                print(f"   Recent Transactions for Batch {inv.batch_no}:")
                for trans in transactions:
                    print(f"      {trans.transaction_type} | Qty: {trans.quantity} | Ref: {trans.reference_type} | {trans.transaction_date.strftime('%Y-%m-%d %H:%M')}")

def debug_recent_stock_issues():
    """Debug recent stock issues"""
    print("\nRECENT STOCK ISSUES")
    print("=" * 50)
    
    recent_issues = StockIssueMaster.objects.all().order_by('-created_at')[:5]
    
    for issue in recent_issues:
        print(f"\nIssue: {issue.issue_no} | Type: {issue.get_issue_type_display()}")
        print(f"   Date: {issue.created_at.strftime('%Y-%m-%d %H:%M')} | Total Value: Rs.{issue.total_value}")
        
        details = issue.details.all()
        for detail in details:
            print(f"   - {detail.product.product_name} | Batch: {detail.batch_no} | Qty: {detail.quantity_issued}")

def debug_inventory_transactions():
    """Debug recent inventory transactions"""
    print("\nRECENT INVENTORY TRANSACTIONS")
    print("=" * 50)
    
    recent_transactions = InventoryTransaction.objects.all().order_by('-transaction_date')[:10]
    
    for trans in recent_transactions:
        print(f"{trans.transaction_date.strftime('%Y-%m-%d %H:%M')} | {trans.transaction_type}")
        print(f"   Product: {trans.inventory.product.product_name} | Batch: {trans.inventory.batch_no}")
        print(f"   Quantity: {trans.quantity} | Reference: {trans.reference_type} ({trans.reference_id})")
        print(f"   Remarks: {trans.remarks}")
        print()

if __name__ == "__main__":
    debug_paracetamol_inventory()
    debug_recent_stock_issues()
    debug_inventory_transactions()