"""
Cache Rebuild Time Benchmark
"""
import time
from django.db import transaction

def benchmark_cache_rebuild():
    """Measure cache rebuild time for different data sizes"""
    
    sizes = [1000, 5000, 10000, 25000]
    
    for size in sizes:
        print(f"\nTesting {size:,} products...")
        
        start_time = time.time()
        
        # Simulate cache rebuild
        with transaction.atomic():
            # Clear cache
            ProductInventoryCache.objects.all().delete()
            BatchInventoryCache.objects.all().delete()
            
            # Rebuild for 'size' products
            products = ProductMaster.objects.all()[:size]
            
            for product in products:
                # Calculate stock (simplified)
                purchases = PurchaseMaster.objects.filter(productid=product)
                sales = SalesMaster.objects.filter(productid=product)
                
                total_purchased = sum(p.product_quantity or 0 for p in purchases)
                total_sold = sum(s.sale_quantity or 0 for s in sales)
                current_stock = total_purchased - total_sold
                
                # Create cache
                ProductInventoryCache.objects.create(
                    product=product,
                    total_stock=current_stock,
                    stock_status='in_stock' if current_stock > 0 else 'out_of_stock'
                )
        
        rebuild_time = time.time() - start_time
        
        print(f"Cache rebuild time: {rebuild_time:.2f} seconds")
        print(f"Per product: {rebuild_time/size*1000:.2f} ms")

# Expected Results:
# 1K products = ~5 seconds
# 5K products = ~25 seconds  
# 10K products = ~50 seconds
# 25K products = ~120 seconds (2 minutes)