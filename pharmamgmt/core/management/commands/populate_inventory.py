from django.core.management.base import BaseCommand
from core.models import InventoryMaster, PurchaseMaster, SalesMaster
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Populate inventory from existing purchase and sales data'

    def handle(self, *args, **options):
        self.stdout.write('Populating inventory...')
        
        # Get all unique product-batch combinations from purchases
        purchases = PurchaseMaster.objects.values(
            'productid', 'product_batch_no', 'product_expiry'
        ).annotate(
            total_purchased=Sum('product_quantity'),
            avg_rate=Sum('product_purchase_rate')/Sum('product_quantity')
        ).distinct()
        
        created_count = 0
        updated_count = 0
        
        for purchase in purchases:
            # Calculate total sold for this batch
            total_sold = SalesMaster.objects.filter(
                productid=purchase['productid'],
                product_batch_no=purchase['product_batch_no']
            ).aggregate(Sum('sale_quantity'))['sale_quantity__sum'] or 0
            
            current_stock = purchase['total_purchased'] - total_sold
            
            # Create or update inventory
            inventory, created = InventoryMaster.objects.get_or_create(
                product_id=purchase['productid'],
                batch_no=purchase['product_batch_no'],
                defaults={
                    'expiry_date': purchase['product_expiry'],
                    'current_stock': current_stock,
                    'purchase_rate': purchase['avg_rate'] or 0,
                    'available_stock': current_stock,
                }
            )
            
            if created:
                created_count += 1
            else:
                inventory.current_stock = current_stock
                inventory.available_stock = current_stock
                inventory.save()
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated inventory: {created_count} created, {updated_count} updated'
            )
        )