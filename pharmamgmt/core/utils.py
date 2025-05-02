from django.db.models import Sum, F
from django.utils import timezone
from io import BytesIO
from datetime import datetime
import tempfile
import os

from .models import PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster


def get_batch_stock_status(product_id, batch_no):
    """
    Calculate current stock for a specific product batch
    Returns a tuple of (available_quantity, is_available)
    """
    # Get total purchased quantity for this batch
    purchased = PurchaseMaster.objects.filter(
        productid=product_id, 
        product_batch_no=batch_no
    ).aggregate(total=Sum('product_quantity'))['total'] or 0
    
    # Get total sold quantity for this batch
    sold = SalesMaster.objects.filter(
        productid=product_id, 
        product_batch_no=batch_no
    ).aggregate(total=Sum('sale_quantity'))['total'] or 0
    
    # Get total purchased returns quantity for this batch
    purchase_returns = ReturnPurchaseMaster.objects.filter(
        returnproductid=product_id, 
        returnproduct_batch_no=batch_no
    ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
    
    # Get total sales returns quantity for this batch
    sales_returns = ReturnSalesMaster.objects.filter(
        return_productid=product_id, 
        return_product_batch_no=batch_no
    ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
    
    # Calculate current batch stock: purchases - sales - purchase returns + sales returns
    batch_stock = purchased - sold - purchase_returns + sales_returns
    
    return batch_stock, batch_stock > 0


def get_stock_status(product_id):
    """
    Calculate current stock for a product based on purchases, sales, and returns
    """
    # Get total purchased quantity
    purchased = PurchaseMaster.objects.filter(productid=product_id).aggregate(
        total=Sum('product_quantity')
    )['total'] or 0
    
    # Get total sold quantity
    sold = SalesMaster.objects.filter(productid=product_id).aggregate(
        total=Sum('sale_quantity')
    )['total'] or 0
    
    # Get total purchased returns quantity
    purchase_returns = ReturnPurchaseMaster.objects.filter(returnproductid=product_id).aggregate(
        total=Sum('returnproduct_quantity')
    )['total'] or 0
    
    # Get total sales returns quantity
    sales_returns = ReturnSalesMaster.objects.filter(return_productid=product_id).aggregate(
        total=Sum('return_sale_quantity')
    )['total'] or 0
    
    # Calculate current stock: purchases - sales - purchase returns + sales returns
    current_stock = purchased - sold - purchase_returns + sales_returns
    
    # Get expiry-wise stock quantity
    expiry_stock = []
    
    purchases = PurchaseMaster.objects.filter(productid=product_id)
    for purchase in purchases:
        # Look for sales of this batch
        batch_sold = SalesMaster.objects.filter(
            productid=product_id, 
            product_batch_no=purchase.product_batch_no
        ).aggregate(total=Sum('sale_quantity'))['total'] or 0
        
        # Look for returns of this batch
        batch_returned = ReturnPurchaseMaster.objects.filter(
            returnproductid=product_id, 
            returnproduct_batch_no=purchase.product_batch_no
        ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        
        # Look for sales returns of this batch
        batch_sales_returned = ReturnSalesMaster.objects.filter(
            return_productid=product_id, 
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
