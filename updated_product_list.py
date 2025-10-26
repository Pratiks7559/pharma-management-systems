from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from pharmamgmt.core.models import ProductMaster
from pharmamgmt.core.utils import get_stock_status

@login_required
def product_list(request):
    products = ProductMaster.objects.all().order_by('product_name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(product_company__icontains=search_query) |
            Q(product_salt__icontains=search_query) |
            Q(product_barcode__icontains=search_query)
        )
    
    # Pagination first to limit database queries
    paginator = Paginator(products, 10)  # 10 products per page
    page_number = request.GET.get('page')
    page_products = paginator.get_page(page_number)
    
    # Get stock data only for current page products
    products_with_stock = []
    for product in page_products:
        try:
            stock_info = get_stock_status(product.id)
            stock_level = stock_info.get('current_stock', 0)
        except Exception:
            stock_level = 0  # Default if stock check fails
        
        products_with_stock.append({
            'product': product,
            'stock_level': stock_level
        })
    
    context = {
        'products': page_products,
        'products_with_stock': products_with_stock,
        'search_query': search_query,
        'title': 'Product List'
    }
    return render(request, 'products/product_list.html', context)
