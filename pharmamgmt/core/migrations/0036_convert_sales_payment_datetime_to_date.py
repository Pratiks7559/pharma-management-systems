# Generated migration to convert sales payment datetime fields to date fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_alter_paymentmaster_payment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesinvoicepaid',
            name='sales_payment_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='returnsalesinvoicepaid',
            name='return_sales_payment_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]