from django.db.models import Sum, Q
from collections import defaultdict
from .models import PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster, SupplierChallanMaster, ProductMaster, CustomerChallanMaster

class FastInventory:
    @staticmethod
    def get_batch_inventory_data(search_query=''):
        """Optimized batch inventory - fetch all data in bulk"""
        products_query = ProductMaster.objects.all().order_by('product_name')
        if search_query:
            products_query = products_query.filter(
                Q(product_name__icontains=search_query) | Q(product_company__icontains=search_query)
            )
        
        product_ids = list(products_query.values_list('productid', flat=True))
        products_dict = {p.productid: p for p in products_query}
        
        # Bulk fetch all transactions with expiry
        purchases = defaultdict(lambda: {'qty': 0, 'mrp': 0, 'expiry': None})
        for p in PurchaseMaster.objects.filter(productid__in=product_ids).values('productid', 'product_batch_no', 'product_quantity', 'product_MRP', 'product_expiry'):
            key = (p['productid'], p['product_batch_no'])
            purchases[key]['qty'] += p['product_quantity']
            if not purchases[key]['mrp']:
                purchases[key]['mrp'] = p['product_MRP'] or 0
            if not purchases[key]['expiry']:
                purchases[key]['expiry'] = p['product_expiry']
        
        for c in SupplierChallanMaster.objects.filter(product_id__in=product_ids).values('product_id', 'product_batch_no', 'product_quantity', 'product_mrp', 'product_expiry'):
            key = (c['product_id'], c['product_batch_no'])
            purchases[key]['qty'] += c['product_quantity']
            if not purchases[key]['mrp']:
                purchases[key]['mrp'] = c['product_mrp'] or 0
            if not purchases[key]['expiry']:
                purchases[key]['expiry'] = c['product_expiry']
        
        sales = defaultdict(int)
        for s in SalesMaster.objects.filter(productid__in=product_ids).values('productid', 'product_batch_no').annotate(total=Sum('sale_quantity')):
            sales[(s['productid'], s['product_batch_no'])] = s['total']
        
        # Add customer challan sales
        for cc in CustomerChallanMaster.objects.filter(product_id__in=product_ids).values('product_id', 'product_batch_no').annotate(total=Sum('sale_quantity')):
            key = (cc['product_id'], cc['product_batch_no'])
            sales[key] += cc['total']
        
        pr = defaultdict(int)
        for r in ReturnPurchaseMaster.objects.filter(returnproductid__in=product_ids).values('returnproductid', 'returnproduct_batch_no').annotate(total=Sum('returnproduct_quantity')):
            pr[(r['returnproductid'], r['returnproduct_batch_no'])] = r['total']
        
        sr = defaultdict(int)
        for r in ReturnSalesMaster.objects.filter(return_productid__in=product_ids).values('return_productid', 'return_product_batch_no').annotate(total=Sum('return_sale_quantity')):
            sr[(r['return_productid'], r['return_product_batch_no'])] = r['total']
        
        # Calculate inventory
        inventory = []
        for key, data in purchases.items():
            pid, batch = key
            stock = data['qty'] - sales.get(key, 0) - pr.get(key, 0) + sr.get(key, 0)
            if stock > 0 and pid in products_dict:
                p = products_dict[pid]
                inventory.append({
                    'product_id': pid,
                    'product_name': p.product_name,
                    'product_company': p.product_company,
                    'product_packing': p.product_packing,
                    'batch_no': batch,
                    'expiry': data['expiry'] or '',
                    'mrp': data['mrp'],
                    'stock': stock,
                    'value': stock * data['mrp']
                })
        
        return inventory
    
    @staticmethod
    def get_dateexpiry_inventory_data(search_query=''):
        """Optimized date/expiry inventory"""
        products_query = ProductMaster.objects.all()
        if search_query:
            products_query = products_query.filter(
                Q(product_name__icontains=search_query) | Q(product_company__icontains=search_query)
            )
        
        product_ids = list(products_query.values_list('productid', flat=True))
        products_dict = {p.productid: p for p in products_query}
        
        # Bulk fetch with expiry
        purchases = defaultdict(lambda: {'qty': 0, 'rate': 0, 'mrp': 0, 'expiry': None})
        for p in PurchaseMaster.objects.filter(productid__in=product_ids).values('productid', 'product_batch_no', 'product_quantity', 'product_actual_rate', 'product_MRP', 'product_expiry'):
            key = (p['productid'], p['product_batch_no'])
            purchases[key]['qty'] += p['product_quantity']
            if not purchases[key]['rate']:
                purchases[key]['rate'] = p['product_actual_rate'] or 0
                purchases[key]['mrp'] = p['product_MRP'] or 0
                purchases[key]['expiry'] = p['product_expiry']
        
        for c in SupplierChallanMaster.objects.filter(product_id__in=product_ids).values('product_id', 'product_batch_no', 'product_quantity', 'product_purchase_rate', 'product_mrp', 'product_expiry'):
            key = (c['product_id'], c['product_batch_no'])
            purchases[key]['qty'] += c['product_quantity']
            if not purchases[key]['rate']:
                purchases[key]['rate'] = c['product_purchase_rate'] or 0
                purchases[key]['mrp'] = c['product_mrp'] or 0
                purchases[key]['expiry'] = c['product_expiry']
        
        sales = defaultdict(int)
        for s in SalesMaster.objects.filter(productid__in=product_ids).values('productid', 'product_batch_no').annotate(total=Sum('sale_quantity')):
            sales[(s['productid'], s['product_batch_no'])] = s['total']
        
        # Add customer challan sales
        for cc in CustomerChallanMaster.objects.filter(product_id__in=product_ids).values('product_id', 'product_batch_no').annotate(total=Sum('sale_quantity')):
            key = (cc['product_id'], cc['product_batch_no'])
            sales[key] += cc['total']
        
        pr = defaultdict(int)
        for r in ReturnPurchaseMaster.objects.filter(returnproductid__in=product_ids).values('returnproductid', 'returnproduct_batch_no').annotate(total=Sum('returnproduct_quantity')):
            pr[(r['returnproductid'], r['returnproduct_batch_no'])] = r['total']
        
        sr = defaultdict(int)
        for r in ReturnSalesMaster.objects.filter(return_productid__in=product_ids).values('return_productid', 'return_product_batch_no').annotate(total=Sum('return_sale_quantity')):
            sr[(r['return_productid'], r['return_product_batch_no'])] = r['total']
        
        # Group by expiry
        from datetime import datetime
        import calendar
        grouped = defaultdict(list)
        today = datetime.now().date()
        
        for key, data in purchases.items():
            pid, batch = key
            stock = data['qty'] - sales.get(key, 0) - pr.get(key, 0) + sr.get(key, 0)
            if stock > 0 and pid in products_dict:
                p = products_dict[pid]
                expiry = data['expiry']
                
                # Skip products without expiry date
                if not expiry:
                    continue
                
                # Parse expiry
                expiry_key = None
                days = 999999
                try:
                    if isinstance(expiry, str):
                        exp_date = datetime.strptime(expiry, '%m-%Y')
                        # Skip unrealistic dates (more than 10 years in future)
                        if exp_date.year > today.year + 10:
                            continue
                        expiry_key = expiry
                        last_day = calendar.monthrange(exp_date.year, exp_date.month)[1]
                        month_end = datetime(exp_date.year, exp_date.month, last_day).date()
                        days = (month_end - today).days
                    elif hasattr(expiry, 'strftime'):
                        # Skip unrealistic dates (more than 10 years in future)
                        if expiry.year > today.year + 10:
                            continue
                        expiry_key = expiry.strftime('%m-%Y')
                        last_day = calendar.monthrange(expiry.year, expiry.month)[1]
                        month_end = datetime(expiry.year, expiry.month, last_day).date()
                        days = (month_end - today).days
                except:
                    continue
                
                if not expiry_key:
                    continue
                
                grouped[expiry_key].append({
                    'product_name': p.product_name,
                    'product_company': p.product_company,
                    'product_packing': p.product_packing,
                    'batch_no': batch,
                    'quantity': stock,
                    'purchase_rate': data['rate'],
                    'mrp': data['mrp'],
                    'value': stock * data['rate'],
                    'days_to_expiry': days,
                    'expiry_display': expiry_key
                })
        
        # Format output
        result = []
        for exp_key, items in grouped.items():
            total = sum(i['value'] for i in items)
            days = items[0]['days_to_expiry'] if items else 999999
            result.append({
                'expiry_display': exp_key,
                'expiry_date': exp_key,
                'days_to_expiry': days,
                'products': items,
                'total_value': total
            })
        
        result.sort(key=lambda x: x['days_to_expiry'])
        return result, sum(g['total_value'] for g in result)
