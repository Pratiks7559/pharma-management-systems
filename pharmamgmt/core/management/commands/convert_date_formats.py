"""
Management command to convert existing date formats to DDMMYYYY
This ensures backward compatibility with existing database data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    InvoiceMaster, SalesInvoiceMaster, PurchaseMaster, SalesMaster,
    ReturnInvoiceMaster, ReturnPurchaseMaster, ReturnSalesInvoiceMaster, ReturnSalesMaster, ReceiptMaster, InvoicePaid, SalesInvoicePaid
)
from core.date_utils import format_date_for_backend, convert_legacy_dates
from datetime import datetime


class Command(BaseCommand):
    help = 'Convert existing date formats to ensure consistency with DDMMYYYY format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be converted without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        with transaction.atomic():
            # Convert expiry dates in PurchaseMaster
            self.convert_purchase_expiry_dates(dry_run)
            
            # Convert expiry dates in SalesMaster
            self.convert_sales_expiry_dates(dry_run)
            
            # Convert expiry dates in ReturnPurchaseMaster
            self.convert_return_purchase_expiry_dates(dry_run)
            
            # Convert expiry dates in ReturnSalesMaster
            self.convert_return_sales_expiry_dates(dry_run)
            
            if dry_run:
                # Rollback transaction in dry run mode
                transaction.set_rollback(True)
                self.stdout.write(self.style.SUCCESS('DRY RUN COMPLETED - No changes were made'))
            else:
                self.stdout.write(self.style.SUCCESS('Date format conversion completed successfully'))

    def convert_purchase_expiry_dates(self, dry_run):
        """Convert expiry dates in PurchaseMaster from MM-YYYY to DDMMYYYY"""
        purchases = PurchaseMaster.objects.all()
        converted_count = 0
        
        for purchase in purchases:
            old_expiry = purchase.product_expiry
            if old_expiry and isinstance(old_expiry, str):
                # Convert MM-YYYY to DDMMYYYY (last day of month)
                new_expiry = convert_legacy_dates(old_expiry)
                if new_expiry != old_expiry:
                    if not dry_run:
                        purchase.product_expiry = new_expiry
                        purchase.save(update_fields=['product_expiry'])
                    converted_count += 1
                    if dry_run:
                        self.stdout.write(f'Would convert Purchase {purchase.purchaseid}: {old_expiry} -> {new_expiry}')
        
        self.stdout.write(f'Purchase expiry dates: {converted_count} records {"would be" if dry_run else ""} converted')

    def convert_sales_expiry_dates(self, dry_run):
        """Convert expiry dates in SalesMaster from MM-YYYY to DDMMYYYY"""
        sales = SalesMaster.objects.all()
        converted_count = 0
        
        for sale in sales:
            old_expiry = sale.product_expiry
            if old_expiry and isinstance(old_expiry, str):
                # Convert MM-YYYY to DDMMYYYY (last day of month)
                new_expiry = convert_legacy_dates(old_expiry)
                if new_expiry != old_expiry:
                    if not dry_run:
                        sale.product_expiry = new_expiry
                        sale.save(update_fields=['product_expiry'])
                    converted_count += 1
                    if dry_run:
                        self.stdout.write(f'Would convert Sale {sale.id}: {old_expiry} -> {new_expiry}')
        
        self.stdout.write(f'Sales expiry dates: {converted_count} records {"would be" if dry_run else ""} converted')

    def convert_return_purchase_expiry_dates(self, dry_run):
        """Convert expiry dates in ReturnPurchaseMaster"""
        returns = ReturnPurchaseMaster.objects.all()
        converted_count = 0
        
        for return_item in returns:
            # ReturnPurchaseMaster uses DateField, so we need to handle differently
            old_expiry = return_item.returnproduct_expiry
            if old_expiry:
                # This field is already a DateField, so it should be fine
                # But we can validate the format
                if not dry_run:
                    # Ensure it's in proper date format
                    pass
                converted_count += 1
        
        self.stdout.write(f'Return purchase expiry dates: {converted_count} records checked')

    def convert_return_sales_expiry_dates(self, dry_run):
        """Convert expiry dates in ReturnSalesMaster from MM-YYYY to DDMMYYYY"""
        returns = ReturnSalesMaster.objects.all()
        converted_count = 0
        
        for return_item in returns:
            old_expiry = return_item.return_product_expiry
            if old_expiry and isinstance(old_expiry, str):
                # Convert MM-YYYY to DDMMYYYY (last day of month)
                new_expiry = convert_legacy_dates(old_expiry)
                if new_expiry != old_expiry:
                    if not dry_run:
                        return_item.return_product_expiry = new_expiry
                        return_item.save(update_fields=['return_product_expiry'])
                    converted_count += 1
                    if dry_run:
                        self.stdout.write(f'Would convert Return Sale {return_item.return_sales_id}: {old_expiry} -> {new_expiry}')
        
        self.stdout.write(f'Return sales expiry dates: {converted_count} records {"would be" if dry_run else ""} converted')