# Generated migration for adding return reason choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '1016_add_transport_charges_to_sales_return'),
    ]

    operations = [
        migrations.AlterField(
            model_name='returnsalesmaster',
            name='return_reason',
            field=models.CharField(blank=True, choices=[('', 'Select Reason'), ('non_moving', 'Non Moving'), ('breakage', 'Breakage'), ('expiry', 'Expiry')], max_length=200, null=True),
        ),
    ]
