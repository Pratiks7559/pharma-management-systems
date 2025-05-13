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
    
    # Get products with stock data for display
    products_with_stock = []
    for product in products:
        stock_info = get_stock_status(product.productid)
        product.stock_level = stock_info['current_stock']
        products_with_stock.append(product)
    
    # Pagination
    paginator = Paginator(products_with_stock, 10)  # 10 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'search_query': search_query,
        'title': 'Product List'
    }
    return render(request, 'products/product_list.html', context)
