# Generated migration for SupplierChallanMaster

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_add_enhanced_sales_return_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='Challan1',
            fields=[
                ('challan_id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('challan_no', models.CharField(max_length=50, unique=True)),
                ('challan_date', models.DateField(default=timezone.now)),
                ('challan_total', models.FloatField(default=0.0)),
                ('transport_charges', models.FloatField(default=0.0)),
                ('challan_paid', models.FloatField(default=0.0)),
                ('challan_remark', models.TextField(default='None')),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.suppliermaster')),
            ],
            options={
                'db_table': 'challan1',
                'ordering': ['-challan_date', '-challan_id'],
            },
        ),
    ]
