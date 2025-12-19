"""
Cached Inventory Views - Using ProductInventoryCache and BatchInventoryCache
Super fast inventory display using pre-calculated cache tables
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from .models import ProductInventoryCache, BatchInventoryCache, ProductMaster


@login_required
def inventory_list_cached(request):
    """
    Show ALL products (with and without stock) - cache on-the-fly
    """
    from .inventory_cache import update_all_batches_for_product
    
    search_query = request.GET.get('search', '').strip()
    
    # Get ALL products (not just cached ones)
    products = ProductMaster.objects.all()
    
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(product_company__icontains=search_query) |
            Q(product_category__icontains=search_query)
        )
    
    products = products.order_by('product_name')
    
    # Pagination
    paginator = Paginator(products, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Prepare data with on-the-fly cache
    inventory_data = []
    for product in page_obj:
        # Get or create cache
        cache = ProductInventoryCache.objects.filter(product=product).first()
        if not cache:
            # Create cache on-the-fly for products without cache
            update_all_batches_for_product(product.productid)
            cache = ProductInventoryCache.objects.filter(product=product).first()
        
        # Get batches
        batches = BatchInventoryCache.objects.filter(
            product=product,
            current_stock__gt=0
        ).order_by('expiry_date')
        
        batches_info = [{
            'batch_no': b.batch_no,
            'expiry': b.expiry_date,
            'stock': b.current_stock,
            'mrp': b.mrp,
            'purchase_rate': b.purchase_rate,
            'rates': {'rate_A': b.rate_a, 'rate_B': b.rate_b, 'rate_C': b.rate_c}
        } for b in batches]
        
        inventory_data.append({
            'product': product,
            'total_stock': cache.total_stock if cache else 0,
            'total_batches': len(batches_info),
            'stock_value': cache.total_stock_value if cache else 0,
            'status': cache.stock_status if cache else 'out_of_stock',
            'batches_info': batches_info
        })
    
    # Statistics
    page_total_value = sum(item['stock_value'] for item in inventory_data)
    page_low_stock = sum(1 for item in inventory_data if item['status'] == 'low_stock')
    page_out_of_stock = sum(1 for item in inventory_data if item['status'] == 'out_of_stock')
    
    # Check if AJAX request for Load More
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        from django.template.loader import render_to_string
        
        html = render_to_string('inventory/inventory_rows.html', {'inventory_data': inventory_data})
        
        return JsonResponse({
            'success': True,
            'html': html,
            'has_more': page_obj.has_next(),
            'next_offset': page_obj.next_page_number() if page_obj.has_next() else None,
            'total_count': products.count(),
            'batch_stats': {
                'total_value': page_total_value,
                'low_stock': page_low_stock,
                'out_of_stock': page_out_of_stock
            }
        })
    
    context = {
        'inventory_data': inventory_data,
        'page_obj': page_obj,
        'search_query': search_query,
        'total_products': products.count(),
        'page_total_value': page_total_value,
        'page_low_stock': page_low_stock,
        'page_out_of_stock': page_out_of_stock,
        'has_more': page_obj.has_next(),
        'next_offset': page_obj.next_page_number() if page_obj.has_next() else None,
    }
    
    return render(request, 'inventory/inventory_list.html', context)
