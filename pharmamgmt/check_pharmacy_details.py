#!/usr/bin/env python
"""
Quick script to check pharmacy details in database
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import Pharmacy_Details

def main():
    print("🏥 CHECKING PHARMACY DETAILS")
    print("=" * 60)
    
    try:
        pharmacy = Pharmacy_Details.objects.first()
        
        if pharmacy:
            print("\n✅ Pharmacy details found in database!\n")
            print(f"Pharmacy Name: {pharmacy.pharmaname or '[NOT SET]'}")
            print(f"Proprietor Name: {pharmacy.proprietorname or '[NOT SET]'}")
            print(f"Contact: {pharmacy.proprietorcontact or '[NOT SET]'}")
            print(f"Email: {pharmacy.proprietoremail or '[NOT SET]'}")
            print(f"Website: {pharmacy.pharmaweburl or '[NOT SET]'}")
            
            # Check if any field is empty
            empty_fields = []
            if not pharmacy.pharmaname:
                empty_fields.append("Pharmacy Name")
            if not pharmacy.proprietorname:
                empty_fields.append("Proprietor Name")
            if not pharmacy.proprietorcontact:
                empty_fields.append("Contact")
            if not pharmacy.proprietoremail:
                empty_fields.append("Email")
            
            if empty_fields:
                print(f"\n⚠️  Warning: Following fields are empty:")
                for field in empty_fields:
                    print(f"   - {field}")
                print("\n💡 Please update pharmacy details from:")
                print("   Dashboard → Pharmacy Details")
            else:
                print("\n✅ All important fields are filled!")
        else:
            print("\n❌ No pharmacy details found in database!")
            print("\n💡 Please add pharmacy details:")
            print("   1. Login to your system")
            print("   2. Go to Dashboard")
            print("   3. Click on 'Pharmacy Details'")
            print("   4. Fill all the required information")
            print("   5. Save the details")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check your database connection.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
