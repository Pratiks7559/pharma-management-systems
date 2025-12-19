"""
View Optimization - Add pagination and caching
"""

OPTIMIZATIONS = """
# Add to settings.py:

# Pagination
ITEMS_PER_PAGE = 50

# Query optimization
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
}

# Cache for dashboard
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# In views.py - Add pagination:
from django.core.paginator import Paginator

def product_list(request):
    products = ProductMaster.objects.all().only('product_id', 'product_name', 'product_company')
    paginator = Paginator(products, 50)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)
    return render(request, 'products.html', {'products': products_page})

# Dashboard - Use select_related and prefetch_related:
def dashboard(request):
    from django.core.cache import cache
    
    stats = cache.get('dashboard_stats')
    if not stats:
        stats = {
            'total_sales': SalesMaster.objects.count(),
            'total_purchases': PurchaseMaster.objects.count(),
            'total_products': ProductMaster.objects.count(),
        }
        cache.set('dashboard_stats', stats, 300)  # Cache for 5 min
    
    return render(request, 'dashboard.html', stats)
"""

print(OPTIMIZATIONS)
print("\n" + "="*60)
print("QUICK FIXES:")
print("="*60)
print("1. Add pagination to Products List")
print("2. Cache dashboard stats for 5 minutes")
print("3. Use .only() to fetch specific fields")
print("4. Add database indexes (run optimize_performance.py)")
