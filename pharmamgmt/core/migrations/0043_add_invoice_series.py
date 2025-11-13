# Generated migration for Invoice Series functionality

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def create_default_series(apps, schema_editor):
    """Create default ABC series"""
    InvoiceSeries = apps.get_model('core', 'InvoiceSeries')
    InvoiceSeries.objects.create(
        series_name='ABC',
        series_prefix='ABC',
        current_number=1,
        is_active=True
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_replace_sales_igst_with_cgst_sgst'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceSeries',
            fields=[
                ('series_id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('series_name', models.CharField(max_length=10, unique=True)),
                ('series_prefix', models.CharField(blank=True, max_length=5)),
                ('current_number', models.IntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(default=timezone.now)),
            ],
            options={
                'verbose_name_plural': 'Invoice Series',
            },
        ),
        migrations.AddField(
            model_name='salesinvoicemaster',
            name='invoice_series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.invoiceseries'),
        ),
        migrations.RunPython(create_default_series),
    ]