import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.db import connection

print("⚡ ULTRA FAST Cache Rebuild - Raw SQL")
print("=" * 60)

with connection.cursor() as cursor:
    # Clear old cache
    print("🗑️  Clearing old cache...")
    cursor.execute("DELETE FROM core_batchinventorycache")
    cursor.execute("DELETE FROM core_productinventorycache")
    
    # Create batch cache with single query
    print("💾 Creating batch cache (this may take 30-60 seconds)...")
    cursor.execute("""
        INSERT INTO core_batchinventorycache 
        (product_id, batch_no, expiry_date, current_stock, mrp, purchase_rate, rate_a, rate_b, rate_c, is_expired, expiry_status)
        SELECT 
            productid,
            product_batch_no,
            product_expiry,
            COALESCE(
                (SELECT SUM(product_quantity) FROM core_purchasemaster WHERE productid = p.productid AND product_batch_no = p.product_batch_no AND product_expiry = p.product_expiry) +
                COALESCE((SELECT SUM(product_quantity) FROM core_supplierchallanmaster WHERE product_id = p.productid AND product_batch_no = p.product_batch_no AND product_expiry = p.product_expiry), 0) +
                COALESCE((SELECT SUM(return_sale_quantity) FROM core_returnsalesmaster WHERE return_productid = p.productid AND return_product_batch_no = p.product_batch_no AND return_product_expiry = p.product_expiry), 0) -
                COALESCE((SELECT SUM(sale_quantity) FROM core_salesmaster WHERE productid = p.productid AND product_batch_no = p.product_batch_no AND product_expiry = p.product_expiry), 0) -
                COALESCE((SELECT SUM(sale_quantity) FROM core_customerchallanmaster WHERE product_id = p.productid AND product_batch_no = p.product_batch_no AND product_expiry = p.product_expiry), 0) -
                COALESCE((SELECT SUM(returnproduct_quantity) FROM core_returnpurchasemaster WHERE returnproductid = p.productid AND returnproduct_batch_no = p.product_batch_no), 0),
            0) as stock,
            MAX(product_MRP),
            MAX(product_purchase_rate),
            MAX(rate_a),
            MAX(rate_b),
            MAX(rate_c),
            0,
            'valid'
        FROM core_purchasemaster p
        GROUP BY productid, product_batch_no, product_expiry
        HAVING stock > 0
    """)
    
    batch_count = cursor.rowcount
    print(f"✅ Created {batch_count} batch cache entries")
    
    # Create product cache
    print("📦 Creating product cache...")
    cursor.execute("""
        INSERT INTO core_productinventorycache 
        (product_id, total_stock, total_batches, avg_mrp, avg_purchase_rate, total_stock_value, stock_status, has_expired_batches)
        SELECT 
            product_id,
            SUM(current_stock),
            COUNT(*),
            AVG(mrp),
            AVG(purchase_rate),
            SUM(current_stock * mrp),
            CASE 
                WHEN SUM(current_stock) > 10 THEN 'in_stock'
                WHEN SUM(current_stock) > 0 THEN 'low_stock'
                ELSE 'out_of_stock'
            END,
            0
        FROM core_batchinventorycache
        GROUP BY product_id
    """)
    
    product_count = cursor.rowcount
    print(f"✅ Created {product_count} product cache entries")

print("=" * 60)
print("✅ DONE in seconds!")
