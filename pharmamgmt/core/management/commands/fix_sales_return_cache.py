"""
Django Management Command: Fix Sales Return Cache
Usage: python manage.py fix_sales_return_cache
"""
from django.core.management.base import BaseCommand
from core.inventory_cache import update_all_batches_for_product, rebuild_all_cache
from core.models import ReturnSalesMaster


class Command(BaseCommand):
    help = 'Fix inventory cache for sales returns'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Rebuild entire cache instead of just sales returns',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("SALES RETURN CACHE FIX"))
        self.stdout.write("=" * 60)
        
        if options['full']:
            self.stdout.write("\n🔧 Rebuilding entire cache...")
            rebuild_all_cache()
        else:
            self.stdout.write("\n🔧 Fixing sales return cache...")
            
            # Get all unique products from sales returns
            returns = ReturnSalesMaster.objects.values('return_productid').distinct()
            
            fixed_count = 0
            total = returns.count()
            
            for idx, ret in enumerate(returns, 1):
                product_id = ret['return_productid']
                try:
                    update_all_batches_for_product(product_id)
                    fixed_count += 1
                    self.stdout.write(f"✅ [{idx}/{total}] Fixed product {product_id}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error fixing product {product_id}: {e}"))
            
            self.stdout.write(self.style.SUCCESS(f"\n✅ Fixed {fixed_count}/{total} products"))
        
        self.stdout.write(self.style.SUCCESS("\n✅ Done! Check All Product Inventory now."))
