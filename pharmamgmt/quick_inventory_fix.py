#!/usr/bin/env python
"""
Quick fix script for inventory display issues
Run this script to fix all common inventory display problems
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
from django.db.models import Avg, Count
from django.db import transaction

def main():
    """Main function to fix all inventory display issues"""
    print("🔧 QUICK INVENTORY DISPLAY FIX")
    print("=" * 50)
    
    # Step 1: Check database status
    print("\n📊 Checking database status...")
    total_products = ProductMaster.objects.count()
    products_with_purchases = ProductMaster.objects.filter(purchasemaster__isnull=False).distinct().count()
    products_with_rates = ProductMaster.objects.filter(saleratemaster__isnull=False).distinct().count()
    
    print(f"   Total Products: {total_products}")
    print(f"   Products with Purchases: {products_with_purchases}")
    print(f"   Products with Sale Rates: {products_with_rates}")
    
    if total_products == 0:
        print("❌ No products found! Please add some products first.")
        return
    
    # Step 2: Fix missing sale rates
    print("\n🔨 Fixing missing sale rates...")
    fixed_rates = fix_missing_sale_rates()
    
    # Step 3: Update zero rates
    print("\n🔄 Updating zero/invalid rates...")
    updated_rates = update_zero_rates()
    
    # Step 4: Verify fixes
    print("\n✅ Verifying fixes...")
    verify_fixes()
    
    # Step 5: Summary
    print(f"\n🎉 SUMMARY")
    print(f"   Sale rates created: {fixed_rates}")
    print(f"   Rates updated: {updated_rates}")
    print(f"   Total products now have rates: {ProductMaster.objects.filter(saleratemaster__isnull=False).distinct().count()}")
    
    print("\n✅ Inventory display fix completed!")
    print("   Now refresh your browser and check the inventory/product list pages.")

def fix_missing_sale_rates():
    """Create missing sale rates for products with purchases"""
    fixed_count = 0
    
    # Get products with purchases but missing rates
    products_needing_rates = []
    
    for product in ProductMaster.objects.filter(purchasemaster__isnull=False).distinct():
        # Get unique batches for this product
        batches = PurchaseMaster.objects.filter(
            productid=product.productid
        ).values('product_batch_no').distinct()
        
        for batch_info in batches:
            batch_no = batch_info['product_batch_no']
            
            # Check if rate exists for this batch
            if not SaleRateMaster.objects.filter(
                productid=product.productid,
                product_batch_no=batch_no
            ).exists():
                products_needing_rates.append((product, batch_no))
    
    print(f"   Found {len(products_needing_rates)} product-batch combinations needing rates")
    
    # Create rates in batches for better performance
    with transaction.atomic():
        for product, batch_no in products_needing_rates:
            try:
                # Get average MRP for this batch
                avg_mrp = PurchaseMaster.objects.filter(
                    productid=product.productid,
                    product_batch_no=batch_no
                ).aggregate(avg_mrp=Avg('product_MRP'))['avg_mrp'] or 0
                
                if avg_mrp > 0:
                    # Create tiered rates
                    rate_A = round(avg_mrp, 2)  # Retail (MRP)
                    rate_B = round(avg_mrp * 0.95, 2)  # Regular customer (5% discount)
                    rate_C = round(avg_mrp * 0.90, 2)  # Wholesale (10% discount)
                    
                    SaleRateMaster.objects.create(
                        productid=product,
                        product_batch_no=batch_no,
                        rate_A=rate_A,
                        rate_B=rate_B,
                        rate_C=rate_C
                    )
                    
                    fixed_count += 1
                    if fixed_count % 10 == 0:
                        print(f"   Created {fixed_count} rate records...")
                        
            except Exception as e:
                print(f"   ⚠️  Error creating rate for {product.product_name} - {batch_no}: {e}")
    
    return fixed_count

def update_zero_rates():
    """Update existing rates that have zero values"""
    updated_count = 0
    
    # Find rates with all zero values
    zero_rates = SaleRateMaster.objects.filter(
        rate_A__lte=0, rate_B__lte=0, rate_C__lte=0
    )
    
    print(f"   Found {zero_rates.count()} rate records with zero/negative values")
    
    with transaction.atomic():
        for rate_record in zero_rates:
            try:
                # Get average MRP for this product-batch combination
                avg_mrp = PurchaseMaster.objects.filter(
                    productid=rate_record.productid,
                    product_batch_no=rate_record.product_batch_no
                ).aggregate(avg_mrp=Avg('product_MRP'))['avg_mrp'] or 0
                
                if avg_mrp > 0:
                    # Update with proper rates
                    rate_record.rate_A = round(avg_mrp, 2)
                    rate_record.rate_B = round(avg_mrp * 0.95, 2)
                    rate_record.rate_C = round(avg_mrp * 0.90, 2)
                    rate_record.save()
                    
                    updated_count += 1
                    
            except Exception as e:
                print(f"   ⚠️  Error updating rate: {e}")
    
    return updated_count

def verify_fixes():
    """Verify that fixes were applied correctly"""
    
    # Check products with complete data
    complete_products = 0
    incomplete_products = []
    
    for product in ProductMaster.objects.filter(purchasemaster__isnull=False).distinct()[:10]:
        has_rates = SaleRateMaster.objects.filter(productid=product.productid).exists()
        has_mrp = PurchaseMaster.objects.filter(
            productid=product.productid, 
            product_MRP__gt=0
        ).exists()
        
        if has_rates and has_mrp:
            complete_products += 1
        else:
            incomplete_products.append({
                'name': product.product_name,
                'has_rates': has_rates,
                'has_mrp': has_mrp
            })
    
    print(f"   Products with complete data: {complete_products}/10 (sample)")
    
    if incomplete_products:
        print(f"   Products still missing data:")
        for prod in incomplete_products[:3]:
            print(f"     - {prod['name']}: Rates={prod['has_rates']}, MRP={prod['has_mrp']}")
    
    # Check rate distribution
    rate_stats = SaleRateMaster.objects.aggregate(
        total_rates=Count('id'),
        valid_rates=Count('id', filter=django.db.models.Q(rate_A__gt=0))
    )
    
    print(f"   Total rate records: {rate_stats['total_rates']}")
    print(f"   Valid rate records: {rate_stats['valid_rates']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running fix: {e}")
        print("Please check your Django setup and database connection.")