from django.core.management.base import BaseCommand
from django.db import transaction, models
from core.models import SalesInvoiceMaster, SalesInvoicePaid, InvoiceMaster, InvoicePaid

class Command(BaseCommand):
    help = 'Sync payment totals for sales and purchase invoices'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Syncing payment totals...")
        
        # Fix Sales Invoices
        sales_fixed = 0
        for invoice in SalesInvoiceMaster.objects.all():
            actual_paid = SalesInvoicePaid.objects.filter(
                sales_ip_invoice_no=invoice
            ).aggregate(total=models.Sum('sales_payment_amount'))['total'] or 0
            
            if invoice.sales_invoice_paid != actual_paid:
                self.stdout.write(f"📋 Sales Invoice {invoice.sales_invoice_no}: {invoice.sales_invoice_paid} → {actual_paid}")
                invoice.sales_invoice_paid = actual_paid
                invoice.save()
                sales_fixed += 1
        
        # Fix Purchase Invoices  
        purchase_fixed = 0
        for invoice in InvoiceMaster.objects.all():
            actual_paid = InvoicePaid.objects.filter(
                ip_invoiceid=invoice
            ).aggregate(total=models.Sum('payment_amount'))['total'] or 0
            
            if invoice.invoice_paid != actual_paid:
                self.stdout.write(f"📋 Purchase Invoice {invoice.invoice_no}: {invoice.invoice_paid} → {actual_paid}")
                invoice.invoice_paid = actual_paid
                invoice.save()
                purchase_fixed += 1
        
        self.stdout.write(f"✅ Fixed {sales_fixed} sales invoices and {purchase_fixed} purchase invoices")