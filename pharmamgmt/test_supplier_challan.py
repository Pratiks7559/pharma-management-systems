import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import SupplierMaster, ProductMaster, Challan1, SupplierChallanMaster
from datetime import datetime, timedelta
import random

def test_supplier_challan():
    """Test supplier challan creation"""
    
    print("=" * 60)
    print("SUPPLIER CHALLAN TEST")
    print("=" * 60)
    
    # Get or create supplier
    supplier = SupplierMaster.objects.first()
    if not supplier:
        print("❌ No supplier found. Creating test supplier...")
        supplier = SupplierMaster.objects.create(
            supplier_name="Test Supplier",
            supplier_mobile="9999999999",
            supplier_type="Wholesaler"
        )
        print(f"✅ Created supplier: {supplier.supplier_name}")
    else:
        print(f"✅ Using supplier: {supplier.supplier_name}")
    
    # Get products
    products = list(ProductMaster.objects.all()[:5])
    if not products:
        print("❌ No products found. Please add products first.")
        return
    
    print(f"✅ Found {len(products)} products")
    
    # Create challan
    challan_no = f"CH{datetime.now().strftime('%Y%m%d%H%M%S')}"
    challan_date = datetime.now().date()
    
    print(f"\n📝 Creating Challan: {challan_no}")
    
    challan = Challan1.objects.create(
        challan_no=challan_no,
        challan_date=challan_date,
        supplier=supplier,
        challan_total=0,
        transport_charges=50,
        challan_paid=0,
        challan_remark="Test challan"
    )
    
    print(f"✅ Challan created: {challan.challan_no}")
    
    # Add challan items
    total_amount = 0
    print(f"\n📦 Adding {len(products)} items to challan:")
    
    for product in products:
        qty = random.randint(10, 50)
        rate = random.uniform(50, 500)
        mrp = rate * 1.3
        discount = random.uniform(0, 10)
        
        actual_rate = rate - discount
        total = qty * actual_rate
        total_amount += total
        
        item = SupplierChallanMaster.objects.create(
            product_suppliername=supplier,
            product_challan_id=challan,
            product_challan_no=challan_no,
            product_id=product,
            product_name=product.product_name,
            product_company=product.product_company,
            product_packing=product.product_packing,
            product_batch_no=f"B{random.randint(1000, 9999)}",
            product_expiry=f"{random.randint(1, 12):02d}-{random.randint(2025, 2027)}",
            product_mrp=mrp,
            product_purchase_rate=rate,
            product_quantity=qty,
            product_scheme=0,
            product_discount=discount,
            product_transportation_charges=0,
            actual_rate_per_qty=actual_rate,
            product_actual_rate=actual_rate,
            total_amount=total,
            cgst=2.5,
            sgst=2.5,
            challan_calculation_mode='flat',
            rate_a=mrp * 0.95,
            rate_b=mrp * 0.90,
            rate_c=mrp * 0.85
        )
        
        print(f"  ✅ {product.product_name[:30]:30} | Qty: {qty:3} | Rate: ₹{rate:6.2f} | Total: ₹{total:8.2f}")
    
    # Update challan total
    challan.challan_total = total_amount
    challan.save()
    
    print(f"\n💰 Challan Total: ₹{total_amount:.2f}")
    print(f"🚚 Transport Charges: ₹{challan.transport_charges:.2f}")
    print(f"💵 Grand Total: ₹{total_amount + challan.transport_charges:.2f}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Challan No: {challan.challan_no}")
    print(f"Supplier: {supplier.supplier_name}")
    print(f"Items: {len(products)}")
    print(f"Total Amount: ₹{total_amount:.2f}")
    print(f"Status: {'Invoiced' if challan.is_invoiced else 'Pending'}")
    print("=" * 60)
    print("✅ TEST COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    test_supplier_challan()
