#!/usr/bin/env python
"""
Script to fix inventory duplicate entries and stock counting issues
Run this script to clean up inventory master table
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import InventoryMaster, SupplierChallanMaster, CustomerChallanMaster, PurchaseMaster, SalesMaster
from django.db.models import Sum
from django.db import transaction

def fix_inventory_duplicates():
    """Fix duplicate inventory entries and recalculate stock"""
    
    print("🔧 Starting inventory duplicate fix...")
    
    # Get all unique product-batch combinations
    unique_combinations = set()
    
    # From supplier challans
    supplier_challans = SupplierChallanMaster.objects.all()
    for challan in supplier_challans:
        unique_combinations.add((challan.product_id.productid, challan.product_batch_no))
    
    # From customer challans  
    customer_challans = CustomerChallanMaster.objects.all()
    for challan in customer_challans:
        unique_combinations.add((challan.product_id.productid, challan.product_batch_no))
    
    # From purchases
    purchases = PurchaseMaster.objects.all()
    for purchase in purchases:
        unique_combinations.add((purchase.productid.productid, purchase.product_batch_no))
    
    # From sales
    sales = SalesMaster.objects.all()
    for sale in sales:
        unique_combinations.add((sale.productid.productid, sale.product_batch_no))
    
    print(f"📊 Found {len(unique_combinations)} unique product-batch combinations")
    
    fixed_count = 0
    
    with transaction.atomic():
        for product_id, batch_no in unique_combinations:
            try:
                # Find all inventory records for this product-batch combination
                inventory_records = InventoryMaster.objects.filter(
                    product_id=product_id,
                    batch_no=batch_no
                )
                
                if inventory_records.count() > 1:
                    print(f"🔍 Found {inventory_records.count()} duplicate records for Product ID {product_id}, Batch {batch_no}")
                    
                    # Keep the first record and merge others into it
                    primary_record = inventory_records.first()
                    duplicate_records = inventory_records.exclude(inventory_id=primary_record.inventory_id)
                    
                    # Sum up all stock from duplicates
                    total_stock = sum(record.current_stock for record in inventory_records)
                    
                    # Delete duplicates
                    duplicate_records.delete()
                    
                    # Update primary record with correct stock
                    primary_record.current_stock = total_stock
                    primary_record.save()
                    
                    print(f"✅ Merged duplicates for Product ID {product_id}, Batch {batch_no}. Total stock: {total_stock}")
                    fixed_count += 1
                
                elif inventory_records.count() == 1:
                    # Recalculate stock for single records
                    inventory = inventory_records.first()
                    
                    # Calculate correct stock from transactions
                    supplier_stock = SupplierChallanMaster.objects.filter(
                        product_id_id=product_id,
                        product_batch_no=batch_no
                    ).aggregate(total=Sum('product_quantity'))['total'] or 0
                    
                    purchase_stock = PurchaseMaster.objects.filter(
                        productid_id=product_id,
                        product_batch_no=batch_no
                    ).aggregate(total=Sum('product_quantity'))['total'] or 0
                    
                    customer_stock = CustomerChallanMaster.objects.filter(
                        product_id_id=product_id,
                        product_batch_no=batch_no
                    ).aggregate(total=Sum('sale_quantity'))['total'] or 0
                    
                    sales_stock = SalesMaster.objects.filter(
                        productid_id=product_id,
                        product_batch_no=batch_no
                    ).aggregate(total=Sum('sale_quantity'))['total'] or 0
                    
                    # Calculate correct stock: (Purchases + Supplier Challans) - (Sales + Customer Challans)
                    correct_stock = (supplier_stock + purchase_stock) - (customer_stock + sales_stock)
                    correct_stock = max(0, correct_stock)  # Ensure non-negative
                    
                    if inventory.current_stock != correct_stock:
                        print(f"🔧 Correcting stock for Product ID {product_id}, Batch {batch_no}: {inventory.current_stock} → {correct_stock}")
                        inventory.current_stock = correct_stock
                        inventory.save()
                        fixed_count += 1
                
            except Exception as e:
                print(f"❌ Error processing Product ID {product_id}, Batch {batch_no}: {e}")
                continue
    
    print(f"✅ Fixed {fixed_count} inventory records")
    print("🎉 Inventory duplicate fix completed!")

def verify_inventory_integrity():
    """Verify inventory integrity after fix"""
    
    print("\n🔍 Verifying inventory integrity...")
    
    # Check for remaining duplicates
    from django.db.models import Count
    duplicates = InventoryMaster.objects.values('product', 'batch_no').annotate(
        count=Count('inventory_id')
    ).filter(count__gt=1)
    
    if duplicates.exists():
        print(f"⚠️ Still found {duplicates.count()} duplicate combinations")
        for dup in duplicates:
            print(f"   - Product ID {dup['product']}, Batch {dup['batch_no']}: {dup['count']} records")
    else:
        print("✅ No duplicate combinations found")
    
    # Check for negative stock
    negative_stock = InventoryMaster.objects.filter(current_stock__lt=0)
    if negative_stock.exists():
        print(f"⚠️ Found {negative_stock.count()} records with negative stock")
        for inv in negative_stock[:5]:  # Show first 5
            print(f"   - Product ID {inv.product.productid}, Batch {inv.batch_no}: {inv.current_stock}")
    else:
        print("✅ No negative stock found")
    
    print("🔍 Verification completed!")

if __name__ == "__main__":
    print("🚀 Starting Inventory Fix Script")
    print("=" * 50)
    
    fix_inventory_duplicates()
    verify_inventory_integrity()
    
    print("\n" + "=" * 50)
    print("✅ Script completed successfully!")
    print("\nNext steps:")
    print("1. Test creating a new supplier challan")
    print("2. Verify stock shows correct quantity (1 instead of 2)")
    print("3. Check inventory master table for accurate stock levels")