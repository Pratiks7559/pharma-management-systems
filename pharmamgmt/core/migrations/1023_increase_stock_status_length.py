from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '1022_add_inventory_performance_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinventorycache',
            name='stock_status',
            field=models.CharField(max_length=50, db_index=True, default='out_of_stock', 
                                  help_text="in_stock, low_stock, out_of_stock"),
        ),
    ]
