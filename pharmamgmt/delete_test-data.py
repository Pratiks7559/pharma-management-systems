import os
import django
import time
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

def delete_test_data_fast():
    print("=" * 60)
    print("FAST DELETE TEST DATA")
    print("=" * 60)
    
    start_time = time.time()
    
    with connection.cursor() as cursor:
        print("\nDeleting test data using optimized queries...\n")
        
        # Disable triggers for faster deletion (PostgreSQL)
        cursor.execute("SET session_replication_role = 'replica';")
        
        # Delete Purchase Records
        print("  Deleting Purchase records...")
        cursor.execute("DELETE FROM core_purchasemaster WHERE product_invoice_no LIKE 'TINV%';")
        purchase_count = cursor.rowcount
        print(f"    > Deleted {purchase_count} purchase records")
        
        # Delete Purchase Invoices
        print("  Deleting Purchase invoices...")
        cursor.execute("DELETE FROM core_invoicemaster WHERE invoice_no LIKE 'TINV%';")
        invoice_count = cursor.rowcount
        print(f"    > Deleted {invoice_count} purchase invoices")
        
        # Delete Sales Records
        print("  Deleting Sales records...")
        cursor.execute("""
            DELETE FROM core_salesmaster 
            WHERE sales_invoice_no_id IN (
                SELECT sales_invoice_no FROM core_salesinvoicemaster 
                WHERE sales_invoice_no LIKE 'TSINV%'
            );
        """)
        sales_count = cursor.rowcount
        print(f"    > Deleted {sales_count} sales records")
        
        # Delete Sales Invoices
        print("  Deleting Sales invoices...")
        cursor.execute("DELETE FROM core_salesinvoicemaster WHERE sales_invoice_no LIKE 'TSINV%';")
        sales_invoice_count = cursor.rowcount
        print(f"    > Deleted {sales_invoice_count} sales invoices")
        
        # Delete Sales Return Records
        print("  Deleting Sales return records...")
        cursor.execute("""
            DELETE FROM core_returnsalesmaster 
            WHERE return_sales_invoice_no_id IN (
                SELECT return_sales_invoice_no FROM core_returnsalesinvoicemaster 
                WHERE return_sales_invoice_no LIKE 'TSRINV%'
            );
        """)
        sales_return_count = cursor.rowcount
        print(f"    > Deleted {sales_return_count} sales return records")
        
        # Delete Sales Return Invoices
        print("  Deleting Sales return invoices...")
        cursor.execute("DELETE FROM core_returnsalesinvoicemaster WHERE return_sales_invoice_no LIKE 'TSRINV%';")
        sales_return_invoice_count = cursor.rowcount
        print(f"    > Deleted {sales_return_invoice_count} sales return invoices")
        
        # Delete Purchase Return Records
        print("  Deleting Purchase return records...")
        cursor.execute("""
            DELETE FROM core_returnpurchasemaster 
            WHERE returninvoiceid_id IN (
                SELECT returninvoiceid FROM core_returninvoicemaster 
                WHERE returninvoiceid LIKE 'TPRINV%'
            );
        """)
        purchase_return_count = cursor.rowcount
        print(f"    > Deleted {purchase_return_count} purchase return records")
        
        # Delete Purchase Return Invoices
        print("  Deleting Purchase return invoices...")
        cursor.execute("DELETE FROM core_returninvoicemaster WHERE returninvoiceid LIKE 'TPRINV%';")
        purchase_return_invoice_count = cursor.rowcount
        print(f"    > Deleted {purchase_return_invoice_count} purchase return invoices")
        
        # Delete Supplier Challan Details (child first)
        print("  Deleting Supplier challan details...")
        cursor.execute("DELETE FROM supplier_challan_master WHERE product_challan_no LIKE 'TSCHAL%';")
        supplier_challan_detail_count = cursor.rowcount
        print(f"    > Deleted {supplier_challan_detail_count} supplier challan details")
        
        # Delete Supplier Challans (then parent)
        print("  Deleting Supplier challans...")
        cursor.execute("DELETE FROM challan1 WHERE challan_no LIKE 'TSCHAL%';")
        supplier_challan_count = cursor.rowcount
        print(f"    > Deleted {supplier_challan_count} supplier challans")
        
        # Delete Customer Challan Details (child first)
        print("  Deleting Customer challan details...")
        cursor.execute("DELETE FROM customer_challan_master WHERE customer_challan_no LIKE 'TCCHAL%';")
        customer_challan_detail_count = cursor.rowcount
        print(f"    > Deleted {customer_challan_detail_count} customer challan details")
        
        # Delete Customer Challans (then parent)
        print("  Deleting Customer challans...")
        cursor.execute("DELETE FROM customer_challan WHERE customer_challan_no LIKE 'TCCHAL%';")
        customer_challan_count = cursor.rowcount
        print(f"    > Deleted {customer_challan_count} customer challans")
        
        # Get test product IDs first
        cursor.execute("SELECT productid FROM core_productmaster WHERE product_name LIKE 'Test Medicine%';")
        test_product_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete Batch Inventory Cache for test products
        print("  Deleting Batch inventory cache...")
        if test_product_ids:
            placeholders = ','.join(['%s'] * len(test_product_ids))
            cursor.execute(f"DELETE FROM batch_inventory_cache WHERE product_id IN ({placeholders});", test_product_ids)
            batch_cache_count = cursor.rowcount
        else:
            batch_cache_count = 0
        print(f"    > Deleted {batch_cache_count} batch cache records")
        
        # Delete Product Inventory Cache for test products
        print("  Deleting Product inventory cache...")
        if test_product_ids:
            placeholders = ','.join(['%s'] * len(test_product_ids))
            cursor.execute(f"DELETE FROM product_inventory_cache WHERE product_id IN ({placeholders});", test_product_ids)
            product_cache_count = cursor.rowcount
        else:
            product_cache_count = 0
        print(f"    > Deleted {product_cache_count} product cache records")
        
        # Delete Test Products (after cache is cleared)
        print("  Deleting Test products...")
        cursor.execute("DELETE FROM core_productmaster WHERE product_name LIKE 'Test Medicine%';")
        product_count = cursor.rowcount
        print(f"    > Deleted {product_count} products")
        
        # Delete Test Suppliers (last - after all their related records)
        print("  Deleting Test suppliers...")
        cursor.execute("DELETE FROM core_suppliermaster WHERE supplier_name LIKE 'Test Supplier%';")
        supplier_count = cursor.rowcount
        print(f"    > Deleted {supplier_count} suppliers")
        
        # Delete Test Customers (last - after all their related records)
        print("  Deleting Test customers...")
        cursor.execute("DELETE FROM core_customermaster WHERE customer_name LIKE 'Test Customer%';")
        customer_count = cursor.rowcount
        print(f"    > Deleted {customer_count} customers")
        
        # Clean up orphan cache records (products that no longer exist)
        print("  Cleaning orphan batch cache...")
        cursor.execute("""
            DELETE FROM batch_inventory_cache 
            WHERE product_id NOT IN (SELECT productid FROM core_productmaster);
        """)
        orphan_batch_count = cursor.rowcount
        print(f"    > Deleted {orphan_batch_count} orphan batch cache records")
        
        print("  Cleaning orphan product cache...")
        cursor.execute("""
            DELETE FROM product_inventory_cache 
            WHERE product_id NOT IN (SELECT productid FROM core_productmaster);
        """)
        orphan_product_count = cursor.rowcount
        print(f"    > Deleted {orphan_product_count} orphan product cache records")
        
        # Re-enable triggers
        cursor.execute("SET session_replication_role = 'origin';")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    total_deleted = (purchase_count + invoice_count + sales_count + sales_invoice_count + 
                    sales_return_count + sales_return_invoice_count + purchase_return_count + 
                    purchase_return_invoice_count + supplier_challan_detail_count + 
                    supplier_challan_count + customer_challan_detail_count + 
                    customer_challan_count + batch_cache_count + product_cache_count + 
                    orphan_batch_count + orphan_product_count + 
                    supplier_count + customer_count + product_count)
    
    print("\n" + "=" * 60)
    print("DELETION COMPLETED!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  - Suppliers: {supplier_count}")
    print(f"  - Customers: {customer_count}")
    print(f"  - Products: {product_count}")
    print(f"  - Purchase Invoices: {invoice_count}")
    print(f"  - Purchase Items: {purchase_count}")
    print(f"  - Sales Invoices: {sales_invoice_count}")
    print(f"  - Sales Items: {sales_count}")
    print(f"  - Purchase Return Invoices: {purchase_return_invoice_count}")
    print(f"  - Purchase Return Items: {purchase_return_count}")
    print(f"  - Sales Return Invoices: {sales_return_invoice_count}")
    print(f"  - Sales Return Items: {sales_return_count}")
    print(f"  - Supplier Challans: {supplier_challan_count}")
    print(f"  - Supplier Challan Details: {supplier_challan_detail_count}")
    print(f"  - Customer Challans: {customer_challan_count}")
    print(f"  - Customer Challan Details: {customer_challan_detail_count}")
    print(f"  - Batch Cache Records: {batch_cache_count}")
    print(f"  - Product Cache Records: {product_cache_count}")
    print(f"  - Orphan Batch Cache: {orphan_batch_count}")
    print(f"  - Orphan Product Cache: {orphan_product_count}")
    print(f"\nTotal Records Deleted: {total_deleted}")
    print(f"Time Taken: {elapsed_time:.2f} seconds")
    print("=" * 60)

if __name__ == "__main__":
    try:
        delete_test_data_fast()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
