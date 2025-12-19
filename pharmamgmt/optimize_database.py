import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.db import connection

print("Adding database indexes for better performance...")

indexes = [
    "CREATE INDEX IF NOT EXISTS idx_product_name ON core_product(product_name);",
    "CREATE INDEX IF NOT EXISTS idx_invoice_date ON core_invoice(invoice_date);",
    "CREATE INDEX IF NOT EXISTS idx_sales_date ON core_salesinvoice(invoice_date);",
    "CREATE INDEX IF NOT EXISTS idx_inventory_product ON core_inventory(product_id);",
    "CREATE INDEX IF NOT EXISTS idx_inventory_batch ON core_inventory(batch_no);",
    "CREATE INDEX IF NOT EXISTS idx_customer_name ON core_customer(customer_name);",
    "CREATE INDEX IF NOT EXISTS idx_supplier_name ON core_supplier(supplier_name);",
]

with connection.cursor() as cursor:
    for idx in indexes:
        try:
            cursor.execute(idx)
            print(f"✓ Created: {idx.split('idx_')[1].split(' ')[0]}")
        except Exception as e:
            print(f"✗ Error: {e}")

print("\nOptimization complete! Restart server.")
