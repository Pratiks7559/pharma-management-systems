# Generated migration to add source challan fields to SalesMaster

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '1007_add_challan_reference_to_purchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesmaster',
            name='source_challan_no',
            field=models.CharField(max_length=50, blank=True, null=True, help_text='Source customer challan number if pulled from challan'),
        ),
        migrations.AddField(
            model_name='salesmaster',
            name='source_challan_date',
            field=models.DateField(blank=True, null=True, help_text='Source customer challan date if pulled from challan'),
        ),
    ]
