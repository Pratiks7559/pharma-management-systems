"""
Performance Optimization Script
Fixes slow pages: Dashboard, Products List, Inventory
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.core.management import call_command

print("Creating performance optimization migration...")

migration_content = '''
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '1014_merge_20251202_2140'),
    ]
    
    operations = [
        # Add indexes for dashboard queries
        migrations.AddIndex(
            model_name='salesmaster',
            index=models.Index(fields=['-sale_entry_date'], name='idx_sale_date'),
        ),
        migrations.AddIndex(
            model_name='purchasemaster',
            index=models.Index(fields=['-purchase_entry_date'], name='idx_purchase_date'),
        ),
        migrations.AddIndex(
            model_name='productmaster',
            index=models.Index(fields=['product_name'], name='idx_product_name'),
        ),
        migrations.AddIndex(
            model_name='productmaster',
            index=models.Index(fields=['product_company'], name='idx_product_company'),
        ),
    ]
'''

# Write migration file
migration_path = 'core/migrations/1016_performance_optimization.py'
with open(migration_path, 'w') as f:
    f.write(migration_content)

print(f"✓ Created {migration_path}")
print("\nRun: python manage.py migrate")
