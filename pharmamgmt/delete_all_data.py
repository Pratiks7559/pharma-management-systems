"""
Delete ALL data from database tables (except users)
Run: python delete_all_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.db import connection

def delete_all_data():
    print("⚠️  WARNING: This will delete ALL DATA from database!")
    print("Only Users table will be kept.")
    confirm = input("\nType 'YES DELETE ALL' to confirm: ")
    
    if confirm != 'YES DELETE ALL':
        print("❌ Cancelled")
        return
    
    with connection.cursor() as cursor:
        print("\n🗑️  Deleting all data...")
        
        # Disable foreign key checks
        cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
        
        tables = [
            'core_invoicepaid',
            'core_salesinvoicepaid', 
            'core_purchasereturnvoicepaid',
            'core_returnsalesinvoicepaid',
            'core_purchasemaster',
            'core_salesmaster',
            'core_returnpurchasemaster',
            'core_returnsalesmaster',
            'supplier_challan_master',
            'supplier_challan_master2',
            'customer_challan_master',
            'customer_challan_master2',
            'core_stockissuedetail',
            'core_invoicemaster',
            'core_salesinvoicemaster',
            'core_returninvoicemaster',
            'core_returnsalesinvoicemaster',
            'challan1',
            'customer_challan',
            'core_stockissuemaster',
            'core_contraentry',
            'core_saleratemaster',
            'core_productratemaster',
            'batch_inventory_cache',
            'product_inventory_cache',
            'core_invoiceseries',
            'core_challanseries',
            'core_productmaster',
            'core_suppliermaster',
            'core_customermaster',
            'core_pharmacy_details',
        ]
        
        total = 0
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                count = cursor.rowcount
                total += count
                print(f"✅ {table}: {count}")
            except Exception as e:
                print(f"⚠️  {table}: {e}")
        
        print(f"\n✅ Total deleted: {total:,} records")
        print("✅ Database cleaned!")

if __name__ == '__main__':
    delete_all_data()
