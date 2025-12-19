import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import *
import time
import statistics

User = get_user_model()

class WebsitePerformanceTest:
    def __init__(self):
        self.client = Client()
        self.results = []
        self.user = None
        
    def setup(self):
        """Create test user and login"""
        print("Setting up test user...")
        self.user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={
                'user_type': 'admin',
                'user_contact': '9999999999'
            }
        )
        self.user.set_password('test123')
        self.user.save()
        
        # Login
        self.client.login(username='testuser', password='test123')
        print("✓ Test user logged in")
    
    def test_page_load(self, url, name, expected_max_time=2.0):
        """Test page load time"""
        times = []
        for i in range(5):
            start = time.time()
            response = self.client.get(url)
            elapsed = time.time() - start
            times.append(elapsed)
            
            if response.status_code != 200:
                return {
                    'name': name,
                    'status': 'FAILED',
                    'error': f'Status {response.status_code}',
                    'avg_time': 0,
                    'min_time': 0,
                    'max_time': 0,
                    'expected': expected_max_time
                }
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        status = 'PASSED' if avg_time < expected_max_time else 'SLOW'
        
        return {
            'name': name,
            'status': status,
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'expected': expected_max_time
        }
    
    def test_all_pages(self):
        """Test all major pages"""
        print("\n" + "="*60)
        print("PAGE LOAD TESTING")
        print("="*60)
        
        pages = [
            ('/', 'Dashboard', 1.0),
            ('/products/', 'Products List', 2.0),
            ('/suppliers/', 'Suppliers List', 1.5),
            ('/customers/', 'Customers List', 1.5),
            ('/invoices/', 'Purchase Invoices', 2.0),
            ('/sales/', 'Sales Invoices', 2.0),
            ('/purchase-returns/', 'Purchase Returns', 2.0),
            ('/sales-returns/', 'Sales Returns', 2.0),
            ('/challan/supplier/', 'Supplier Challans', 2.0),
            ('/challan/customer/', 'Customer Challans', 2.0),
            ('/inventory/', 'Inventory', 2.5),
            ('/contra/', 'Contra Entries', 1.5),
        ]
        
        results = []
        for url, name, max_time in pages:
            print(f"\nTesting: {name}...")
            result = self.test_page_load(url, name, max_time)
            results.append(result)
            
            status_icon = "✓" if result['status'] == 'PASSED' else "⚠" if result['status'] == 'SLOW' else "✗"
            print(f"  {status_icon} {result['status']}: {result['avg_time']:.3f}s (max: {result['max_time']:.3f}s)")
        
        return results
    
    def test_database_queries(self):
        """Test database query performance"""
        print("\n" + "="*60)
        print("DATABASE QUERY TESTING")
        print("="*60)
        
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        
        tests = [
            ('Products', lambda: list(ProductMaster.objects.all()[:100])),
            ('Suppliers', lambda: list(SupplierMaster.objects.all()[:100])),
            ('Customers', lambda: list(CustomerMaster.objects.all()[:100])),
            ('Purchases', lambda: list(InvoiceMaster.objects.select_related('supplierid')[:100])),
            ('Sales', lambda: list(SalesInvoiceMaster.objects.select_related('customerid')[:100])),
        ]
        
        results = []
        for name, query_func in tests:
            with CaptureQueriesContext(connection) as queries:
                start = time.time()
                query_func()
                elapsed = time.time() - start
                
                result = {
                    'name': name,
                    'time': elapsed,
                    'queries': len(queries),
                    'status': 'PASSED' if elapsed < 0.5 else 'SLOW'
                }
                results.append(result)
                
                status_icon = "✓" if result['status'] == 'PASSED' else "⚠"
                print(f"{status_icon} {name:20s}: {elapsed*1000:.2f}ms ({len(queries)} queries)")
        
        return results
    
    def test_data_counts(self):
        """Test data scalability"""
        print("\n" + "="*60)
        print("DATA SCALABILITY TESTING")
        print("="*60)
        
        counts = {
            'Products': ProductMaster.objects.count(),
            'Suppliers': SupplierMaster.objects.count(),
            'Customers': CustomerMaster.objects.count(),
            'Purchase Invoices': InvoiceMaster.objects.count(),
            'Purchases': PurchaseMaster.objects.count(),
            'Sales Invoices': SalesInvoiceMaster.objects.count(),
            'Sales': SalesMaster.objects.count(),
            'Purchase Returns': ReturnInvoiceMaster.objects.count(),
            'Sales Returns': ReturnSalesInvoiceMaster.objects.count(),
            'Supplier Challans': Challan1.objects.count(),
            'Customer Challans': CustomerChallan.objects.count(),
            'Contra Entries': ContraEntry.objects.count(),
        }
        
        total = sum(counts.values())
        
        for name, count in counts.items():
            print(f"{name:25s}: {count:,}")
        
        print(f"{'='*35}")
        print(f"{'TOTAL RECORDS':25s}: {total:,}")
        print(f"{'='*35}")
        
        if total > 10000:
            print("✓ SCALABILITY: Excellent (>10K records)")
        elif total > 5000:
            print("✓ SCALABILITY: Good (>5K records)")
        else:
            print("⚠ SCALABILITY: Limited (<5K records)")
        
        return counts
    
    def test_concurrent_load(self):
        """Test concurrent user simulation"""
        print("\n" + "="*60)
        print("CONCURRENT LOAD TESTING")
        print("="*60)
        
        import threading
        
        def simulate_user(user_id, results):
            client = Client()
            client.login(username='testuser', password='test123')
            
            start = time.time()
            urls = ['/', '/products/', '/invoices/', '/sales/']
            
            for url in urls:
                try:
                    response = client.get(url)
                    if response.status_code != 200:
                        results[user_id] = {'status': 'FAILED', 'time': 0}
                        return
                except Exception as e:
                    results[user_id] = {'status': 'ERROR', 'time': 0, 'error': str(e)}
                    return
            
            elapsed = time.time() - start
            results[user_id] = {'status': 'SUCCESS', 'time': elapsed}
        
        # Simulate 10 concurrent users
        num_users = 10
        results = {}
        threads = []
        
        print(f"Simulating {num_users} concurrent users...")
        start = time.time()
        
        for i in range(num_users):
            t = threading.Thread(target=simulate_user, args=(i, results))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        total_time = time.time() - start
        
        success = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
        avg_time = statistics.mean([r['time'] for r in results.values() if r['status'] == 'SUCCESS']) if success > 0 else 0
        
        print(f"\nResults:")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Success: {success}/{num_users}")
        print(f"  Avg User Time: {avg_time:.2f}s")
        
        if success == num_users and avg_time < 5:
            print("✓ RELIABILITY: Excellent")
        elif success >= num_users * 0.8:
            print("✓ RELIABILITY: Good")
        else:
            print("⚠ RELIABILITY: Needs improvement")
        
        return {'success': success, 'total': num_users, 'avg_time': avg_time}
    
    def generate_report(self, page_results, query_results, counts, load_results):
        """Generate final report"""
        from datetime import datetime
        
        print("\n" + "="*60)
        print("FINAL REPORT")
        print("="*60)
        
        # Page Load Summary
        passed = sum(1 for r in page_results if r['status'] == 'PASSED')
        slow = sum(1 for r in page_results if r['status'] == 'SLOW')
        failed = sum(1 for r in page_results if r['status'] == 'FAILED')
        
        print(f"\n1. PAGE LOAD TESTS:")
        print(f"   Passed: {passed}/{len(page_results)}")
        print(f"   Slow: {slow}/{len(page_results)}")
        print(f"   Failed: {failed}/{len(page_results)}")
        
        # Query Performance
        fast_queries = sum(1 for r in query_results if r['status'] == 'PASSED')
        print(f"\n2. QUERY PERFORMANCE:")
        print(f"   Fast: {fast_queries}/{len(query_results)}")
        
        # Data Scale
        total_records = sum(counts.values())
        print(f"\n3. DATA SCALE:")
        print(f"   Total Records: {total_records:,}")
        
        # Reliability
        print(f"\n4. RELIABILITY:")
        print(f"   Concurrent Users: {load_results['success']}/{load_results['total']}")
        
        # Overall Score
        page_score = (passed / len(page_results)) * 100
        query_score = (fast_queries / len(query_results)) * 100
        reliability_score = (load_results['success'] / load_results['total']) * 100
        
        overall = (page_score + query_score + reliability_score) / 3
        
        print(f"\n{'='*60}")
        print(f"OVERALL SCORE: {overall:.1f}%")
        
        if overall >= 90:
            status = "✓ EXCELLENT - Production Ready"
        elif overall >= 75:
            status = "✓ GOOD - Minor optimizations needed"
        elif overall >= 60:
            status = "⚠ FAIR - Optimization recommended"
        else:
            status = "✗ POOR - Major improvements needed"
        
        print(status)
        print("="*60)
        
        # Save detailed report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("PHARMA MANAGEMENT SYSTEM - PERFORMANCE TEST REPORT\n")
            f.write("="*60 + "\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
            
            # Page Load Details
            f.write("1. PAGE LOAD PERFORMANCE\n")
            f.write("-" * 60 + "\n")
            for r in page_results:
                status_icon = "✓" if r['status'] == 'PASSED' else "⚠" if r['status'] == 'SLOW' else "✗"
                f.write(f"{status_icon} {r['name']:25s}: {r['avg_time']:.3f}s (expected: <{r['expected']}s)\n")
            f.write(f"\nSummary: {passed} passed, {slow} slow, {failed} failed\n")
            f.write("\n")
            
            # Query Performance
            f.write("2. DATABASE QUERY PERFORMANCE\n")
            f.write("-" * 60 + "\n")
            for r in query_results:
                status_icon = "✓" if r['status'] == 'PASSED' else "⚠"
                f.write(f"{status_icon} {r['name']:20s}: {r['time']*1000:.2f}ms ({r['queries']} queries)\n")
            f.write(f"\nSummary: {fast_queries}/{len(query_results)} fast queries\n")
            f.write("\n")
            
            # Data Scale
            f.write("3. DATA SCALABILITY\n")
            f.write("-" * 60 + "\n")
            for name, count in counts.items():
                f.write(f"{name:25s}: {count:,}\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'TOTAL RECORDS':25s}: {total_records:,}\n")
            f.write("\n")
            
            # Concurrent Load
            f.write("4. CONCURRENT LOAD TEST\n")
            f.write("-" * 60 + "\n")
            f.write(f"Concurrent Users: {load_results['total']}\n")
            f.write(f"Successful: {load_results['success']}\n")
            f.write(f"Average Time: {load_results['avg_time']:.2f}s\n")
            f.write("\n")
            
            # Overall Score
            f.write("5. OVERALL ASSESSMENT\n")
            f.write("-" * 60 + "\n")
            f.write(f"Page Load Score: {page_score:.1f}%\n")
            f.write(f"Query Performance Score: {query_score:.1f}%\n")
            f.write(f"Reliability Score: {reliability_score:.1f}%\n")
            f.write("\n")
            f.write(f"OVERALL SCORE: {overall:.1f}%\n")
            f.write(f"STATUS: {status}\n")
            f.write("\n")
            
            # Recommendations
            f.write("6. RECOMMENDATIONS\n")
            f.write("-" * 60 + "\n")
            if slow > 0:
                f.write(f"- Optimize {slow} slow pages\n")
            if failed > 0:
                f.write(f"- Fix {failed} failed pages\n")
            if fast_queries < len(query_results):
                f.write("- Add database indexes for slow queries\n")
            if load_results['success'] < load_results['total']:
                f.write("- Improve concurrent user handling\n")
            if overall < 75:
                f.write("- Consider caching implementation\n")
                f.write("- Review database query optimization\n")
            if overall >= 90:
                f.write("- System is production ready!\n")
            f.write("\n")
            f.write("="*60 + "\n")
        
        print(f"\n✓ Detailed report saved: {report_file}")
    
    def run_all_tests(self):
        """Run all tests"""
        from datetime import datetime
        start_time = datetime.now()
        
        print("\n" + "="*60)
        print("WEBSITE PERFORMANCE & RELIABILITY TEST")
        print("="*60)
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self.setup()
        
        page_results = self.test_all_pages()
        query_results = self.test_database_queries()
        counts = self.test_data_counts()
        load_results = self.test_concurrent_load()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\nTest Duration: {duration:.2f}s")
        
        self.generate_report(page_results, query_results, counts, load_results)

if __name__ == '__main__':
    tester = WebsitePerformanceTest()
    tester.run_all_tests()
