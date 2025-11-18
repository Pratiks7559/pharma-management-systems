# Generated migration for SupplierChallanMaster

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_add_supplier_challan_master'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierChallanMaster',
            fields=[
                ('challan_id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('product_challan_no', models.CharField(max_length=50)),
                ('product_name', models.CharField(max_length=200)),
                ('product_company', models.CharField(max_length=200)),
                ('product_packing', models.CharField(max_length=20)),
                ('product_batch_no', models.CharField(max_length=20)),
                ('product_expiry', models.CharField(max_length=7, help_text='Format: MM-YYYY')),
                ('product_mrp', models.FloatField()),
                ('product_purchase_rate', models.FloatField()),
                ('product_quantity', models.FloatField()),
                ('product_scheme', models.FloatField(default=0.0)),
                ('product_discount', models.FloatField(default=0.0)),
                ('product_transportation_charges', models.FloatField(default=0.0)),
                ('actual_rate_per_qty', models.FloatField(default=0.0)),
                ('product_actual_rate', models.FloatField(default=0.0)),
                ('total_amount', models.FloatField(default=0.0)),
                ('challan_entry_date', models.DateTimeField(default=timezone.now)),
                ('cgst', models.FloatField(default=2.5)),
                ('sgst', models.FloatField(default=2.5)),
                ('challan_calculation_mode', models.CharField(max_length=10, default='flat')),
                ('product_suppliername', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.suppliermaster')),
                ('product_challan_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.challan1')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.productmaster')),
            ],
            options={
                'db_table': 'supplier_challan_master',
                'ordering': ['-challan_entry_date'],
            },
        ),
    ]
