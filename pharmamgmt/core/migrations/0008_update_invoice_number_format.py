# Generated migration to handle invoice number format change
from django.db import migrations

def update_invoice_format(apps, schema_editor):
    """
    This migration handles the transition from old invoice format (SINV-YYYYMMDD-XXX) 
    to new format (11-digit sequential numbers).
    
    Note: This migration doesn't modify existing data to preserve historical records.
    New invoices will use the new format starting from the next sequential number.
    """
    pass

def reverse_update_invoice_format(apps, schema_editor):
    """
    Reverse migration - no action needed as we're not modifying existing data
    """
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_purchasemaster_product_expiry_and_more'),
    ]

    operations = [
        migrations.RunPython(update_invoice_format, reverse_update_invoice_format),
    ]