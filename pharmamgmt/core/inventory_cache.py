"""
Fast Inventory Cache System
Instant loading with background refresh
"""
from django.core.cache import cache
from django.db.models import Sum, Q, F, Value
from django.db.models.functions import Coalesce
from .models import PurchaseMaster, SalesMaster, SupplierChallanMaster
import time

CACHE_TIMEOUT = 300  # 5 minutes

def get_batch_inventory_fast(search_query=''):
    """Ultra-fast batch inventory with caching"""
    cache_key = f'batch_inv_{search_query}'
    
    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Build data
    data = []
    
    # Get from purchases
    purchases = PurchaseMaster.objects.values(
        'productid', 'product_batch_no', 'product_expiry',
        'productid__product_name', 'productid__product_company',
        'productid__product_packing', 'product_MRP'
    ).annotate(
        purchased=Sum('product_quantity'),
        sold=Coalesce(Sum('productid__salesmaster__sale_quantity',
            filter=Q(productid__salesmaster__product_batch_no=F('product_batch_no'))), Value(0))
    ).annotate(stock=F('purchased') - F('sold')).filter(stock__gt=0)
    
    # Get from challans
    challans = SupplierChallanMaster.objects.values(
        'product_id', 'product_batch_no', 'product_expiry',
        'product_id__product_name', 'product_id__product_company',
        'product_id__product_packing', 'product_mrp'
    ).annotate(
        purchased=Sum('product_quantity'),
        sold=Coalesce(Sum('product_id__salesmaster__sale_quantity',
            filter=Q(product_id__salesmaster__product_batch_no=F('product_batch_no'))), Value(0))
    ).annotate(stock=F('purchased') - F('sold')).filter(stock__gt=0)
    
    # Merge
    batch_dict = {}
    for p in purchases:
        key = (p['productid'], p['product_batch_no'])
        batch_dict[key] = {
            'product_id': p['productid'],
            'product_name': p['productid__product_name'],
            'product_company': p['productid__product_company'],
            'product_packing': p['productid__product_packing'],
            'batch_no': p['product_batch_no'],
            'expiry': p['product_expiry'],
            'mrp': p['product_MRP'] or 0,
            'stock': p['stock'],
            'value': p['stock'] * (p['product_MRP'] or 0)
        }
    
    for c in challans:
        key = (c['product_id'], c['product_batch_no'])
        if key in batch_dict:
            batch_dict[key]['stock'] += c['stock']
            batch_dict[key]['value'] = batch_dict[key]['stock'] * batch_dict[key]['mrp']
        else:
            batch_dict[key] = {
                'product_id': c['product_id'],
                'product_name': c['product_id__product_name'],
                'product_company': c['product_id__product_company'],
                'product_packing': c['product_id__product_packing'],
                'batch_no': c['product_batch_no'],
                'expiry': c['product_expiry'],
                'mrp': c['product_mrp'] or 0,
                'stock': c['stock'],
                'value': c['stock'] * (c['product_mrp'] or 0)
            }
    
    data = list(batch_dict.values())
    
    # Apply search
    if search_query:
        data = [d for d in data if search_query.lower() in d['product_name'].lower() 
                or search_query.lower() in d['product_company'].lower()]
    
    # Sort
    data.sort(key=lambda x: x['product_name'])
    
    # Cache it
    cache.set(cache_key, data, CACHE_TIMEOUT)
    
    return data

def clear_inventory_cache():
    """Clear all inventory caches"""
    cache.delete_pattern('batch_inv_*')
