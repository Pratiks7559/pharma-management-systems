"""
Simple Load Test - Tests public pages without login
"""

import requests
import threading
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
NUM_USERS = 200

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

def simulate_user(user_id):
    """Simulate user accessing public pages"""
    session = requests.Session()
    
    try:
        # Test login page (public)
        start = time.time()
        response = session.get(f"{BASE_URL}/login/", timeout=10)
        update_stats(response.status_code == 200, time.time() - start)
        
        # Test home/root page
        start = time.time()
        response = session.get(f"{BASE_URL}/", timeout=10)
        update_stats(response.status_code in [200, 302], time.time() - start)
        
    except Exception as e:
        update_stats(False, 0)
    finally:
        session.close()

def run_test():
    print(f"\n{'='*70}")
    print(f"Simple Load Test - {NUM_USERS} Concurrent Users")
    print(f"{'='*70}")
    print(f"Target: {BASE_URL}")
    print(f"{'='*70}\n")
    
    # Check server
    try:
        requests.get(BASE_URL, timeout=5)
        print(f"[OK] Server is running\n")
    except:
        print(f"[ERROR] Server not running")
        return
    
    stats['start_time'] = time.time()
    
    # Create and start threads
    threads = []
    for i in range(NUM_USERS):
        thread = threading.Thread(target=simulate_user, args=(i+1,))
        threads.append(thread)
        thread.start()
        time.sleep(0.01)
    
    print(f"[RUNNING] Test in progress...\n")
    
    # Wait for completion
    for i, thread in enumerate(threads):
        thread.join()
        if (i + 1) % 50 == 0:
            print(f"[OK] {i + 1}/{NUM_USERS} users completed")
    
    stats['end_time'] = time.time()
    
    # Print results
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
        print("[ERROR] High failure rate")

if __name__ == '__main__':
    input("Press Enter to start load test...")
    try:
        run_test()
    except KeyboardInterrupt:
        print("\n[WARNING] Test interrupted")
