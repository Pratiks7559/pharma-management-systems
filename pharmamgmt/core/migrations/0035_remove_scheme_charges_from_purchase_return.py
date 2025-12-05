from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_add_cgst_sgst_to_purchase_return'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='returnpurchasemaster',
            name='returnproduct_scheme',
        ),
        migrations.RemoveField(
            model_name='returnpurchasemaster',
            name='returnproduct_charges',
        ),
    ]
