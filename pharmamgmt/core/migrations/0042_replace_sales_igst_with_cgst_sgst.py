# Generated migration to replace IGST with CGST and SGST in sales models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_replace_igst_with_cgst_sgst'),
    ]

    operations = [
        # Add CGST and SGST fields to SalesMaster
        migrations.AddField(
            model_name='salesmaster',
            name='sale_cgst',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='salesmaster',
            name='sale_sgst',
            field=models.FloatField(default=0.0),
        ),
        # Remove IGST field from SalesMaster
        migrations.RemoveField(
            model_name='salesmaster',
            name='sale_igst',
        ),
        
        # Add CGST and SGST fields to ReturnSalesMaster
        migrations.AddField(
            model_name='returnsalesmaster',
            name='return_sale_cgst',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='returnsalesmaster',
            name='return_sale_sgst',
            field=models.FloatField(default=0.0),
        ),
        # Remove IGST field from ReturnSalesMaster
        migrations.RemoveField(
            model_name='returnsalesmaster',
            name='return_sale_igst',
        ),
    ]