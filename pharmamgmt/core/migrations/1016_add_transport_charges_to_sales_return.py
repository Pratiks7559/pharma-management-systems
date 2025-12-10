# Generated migration to add transport_charges field to ReturnSalesInvoiceMaster

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '1015_remove_inventorymaster_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='returnsalesinvoicemaster',
            name='transport_charges',
            field=models.FloatField(default=0),
        ),
    ]
