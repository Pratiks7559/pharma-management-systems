# Generated migration to make supplier fields optional

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '1001_batchstocksummary_inventorymaster_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_type',
            field=models.CharField(max_length=200, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_address',
            field=models.CharField(max_length=200, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_whatsapp',
            field=models.CharField(max_length=15, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_emailid',
            field=models.CharField(max_length=60, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_spoc',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_dlno',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_gstno',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_bank',
            field=models.CharField(max_length=200, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_bankaccountno',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_bankifsc',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='suppliermaster',
            name='supplier_upi',
            field=models.CharField(max_length=50, null=True, blank=True, default=''),
        ),
    ]