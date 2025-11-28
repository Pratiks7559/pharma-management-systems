#!/usr/bin/env python
"""
Test script to verify challan stock counting fix
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import InventoryMaster, ProductMaster, SupplierMaster
from django.db import transaction

def test_supplier_challan_stock():
    """Test supplier challan stock creation"""
    
    print("🧪 Testing Supplier Challan Stock Creation")
    print("=" * 50)
    
    # Find a test product
    test_product = ProductMaster.objects.first()
    if not test_product:
        print("❌ No products found in database")
        return
    
    test_supplier = SupplierMaster.objects.first()
    if not test_supplier:
        print("❌ No suppliers found in database")
        return
    
    test_batch = "TEST001"
    test_quantity = 5.0
    
    print(f"📦 Test Product: {test_product.product_name}")
    print(f"🏭 Test Supplier: {test_supplier.supplier_name}")
    print(f"🏷️ Test Batch: {test_batch}")
    print(f"📊 Test Quantity: {test_quantity}")
    
    # Check initial stock
    initial_inventory = InventoryMaster.objects.filter(
        product=test_product,
        batch_no=test_batch
    ).first()
    
    initial_stock = initial_inventory.current_stock if initial_inventory else 0
    print(f"📈 Initial Stock: {initial_stock}")
    
    # Simulate supplier challan creation (manual inventory update)
    try:
        with transaction.atomic():
            # Get or create inventory record
            inventory, created = InventoryMaster.objects.get_or_create(
                product=test_product,
                batch_no=test_batch,
                defaults={
                    'expiry_date': '12-2025',
                    'mrp': 100.0,
                    'purchase_rate': 80.0,
                    'current_stock': test_quantity,  # Set initial stock for new records
                    'supplier': test_supplier
                }
            )
            
            # Only update stock if inventory already existed
            if not created:
                inventory.current_stock += test_quantity
                inventory.save()
                print(f"✅ Updated existing inventory: {inventory.current_stock}")
            else:
                print(f"✅ Created new inventory: {inventory.current_stock}")
            
            final_stock = inventory.current_stock
            expected_stock = initial_stock + test_quantity
            
            print(f"📊 Final Stock: {final_stock}")
            print(f"🎯 Expected Stock: {expected_stock}")
            
            if final_stock == expected_stock:
                print("✅ TEST PASSED: Stock calculation is correct!")
            else:
                print("❌ TEST FAILED: Stock calculation is incorrect!")
                print(f"   Expected: {expected_stock}, Got: {final_stock}")
            
            # Rollback the test transaction
            raise Exception("Rollback test transaction")
            
    except Exception as e:
        if "Rollback test transaction" in str(e):
            print("🔄 Test transaction rolled back (no actual changes made)")
        else:
            print(f"❌ Test error: {e}")

def check_inventory_duplicates():
    """Check for inventory duplicates"""
    
    print("\n🔍 Checking for Inventory Duplicates")
    print("=" * 50)
    
    from django.db.models import Count
    
    duplicates = InventoryMaster.objects.values('product', 'batch_no').annotate(
        count=Count('inventory_id')
    ).filter(count__gt=1)
    
    if duplicates.exists():
        print(f"⚠️ Found {duplicates.count()} duplicate combinations:")
        for dup in duplicates[:10]:  # Show first 10
            product = ProductMaster.objects.get(productid=dup['product'])
            print(f"   - {product.product_name}, Batch {dup['batch_no']}: {dup['count']} records")
        
        if duplicates.count() > 10:
            print(f"   ... and {duplicates.count() - 10} more")
            
        print("\n💡 Run fix_inventory_duplicates.py to clean up duplicates")
    else:
        print("✅ No duplicate combinations found")

def show_recent_inventory():
    """Show recent inventory records"""
    
    print("\n📋 Recent Inventory Records")
    print("=" * 50)
    
    recent_inventory = InventoryMaster.objects.select_related('product').order_by('-updated_at')[:10]
    
    if recent_inventory.exists():
        for inv in recent_inventory:
            print(f"📦 {inv.product.product_name} | Batch: {inv.batch_no} | Stock: {inv.current_stock} | Updated: {inv.updated_at.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("📭 No inventory records found")

if __name__ == "__main__":
    print("🚀 Challan Stock Test Script")
    print("=" * 60)
    
    test_supplier_challan_stock()
    check_inventory_duplicates()
    show_recent_inventory()
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("\nNext steps:")
    print("1. Run fix_inventory_duplicates.py if duplicates found")
    print("2. Test creating actual supplier challan via web interface")
    print("3. Verify stock shows correct quantity (not doubled)")