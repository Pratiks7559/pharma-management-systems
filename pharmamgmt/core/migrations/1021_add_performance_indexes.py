from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '1020_drop_stock_inventory'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='purchasemaster',
            index=models.Index(fields=['productid', 'product_batch_no'], name='idx_purchase_prod_batch'),
        ),
        migrations.AddIndex(
            model_name='purchasemaster',
            index=models.Index(fields=['product_invoice_no'], name='idx_purchase_invoice'),
        ),
        migrations.AddIndex(
            model_name='salesmaster',
            index=models.Index(fields=['productid', 'product_batch_no'], name='idx_sales_prod_batch'),
        ),
        migrations.AddIndex(
            model_name='salesmaster',
            index=models.Index(fields=['sales_invoice_no'], name='idx_sales_invoice'),
        ),
        migrations.AddIndex(
            model_name='returnpurchasemaster',
            index=models.Index(fields=['returnproductid', 'returnproduct_batch_no'], name='idx_ret_pur_prod_batch'),
        ),
        migrations.AddIndex(
            model_name='returnsalesmaster',
            index=models.Index(fields=['return_productid', 'return_product_batch_no'], name='idx_ret_sal_prod_batch'),
        ),
        migrations.AddIndex(
            model_name='supplierchallanmaster',
            index=models.Index(fields=['product_id', 'product_batch_no'], name='idx_sup_chal_prod_batch'),
        ),
        migrations.AddIndex(
            model_name='customerchallanmaster',
            index=models.Index(fields=['product_id', 'product_batch_no'], name='idx_cust_chal_prod_batch'),
        ),
    ]
