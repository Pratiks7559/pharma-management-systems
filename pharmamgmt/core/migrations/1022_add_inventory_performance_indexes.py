from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('core', '1021_add_performance_indexes'),
    ]

    operations = [
        # ProductMaster indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_name ON core_productmaster(product_name);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_product_company ON core_productmaster(product_company);",
            reverse_sql="DROP INDEX IF EXISTS idx_product_company;"
        ),
        
        # PurchaseMaster indexes for inventory calculation
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_purchase_product_batch ON core_purchasemaster(productid_id, product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_purchase_product_batch;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_purchase_expiry ON core_purchasemaster(product_expiry);",
            reverse_sql="DROP INDEX IF EXISTS idx_purchase_expiry;"
        ),
        
        # SalesMaster indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_sales_product_batch ON core_salesmaster(productid_id, product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_sales_product_batch;"
        ),
        
        # SaleRateMaster indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_salerate_product_batch ON core_saleratemaster(productid_id, product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_salerate_product_batch;"
        ),
        
        # ReturnPurchaseMaster indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_return_purchase_product_batch ON core_returnpurchasemaster(returnproductid_id, returnproduct_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_return_purchase_product_batch;"
        ),
        
        # ReturnSalesMaster indexes
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_return_sales_product_batch ON core_returnsalesmaster(return_productid_id, return_product_batch_no);",
            reverse_sql="DROP INDEX IF EXISTS idx_return_sales_product_batch;"
        ),
        

        

    ]
