# Generated migration for adding challan reference fields to PurchaseMaster

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '1006_purchasemaster_rate_a_purchasemaster_rate_b_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasemaster',
            name='source_challan_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='purchasemaster',
            name='source_challan_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
