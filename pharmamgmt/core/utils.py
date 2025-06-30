from django.db.models import Sum, F
from django.utils import timezone
from io import BytesIO
from datetime import datetime, date
import tempfile
import os

from .models import PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster


def parse_expiry_date(expiry_str):
    """
    Convert MM-YYYY string to datetime object for the last day of that month
    """
    if not expiry_str or expiry_str == 'NA':
        return None
    try:
        # Parse MM-YYYY format
        month, year = map(int, expiry_str.split('-'))
        # Return last day of the month
        if month == 12:
            return date(year + 1, 1, 1) - timezone.timedelta(days=1)
        else:
            return date(year, month + 1, 1) - timezone.timedelta(days=1)
    except (ValueError, AttributeError):
        return None


def format_expiry_date(date_obj):
    """
    Convert datetime object to MM-YYYY string format
    """
    if not date_obj:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%m-%Y")


def validate_expiry_format(expiry_str):
    """
    Validate MM-YYYY format
    """
    if not expiry_str:
        return False
    try:
        parts = expiry_str.split('-')
        if len(parts) != 2:
            return False
        month, year = map(int, parts)
        return 1 <= month <= 12 and 2000 <= year <= 2050
    except (ValueError, AttributeError):
        return False


def get_batch_stock_status(product_id, batch_no):
    """
    Calculate current stock for a specific product batch
    Returns a tuple of (available_quantity, is_available)
    """
    try:
        # Simple calculation using basic iteration instead of aggregate
        purchased = 0
        for purchase in PurchaseMaster.objects.filter(productid_id=product_id, product_batch_no=batch_no):
            purchased += purchase.product_quantity or 0
        
        sold = 0
        for sale in SalesMaster.objects.filter(productid_id=product_id, product_batch_no=batch_no):
            sold += sale.sale_quantity or 0
        
        # For now, skip returns to simplify
        purchase_returns = 0
        sales_returns = 0
        
        # Calculate current batch stock
        batch_stock = purchased - sold - purchase_returns + sales_returns
        
        return batch_stock, batch_stock > 0
    except Exception as e:
        print(f"Error in get_batch_stock_status: {e}")
        return 0, False


def get_stock_status(product_id):
    """
    Calculate current stock for a product based on purchases, sales, and returns
    """
    # Get total purchased quantity
    purchased = PurchaseMaster.objects.filter(productid_id=product_id).aggregate(
        total=Sum('product_quantity')
    )['total'] or 0
    
    # Get total sold quantity
    sold = SalesMaster.objects.filter(productid_id=product_id).aggregate(
        total=Sum('sale_quantity')
    )['total'] or 0
    
    # Get total purchased returns quantity
    purchase_returns = ReturnPurchaseMaster.objects.filter(returnproductid_id=product_id).aggregate(
        total=Sum('returnproduct_quantity')
    )['total'] or 0
    
    # Get total sales returns quantity
    sales_returns = ReturnSalesMaster.objects.filter(return_productid_id=product_id).aggregate(
        total=Sum('return_sale_quantity')
    )['total'] or 0
    
    # Calculate current stock: purchases - sales - purchase returns + sales returns
    current_stock = purchased - sold - purchase_returns + sales_returns
    
    # Get expiry-wise stock quantity
    expiry_stock = []
    
    purchases = PurchaseMaster.objects.filter(productid_id=product_id)
    for purchase in purchases:
        # Look for sales of this batch
        batch_sold = SalesMaster.objects.filter(
            productid_id=product_id, 
            product_batch_no=purchase.product_batch_no
        ).aggregate(total=Sum('sale_quantity'))['total'] or 0
        
        # Look for returns of this batch
        batch_returned = ReturnPurchaseMaster.objects.filter(
            returnproductid_id=product_id, 
            returnproduct_batch_no=purchase.product_batch_no
        ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        
        # Look for sales returns of this batch
        batch_sales_returned = ReturnSalesMaster.objects.filter(
            return_productid_id=product_id, 
            return_product_batch_no=purchase.product_batch_no
        ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
        
        batch_remaining = purchase.product_quantity - batch_sold - batch_returned + batch_sales_returned
        
        if batch_remaining > 0:
            expiry_stock.append({
                'batch_no': purchase.product_batch_no,
                'expiry': purchase.product_expiry,
                'quantity': batch_remaining,
                'purchase_rate': purchase.product_purchase_rate,
                'mrp': purchase.product_MRP
            })
    
    return {
        'purchased': purchased,
        'sold': sold,
        'purchase_returns': purchase_returns,
        'sales_returns': sales_returns,
        'current_stock': current_stock,
        'expiry_stock': expiry_stock
    }


def generate_invoice_pdf(invoice):
    """
    Generate a PDF for purchase invoice
    Note: This is a placeholder function. In a real implementation, 
    you would use a PDF library like ReportLab or WeasyPrint
    """
    # In a real implementation, you would create a PDF here
    # For now, this is just a placeholder
    return None


def generate_sales_invoice_pdf(invoice):
    """
    Generate a PDF for sales invoice
    Note: This is a placeholder function. In a real implementation, 
    you would use a PDF library like ReportLab or WeasyPrint
    """
    # In a real implementation, you would create a PDF here
    # For now, this is just a placeholder
    return None


def get_avg_mrp(product_id):
    """
    Calculate the average purchase rate for a product based on all available batches
    Used for inventory valuation (formerly used rate_A field)
    """
    # Get all purchase entries for this product with stock remaining
    stock_info = get_stock_status(product_id)
    
    if not stock_info['expiry_stock']:
        # No stock available, try to get the most recent purchase rate
        latest_purchase = PurchaseMaster.objects.filter(productid=product_id).order_by('-purchase_entry_date').first()
        if latest_purchase:
            return latest_purchase.product_purchase_rate
        return 0.0  # No purchases found
    
    # Calculate weighted average purchase rate based on available batches
    total_value = 0
    total_quantity = 0
    
    for batch in stock_info['expiry_stock']:
        batch_value = batch['quantity'] * batch['purchase_rate']  # Using purchase_rate instead of mrp
        total_value += batch_value
        total_quantity += batch['quantity']
    
    if total_quantity > 0:
        return total_value / total_quantity
    return 0.0
