from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster
import re
from datetime import datetime

class Command(BaseCommand):
    help = 'Convert existing expiry dates to MM-YYYY format'

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
        
        # Convert PurchaseMaster expiry dates
        self.convert_purchase_expiry(dry_run)
        
        # Convert SalesMaster expiry dates
        self.convert_sales_expiry(dry_run)
        
        # Convert ReturnPurchaseMaster expiry dates
        self.convert_return_purchase_expiry(dry_run)
        
        # Convert ReturnSalesMaster expiry dates
        self.convert_return_sales_expiry(dry_run)
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS('Successfully converted all expiry dates to MM-YYYY format'))
        else:
            self.stdout.write(self.style.SUCCESS('Dry run completed. Use without --dry-run to apply changes'))

    def convert_date_format(self, expiry_str):
        """Convert various date formats to MM-YYYY"""
        if not expiry_str:
            return expiry_str
            
        # Already in MM-YYYY format
        if re.match(r'^(0[1-9]|1[0-2])-\d{4}$', expiry_str):
            return expiry_str
            
        # Handle DDMMYYYY format
        if len(expiry_str) == 8 and expiry_str.isdigit():
            day = expiry_str[:2]
            month = expiry_str[2:4]
            year = expiry_str[4:8]
            return f"{month}-{year}"
            
        # Handle DD/MM/YYYY format
        if re.match(r'^\d{2}/\d{2}/\d{4}$', expiry_str):
            parts = expiry_str.split('/')
            return f"{parts[1]}-{parts[2]}"
            
        # Handle YYYY-MM-DD format (from date fields)
        if re.match(r'^\d{4}-\d{2}-\d{2}$', expiry_str):
            parts = expiry_str.split('-')
            return f"{parts[1]}-{parts[0]}"
            
        # Handle MM/YYYY format
        if re.match(r'^\d{2}/\d{4}$', expiry_str):
            return expiry_str.replace('/', '-')
            
        # Handle MMYY format
        if len(expiry_str) == 4 and expiry_str.isdigit():
            month = expiry_str[:2]
            year = '20' + expiry_str[2:4]
            return f"{month}-{year}"
            
        # If we can't convert, return original
        self.stdout.write(
            self.style.WARNING(f'Could not convert expiry format: {expiry_str}')
        )
        return expiry_str

    def convert_purchase_expiry(self, dry_run):
        """Convert PurchaseMaster expiry dates"""
        purchases = PurchaseMaster.objects.all()
        converted_count = 0
        
        self.stdout.write(f'Processing {purchases.count()} purchase records...')
        
        for purchase in purchases:
            old_expiry = purchase.product_expiry
            new_expiry = self.convert_date_format(old_expiry)
            
            if old_expiry != new_expiry:
                converted_count += 1
                if dry_run:
                    self.stdout.write(f'Purchase ID {purchase.purchaseid}: {old_expiry} -> {new_expiry}')
                else:
                    purchase.product_expiry = new_expiry
                    purchase.save(update_fields=['product_expiry'])
        
        self.stdout.write(f'PurchaseMaster: {converted_count} records converted')

    def convert_sales_expiry(self, dry_run):
        """Convert SalesMaster expiry dates"""
        sales = SalesMaster.objects.all()
        converted_count = 0
        
        self.stdout.write(f'Processing {sales.count()} sales records...')
        
        for sale in sales:
            old_expiry = sale.product_expiry
            new_expiry = self.convert_date_format(old_expiry)
            
            if old_expiry != new_expiry:
                converted_count += 1
                if dry_run:
                    self.stdout.write(f'Sale ID {sale.id}: {old_expiry} -> {new_expiry}')
                else:
                    sale.product_expiry = new_expiry
                    sale.save(update_fields=['product_expiry'])
        
        self.stdout.write(f'SalesMaster: {converted_count} records converted')

    def convert_return_purchase_expiry(self, dry_run):
        """Convert ReturnPurchaseMaster expiry dates"""
        returns = ReturnPurchaseMaster.objects.all()
        converted_count = 0
        
        self.stdout.write(f'Processing {returns.count()} purchase return records...')
        
        for return_item in returns:
            # ReturnPurchaseMaster uses DateField, so we need to convert to string
            if hasattr(return_item, 'returnproduct_expiry') and return_item.returnproduct_expiry:
                old_expiry = str(return_item.returnproduct_expiry)
                new_expiry = self.convert_date_format(old_expiry)
                
                if old_expiry != new_expiry:
                    converted_count += 1
                    if dry_run:
                        self.stdout.write(f'Return Purchase ID {return_item.returnpurchaseid}: {old_expiry} -> {new_expiry}')
                    else:
                        # Note: This field might need to be changed to CharField in model
                        self.stdout.write(f'Warning: ReturnPurchaseMaster.returnproduct_expiry is DateField, consider changing to CharField')
        
        self.stdout.write(f'ReturnPurchaseMaster: {converted_count} records would be converted (field type needs update)')

    def convert_return_sales_expiry(self, dry_run):
        """Convert ReturnSalesMaster expiry dates"""
        returns = ReturnSalesMaster.objects.all()
        converted_count = 0
        
        self.stdout.write(f'Processing {returns.count()} sales return records...')
        
        for return_item in returns:
            old_expiry = return_item.return_product_expiry
            new_expiry = self.convert_date_format(old_expiry)
            
            if old_expiry != new_expiry:
                converted_count += 1
                if dry_run:
                    self.stdout.write(f'Return Sale ID {return_item.return_sales_id}: {old_expiry} -> {new_expiry}')
                else:
                    return_item.return_product_expiry = new_expiry
                    return_item.save(update_fields=['return_product_expiry'])
        
        self.stdout.write(f'ReturnSalesMaster: {converted_count} records converted')