"""
Stock validation utilities for sales operations
Handles stock checking with edit mode support
"""

from .utils import get_batch_stock_status
from .models import SalesMaster


def validate_sale_stock(product_id, batch_no, required_quantity, exclude_sale_id=None):
    """
    Validate if sufficient stock is available for a sale
    
    Args:
        product_id: Product ID
        batch_no: Batch number
        required_quantity: Quantity needed
        exclude_sale_id: Sale ID to exclude from calculation (for edit mode)
    
    Returns:
        dict: {
            'valid': bool,
            'available_stock': int,
            'message': str
        }
    """
    try:
        # Get current stock excluding the sale being edited
        available_stock, is_available = get_batch_stock_status(
            product_id, batch_no, exclude_sale_id=exclude_sale_id
        )
        
        if not is_available:
            return {
                'valid': False,
                'available_stock': 0,
                'message': f'Product batch {batch_no} is out of stock.'
            }
        
        if available_stock < required_quantity:
            return {
                'valid': False,
                'available_stock': available_stock,
                'message': f'Insufficient stock. Available: {available_stock}, Required: {required_quantity}'
            }
        
        return {
            'valid': True,
            'available_stock': available_stock,
            'message': 'Stock available'
        }
        
    except Exception as e:
        return {
            'valid': False,
            'available_stock': 0,
            'message': f'Error checking stock: {str(e)}'
        }


def validate_edit_sale_stock(sale_id, new_product_id, new_batch_no, new_quantity):
    """
    Validate stock for editing an existing sale
    
    Args:
        sale_id: ID of sale being edited
        new_product_id: New product ID
        new_batch_no: New batch number
        new_quantity: New quantity
    
    Returns:
        dict: Validation result
    """
    try:
        # Get current sale data
        current_sale = SalesMaster.objects.get(id=sale_id)
        
        # Check if product or batch changed
        product_changed = new_product_id != current_sale.productid.productid
        batch_changed = new_batch_no != current_sale.product_batch_no
        quantity_increased = new_quantity > current_sale.sale_quantity
        
        # If nothing critical changed, no validation needed
        if not (product_changed or batch_changed or quantity_increased):
            return {
                'valid': True,
                'available_stock': 0,
                'message': 'No stock validation required'
            }
        
        # Calculate additional quantity needed
        if product_changed or batch_changed:
            # If product/batch changed, need full quantity for new batch
            required_quantity = new_quantity
        else:
            # Same product/batch, only need additional quantity
            required_quantity = new_quantity - current_sale.sale_quantity
        
        # Validate stock
        return validate_sale_stock(
            new_product_id, 
            new_batch_no, 
            required_quantity, 
            exclude_sale_id=sale_id
        )
        
    except SalesMaster.DoesNotExist:
        return {
            'valid': False,
            'available_stock': 0,
            'message': 'Sale record not found'
        }
    except Exception as e:
        return {
            'valid': False,
            'available_stock': 0,
            'message': f'Validation error: {str(e)}'
        }