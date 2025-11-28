# Generated migration for adding challan transaction types

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '1004_add_stock_issue_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorytransaction',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('purchase', 'Purchase'),
                    ('sale', 'Sale'),
                    ('purchase_return', 'Purchase Return'),
                    ('sales_return', 'Sales Return'),
                    ('adjustment', 'Stock Adjustment'),
                    ('transfer', 'Stock Transfer'),
                    ('damage', 'Damage/Expiry'),
                    ('stock_issue_reversal', 'Stock Issue Reversal'),
                    ('supplier_challan', 'Supplier Challan'),
                    ('customer_challan', 'Customer Challan'),
                ],
                max_length=20
            ),
        ),
    ]