# Generated migration to remove scroll_no field from InvoiceMaster

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_alter_returnsalesinvoicepaid_return_sales_payment_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoicemaster',
            name='scroll_no',
        ),
    ]
