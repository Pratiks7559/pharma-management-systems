import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from test_all_sections import TestDataGenerator

if __name__ == '__main__':
    print("\n" + "="*60)
    print("QUICK TEST - 1000 records per section")
    print("="*60)
    
    generator = TestDataGenerator()
    generator.setup_base_data()
    
    generator.test_purchases(1000)
    generator.test_sales(1000)
    generator.test_inventory(1000)
    generator.test_payments(1000)
    generator.test_receipts(1000)
    generator.test_contra(1000)
    
    print("\n✓ Quick test completed!")
