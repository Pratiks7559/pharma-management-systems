import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.core.management import call_command
from core.models import InvoiceSeries

print("Cleaning existing data...")
# Delete default invoice series created by migration
InvoiceSeries.objects.all().delete()
print("✓ Cleaned")

print("\nImporting data (excluding admin logs)...")
try:
    call_command('loaddata', 'datadump.json', verbosity=2, exclude=['admin.logentry'])
    print("\n✓ Data imported successfully!")
except Exception as e:
    print(f"\nPartial import completed with warnings: {e}")
    print("\nTrying without admin logs...")
    # Manually load without problematic data
    import json
    from django.core import serializers
    
    with open('datadump.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter out admin.logentry
    filtered_data = [obj for obj in data if obj['model'] != 'admin.logentry']
    
    print(f"Loading {len(filtered_data)} objects...")
    for obj in serializers.deserialize('json', json.dumps(filtered_data)):
        try:
            obj.save()
        except Exception as ex:
            print(f"Skipped {obj.object}: {ex}")
    
    print("\n✓ Data imported (admin logs skipped)!")
