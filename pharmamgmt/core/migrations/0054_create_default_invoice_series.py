# Generated migration for creating default invoice series

from django.db import migrations

def create_default_series(apps, schema_editor):
    InvoiceSeries = apps.get_model('core', 'InvoiceSeries')
    
    # Create default ABC series if it doesn't exist
    if not InvoiceSeries.objects.filter(series_name='ABC').exists():
        InvoiceSeries.objects.create(
            series_name='ABC',
            series_prefix='ABC',
            current_number=1,
            is_active=True
        )
    
    # Create some common series
    common_series = ['XYZ', 'INV', 'SAL']
    for series_name in common_series:
        if not InvoiceSeries.objects.filter(series_name=series_name).exists():
            InvoiceSeries.objects.create(
                series_name=series_name,
                series_prefix=series_name,
                current_number=1,
                is_active=True
            )

def reverse_default_series(apps, schema_editor):
    # Don't delete series in reverse migration to avoid data loss
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_challaninvoicepaid'),
    ]

    operations = [
        migrations.RunPython(create_default_series, reverse_default_series),
    ]