# Generated migration to replace IGST with CGST and SGST

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_remove_customermaster_customer_bank_and_more'),
    ]

    operations = [
        # Add CGST and SGST fields
        migrations.AddField(
            model_name='purchasemaster',
            name='CGST',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='purchasemaster',
            name='SGST',
            field=models.FloatField(default=0.0),
        ),
        # Remove IGST field
        migrations.RemoveField(
            model_name='purchasemaster',
            name='IGST',
        ),
    ]
