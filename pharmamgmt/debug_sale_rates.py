#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import SaleRateMaster, ProductMaster, PurchaseMaster

def debug_sale_rates():
    print("=== DEBUGGING SALE RATES ===")
    
    # Check total records
    total_rates = SaleRateMaster.objects.count()
    print(f"Total SaleRateMaster records: {total_rates}")
    
    if total_rates > 0:
        print("\nSample records:")
        for rate in SaleRateMaster.objects.all()[:10]:
            print(f"ID: {rate.id}, Product: {rate.productid.product_name}, Batch: {rate.product_batch_no}, Rate A: {rate.rate_A}, Rate B: {rate.rate_B}, Rate C: {rate.rate_C}")
    else:
        print("No SaleRateMaster records found!")
        
        # Check if we have products and purchases
        products_count = ProductMaster.objects.count()
        purchases_count = PurchaseMaster.objects.count()
        
        print(f"Total Products: {products_count}")
        print(f"Total Purchases: {purchases_count}")
        
        if purchases_count > 0:
            print("\nSample purchase records with batches:")
            for purchase in PurchaseMaster.objects.all()[:5]:
                print(f"Product: {purchase.productid.product_name}, Batch: {purchase.product_batch_no}, MRP: {purchase.product_MRP}")

if __name__ == "__main__":
    debug_sale_rates()