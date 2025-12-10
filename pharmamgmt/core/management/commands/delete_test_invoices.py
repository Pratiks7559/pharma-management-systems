from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import InvoiceMaster, PurchaseMaster

class Command(BaseCommand):
    help = 'Delete all test purchase invoices (starting with TEST-INV-)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting test invoices...')
        
        with transaction.atomic():
            # Delete purchases first
            deleted_purchases = PurchaseMaster.objects.filter(
                product_invoice_no__startswith='TEST-INV-'
            ).delete()
            
            # Delete invoices
            deleted_invoices = InvoiceMaster.objects.filter(
                invoice_no__startswith='TEST-INV-'
            ).delete()
        
        self.stdout.write(self.style.SUCCESS(
            f'Deleted {deleted_invoices[0]} invoices and {deleted_purchases[0]} purchase records!'
        ))
