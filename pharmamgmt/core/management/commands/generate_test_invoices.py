from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import InvoiceMaster, PurchaseMaster, SupplierMaster, ProductMaster
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Generate 100,000 test purchase invoice records'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to generate 100,000 purchase invoices...')
        
        # Get existing suppliers and products
        suppliers = list(SupplierMaster.objects.all())
        products = list(ProductMaster.objects.all())
        
        if not suppliers:
            self.stdout.write(self.style.ERROR('No suppliers found. Please add suppliers first.'))
            return
        
        if not products:
            self.stdout.write(self.style.ERROR('No products found. Please add products first.'))
            return
        
        batch_size = 1000
        total_invoices = 100000
        start_date = datetime.now() - timedelta(days=365)
        
        for batch_num in range(0, total_invoices, batch_size):
            invoices_to_create = []
            purchases_to_create = []
            
            with transaction.atomic():
                for i in range(batch_size):
                    if batch_num + i >= total_invoices:
                        break
                    
                    # Random invoice data
                    supplier = random.choice(suppliers)
                    invoice_date = start_date + timedelta(days=random.randint(0, 365))
                    invoice_no = f'TEST-INV-{batch_num + i + 1:06d}'
                    
                    # Create invoice
                    invoice = InvoiceMaster.objects.create(
                        supplierid=supplier,
                        invoice_no=invoice_no,
                        invoice_date=invoice_date,
                        invoice_total=0,
                        invoice_paid=0,
                        transport_charges=random.uniform(0, 500)
                    )
                    
                    # Add 1-5 products per invoice
                    num_products = random.randint(1, 5)
                    invoice_total = 0
                    
                    for _ in range(num_products):
                        product = random.choice(products)
                        quantity = random.randint(10, 100)
                        rate = random.uniform(10, 500)
                        discount = random.uniform(0, rate * 0.1)
                        
                        actual_rate = rate - (discount / quantity)
                        total = actual_rate * quantity
                        invoice_total += total
                        
                        PurchaseMaster.objects.create(
                            product_supplierid=supplier,
                            product_invoiceid=invoice,
                            product_invoice_no=invoice_no,
                            productid=product,
                            product_name=product.product_name,
                            product_company=product.product_company,
                            product_packing=product.product_packing,
                            product_batch_no=f'BATCH-{random.randint(1000, 9999)}',
                            product_expiry=f'{random.randint(1, 12):02d}-{random.randint(2024, 2026)}',
                            product_MRP=rate * 1.5,
                            product_purchase_rate=rate,
                            product_quantity=quantity,
                            product_scheme=0,
                            product_discount_got=discount,
                            CGST=2.5,
                            SGST=2.5,
                            purchase_calculation_mode='flat',
                            actual_rate_per_qty=actual_rate,
                            product_actual_rate=actual_rate,
                            total_amount=total,
                            product_transportation_charges=0
                        )
                    
                    # Update invoice total
                    invoice.invoice_total = invoice_total + invoice.transport_charges
                    invoice.invoice_paid = random.uniform(0, invoice_total) if random.random() > 0.3 else 0
                    invoice.save()
            
            self.stdout.write(f'Created {batch_num + batch_size}/{total_invoices} invoices...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {total_invoices} test invoices!'))
