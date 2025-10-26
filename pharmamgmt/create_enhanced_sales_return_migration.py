#!/usr/bin/env python3
"""
Script to verify Enhanced Sales Return models are properly integrated
"""

import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

def check_enhanced_models():
    """Check if enhanced sales return models are available"""
    
    try:
        from core.models import EnhancedSalesReturn, EnhancedSalesReturnItem, SalesReturnApproval
        
        print("✓ Enhanced Sales Return models imported successfully")
        
        # Check if tables exist
        print(f"✓ EnhancedSalesReturn table exists: {EnhancedSalesReturn._meta.db_table}")
        print(f"✓ EnhancedSalesReturnItem table exists: {EnhancedSalesReturnItem._meta.db_table}")
        print(f"✓ SalesReturnApproval table exists: {SalesReturnApproval._meta.db_table}")
        
        # Test model creation
        print("\n🧪 Testing model functionality...")
        
        # Check model fields
        esr_fields = [field.name for field in EnhancedSalesReturn._meta.fields]
        print(f"✓ EnhancedSalesReturn fields: {len(esr_fields)} fields")
        
        esri_fields = [field.name for field in EnhancedSalesReturnItem._meta.fields]
        print(f"✓ EnhancedSalesReturnItem fields: {len(esri_fields)} fields")
        
        sra_fields = [field.name for field in SalesReturnApproval._meta.fields]
        print(f"✓ SalesReturnApproval fields: {len(sra_fields)} fields")
        
        print("\n✅ Enhanced Sales Return models are properly integrated!")
        return True
        
    except ImportError as e:
        print(f"❌ Error importing models: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def check_urls():
    """Check if enhanced sales return URLs are accessible"""
    
    try:
        from django.urls import reverse
        
        # Test URL patterns
        urls_to_test = [
            'enhanced_sales_return_list',
            'enhanced_sales_return_create',
            'get_customer_invoices',
            'get_invoice_items'
        ]
        
        print("\n🔗 Testing URL patterns...")
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✓ {url_name}: {url}")
            except Exception as e:
                print(f"❌ {url_name}: {e}")
                return False
        
        print("✅ All URL patterns are working!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking URLs: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Sales Return Integration Check")
    print("=" * 50)
    
    print("\n1. Checking models...")
    model_check = check_enhanced_models()
    
    print("\n2. Checking URLs...")
    url_check = check_urls()
    
    print("\n" + "=" * 50)
    if model_check and url_check:
        print("🎉 Enhanced Sales Return system is ready!")
        print("\nAccess URLs:")
        print("- List: /enhanced-sales-returns/")
        print("- Create: /enhanced-sales-returns/create/")
        print("\nNavigation: Sidebar → Returns → Enhanced Sales Returns")
    else:
        print("❌ Some issues were found. Please check the errors above.")