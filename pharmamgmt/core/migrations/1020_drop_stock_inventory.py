from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '1019_stockinventory'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS stock_inventory CASCADE;",
            reverse_sql="",
        ),
    ]
