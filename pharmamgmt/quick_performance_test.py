#!/usr/bin/env python
"""
Quick performance test for the optimized views
"""
import os
import sys
import django
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def test_optimized_views():
    """Test the optimized views performance"""
    print("🚀 Testing Optimized Views Performance")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Create or get a test user
    User = get_user_model()
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='admin',
            password='admin123',
            user_type='admin',
            user_contact='1234567890'
        )
    
    # Login
    client.login(username='admin', password='admin123')
    
    # Test cases
    test_cases = [
        ('/', 'Dashboard'),
        ('/products/', 'Products List'),
        ('/inventory/', 'Inventory List'),
    ]
    
    results = []
    
    for url, name in test_cases:
        print(f"\n🔍 Testing {name}...")
        
        try:
            start_time = time.time()
            response = client.get(url)
            end_time = time.time()
            
            load_time = end_time - start_time
            
            if response.status_code == 200:
                if load_time <= 5.0:
                    status = "✅ FAST"
                elif load_time <= 10.0:
                    status = "⚠️ ACCEPTABLE"
                else:
                    status = "❌ SLOW"
                
                print(f"   {status}: {load_time:.3f}s")
                results.append({
                    'page': name,
                    'time': load_time,
                    'status': status,
                    'success': True
                })
            else:
                print(f"   ❌ ERROR: HTTP {response.status_code}")
                results.append({
                    'page': name,
                    'time': 0,
                    'status': 'ERROR',
                    'success': False
                })
                
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
            results.append({
                'page': name,
                'time': 0,
                'status': 'FAILED',
                'success': False
            })
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    
    successful = [r for r in results if r['success']]
    fast = [r for r in successful if '✅' in r['status']]
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Fast (≤5s): {len(fast)}")
    
    if len(successful) > 0:
        total_time = sum(r['time'] for r in successful)
        avg_time = total_time / len(successful)
        print(f"Average Time: {avg_time:.3f}s")
        
        if len(fast) == len(successful):
            print("🎉 ALL PAGES OPTIMIZED SUCCESSFULLY!")
        elif len(fast) >= len(successful) * 0.8:
            print("👍 GOOD - Most pages are fast")
        else:
            print("⚠️ NEEDS MORE WORK - Some pages still slow")
    
    return results

if __name__ == "__main__":
    test_optimized_views()