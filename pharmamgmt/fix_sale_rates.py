#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import SaleRateMaster

def fix_sale_rates():
    print("=== FIXING SALE RATES ISSUE ===")
    
    # Check total records
    total_rates = SaleRateMaster.objects.count()
    print(f"Total SaleRateMaster records: {total_rates}")
    
    if total_rates > 0:
        print("\nAll sale rates:")
        for rate in SaleRateMaster.objects.select_related('productid').all():
            print(f"ID: {rate.id}, Product: {rate.productid.product_name}, Batch: {rate.product_batch_no}, Rate A: {rate.rate_A}, Rate B: {rate.rate_B}, Rate C: {rate.rate_C}")
    
    print("\n=== TESTING VIEWS ===")
    
    # Test the view function directly
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    from core.models import Web_User
    from core.views import sale_rate_list
    
    factory = RequestFactory()
    request = factory.get('/rates/')
    
    # Create a test user
    try:
        user = Web_User.objects.first()
        if not user:
            user = Web_User.objects.create_user(username='testuser', password='testpass', user_type='admin')
        request.user = user
    except Exception as e:
        print(f"Error creating user: {e}")
        return
    
    try:
        response = sale_rate_list(request)
        print(f"View response status: {response.status_code}")
        print("View executed successfully!")
    except Exception as e:
        print(f"Error in view: {e}")

if __name__ == "__main__":
    fix_sale_rates()