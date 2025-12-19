"""
Delete Bulk Test Data
Removes all test records created by create_bulk_test_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import (
    SupplierMaster, CustomerMaster,
    InvoiceMaster, PurchaseMaster,
    SalesInvoiceMaster, SalesMaster,
    ReturnInvoiceMaster, ReturnPurchaseMaster,
    ReturnSalesInvoiceMaster, ReturnSalesMaster,
    SupplierChallanMaster, CustomerChallanMaster
)

def delete_test_data():
    print("=" * 60)
    print("DELETE BULK TEST DATA")
    print("=" * 60)
    
    confirm = input("\n⚠️  Delete ALL test records? (Y/N): ").strip().upper()
    if confirm != 'Y':
        print("❌ Cancelled")
        return
    
    print("\n🗑️  Deleting test data...")
    
    # Delete in correct order (child records first)
    counts = {}
    
    print("\n  Deleting purchase items...")
    counts['purchases'] = PurchaseMaster.objects.filter(
        product_invoice_no__startswith='TPI'
    ).delete()[0]
    
    print("  Deleting purchase invoices...")
    counts['purchase_invoices'] = InvoiceMaster.objects.filter(
        invoice_no__startswith='TPI'
    ).delete()[0]
    
    print("  Deleting sales items...")
    counts['sales'] = SalesMaster.objects.filter(
        sales_invoice_no__sales_invoice_no__startswith='TSI'
    ).delete()[0]
    
    print("  Deleting sales invoices...")
    counts['sales_invoices'] = SalesInvoiceMaster.objects.filter(
        sales_invoice_no__startswith='TSI'
    ).delete()[0]
    
    print("  Deleting purchase return items...")
    counts['purchase_return_items'] = ReturnPurchaseMaster.objects.filter(
        returninvoiceid__returninvoiceid__startswith='TPR'
    ).delete()[0]
    
    print("  Deleting purchase returns...")
    counts['purchase_returns'] = ReturnInvoiceMaster.objects.filter(
        returninvoiceid__startswith='TPR'
    ).delete()[0]
    
    print("  Deleting sales return items...")
    counts['sales_return_items'] = ReturnSalesMaster.objects.filter(
        return_sales_invoice_no__return_sales_invoice_no__startswith='TSR'
    ).delete()[0]
    
    print("  Deleting sales returns...")
    counts['sales_returns'] = ReturnSalesInvoiceMaster.objects.filter(
        return_sales_invoice_no__startswith='TSR'
    ).delete()[0]
    
    print("  Deleting supplier challans...")
    counts['supplier_challans'] = SupplierChallanMaster.objects.filter(
        product_challan_no__startswith='TSC'
    ).delete()[0]
    
    print("  Deleting customer challans...")
    counts['customer_challans'] = CustomerChallanMaster.objects.filter(
        customer_challan_no__startswith='TCC'
    ).delete()[0]
    
    print("  Deleting test suppliers...")
    counts['suppliers'] = SupplierMaster.objects.filter(
        supplier_name__startswith='Test Supplier'
    ).delete()[0]
    
    print("  Deleting test customers...")
    counts['customers'] = CustomerMaster.objects.filter(
        customer_name__startswith='Test Customer'
    ).delete()[0]
    
    total = sum(counts.values())
    
    print("\n" + "=" * 60)
    print("✅ DELETION COMPLETE")
    print("=" * 60)
    print(f"\nRecords deleted:")
    print(f"  • Suppliers: {counts.get('suppliers', 0)}")
    print(f"  • Customers: {counts.get('customers', 0)}")
    print(f"  • Purchase Invoices: {counts.get('purchase_invoices', 0)}")
    print(f"  • Purchase Items: {counts.get('purchases', 0)}")
    print(f"  • Sales Invoices: {counts.get('sales_invoices', 0)}")
    print(f"  • Sales Items: {counts.get('sales', 0)}")
    print(f"  • Purchase Returns: {counts.get('purchase_returns', 0)}")
    print(f"  • Purchase Return Items: {counts.get('purchase_return_items', 0)}")
    print(f"  • Sales Returns: {counts.get('sales_returns', 0)}")
    print(f"  • Sales Return Items: {counts.get('sales_return_items', 0)}")
    print(f"  • Supplier Challans: {counts.get('supplier_challans', 0)}")
    print(f"  • Customer Challans: {counts.get('customer_challans', 0)}")
    print(f"\n📊 Total deleted: {total} records")
    print("=" * 60)

if __name__ == "__main__":
    delete_test_data()
