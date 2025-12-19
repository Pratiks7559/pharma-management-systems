import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import *
import time

def clean_test_data():
    """Delete all test data created by test_complete.py"""
    print("\n" + "="*60)
    print("CLEANING TEST DATA")
    print("="*60)
    
    start = time.time()
    
    # Delete test suppliers
    print("\n🗑️  Deleting test suppliers...")
    deleted = SupplierMaster.objects.filter(supplier_name__startswith='TestSupplier_').delete()
    print(f"   Deleted: {deleted[0]} suppliers")
    
    # Delete test customers
    print("🗑️  Deleting test customers...")
    deleted = CustomerMaster.objects.filter(customer_name__startswith='TestCustomer_').delete()
    print(f"   Deleted: {deleted[0]} customers")
    
    # Delete test products
    print("🗑️  Deleting test products...")
    deleted = ProductMaster.objects.filter(product_name__startswith='TestProduct_').delete()
    print(f"   Deleted: {deleted[0]} products")
    
    # Delete test purchase invoices
    print("🗑️  Deleting test purchase invoices...")
    deleted = InvoiceMaster.objects.filter(invoice_no__startswith='TPI').delete()
    print(f"   Deleted: {deleted[0]} purchase invoices")
    
    # Delete test sales invoices
    print("🗑️  Deleting test sales invoices...")
    deleted = SalesInvoiceMaster.objects.filter(sales_invoice_no__startswith='TSI').delete()
    print(f"   Deleted: {deleted[0]} sales invoices")
    
    # Delete orphaned payments
    print("🗑️  Cleaning orphaned payments...")
    deleted = InvoicePaid.objects.filter(ip_invoiceid__isnull=True).delete()
    print(f"   Deleted: {deleted[0]} orphaned payments")
    
    # Delete orphaned receipts
    print("🗑️  Cleaning orphaned receipts...")
    deleted = SalesInvoicePaid.objects.filter(sales_ip_invoice_no__isnull=True).delete()
    print(f"   Deleted: {deleted[0]} orphaned receipts")
    
    elapsed = time.time() - start
    
    print("\n" + "="*60)
    print(f"✅ CLEANUP COMPLETED in {elapsed:.2f}s")
    print("="*60)
    print("\n💡 Your database is now clean!")

def clean_all_test_data_aggressive():
    """Aggressive cleanup - deletes ALL test-related data"""
    print("\n" + "="*60)
    print("⚠️  AGGRESSIVE CLEANUP - DELETING ALL TEST DATA")
    print("="*60)
    
    confirm = input("\n⚠️  This will delete ALL test data. Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Cleanup cancelled")
        return
    
    start = time.time()
    
    # Delete in correct order to avoid foreign key issues
    tables = [
        ('ContraEntry', ContraEntry, None),
        ('SalesInvoicePaid', SalesInvoicePaid, None),
        ('InvoicePaid', InvoicePaid, None),
        ('SalesMaster', SalesMaster, None),
        ('PurchaseMaster', PurchaseMaster, None),
        ('SalesInvoiceMaster', SalesInvoiceMaster, 'sales_invoice_no__startswith'),
        ('InvoiceMaster', InvoiceMaster, 'invoice_no__startswith'),
        ('ProductMaster', ProductMaster, 'product_name__startswith'),
        ('CustomerMaster', CustomerMaster, 'customer_name__startswith'),
        ('SupplierMaster', SupplierMaster, 'supplier_name__startswith'),
    ]
    
    total_deleted = 0
    for name, model, filter_field in tables:
        try:
            if filter_field:
                if 'supplier' in filter_field:
                    deleted = model.objects.filter(**{filter_field: 'TestSupplier_'}).delete()
                elif 'customer' in filter_field:
                    deleted = model.objects.filter(**{filter_field: 'TestCustomer_'}).delete()
                elif 'product' in filter_field:
                    deleted = model.objects.filter(**{filter_field: 'TestProduct_'}).delete()
                elif 'invoice_no' in filter_field:
                    deleted = model.objects.filter(Q(**{filter_field: 'TPI'}) | Q(**{filter_field: 'TSI'})).delete()
                else:
                    continue
            else:
                # For related tables, they'll be deleted via CASCADE
                continue
            
            print(f"🗑️  {name}: {deleted[0]} records")
            total_deleted += deleted[0]
        except Exception as e:
            print(f"⚠️  {name}: {e}")
    
    elapsed = time.time() - start
    
    print("\n" + "="*60)
    print(f"✅ AGGRESSIVE CLEANUP COMPLETED")
    print(f"   Total deleted: {total_deleted:,} records")
    print(f"   Time taken: {elapsed:.2f}s")
    print("="*60)

if __name__ == '__main__':
    import sys
    
    print("\n" + "="*60)
    print("TEST DATA CLEANUP UTILITY")
    print("="*60)
    print("\nOptions:")
    print("1. Clean test data (safe)")
    print("2. Aggressive cleanup (deletes everything)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        clean_test_data()
    elif choice == '2':
        clean_all_test_data_aggressive()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")
