from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_alter_purchasereturninvoicepaid_pr_payment_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='returnpurchasemaster',
            name='returnproduct_cgst',
            field=models.FloatField(default=2.5),
        ),
        migrations.AddField(
            model_name='returnpurchasemaster',
            name='returnproduct_sgst',
            field=models.FloatField(default=2.5),
        ),
    ]
