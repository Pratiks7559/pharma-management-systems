"""
Alternative data import script
Use this if loaddata command fails
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.core.management import call_command
from django.apps import apps

print("Importing data to PostgreSQL...")

try:
    # Load the data
    with open('datadump.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} records to import")
    
    # Import using loaddata
    call_command('loaddata', 'datadump.json', verbosity=2)
    
    print("\n✓ Migration completed successfully!")
    print("\nVerify your data:")
    print("python manage.py shell")
    print(">>> from core.models import *")
    print(">>> Web_User.objects.count()")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nTry running:")
    print("python manage.py loaddata datadump.json --traceback")
