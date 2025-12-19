"""
Load Test Script - 200 Concurrent Users
Simulates 200 users accessing the pharmacy management system
"""

import os
import django
import threading
import time
import random
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.contrib.auth import authenticate
from core.models import (
    Web_User, ProductMaster, SupplierMaster, CustomerMaster,
    InvoiceMaster, SalesInvoiceMaster, PurchaseMaster, SalesMaster
)

# Test statistics
stats = {
    'total_requests': 0,
    'successful': 0,
    'failed': 0,
    'start_time': None,
    'end_time': None
}
stats_lock = threading.Lock()

def update_stats(success=True):
    with stats_lock:
        stats['total_requests'] += 1
        if success:
            stats['successful'] += 1
        else:
            stats['failed'] += 1

def simulate_user(user_id):
    """Simulate a single user performing various operations"""
    try:
        # Random operations each user will perform
        operations = [
            'view_products',
            'view_invoices',
            'view_sales',
            'view_customers',
            'view_suppliers',
            'dashboard'
        ]
        
        for _ in range(random.randint(5, 15)):  # Each user does 5-15 operations
            operation = random.choice(operations)
            
            try:
                if operation == 'view_products':
                    products = ProductMaster.objects.all()[:50]
                    _ = list(products)
                    
                elif operation == 'view_invoices':
                    invoices = InvoiceMaster.objects.all()[:20]
                    _ = list(invoices)
                    
                elif operation == 'view_sales':
                    sales = SalesInvoiceMaster.objects.all()[:20]
                    _ = list(sales)
                    
                elif operation == 'view_customers':
                    customers = CustomerMaster.objects.all()[:30]
                    _ = list(customers)
                    
                elif operation == 'view_suppliers':
                    suppliers = SupplierMaster.objects.all()[:30]
                    _ = list(suppliers)
                    
                elif operation == 'dashboard':
                    # Simulate dashboard queries
                    _ = ProductMaster.objects.count()
                    _ = CustomerMaster.objects.count()
                    _ = SupplierMaster.objects.count()
                
                update_stats(success=True)
                time.sleep(random.uniform(0.1, 0.5))  # Random delay between operations
                
            except Exception as e:
                print(f"User {user_id} - Operation {operation} failed: {e}")
                update_stats(success=False)
                
    except Exception as e:
        print(f"User {user_id} failed: {e}")
        update_stats(success=False)

def run_load_test(num_users=200):
    """Run load test with specified number of concurrent users"""
    print(f"\n{'='*60}")
    print(f"🚀 Starting Load Test with {num_users} Concurrent Users")
    print(f"{'='*60}\n")
    
    stats['start_time'] = time.time()
    
    # Create threads for each user
    threads = []
    for i in range(num_users):
        thread = threading.Thread(target=simulate_user, args=(i+1,))
        threads.append(thread)
    
    # Start all threads
    print(f"⏳ Launching {num_users} users...")
    for thread in threads:
        thread.start()
        time.sleep(0.01)  # Small delay to avoid overwhelming the system
    
    # Wait for all threads to complete
    print(f"⏳ Waiting for all users to complete their operations...\n")
    for i, thread in enumerate(threads):
        thread.join()
        if (i + 1) % 50 == 0:
            print(f"✓ {i + 1}/{num_users} users completed")
    
    stats['end_time'] = time.time()
    
    # Print results
    print_results()

def print_results():
    """Print test results"""
    duration = stats['end_time'] - stats['start_time']
    
    print(f"\n{'='*60}")
    print(f"📊 Load Test Results")
    print(f"{'='*60}")
    print(f"Total Requests:      {stats['total_requests']}")
    print(f"✓ Successful:        {stats['successful']} ({stats['successful']/stats['total_requests']*100:.1f}%)")
    print(f"✗ Failed:            {stats['failed']} ({stats['failed']/stats['total_requests']*100:.1f}%)")
    print(f"Duration:            {duration:.2f} seconds")
    print(f"Requests/Second:     {stats['total_requests']/duration:.2f}")
    print(f"{'='*60}\n")
    
    if stats['failed'] == 0:
        print("✅ All requests successful! System handled the load well.")
    elif stats['failed'] < stats['total_requests'] * 0.05:
        print("⚠️  Less than 5% failures - System performance is acceptable.")
    else:
        print("❌ High failure rate - System may need optimization.")

if __name__ == '__main__':
    try:
        # Check if database has data
        product_count = ProductMaster.objects.count()
        if product_count == 0:
            print("⚠️  Warning: No products in database. Run generate_test_invoices first.")
            print("   Command: python manage.py generate_test_invoices")
            exit(1)
        
        print(f"✓ Database has {product_count} products")
        
        # Run the load test
        run_load_test(num_users=200)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
