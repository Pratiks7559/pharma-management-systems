"""
Optimized views to fix performance issues in Dashboard, Product List, and Inventory pages
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q, Avg, Case, When, FloatField, DecimalField
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from collections import defaultdict
import json

from .models import (
    ProductMaster, SupplierMaster, CustomerMaster, InvoiceMaster, SalesInvoiceMaster, 
    SalesMaster, PurchaseMaster, ReturnPurchaseMaster, ReturnSalesMaster,
    SupplierChallanMaster, CustomerChallanMaster, StockIssueDetail, Pharmacy_Details
)
from .utils import get_stock_status


class OptimizedStockCalculator:
    """Optimized bulk stock calculations"""
    
    @staticmethod
    def get_bulk_stock_data(product_ids=None, limit=None):
        """Calculate stock for multiple products in bulk"""
        if product_ids is None:
            products_query = ProductMaster.objects.all()
            if limit:
                products_query = products_query[:limit]
            product_ids = list(products_query.values_list('productid', flat=True))
        
        # Bulk fetch all stock movements
        purchases = defaultdict(int)
        for p in PurchaseMaster.objects.filter(productid__in=product_ids).values('productid').annotate(total=Sum('product_quantity')):
            purchases[p['productid']] = p['total']
        
        # Add supplier challan stock
        for c in SupplierChallanMaster.objects.filter(product_id__in=product_ids).values('product_id').annotate(total=Sum('product_quantity')):
            purchases[c['product_id']] += c['total']
        
        # Sales
        sales = defaultdict(int)
        for s in SalesMaster.objects.filter(productid__in=product_ids).values('productid').annotate(total=Sum('sale_quantity')):
            sales[s['productid']] = s['total']
        
        # Add customer challan sales
        for cc in CustomerChallanMaster.objects.filter(product_id__in=product_ids).values('product_id').annotate(total=Sum('sale_quantity')):
            sales[cc['product_id']] += cc['total']
        
        # Returns
        purchase_returns = defaultdict(int)
        for pr in ReturnPurchaseMaster.objects.filter(returnproductid__in=product_ids).values('returnproductid').annotate(total=Sum('returnproduct_quantity')):
            purchase_returns[pr['returnproductid']] = pr['total']
        
        sales_returns = defaultdict(int)
        for sr in ReturnSalesMaster.objects.filter(return_productid__in=product_ids).values('return_productid').annotate(total=Sum('return_sale_quantity')):
            sales_returns[sr['return_productid']] = sr['total']
        
        # Stock issues
        stock_issues = defaultdict(int)
        for si in StockIssueDetail.objects.filter(product__in=product_ids).values('product').annotate(total=Sum('quantity_issued')):
            stock_issues[si['product']] = si['total']
        
        # Calculate final stock
        stock_data = {}
        for pid in product_ids:
            current_stock = (purchases.get(pid, 0) - sales.get(pid, 0) - 
                           purchase_returns.get(pid, 0) + sales_returns.get(pid, 0) - 
                           stock_issues.get(pid, 0))
            stock_data[pid] = max(0, current_stock)
        
        return stock_data

    @staticmethod
    def get_bulk_batch_data(product_ids=None):
        """Get batch information for multiple products"""
        if product_ids is None:
            product_ids = list(ProductMaster.objects.values_list('productid', flat=True))
        
        # Get MRP and batch info from purchases
        batch_data = defaultdict(lambda: {'mrp': 0, 'batch_no': '', 'expiry': ''})
        
        purchases = PurchaseMaster.objects.filter(
            productid__in=product_ids
        ).values('productid', 'product_MRP', 'product_batch_no', 'product_expiry').order_by('-purchaseid')
        
        for p in purchases:
            pid = p['productid']
            if not batch_data[pid]['mrp']:  # Use first (latest) record
                batch_data[pid] = {
                    'mrp': p['product_MRP'] or 0,
                    'batch_no': p['product_batch_no'] or '',
                    'expiry': p['product_expiry'] or ''
                }
        
        return dict(batch_data)


@login_required
def optimized_dashboard(request):
    """Optimized dashboard with bulk queries"""
    # Basic counts (fast)
    product_count = ProductMaster.objects.count()
    supplier_count = SupplierMaster.objects.count()
    customer_count = CustomerMaster.objects.count()
    
    # Recent records (fast - limited)
    recent_sales = SalesInvoiceMaster.objects.select_related('customerid').order_by('-sales_invoice_date')[:5]
    recent_purchases = InvoiceMaster.objects.select_related('supplierid').order_by('-invoice_date')[:5]
    
    # Optimized low stock calculation
    low_stock_products = []
    try:
        # Get stock for first 50 products only (for performance)
        product_ids = list(ProductMaster.objects.values_list('productid', flat=True)[:50])
        stock_data = OptimizedStockCalculator.get_bulk_stock_data(product_ids)
        
        # Get product details for low stock items
        low_stock_ids = [pid for pid, stock in stock_data.items() if 0 < stock <= 10][:10]
        if low_stock_ids:
            products = ProductMaster.objects.filter(productid__in=low_stock_ids)
            for product in products:
                low_stock_products.append({
                    'product': product,
                    'current_stock': stock_data[product.productid]
                })
    except Exception as e:
        print(f"Dashboard: Error in low stock calculation: {e}")
    
    # Optimized expiry calculation
    expired_products = []
    try:
        current_date = datetime.now().date()
        warning_date = current_date + timedelta(days=30)
        
        # Get products with expiry in next 30 days (limited query)
        expiring_purchases = PurchaseMaster.objects.filter(
            product_expiry__isnull=False
        ).exclude(product_expiry='').select_related('productid')[:30]  # Reduced limit
        
        for purchase in expiring_purchases:
            try:
                expiry_str = str(purchase.product_expiry)
                expiry_date = None
                
                if len(expiry_str) == 10 and '-' in expiry_str:  # YYYY-MM-DD
                    expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
                elif len(expiry_str) == 7 and '-' in expiry_str:  # MM-YYYY
                    month, year = expiry_str.split('-')
                    import calendar
                    last_day = calendar.monthrange(int(year), int(month))[1]
                    expiry_date = datetime(int(year), int(month), last_day).date()
                
                if expiry_date and expiry_date <= warning_date:
                    # Quick stock check (simplified)
                    stock_info = get_stock_status(purchase.productid.productid)
                    if stock_info.get('current_stock', 0) > 0:
                        expired_products.append({
                            'product': purchase.productid,
                            'batch_no': purchase.product_batch_no,
                            'expiry_date': expiry_date,
                            'current_stock': stock_info['current_stock'],
                            'days_to_expiry': (expiry_date - current_date).days
                        })
                        
                        if len(expired_products) >= 10:
                            break
            except Exception as e:
                continue
    except Exception as e:
        print(f"Dashboard: Error in expiry calculation: {e}")
    
    # Financial calculations (optimized with single queries)
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    
    # Monthly sales (single query)
    monthly_sales = SalesMaster.objects.filter(
        sales_invoice_no__sales_invoice_date__gte=current_month_start
    ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
    
    # Monthly purchases (single query)
    monthly_purchases = InvoiceMaster.objects.filter(
        invoice_date__gte=current_month_start
    ).aggregate(total=Sum('invoice_total'))['total'] or 0
    
    # Today's sales (single query)
    today_sales = SalesMaster.objects.filter(
        sales_invoice_no__sales_invoice_date=today
    ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
    
    # Today's purchases (single query)
    today_purchases = InvoiceMaster.objects.filter(
        invoice_date=today
    ).aggregate(total=Sum('invoice_total'))['total'] or 0
    
    # Simplified profit calculation
    today_profit = today_sales - today_purchases