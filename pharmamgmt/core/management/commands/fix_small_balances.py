from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from core.models import InvoiceMaster, SalesInvoiceMaster

class Command(BaseCommand):
    help = 'Fix invoices with small balance issues (≤ 10 paisa)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.10,
            help='Balance threshold for auto-fix (default: 0.10)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        threshold = Decimal(str(options['threshold'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        self.stdout.write(f"Scanning for invoices with small balances ≤ Rs.{threshold}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
        
        # Fix supplier invoices
        supplier_invoices_fixed = 0
        supplier_invoices = InvoiceMaster.objects.all()
        
        for invoice in supplier_invoices:
            total = Decimal(str(invoice.invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            paid = Decimal(str(invoice.invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            balance = total - paid
            
            if 0 < balance <= threshold:
                self.stdout.write(f"Found supplier invoice {invoice.invoice_no} with small balance: Rs.{balance}")
                
                if not dry_run:
                    with transaction.atomic():
                        # Mark as fully paid by adjusting paid amount
                        invoice.invoice_paid = float(total)
                        invoice.payment_status = 'paid'
                        invoice.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Fixed supplier invoice {invoice.invoice_no}: Rs.{balance} written off")
                        )
                else:
                    self.stdout.write(f"Would fix supplier invoice {invoice.invoice_no}: Rs.{balance}")
                
                supplier_invoices_fixed += 1
        
        # Fix customer invoices
        customer_invoices_fixed = 0
        customer_invoices = SalesInvoiceMaster.objects.all()
        
        for invoice in customer_invoices:
            total = Decimal(str(invoice.sales_invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            paid = Decimal(str(invoice.sales_invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            balance = total - paid
            
            if 0 < balance <= threshold:
                self.stdout.write(f"Found customer invoice {invoice.sales_invoice_no} with small balance: Rs.{balance}")
                
                if not dry_run:
                    with transaction.atomic():
                        # Mark as fully paid by adjusting paid amount
                        invoice.sales_invoice_paid = float(total)
                        invoice.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Fixed customer invoice {invoice.sales_invoice_no}: Rs.{balance} written off")
                        )
                else:
                    self.stdout.write(f"Would fix customer invoice {invoice.sales_invoice_no}: Rs.{balance}")
                
                customer_invoices_fixed += 1
        
        # Summary
        total_fixed = supplier_invoices_fixed + customer_invoices_fixed
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"\nDRY RUN SUMMARY:")
            )
            self.stdout.write(f"Would fix {supplier_invoices_fixed} supplier invoices")
            self.stdout.write(f"Would fix {customer_invoices_fixed} customer invoices")
            self.stdout.write(f"Total invoices that would be fixed: {total_fixed}")
            self.stdout.write("\nRun without --dry-run to apply fixes")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\nFIX SUMMARY:")
            )
            self.stdout.write(f"Fixed {supplier_invoices_fixed} supplier invoices")
            self.stdout.write(f"Fixed {customer_invoices_fixed} customer invoices")
            self.stdout.write(f"Total invoices fixed: {total_fixed}")
        
        if total_fixed == 0:
            self.stdout.write(self.style.SUCCESS("No invoices with small balances found!"))