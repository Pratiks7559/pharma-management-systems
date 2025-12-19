import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import *
from django.db import connection
from django.test.utils import CaptureQueriesContext
import time

class PerformanceTest:
    """Test query performance and optimization"""
    
    def test_query_performance(self):
        print("\n" + "="*60)
        print("QUERY PERFORMANCE TEST")
        print("="*60)
        
        tests = [
            ("Product List (100)", lambda: list(ProductMaster.objects.all()[:100])),
            ("Purchase Invoices (100)", lambda: list(InvoiceMaster.objects.select_related('supplierid')[:100])),
            ("Sales Invoices (100)", lambda: list(SalesInvoice.objects.select_related('customer')[:100])),
            ("Inventory (100)", lambda: list(Inventory.objects.select_related('product')[:100])),
            ("Payments (100)", lambda: list(Payment.objects.select_related('supplier', 'invoice')[:100])),
            ("Receipts (100)", lambda: list(Receipt.objects.select_related('customer', 'sales_invoice')[:100])),
        ]
        
        for test_name, test_func in tests:
            with CaptureQueriesContext(connection) as queries:
                start = time.time()
                test_func()
                elapsed = time.time() - start
                
                print(f"\n{test_name}")
                print(f"  Time: {elapsed*1000:.2f}ms")
                print(f"  Queries: {len(queries)}")
                
                if elapsed > 1.0:
                    print(f"  ⚠ WARNING: Slow query (>{1000}ms)")
                else:
                    print(f"  ✓ PASSED")
    
    def test_database_size(self):
        print("\n" + "="*60)
        print("DATABASE SIZE TEST")
        print("="*60)
        
        tables = [
            ('Products', ProductMaster),
            ('Suppliers', SupplierMaster),
            ('Customers', CustomerMaster),
            ('Purchase Invoices', InvoiceMaster),
            ('Purchases', PurchaseMaster),
            ('Sales Invoices', SalesInvoice),
            ('Sales', Sale),
            ('Inventory', Inventory),
            ('Payments', Payment),
            ('Receipts', Receipt),
            ('Contra Entries', ContraEntry),
        ]
        
        total = 0
        for name, model in tables:
            count = model.objects.count()
            total += count
            print(f"{name:25s}: {count:,}")
        
        print(f"{'='*35}")
        print(f"{'TOTAL RECORDS':25s}: {total:,}")
        print(f"{'='*35}")
        
        if total > 100000:
            print("✓ SCALABILITY TEST PASSED: >100K records")
        else:
            print(f"⚠ Current: {total:,} records")
    
    def test_indexes(self):
        print("\n" + "="*60)
        print("INDEX CHECK")
        print("="*60)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tablename, indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND tablename LIKE 'core_%'
                ORDER BY tablename;
            """)
            
            indexes = cursor.fetchall()
            print(f"Total Indexes: {len(indexes)}")
            
            for table, index in indexes[:10]:
                print(f"  {table:30s} -> {index}")
            
            if len(indexes) > 10:
                print(f"  ... and {len(indexes) - 10} more")
    
    def run_all(self):
        self.test_database_size()
        self.test_query_performance()
        self.test_indexes()

if __name__ == '__main__':
    tester = PerformanceTest()
    tester.run_all()
