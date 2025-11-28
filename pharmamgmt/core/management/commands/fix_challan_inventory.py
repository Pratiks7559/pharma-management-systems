from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from core.models import (
    PurchaseMaster, SupplierChallanMaster, Challan1, 
    ProductMaster, SalesMaster
)

class Command(BaseCommand):
    help = 'Fix challan inventory double counting issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Apply the fixes',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Challan Inventory Fix Tool')
        )
        
        # Find potential duplicates
        duplicates = self.find_duplicates()
        
        if not duplicates:
            self.stdout.write(
                self.style.SUCCESS('✅ No challan inventory issues found!')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'📊 Found {len(duplicates)} potential duplicate entries')
        )
        
        if options['dry_run'] or not options['fix']:
            self.show_dry_run(duplicates)
        
        if options['fix']:
            self.apply_fixes(duplicates)
    
    def find_duplicates(self):
        """Find purchases that match challan entries"""
        duplicates = []
        invoiced_challans = Challan1.objects.filter(is_invoiced=True)
        
        for challan in invoiced_challans:
            challan_products = SupplierChallanMaster.objects.filter(
                product_challan_id=challan
            )
            
            for challan_product in challan_products:
                matching_purchases = PurchaseMaster.objects.filter(
                    productid=challan_product.product_id,
                    product_batch_no=challan_product.product_batch_no,
                    product_quantity=challan_product.product_quantity
                ).exclude(
                    product_invoice_no__icontains='from challan'
                )
                
                if matching_purchases.exists():
                    duplicates.append({
                        'challan_no': challan.challan_no,
                        'product_name': challan_product.product_name,
                        'batch_no': challan_product.product_batch_no,
                        'quantity': challan_product.product_quantity,
                        'purchase_ids': [p.purchaseid for p in matching_purchases]
                    })
        
        return duplicates
    
    def show_dry_run(self, duplicates):
        """Show what would be fixed"""
        self.stdout.write(
            self.style.WARNING('📋 DRY RUN - Would mark these purchases as challan-sourced:')
        )
        
        for i, dup in enumerate(duplicates[:10]):  # Show first 10
            self.stdout.write(
                f"   {i+1}. Challan {dup['challan_no']} -> {dup['product_name']} "
                f"(Batch: {dup['batch_no']}, Qty: {dup['quantity']})"
            )
        
        if len(duplicates) > 10:
            self.stdout.write(f"   ... and {len(duplicates) - 10} more")
        
        self.stdout.write(
            self.style.WARNING('\nRun with --fix to apply changes')
        )
    
    def apply_fixes(self, duplicates):
        """Apply the fixes"""
        self.stdout.write(
            self.style.SUCCESS('🔧 Applying fixes...')
        )
        
        marked_count = 0
        
        with transaction.atomic():
            for dup in duplicates:
                try:
                    purchases = PurchaseMaster.objects.filter(
                        purchaseid__in=dup['purchase_ids']
                    )
                    
                    for purchase in purchases:
                        original_invoice_no = purchase.product_invoice_no
                        if 'from challan' not in original_invoice_no:
                            purchase.product_invoice_no = f"{original_invoice_no} (from challan {dup['challan_no']})"
                            purchase.save()
                            marked_count += 1
                            
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Error fixing challan {dup['challan_no']}: {e}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Fixed {marked_count} purchase entries')
        )
        
        # Validate results
        self.validate_results()
    
    def validate_results(self):
        """Validate the fixes"""
        self.stdout.write(
            self.style.SUCCESS('🔍 Validating results...')
        )
        
        # Check a few products for negative stock
        test_products = ProductMaster.objects.all()[:5]
        issues = 0
        
        for product in test_products:
            try:
                from core.stock_manager import StockManager
                stock_summary = StockManager.get_stock_summary(product.productid)
                
                if stock_summary['total_stock'] < 0:
                    self.stdout.write(
                        self.style.ERROR(f"⚠️  {product.product_name}: Negative stock ({stock_summary['total_stock']})")
                    )
                    issues += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error checking {product.product_name}: {e}")
                )
                issues += 1
        
        if issues == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Validation passed - no issues detected')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Found {issues} potential issues - manual review recommended')
            )