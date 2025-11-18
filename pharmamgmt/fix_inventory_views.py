# Fixed dateexpiry_inventory_report function
# This should replace the broken function in views.py

FIXED_FUNCTION = '''
@login_required
def dateexpiry_inventory_report(request):
    from datetime import datetime, timedelta
    from collections import defaultdict
    from .stock_manager import StockManager
    from .models import SupplierChallanMaster

    # Get filter parameters
    search_query = request.GET.get('search', '')
    expiry_from = request.GET.get('expiry_from', '')
    expiry_to = request.GET.get('expiry_to', '')

    # Get all products
    products_query = ProductMaster.objects.all()
    
    if search_query:
        products_query = products_query.filter(
            Q(product_name__icontains=search_query) |
            Q(product_company__icontains=search_query)
        )
    
    # Group and process data
    grouped_data = defaultdict(list)
    today = datetime.now().date()
    total_value = 0
    
    for product in products_query:
        try:
            # Get stock summary with batch breakdown
            stock_summary = StockManager.get_stock_summary(product.productid)
            
            # Process each batch
            for batch_info in stock_summary['batches']:
                if batch_info['stock'] <= 0:
                    continue
                
                # Get batch details from purchase or challan
                purchase_rate = 0
                mrp = 0
                expiry_date = batch_info['expiry']
                
                # Try purchase invoice first
                purchase = PurchaseMaster.objects.filter(
                    productid=product,
                    product_batch_no=batch_info['batch_no']
                ).first()
                
                if purchase:
                    purchase_rate = purchase.product_actual_rate or 0
                    mrp = purchase.product_MRP or 0
                    if not expiry_date:
                        expiry_date = purchase.product_expiry
                else:
                    # Try challan
                    challan = SupplierChallanMaster.objects.filter(
                        product_id=product,
                        product_batch_no=batch_info['batch_no']
                    ).first()
                    
                    if challan:
                        purchase_rate = challan.product_purchase_rate or 0
                        mrp = challan.product_mrp or 0
                        if not expiry_date:
                            expiry_date = challan.product_expiry
                
                # Parse expiry date
                parsed_expiry_date = None
                expiry_mmyyyy = None
                
                if expiry_date:
                    if isinstance(expiry_date, str):
                        for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m-%Y', '%d%m%Y']:
                            try:
                                if fmt == '%m-%Y':
                                    temp_date = datetime.strptime(expiry_date, fmt)
                                    parsed_expiry_date = temp_date.replace(day=1).date()
                                    expiry_mmyyyy = expiry_date
                                else:
                                    parsed_expiry_date = datetime.strptime(expiry_date, fmt).date()
                                    expiry_mmyyyy = parsed_expiry_date.strftime('%m-%Y')
                                break
                            except (ValueError, TypeError):
                                continue
                    elif hasattr(expiry_date, 'strftime'):
                        parsed_expiry_date = expiry_date.date() if hasattr(expiry_date, 'date') else expiry_date
                        expiry_mmyyyy = parsed_expiry_date.strftime('%m-%Y')
                
                # Group by expiry
                if not expiry_mmyyyy:
                    group_key = 'No Expiry Date'
                    days_to_expiry = 999999
                    expiry_display = 'No Expiry Date'
                else:
                    group_key = expiry_mmyyyy
                    import calendar
                    month, year = map(int, expiry_mmyyyy.split('-'))
                    last_day = calendar.monthrange(year, month)[1]
                    month_end_date = datetime(year, month, last_day).date()
                    days_to_expiry = (month_end_date - today).days
                    expiry_display = expiry_mmyyyy
                
                stock_value = batch_info['stock'] * purchase_rate
                total_value += stock_value
                
                grouped_data[group_key].append({
                    'product_name': product.product_name,
                    'product_company': product.product_company,
                    'product_packing': product.product_packing,
                    'batch_no': batch_info['batch_no'],
                    'quantity': batch_info['stock'],
                    'purchase_rate': purchase_rate,
                    'mrp': mrp,
                    'value': stock_value,
                    'days_to_expiry': days_to_expiry,
                    'expiry_date': parsed_expiry_date,
                    'expiry_mmyyyy': expiry_mmyyyy,
                    'expiry_display': expiry_display,
                })
        except Exception as e:
            print(f"Error processing product {product.product_name}: {e}")
            continue
    
    # Create sorted groups
    expiry_groups = []
    for group_key, products_list in grouped_data.items():
        group_total_value = sum(p['value'] for p in products_list)
        
        if group_key == 'No Expiry Date':
            days_to_expiry = 999999
            expiry_display = 'No Expiry Date'
            expiry_date = None
        else:
            month, year = map(int, group_key.split('-'))
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            month_end_date = datetime(year, month, last_day).date()
            days_to_expiry = (month_end_date - today).days
            expiry_display = group_key
            expiry_date = month_end_date
        
        expiry_groups.append({
            'expiry_date': expiry_date,
            'expiry_display': expiry_display,
            'days_to_expiry': days_to_expiry,
            'products': products_list,
            'total_value': group_total_value,
        })
    
    # Sort by expiry date
    expiry_groups.sort(key=lambda x: x['days_to_expiry'])
    
    context = {
        'expiry_data': expiry_groups,
        'total_value': total_value,
        'search_query': search_query,
        'expiry_from': expiry_from,
        'expiry_to': expiry_to,
        'title': 'Date-wise Inventory Report'
    }
    return render(request, 'reports/dateexpiry_inventory_report.html', context)
'''

print("Fixed function created. Please manually replace the dateexpiry_inventory_report function in views.py")
print("Starting from line 4324 to line 4491")
