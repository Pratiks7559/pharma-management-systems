# Generated migration for inventory performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Add indexes for frequently queried fields
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_purchase_product_batch ON core_purchasemaster(productid_id, product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_purchase_product_batch;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sales_product_batch ON core_salesmaster(productid_id, product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_sales_product_batch;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_purchase_product ON core_purchasemaster(productid_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_purchase_product;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sales_product ON core_salesmaster(productid_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_sales_product;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_name ON core_productmaster(product_name);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_company ON core_productmaster(product_company);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_company;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_purchase_entry_date ON core_purchasemaster(purchase_entry_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_purchase_entry_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sale_entry_date ON core_salesmaster(sale_entry_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_sale_entry_date;"
        ),
    ]