# Generated migration to delete PaymentMaster table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_convert_sales_payment_datetime_to_date'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PaymentMaster',
        ),
    ]