from django.db.models import Sum, F
from django.utils import timezone
from io import BytesIO
from datetime import datetime, date
import tempfile
import os

from .models import PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster, ProductMaster


def parse_expiry_date(expiry_str):
    """
    Convert expiry string to datetime object
    Handles DDMMYYYY, MM-YYYY, and other formats
    """
    if not expiry_str or expiry_str == 'NA':
        return None
    
    from .date_utils import parse_ddmmyyyy_date, convert_legacy_dates
    from django.core.exceptions import ValidationError
    
    try:
        # First normalize the format
        normalized = normalize_expiry_date(expiry_str)
        
        # Parse using date_utils
        return parse_ddmmyyyy_date(normalized)
        
    except (ValueError, ValidationError):
        # Fallback for MM-YYYY format
        try:
            if '-' in str(expiry_str):
                month, year = map(int, str(expiry_str).split('-'))
                # Return last day of the month
                if month == 12:
                    return date(year + 1, 1, 1) - timezone.timedelta(days=1)
                else:
                    return date(year, month + 1, 1) - timezone.timedelta(days=1)
        except (ValueError, AttributeError):
            pass
        
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


def get_batch_stock_status(product_id, batch_no, expiry_date=None, exclude_sale_id=None):
    """
    Calculate current stock for a specific product batch + expiry combination
    Returns a tuple of (available_quantity, is_available)
    Enhanced with better error handling and user feedback
    
    Args:
        product_id: Product ID
        batch_no: Batch number
        expiry_date: Expiry date (optional)
        exclude_sale_id: Sale ID to exclude from calculation (for edit mode)
    """
    try:
        from django.db.models import Sum
        
        # Get total stock for batch (all expiry dates combined)
        batch_purchased = PurchaseMaster.objects.filter(
            productid=product_id, 
            product_batch_no=batch_no
        ).aggregate(total=Sum('product_quantity'))['total'] or 0
        
        # Get sold quantity, excluding specific sale if provided (for edit mode)
        sales_query = SalesMaster.objects.filter(
            productid=product_id, 
            product_batch_no=batch_no
        )
        
        if exclude_sale_id:
            sales_query = sales_query.exclude(id=exclude_sale_id)
        
        batch_sold = sales_query.aggregate(total=Sum('sale_quantity'))['total'] or 0
        
        purchase_returns = ReturnPurchaseMaster.objects.filter(
            returnproductid=product_id,
            returnproduct_batch_no=batch_no
        ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        
        sales_returns = ReturnSalesMaster.objects.filter(
            return_productid=product_id,
            return_product_batch_no=batch_no
        ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
        
        # Calculate current stock
        current_stock = batch_purchased - batch_sold - purchase_returns + sales_returns
        
        return current_stock, current_stock > 0
    except Exception as e:
        print(f"Error processing inventory for {product_id}: [{e}]")
        return 0, False


def get_stock_status(product_id):
    """
    Calculate current stock for a product using StockManager
    """
    try:
        from .stock_manager import StockManager
        
        stock_summary = StockManager.get_stock_summary(product_id)
        
        # Convert to legacy format for backward compatibility
        expiry_stock = []
        for batch in stock_summary['batches']:
            # Get additional batch details
            purchase = PurchaseMaster.objects.filter(
                productid=product_id,
                product_batch_no=batch['batch_no']
            ).first()
            
            if purchase:
                expiry_stock.append({
                    'batch_no': batch['batch_no'],
                    'expiry': batch['expiry'],
                    'quantity': batch['stock'],
                    'purchase_rate': purchase.product_purchase_rate,
                    'mrp': purchase.product_MRP
                })
        
        return {
            'purchased': stock_summary['total_purchased'],
            'sold': stock_summary['total_sold'],
            'purchase_returns': stock_summary['total_purchase_returns'],
            'sales_returns': stock_summary['total_sales_returns'],
            'current_stock': stock_summary['total_stock'],
            'expiry_stock': expiry_stock
        }
    except Exception as e:
        print(f"Error in get_stock_status: {e}")
        return {
            'purchased': 0,
            'sold': 0,
            'purchase_returns': 0,
            'sales_returns': 0,
            'current_stock': 0,
            'expiry_stock': []
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


def generate_sales_invoice_number():
    """
    Generate sales invoice number in ABC00000000000 format (13 characters total)
    ABC prefix + 11 digit sequential number
    """
    from .models import SalesInvoiceMaster
    
    # Get the latest sales invoice with ABC format
    latest_invoices = SalesInvoiceMaster.objects.filter(
        sales_invoice_no__startswith='ABC'
    ).order_by('-sales_invoice_no')
    
    if latest_invoices.exists():
        latest_number = latest_invoices.first().sales_invoice_no
        try:
            # Extract the numeric part (remove ABC prefix)
            sequence = int(latest_number[3:]) + 1
        except (ValueError, IndexError):
            # If extraction fails, start from 1
            sequence = 1
    else:
        # Check if there are any old format invoices and start from next number
        all_invoices = SalesInvoiceMaster.objects.all().order_by('-sales_invoice_no')
        if all_invoices.exists():
            # Try to get the highest numeric value from existing invoices
            max_sequence = 0
            for invoice in all_invoices:
                try:
                    num = int(invoice.sales_invoice_no)
                    if num > max_sequence:
                        max_sequence = num
                except ValueError:
                    continue
            sequence = max_sequence + 1
        else:
            sequence = 1
    
    # Create the new sales invoice number (ABC + 11 digits with leading zeros)
    return f"ABC{sequence:011d}"


def get_avg_mrp(product_id):
    """
    Calculate the average MRP for a product - Optimized version
    """
    from django.db.models import Avg
    
    # Get average MRP directly from database
    avg_data = PurchaseMaster.objects.filter(
        productid_id=product_id
    ).aggregate(
        avg_mrp=Avg('product_MRP')
    )
    
    return avg_data['avg_mrp'] or 0.0


def get_product_batches_info(product_id):
    """
    Get all batch information for a product with stock details including returns
    Fixed to track stock separately by batch + expiry date combination
    """
    from django.db.models import Sum
    
    batches = []
    
    # Get all unique batch + expiry combinations from purchases
    purchase_combinations = PurchaseMaster.objects.filter(
        productid=product_id
    ).values('product_batch_no', 'product_expiry').distinct()
    
    # Also get combinations from sales, returns to ensure completeness
    sales_combinations = SalesMaster.objects.filter(
        productid=product_id
    ).values('product_batch_no', 'product_expiry').distinct()
    
    pr_combinations = ReturnPurchaseMaster.objects.filter(
        returnproductid=product_id
    ).values('returnproduct_batch_no', 'returnproduct_expiry').distinct()
    
    sr_combinations = ReturnSalesMaster.objects.filter(
        return_productid=product_id
    ).values('return_product_batch_no', 'return_product_expiry').distinct()
    
    # Combine all unique batch + expiry combinations
    all_combinations = set()
    
    for combo in purchase_combinations:
        all_combinations.add((combo['product_batch_no'], combo['product_expiry']))
    
    for combo in sales_combinations:
        all_combinations.add((combo['product_batch_no'], combo['product_expiry']))
    
    for combo in pr_combinations:
        all_combinations.add((combo['returnproduct_batch_no'], combo['returnproduct_expiry']))
    
    for combo in sr_combinations:
        all_combinations.add((combo['return_product_batch_no'], combo['return_product_expiry']))
    
    for batch_no, expiry_date in all_combinations:
        # Calculate stock for this specific batch + expiry combination
        batch_purchased = PurchaseMaster.objects.filter(
            productid=product_id, 
            product_batch_no=batch_no,
            product_expiry=expiry_date
        ).aggregate(total=Sum('product_quantity'))['total'] or 0
        
        batch_sold = SalesMaster.objects.filter(
            productid=product_id, 
            product_batch_no=batch_no,
            product_expiry=expiry_date
        ).aggregate(total=Sum('sale_quantity'))['total'] or 0
        
        # Include returns in calculation for this specific batch + expiry
        purchase_returns = ReturnPurchaseMaster.objects.filter(
            returnproductid=product_id,
            returnproduct_batch_no=batch_no,
            returnproduct_expiry=expiry_date
        ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        
        sales_returns = ReturnSalesMaster.objects.filter(
            return_productid=product_id,
            return_product_batch_no=batch_no,
            return_product_expiry=expiry_date
        ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
        
        # Correct stock calculation: Purchased - Sold - Purchase Returns + Sales Returns
        batch_stock = batch_purchased - batch_sold - purchase_returns + sales_returns
        
        # Include all batches with any activity (for complete inventory tracking)
        if batch_stock != 0 or batch_purchased > 0:
            # Normalize expiry date format
            normalized_expiry = normalize_expiry_date(expiry_date)
            batches.append({
                'batch_no': batch_no,
                'expiry': normalized_expiry,
                'stock': batch_stock
            })
    
    # Sort by expiry date (earliest first)
    batches.sort(key=lambda x: x['expiry'] if x['expiry'] else '9999-12-31')
    
    return batches

def get_bulk_inventory_data(product_ids=None, search_query=None, limit=None):
    """
    Optimized function to get inventory data for multiple products at once
    Reduces database queries significantly
    """
    from django.db.models import Subquery, OuterRef, Value, Q, Avg
    from django.db.models.functions import Coalesce
    
    # Base queryset with select_related for better performance
    products_query = ProductMaster.objects.all().order_by('product_name')
    
    # Apply filters
    if product_ids:
        products_query = products_query.filter(productid__in=product_ids)
    
    if search_query:
        products_query = products_query.filter(
            Q(product_name__icontains=search_query) | 
            Q(product_company__icontains=search_query) |
            Q(product_category__icontains=search_query)
        )
    
    if limit:
        products_query = products_query[:limit]
    
    # Annotate with stock calculations using optimized subqueries including returns
    products_with_stock = products_query.annotate(
        total_purchased=Coalesce(
            Subquery(
                PurchaseMaster.objects.filter(
                    productid=OuterRef('productid')
                ).aggregate(total=Sum('product_quantity'))['total']
            ), Value(0)
        ),
        total_sold=Coalesce(
            Subquery(
                SalesMaster.objects.filter(
                    productid=OuterRef('productid')
                ).aggregate(total=Sum('sale_quantity'))['total']
            ), Value(0)
        ),
        total_purchase_returns=Coalesce(
            Subquery(
                ReturnPurchaseMaster.objects.filter(
                    returnproductid=OuterRef('productid')
                ).aggregate(total=Sum('returnproduct_quantity'))['total']
            ), Value(0)
        ),
        total_sales_returns=Coalesce(
            Subquery(
                ReturnSalesMaster.objects.filter(
                    return_productid=OuterRef('productid')
                ).aggregate(total=Sum('return_sale_quantity'))['total']
            ), Value(0)
        ),
        avg_mrp=Coalesce(
            Subquery(
                PurchaseMaster.objects.filter(
                    productid=OuterRef('productid')
                ).aggregate(avg_mrp=Avg('product_MRP'))['avg_mrp']
            ), Value(0.0)
        )
    ).annotate(
        # Correct stock calculation: Purchased - Sold - Purchase Returns + Sales Returns
        current_stock=F('total_purchased') - F('total_sold') - F('total_purchase_returns') + F('total_sales_returns')
    ).annotate(
        stock_value=F('current_stock') * F('avg_mrp')
    )
    
    return products_with_stock

def normalize_expiry_date(expiry_input):
    """
    Normalize expiry date to consistent format
    Handles MM-YYYY format and converts to YYYY-MM-DD for Django compatibility
    """
    if not expiry_input:
        return ""
    
    try:
        # Convert to string if it's a date object
        if hasattr(expiry_input, 'strftime'):
            return expiry_input.strftime("%Y-%m-%d")
        
        expiry_str = str(expiry_input).strip()
        
        # Handle MM-YYYY format (convert to YYYY-MM-DD)
        if '-' in expiry_str and len(expiry_str.split('-')) == 2:
            parts = expiry_str.split('-')
            if len(parts[0]) <= 2 and len(parts[1]) == 4:  # MM-YYYY
                month, year = int(parts[0]), int(parts[1])
                # Convert to last day of month in YYYY-MM-DD format
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                return f"{year}-{month:02d}-{last_day:02d}"
        
        # Handle YYYY-MM-DD format (already correct)
        if len(expiry_str) == 10 and expiry_str.count('-') == 2:
            parts = expiry_str.split('-')
            if len(parts[0]) == 4:  # YYYY-MM-DD
                return expiry_str
        
        # Use date utilities for other formats
        from .date_utils import convert_legacy_dates, parse_ddmmyyyy_date
        from django.core.exceptions import ValidationError
        
        try:
            normalized = convert_legacy_dates(expiry_str)
            date_obj = parse_ddmmyyyy_date(normalized)
            return date_obj.strftime("%Y-%m-%d")
        except (ValidationError, Exception):
            pass
        
    except Exception as e:
        print(f"Error normalizing expiry date '{expiry_input}': {e}")
    
    # Return as-is if format is not recognized
    return str(expiry_input).strip()


def get_inventory_batches_info(product_id):
    """
    Get all batch information for inventory display with stock details
    Simplified to avoid MM-YYYY date format issues
    """
    from django.db.models import Sum
    from .models import SaleRateMaster
    
    batches = []
    
    try:
        # Get all unique batches from purchases (ignore expiry for now)
        batch_list = PurchaseMaster.objects.filter(productid=product_id).values(
            'product_batch_no'
        ).distinct()
        
        for batch_info in batch_list:
            batch_no = batch_info['product_batch_no']
            
            # Calculate stock for this batch (all expiry dates combined)
            batch_purchased = PurchaseMaster.objects.filter(
                productid=product_id, 
                product_batch_no=batch_no
            ).aggregate(total=Sum('product_quantity'))['total'] or 0
            
            batch_sold = SalesMaster.objects.filter(
                productid=product_id, 
                product_batch_no=batch_no
            ).aggregate(total=Sum('sale_quantity'))['total'] or 0
            
            # Include returns in calculation
            purchase_returns = ReturnPurchaseMaster.objects.filter(
                returnproductid=product_id,
                returnproduct_batch_no=batch_no
            ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
            
            sales_returns = ReturnSalesMaster.objects.filter(
                return_productid=product_id,
                return_product_batch_no=batch_no
            ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
            
            # Calculate stock
            batch_stock = batch_purchased - batch_sold - purchase_returns + sales_returns
            
            # Get MRP from first purchase record
            first_purchase = PurchaseMaster.objects.filter(
                productid=product_id,
                product_batch_no=batch_no
            ).first()
            
            # Get batch rates
            batch_rates = {'rate_A': 0, 'rate_B': 0, 'rate_C': 0}
            try:
                sale_rate = SaleRateMaster.objects.get(
                    productid=product_id, product_batch_no=batch_no
                )
                batch_rates = {
                    'rate_A': float(sale_rate.rate_A or 0),
                    'rate_B': float(sale_rate.rate_B or 0),
                    'rate_C': float(sale_rate.rate_C or 0)
                }
            except SaleRateMaster.DoesNotExist:
                pass
            
            # Include all batches
            batches.append({
                'batch_no': batch_no,
                'expiry': first_purchase.product_expiry if first_purchase else '',
                'stock': batch_stock,
                'mrp': first_purchase.product_MRP if first_purchase else 0,
                'rates': batch_rates
            })
    
    except Exception as e:
        print(f"Error processing inventory for {product_id}: {[str(e)]}")
    
    return batches
