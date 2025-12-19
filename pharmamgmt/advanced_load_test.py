"""
Advanced Load Test - 200 Users with Real HTTP Requests
Uses requests library to simulate actual HTTP traffic
"""

import requests
import threading
import time
import random
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
NUM_USERS = 200

# Test credentials (create a test user first)
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"

# Statistics
stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'response_times': [],
    'start_time': None,
    'end_time': None
}
stats_lock = threading.Lock()

def update_stats(success, response_time):
    with stats_lock:
        stats['total'] += 1
        if success:
            stats['success'] += 1
        else:
            stats['failed'] += 1
        stats['response_times'].append(response_time)

def simulate_user_session(user_id):
    """Simulate a complete user session"""
    session = requests.Session()
    
    try:
        # 1. Login
        start = time.time()
        response = session.get(f"{BASE_URL}/login/")
        if response.status_code == 200:
            # Get CSRF token
            csrf_token = session.cookies.get('csrftoken')
            
            # Attempt login
            login_data = {
                'username': TEST_USERNAME,
                'password': TEST_PASSWORD,
                'csrfmiddlewaretoken': csrf_token
            }
            response = session.post(f"{BASE_URL}/login/", data=login_data)
            update_stats(response.status_code in [200, 302], time.time() - start)
        
        # 2. Dashboard
        start = time.time()
        response = session.get(f"{BASE_URL}/dashboard/")
        update_stats(response.status_code == 200, time.time() - start)
        time.sleep(random.uniform(0.5, 1.5))
        
        # 3. View Products
        start = time.time()
        response = session.get(f"{BASE_URL}/products/")
        update_stats(response.status_code == 200, time.time() - start)
        time.sleep(random.uniform(0.3, 1.0))
        
        # 4. View Invoices
        start = time.time()
        response = session.get(f"{BASE_URL}/invoices/")
        update_stats(response.status_code == 200, time.time() - start)
        time.sleep(random.uniform(0.3, 1.0))
        
        # 5. View Sales
        start = time.time()
        response = session.get(f"{BASE_URL}/sales-invoices/")
        update_stats(response.status_code == 200, time.time() - start)
        time.sleep(random.uniform(0.3, 1.0))
        
        # 6. View Customers
        start = time.time()
        response = session.get(f"{BASE_URL}/customers/")
        update_stats(response.status_code == 200, time.time() - start)
        
    except Exception as e:
        print(f"User {user_id} error: {e}")
        update_stats(False, 0)
    finally:
        session.close()

def run_load_test():
    """Run the load test"""
    print(f"\n{'='*70}")
    print(f"Advanced Load Test - {NUM_USERS} Concurrent Users")
    print(f"{'='*70}")
    print(f"Target: {BASE_URL}")
    print(f"Note: Make sure Django server is running!")
    print(f"{'='*70}\n")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"[OK] Server is running\n")
    except:
        print(f"[ERROR] Server is not running at {BASE_URL}")
        print(f"   Start server: python manage.py runserver")
        return
    
    stats['start_time'] = time.time()
    
    # Create threads
    threads = []
    for i in range(NUM_USERS):
        thread = threading.Thread(target=simulate_user_session, args=(i+1,))
        threads.append(thread)
    
    # Start all threads
    print(f"[STARTING] Launching {NUM_USERS} concurrent users...")
    for thread in threads:
        thread.start()
        time.sleep(0.02)  # Small delay
    
    # Wait for completion
    print(f"[RUNNING] Test in progress...\n")
    for i, thread in enumerate(threads):
        thread.join()
        if (i + 1) % 50 == 0:
            print(f"[OK] {i + 1}/{NUM_USERS} users completed")
    
    stats['end_time'] = time.time()
    
    # Print results
    print_results()

def print_results():
    """Print detailed results"""
    duration = stats['end_time'] - stats['start_time']
    avg_response = sum(stats['response_times']) / len(stats['response_times']) if stats['response_times'] else 0
    
    print(f"\n{'='*70}")
    print(f"Load Test Results")
    print(f"{'='*70}")
    print(f"Total Requests:        {stats['total']}")
    print(f"[OK] Successful:       {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"[FAIL] Failed:         {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    print(f"Duration:              {duration:.2f} seconds")
    print(f"Requests/Second:       {stats['total']/duration:.2f}")
    print(f"Avg Response Time:     {avg_response:.3f} seconds")
    print(f"{'='*70}\n")
    
    if stats['failed'] == 0:
        print("[SUCCESS] Perfect! All requests successful!")
    elif stats['failed'] < stats['total'] * 0.05:
        print("[WARNING] Acceptable - Less than 5% failure rate")
    else:
        print("[ERROR] High failure rate - Check server logs")

if __name__ == '__main__':
    print("\n[INFO] Prerequisites:")
    print("   1. Django server must be running: python manage.py runserver")
    print("   2. Create test user: python manage.py createsuperuser")
    print("   3. Install requests: pip install requests\n")
    
    input("Press Enter to start the load test...")
    
    try:
        run_load_test()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
