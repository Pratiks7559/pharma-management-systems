#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.test import RequestFactory
from core.models import SaleRateMaster, Web_User
from core.views import sale_rate_list

def simple_test():
    print("=== SIMPLE SALE RATES TEST ===")
    
    # Check data
    total_rates = SaleRateMaster.objects.count()
    print(f"Total SaleRateMaster records: {total_rates}")
    
    # Test view directly
    factory = RequestFactory()
    request = factory.get('/rates/')
    
    # Get or create user
    try:
        user = Web_User.objects.first()
        if not user:
            user = Web_User.objects.create_user(
                username='testuser',
                password='testpass',
                user_type='admin',
                user_contact='1234567890'
            )
        request.user = user
        
        # Call view
        response = sale_rate_list(request)
        print(f"View response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check context data
            if hasattr(response, 'context_data'):
                context = response.context_data
                if 'sale_rates' in context:
                    rates = context['sale_rates']
                    print(f"Context has {len(rates)} sale rates")
                else:
                    print("No 'sale_rates' in context")
            
            # Check content
            if 'No sale rates found' in content:
                print("Template shows 'No sale rates found'")
            else:
                print("Template has rate data")
                
            # Check for specific data
            if 'paracetamol' in content:
                print("Found 'paracetamol' in content")
            if 'shilajit' in content:
                print("Found 'shilajit' in content")
                
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_test()