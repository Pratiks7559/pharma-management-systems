import os
import django
import sys
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import (
    ProductMaster, CustomerMaster, SupplierMaster, 
    SalesMaster, PurchaseMaster, SalesInvoiceMaster, 
    InvoiceMaster, CustomerChallan, SupplierChallanMaster,
    SupplierChallanMaster2, CustomerChallanMaster, CustomerChallanMaster2,
    ReturnSalesMaster, ReturnPurchaseMaster, StockIssueMaster, StockIssueDetail
)

def delete_bulk_test_data():
    """Delete bulk test data from all tables"""
    
    print("Starting bulk data deletion...")
    
    try:
        with transaction.atomic():
            # Delete in proper order to avoid foreign key constraints
            
            # 1. Delete Stock Issue data
            print("Deleting stock issue data...")
            StockIssueDetail.objects.all().delete()
            StockIssueMaster.objects.all().delete()
            
            # 2. Delete Sales related data
            print("Deleting sales data...")
            ReturnSalesMaster.objects.all().delete()
            SalesMaster.objects.all().delete()
            SalesInvoiceMaster.objects.all().delete()
            
            # 3. Delete Purchase related data
            print("Deleting purchase data...")
            ReturnPurchaseMaster.objects.all().delete()
            PurchaseMaster.objects.all().delete()
            InvoiceMaster.objects.all().delete()
            
            # 4. Delete Challan data
            print("Deleting challan data...")
            CustomerChallanMaster.objects.all().delete()
            CustomerChallanMaster2.objects.all().delete()
            CustomerChallan.objects.all().delete()
            SupplierChallanMaster.objects.all().delete()
            SupplierChallanMaster2.objects.all().delete()
            
            # 5. Delete Master data (keep some essential ones)
            print("Deleting bulk products...")
            # Delete products that look like test data
            ProductMaster.objects.filter(
                product_name__icontains='test'
            ).delete()
            
            ProductMaster.objects.filter(
                product_name__icontains='sample'
            ).delete()
            
            # Delete customers that look like test data
            print("Deleting bulk customers...")
            CustomerMaster.objects.filter(
                customer_name__icontains='test'
            ).delete()
            
            CustomerMaster.objects.filter(
                customer_name__icontains='customer'
            ).delete()
            
            # Delete suppliers that look like test data
            print("Deleting bulk suppliers...")
            SupplierMaster.objects.filter(
                supplier_name__icontains='test'
            ).delete()
            
            SupplierMaster.objects.filter(
                supplier_name__icontains='supplier'
            ).delete()
            
            print("✅ Bulk data deletion completed successfully!")
            
            # Show remaining counts
            print("\n📊 Remaining data counts:")
            print(f"Products: {ProductMaster.objects.count()}")
            print(f"Customers: {CustomerMaster.objects.count()}")
            print(f"Suppliers: {SupplierMaster.objects.count()}")
            print(f"Sales: {SalesMaster.objects.count()}")
            print(f"Purchases: {PurchaseMaster.objects.count()}")
            print(f"Customer Challans: {CustomerChallan.objects.count()}")
            print(f"Supplier Challans: {SupplierChallanMaster.objects.count()}")
            print(f"Stock Issues: {StockIssueMaster.objects.count()}")
            
    except Exception as e:
        print(f"❌ Error during deletion: {str(e)}")
        return False
    
    return True

def delete_all_test_data():
    """Delete ALL data (use with caution)"""
    
    print("⚠️  WARNING: This will delete ALL data from the database!")
    confirm = input("Type 'DELETE ALL' to confirm: ")
    
    if confirm != 'DELETE ALL':
        print("❌ Deletion cancelled.")
        return
    
    try:
        with transaction.atomic():
            print("Deleting ALL data...")
            
            # Delete all data
            StockIssueDetail.objects.all().delete()
            StockIssueMaster.objects.all().delete()
            ReturnSalesMaster.objects.all().delete()
            ReturnPurchaseMaster.objects.all().delete()
            SalesMaster.objects.all().delete()
            SalesInvoiceMaster.objects.all().delete()
            PurchaseMaster.objects.all().delete()
            InvoiceMaster.objects.all().delete()
            CustomerChallanMaster.objects.all().delete()
            CustomerChallanMaster2.objects.all().delete()
            CustomerChallan.objects.all().delete()
            SupplierChallanMaster.objects.all().delete()
            SupplierChallanMaster2.objects.all().delete()
            ProductMaster.objects.all().delete()
            CustomerMaster.objects.all().delete()
            SupplierMaster.objects.all().delete()
            
            print("✅ ALL data deleted successfully!")
            
    except Exception as e:
        print(f"❌ Error during deletion: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        delete_all_test_data()
    else:
        delete_bulk_test_data()