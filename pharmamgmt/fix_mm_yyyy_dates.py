#!/usr/bin/env python
"""
Fix MM-YYYY format dates in database
Converts MM-YYYY to YYYY-MM-DD format to prevent validation errors
"""

import os
import sys
import django
import calendar
from datetime import date

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster

def normalize_mm_yyyy_date(date_str):
    """Convert MM-YYYY to YYYY-MM-DD format"""
    if not date_str:
        return date_str
    
    try:
        date_str = str(date_str).strip()
        
        # Check if it's MM-YYYY format
        if '-' in date_str and len(date_str.split('-')) == 2:
            parts = date_str.split('-')
            if len(parts[0]) <= 2 and len(parts[1]) == 4:  # MM-YYYY
                month, year = int(parts[0]), int(parts[1])
                # Convert to last day of month
                last_day = calendar.monthrange(year, month)[1]
                return f"{year}-{month:02d}-{last_day:02d}"
        
        return date_str
    except Exception as e:
        print(f"Error normalizing date '{date_str}': {e}")
        return date_str

def fix_purchase_dates():
    """Fix expiry dates in PurchaseMaster"""
    print("Fixing PurchaseMaster expiry dates...")
    
    purchases = PurchaseMaster.objects.all()
    fixed_count = 0
    
    for purchase in purchases:
        original_expiry = purchase.product_expiry
        if original_expiry and '-' in str(original_expiry):
            normalized = normalize_mm_yyyy_date(original_expiry)
            if normalized != str(original_expiry):
                purchase.product_expiry = normalized
                purchase.save()
                fixed_count += 1
                print(f"Fixed: {original_expiry} -> {normalized}")
    
    print(f"Fixed {fixed_count} purchase records")

def fix_sales_dates():
    """Fix expiry dates in SalesMaster"""
    print("Fixing SalesMaster expiry dates...")
    
    sales = SalesMaster.objects.all()
    fixed_count = 0
    
    for sale in sales:
        original_expiry = sale.product_expiry
        if original_expiry and '-' in str(original_expiry):
            normalized = normalize_mm_yyyy_date(original_expiry)
            if normalized != str(original_expiry):
                sale.product_expiry = normalized
                sale.save()
                fixed_count += 1
                print(f"Fixed: {original_expiry} -> {normalized}")
    
    print(f"Fixed {fixed_count} sales records")

def fix_return_purchase_dates():
    """Fix expiry dates in ReturnPurchaseMaster"""
    print("Fixing ReturnPurchaseMaster expiry dates...")
    
    returns = ReturnPurchaseMaster.objects.all()
    fixed_count = 0
    
    for return_item in returns:
        original_expiry = return_item.returnproduct_expiry
        if original_expiry and '-' in str(original_expiry):
            normalized = normalize_mm_yyyy_date(original_expiry)
            if normalized != str(original_expiry):
                return_item.returnproduct_expiry = normalized
                return_item.save()
                fixed_count += 1
                print(f"Fixed: {original_expiry} -> {normalized}")
    
    print(f"Fixed {fixed_count} purchase return records")

def fix_return_sales_dates():
    """Fix expiry dates in ReturnSalesMaster"""
    print("Fixing ReturnSalesMaster expiry dates...")
    
    returns = ReturnSalesMaster.objects.all()
    fixed_count = 0
    
    for return_item in returns:
        original_expiry = return_item.return_product_expiry
        if original_expiry and '-' in str(original_expiry):
            normalized = normalize_mm_yyyy_date(original_expiry)
            if normalized != str(original_expiry):
                return_item.return_product_expiry = normalized
                return_item.save()
                fixed_count += 1
                print(f"Fixed: {original_expiry} -> {normalized}")
    
    print(f"Fixed {fixed_count} sales return records")

def main():
    """Main function to fix all MM-YYYY dates"""
    print("Starting MM-YYYY date format fix...")
    
    try:
        fix_purchase_dates()
        fix_sales_dates()
        fix_return_purchase_dates()
        fix_return_sales_dates()
        
        print("\nAll MM-YYYY dates have been normalized to YYYY-MM-DD format!")
        print("This should resolve the date validation errors.")
        
    except Exception as e:
        print(f"Error during date fix: {e}")

if __name__ == "__main__":
    main()