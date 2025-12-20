"""
FASTEST way to delete ALL test data from database
Run: python delete_all_test_data_fast.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.db import connection

def delete_all_test_data():
    """Delete all test/demo data - FASTEST method using raw SQL"""
    
    print("⚠️  WARNING: This will delete ALL transaction data!")
    print("This will keep: Products, Suppliers, Customers, Users")
    print("This will delete: Invoices, Sales, Purchases, Returns, Challans, Payments, Cache")
    
    confirm = input("\nType 'DELETE ALL' to confirm: ")
    if confirm != 'DELETE ALL':
        print("❌ Cancelled")
        return
    
    with connection.cursor() as cursor:
        print("\n🗑️  Deleting data...")
        
        # Delete in correct order (child tables first)
        tables = [
            # Payments
            ('core_invoicepaid', 'Invoice Payments'),
            ('core_salesinvoicepaid', 'Sales Payments'),
            ('core_purchasereturnvoicepaid', 'Purchase Return Payments'),
            ('core_returnsalesinvoicepaid', 'Sales Return Payments'),
            
            # Transaction Details
            ('core_purchasemaster', 'Purchases'),
            ('core_salesmaster', 'Sales'),
            ('core_returnpurchasemaster', 'Purchase Returns'),
            ('core_returnsalesmaster', 'Sales Returns'),
            ('supplier_challan_master', 'Supplier Challan Items'),
            ('customer_challan_master', 'Customer Challan Items'),
            ('core_stockissuedetail', 'Stock Issue Details'),
            
            # Master Transactions
            ('core_invoicemaster', 'Purchase Invoices'),
            ('core_salesinvoicemaster', 'Sales Invoices'),
            ('core_returninvoicemaster', 'Purchase Return Invoices'),
            ('core_returnsalesinvoicemaster', 'Sales Return Invoices'),
            ('challan1', 'Supplier Challans'),
            ('customer_challan', 'Customer Challans'),
            ('core_stockissuemaster', 'Stock Issues'),
            ('core_contraentry', 'Contra Entries'),
            
            # Rates & Cache
            ('core_saleratemaster', 'Sale Rates'),
            ('batch_inventory_cache', 'Batch Cache'),
            ('product_inventory_cache', 'Product Cache'),
        ]
        
        total_deleted = 0
        for table, name in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                deleted = cursor.rowcount
                total_deleted += deleted
                print(f"✅ {name}: {deleted} records")
            except Exception as e:
                print(f"⚠️  {name}: {e}")
        
        print(f"\n✅ Total deleted: {total_deleted} records")
        print("✅ Database cleaned successfully!")
        print("\n📝 Kept: Products, Suppliers, Customers, Users")

if __name__ == '__main__':
    delete_all_test_data()
