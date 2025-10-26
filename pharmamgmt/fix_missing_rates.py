#!/usr/bin/env python
"""
Script to fix missing sale rates for products with purchases
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import ProductMaster, PurchaseMaster, SaleRateMaster
from django.db.models import Avg

def fix_missing_sale_rates():
    """Create missing sale rates for products that have purchases but no rates"""
    print("=== FIXING MISSING SALE RATES ===\n")
    
    # Find products with purchases but no sale rates
    products_with_purchases = ProductMaster.objects.filter(
        purchasemaster__isnull=False
    ).distinct()
    
    print(f"Found {products_with_purchases.count()} products with purchases")
    
    fixed_count = 0
    skipped_count = 0
    
    for product in products_with_purchases:
        # Get all unique batches for this product
        batches = PurchaseMaster.objects.filter(
            productid=product.productid
        ).values('product_batch_no').distinct()
        
        for batch_info in batches:
            batch_no = batch_info['product_batch_no']
            
            # Check if sale rate already exists for this batch
            if SaleRateMaster.objects.filter(
                productid=product.productid,
                product_batch_no=batch_no
            ).exists():
                skipped_count += 1
                continue
            
            # Get average MRP for this batch
            avg_mrp = PurchaseMaster.objects.filter(
                productid=product.productid,
                product_batch_no=batch_no
            ).aggregate(avg_mrp=Avg('product_MRP'))['avg_mrp'] or 0
            
            if avg_mrp > 0:
                # Create sale rates based on MRP
                # Rate A = MRP (retail price)
                # Rate B = MRP * 0.95 (5% discount for regular customers)
                # Rate C = MRP * 0.90 (10% discount for wholesale customers)
                
                rate_A = round(avg_mrp, 2)
                rate_B = round(avg_mrp * 0.95, 2)
                rate_C = round(avg_mrp * 0.90, 2)
                
                try:
                    SaleRateMaster.objects.create(
                        productid=product,
                        product_batch_no=batch_no,
                        rate_A=rate_A,
                        rate_B=rate_B,
                        rate_C=rate_C
                    )
                    
                    print(f"✅ Created rates for {product.product_name} - Batch {batch_no}")
                    print(f"   Rate A: ₹{rate_A}, Rate B: ₹{rate_B}, Rate C: ₹{rate_C}")
                    fixed_count += 1
                    
                except Exception as e:
                    print(f"❌ Error creating rates for {product.product_name} - Batch {batch_no}: {e}")
            else:
                print(f"⚠️  Skipping {product.product_name} - Batch {batch_no} (No MRP found)")
    
    print(f"\n=== SUMMARY ===")
    print(f"Sale rates created: {fixed_count}")
    print(f"Already existing (skipped): {skipped_count}")
    print(f"✅ Missing sale rates fix completed!")

def update_existing_rates():
    """Update existing sale rates that might be zero or incorrect"""
    print("\n=== UPDATING EXISTING RATES ===\n")
    
    # Find sale rates with zero values
    zero_rates = SaleRateMaster.objects.filter(
        rate_A=0, rate_B=0, rate_C=0
    )
    
    print(f"Found {zero_rates.count()} sale rate records with zero values")
    
    updated_count = 0
    
    for rate_record in zero_rates:
        # Get average MRP for this product and batch
        avg_mrp = PurchaseMaster.objects.filter(
            productid=rate_record.productid,
            product_batch_no=rate_record.product_batch_no
        ).aggregate(avg_mrp=Avg('product_MRP'))['avg_mrp'] or 0
        
        if avg_mrp > 0:
            # Update rates based on MRP
            rate_record.rate_A = round(avg_mrp, 2)
            rate_record.rate_B = round(avg_mrp * 0.95, 2)
            rate_record.rate_C = round(avg_mrp * 0.90, 2)
            
            try:
                rate_record.save()
                print(f"✅ Updated rates for {rate_record.productid.product_name} - Batch {rate_record.product_batch_no}")
                updated_count += 1
            except Exception as e:
                print(f"❌ Error updating rates: {e}")
    
    print(f"\n✅ Updated {updated_count} existing rate records")

if __name__ == "__main__":
    fix_missing_sale_rates()
    update_existing_rates()
    
    print("\n🎉 All fixes completed! Your inventory should now display complete information.")