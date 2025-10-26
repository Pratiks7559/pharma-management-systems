from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_salesmaster_id'),
    ]

    operations = [
        # Add indexes for ProductMaster
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_name ON core_productmaster(product_name);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_company ON core_productmaster(product_company);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_company;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_barcode ON core_productmaster(product_barcode);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_barcode;"
        ),
        
        # Add indexes for PurchaseMaster
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_purchase_productid ON core_purchasemaster(productid_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_purchase_productid;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_purchase_batch ON core_purchasemaster(product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_purchase_batch;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_purchase_expiry ON core_purchasemaster(product_expiry);",
            reverse_sql="DROP INDEX IF EXISTS idx_purchase_expiry;"
        ),
        
        # Add indexes for SalesMaster
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sales_productid ON core_salesmaster(productid_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_sales_productid;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sales_batch ON core_salesmaster(product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_sales_batch;"
        ),
        
        # Add composite indexes for common queries
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_purchase_product_batch ON core_purchasemaster(productid_id, product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_purchase_product_batch;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sales_product_batch ON core_salesmaster(productid_id, product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_sales_product_batch;"
        ),
    ]