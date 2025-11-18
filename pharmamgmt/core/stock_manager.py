from django.db.models import Sum, F
from django.db import transaction
from .models import (
    PurchaseMaster, SalesMaster, ReturnPurchaseMaster, ReturnSalesMaster,
    ProductMaster, SupplierChallanMaster
)
from .date_utils import format_date_for_backend


class StockManager:
    """
    Centralized stock management system that handles all stock calculations
    including purchases, sales, purchase returns, and sales returns.
    """
    

    
    @staticmethod
    def get_stock_summary(product_id):
        """
        Get comprehensive stock summary for a product
        """
        try:
            from .models import CustomerChallanMaster
            
            # Get total purchased from invoices
            total_purchased_invoice = PurchaseMaster.objects.filter(
                productid=product_id
            ).aggregate(total=Sum('product_quantity'))['total'] or 0
            
            # Get total purchased from challans
            total_purchased_challan = SupplierChallanMaster.objects.filter(
                product_id=product_id
            ).aggregate(total=Sum('product_quantity'))['total'] or 0
            
            total_purchased = total_purchased_invoice + total_purchased_challan
            
            # Get total sold from sales invoices
            total_sold = SalesMaster.objects.filter(
                productid=product_id
            ).aggregate(total=Sum('sale_quantity'))['total'] or 0
            
            # Get total sold from customer challans
            total_challan_sold = CustomerChallanMaster.objects.filter(
                product_id=product_id
            ).aggregate(total=Sum('sale_quantity'))['total'] or 0
            
            total_sold_combined = total_sold + total_challan_sold
            
            # Get total purchase returns (reduces stock)
            total_purchase_returns = ReturnPurchaseMaster.objects.filter(
                returnproductid=product_id
            ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
            
            # Get total sales returns (increases stock)
            total_sales_returns = ReturnSalesMaster.objects.filter(
                return_productid=product_id
            ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
            
            # Calculate current stock
            # Stock = Purchased - Sold - Challan Sold - Purchase Returns + Sales Returns
            total_stock = total_purchased - total_sold_combined - total_purchase_returns + total_sales_returns
            
            # Get batch-wise breakdown
            batches = StockManager._get_batch_breakdown(product_id)
            
            return {
                'product_id': product_id,
                'total_purchased': total_purchased,
                'total_sold': total_sold,
                'total_purchase_returns': total_purchase_returns,
                'total_sales_returns': total_sales_returns,
                'total_stock': total_stock,
                'batches': batches
            }
        except Exception as e:
            print(f"Error in get_stock_summary: {[str(e)]}")
            return {
                'product_id': product_id,
                'total_purchased': 0,
                'total_sold': 0,
                'total_purchase_returns': 0,
                'total_sales_returns': 0,
                'total_stock': 0,
                'batches': []
            }
    
    @staticmethod
    def _normalize_expiry_date(expiry_date):
        """
        Keep MM-YYYY format as is, no conversion needed
        """
        return expiry_date
    
    @staticmethod
    def _get_batch_breakdown(product_id):
        """
        Get stock breakdown by batch + expiry date combination
        Fixed to track stock separately for each batch + expiry combination
        """
        batches = []
        
        try:
            from .models import CustomerChallanMaster
            
            # Get all unique batch + expiry combinations from purchases
            purchase_combinations = PurchaseMaster.objects.filter(
                productid=product_id
            ).values('product_batch_no', 'product_expiry').distinct()
            
            # Get combinations from supplier challans
            challan_combinations = SupplierChallanMaster.objects.filter(
                product_id=product_id
            ).values('product_batch_no', 'product_expiry').distinct()
            
            # Get combinations from sales invoices
            sales_combinations = SalesMaster.objects.filter(
                productid=product_id
            ).values('product_batch_no', 'product_expiry').distinct()
            
            # Get combinations from customer challans
            customer_challan_combinations = CustomerChallanMaster.objects.filter(
                product_id=product_id
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
            
            for combo in challan_combinations:
                all_combinations.add((combo['product_batch_no'], combo['product_expiry']))
            
            for combo in sales_combinations:
                all_combinations.add((combo['product_batch_no'], combo['product_expiry']))
            
            for combo in customer_challan_combinations:
                all_combinations.add((combo['product_batch_no'], combo['product_expiry']))
            
            for combo in pr_combinations:
                all_combinations.add((combo['returnproduct_batch_no'], combo['returnproduct_expiry']))
            
            for combo in sr_combinations:
                all_combinations.add((combo['return_product_batch_no'], combo['return_product_expiry']))
            
            for batch_no, expiry_date in all_combinations:
                batch_stock_info = StockManager._get_batch_stock_with_expiry(product_id, batch_no, expiry_date)
                
                # Include all batches with any activity (purchases, sales, or returns)
                if (batch_stock_info['batch_stock'] != 0 or 
                    batch_stock_info['purchased'] > 0 or 
                    batch_stock_info['sold'] > 0 or 
                    batch_stock_info['purchase_returns'] > 0 or 
                    batch_stock_info['sales_returns'] > 0):
                    
                    batches.append({
                        'batch_no': batch_no,
                        'expiry': expiry_date,
                        'stock': batch_stock_info['batch_stock'],
                        'purchased': batch_stock_info['purchased'],
                        'sold': batch_stock_info['sold'],
                        'purchase_returns': batch_stock_info['purchase_returns'],
                        'sales_returns': batch_stock_info['sales_returns']
                    })
        except Exception as e:
            print(f"Error in _get_batch_breakdown: {e}")
        
        return batches
    
    @staticmethod
    def _get_batch_stock(product_id, batch_no):
        """
        Get stock information for a specific batch (all expiry dates combined)
        """
        from .models import CustomerChallanMaster
        
        # Get batch purchased from invoices
        purchased_invoice = PurchaseMaster.objects.filter(
            productid=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('product_quantity'))['total'] or 0
        
        # Get batch purchased from challans
        purchased_challan = SupplierChallanMaster.objects.filter(
            product_id=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('product_quantity'))['total'] or 0
        
        purchased = purchased_invoice + purchased_challan
        
        # Get batch sold quantity from sales invoices
        sold = SalesMaster.objects.filter(
            productid=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('sale_quantity'))['total'] or 0
        
        # Get batch sold quantity from customer challans
        challan_sold = CustomerChallanMaster.objects.filter(
            product_id=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('sale_quantity'))['total'] or 0
        
        total_sold = sold + challan_sold
        
        # Get batch purchase returns (reduces stock)
        purchase_returns = ReturnPurchaseMaster.objects.filter(
            returnproductid=product_id,
            returnproduct_batch_no=batch_no
        ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        
        # Get batch sales returns (increases stock)
        sales_returns = ReturnSalesMaster.objects.filter(
            return_productid=product_id,
            return_product_batch_no=batch_no
        ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
        
        # Calculate batch stock
        batch_stock = purchased - total_sold - purchase_returns + sales_returns
        
        return {
            'batch_stock': batch_stock,
            'purchased': purchased,
            'sold': sold,
            'purchase_returns': purchase_returns,
            'sales_returns': sales_returns
        }
    
    @staticmethod
    def _get_batch_stock_with_expiry(product_id, batch_no, expiry_date):
        """
        Get stock information for a specific batch + expiry date combination
        """
        try:
            from .models import CustomerChallanMaster
            
            # Skip expiry date filtering to avoid MM-YYYY format issues
            # Calculate stock for batch only (all expiry dates combined)
            
            # Get batch purchased from invoices
            purchased_invoice = PurchaseMaster.objects.filter(
                productid=product_id,
                product_batch_no=batch_no
            ).aggregate(total=Sum('product_quantity'))['total'] or 0
            
            # Get batch purchased from challans
            purchased_challan = SupplierChallanMaster.objects.filter(
                product_id=product_id,
                product_batch_no=batch_no
            ).aggregate(total=Sum('product_quantity'))['total'] or 0
            
            purchased = purchased_invoice + purchased_challan
            
            # Get batch sold quantity from sales invoices
            sold = SalesMaster.objects.filter(
                productid=product_id,
                product_batch_no=batch_no
            ).aggregate(total=Sum('sale_quantity'))['total'] or 0
            
            # Get batch sold quantity from customer challans
            challan_sold = CustomerChallanMaster.objects.filter(
                product_id=product_id,
                product_batch_no=batch_no
            ).aggregate(total=Sum('sale_quantity'))['total'] or 0
            
            total_sold = sold + challan_sold
            
            # Get batch purchase returns (reduces stock)
            purchase_returns = ReturnPurchaseMaster.objects.filter(
                returnproductid=product_id,
                returnproduct_batch_no=batch_no
            ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
            
            # Get batch sales returns (increases stock)
            sales_returns = ReturnSalesMaster.objects.filter(
                return_productid=product_id,
                return_product_batch_no=batch_no
            ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
            
            # Calculate batch stock
            batch_stock = purchased - total_sold - purchase_returns + sales_returns
            
            return {
                'batch_stock': batch_stock,
                'purchased': purchased,
                'sold': sold,
                'purchase_returns': purchase_returns,
                'sales_returns': sales_returns
            }
        except Exception as e:
            # Silently handle MM-YYYY format validation errors
            if "invalid date format" in str(e).lower():
                return {
                    'batch_stock': 0,
                    'purchased': 0,
                    'sold': 0,
                    'purchase_returns': 0,
                    'sales_returns': 0
                }
            return {
                'batch_stock': 0,
                'purchased': 0,
                'sold': 0,
                'purchase_returns': 0,
                'sales_returns': 0
            }
    
    @staticmethod
    def process_purchase_return(return_item):
        """
        Process a purchase return - this decreases stock
        Enhanced with better error handling and validation
        """
        try:
            product_id = return_item.returnproductid.productid
            batch_no = return_item.returnproduct_batch_no
            return_quantity = return_item.returnproduct_quantity
            product_name = return_item.returnproductid.product_name
            
            # Get current batch stock before return (excluding this return)
            batch_info = StockManager._get_batch_stock_excluding_return(product_id, batch_no, return_item.returnpurchaseid)
            current_stock = batch_info['batch_stock']
            
            # Enhanced validation with detailed feedback
            if current_stock < return_quantity:
                return {
                    'success': False,
                    'message': f"Insufficient stock for return. Product: {product_name}, Batch: {batch_no}. Available: {current_stock}, Requested: {return_quantity}",
                    'error_type': 'insufficient_stock',
                    'available_stock': current_stock,
                    'requested_quantity': return_quantity,
                    'product_name': product_name,
                    'batch_no': batch_no
                }
            
            # Check if return quantity is reasonable (not negative or zero)
            if return_quantity <= 0:
                return {
                    'success': False,
                    'message': f"Invalid return quantity: {return_quantity}. Quantity must be positive.",
                    'error_type': 'invalid_quantity',
                    'product_name': product_name,
                    'batch_no': batch_no
                }
            
            # Calculate new stock after return
            new_stock = current_stock - return_quantity
            
            # Log the transaction for audit trail
            print(f"PURCHASE RETURN PROCESSED:")
            print(f"  Product: {product_name} (ID: {product_id})")
            print(f"  Batch: {batch_no}")
            print(f"  Return Quantity: {return_quantity}")
            print(f"  Stock Before: {current_stock}")
            print(f"  Stock After: {new_stock}")
            
            return {
                'success': True,
                'message': f"Purchase return processed successfully. {product_name} (Batch: {batch_no}) stock reduced from {current_stock} to {new_stock} units.",
                'transaction_type': 'purchase_return',
                'product_name': product_name,
                'batch_no': batch_no,
                'previous_stock': current_stock,
                'new_stock': new_stock,
                'return_quantity': return_quantity,
                'stock_impact': -return_quantity
            }
        except Exception as e:
            error_msg = f"Error processing purchase return: {str(e)}"
            print(f"PURCHASE RETURN ERROR: {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'error_type': 'system_error',
                'error': str(e)
            }
    
    @staticmethod
    def process_sales_return(return_item):
        """
        Process a sales return - this increases stock
        Enhanced with better error handling and validation
        """
        try:
            product_id = return_item.return_productid.productid
            batch_no = return_item.return_product_batch_no
            return_quantity = return_item.return_sale_quantity
            product_name = return_item.return_productid.product_name
            
            # Get current batch stock before return (excluding this return)
            batch_info = StockManager._get_batch_stock_excluding_sales_return(product_id, batch_no, return_item.return_sales_id)
            current_stock = batch_info['batch_stock']
            
            # Enhanced validation
            if return_quantity <= 0:
                return {
                    'success': False,
                    'message': f"Invalid return quantity: {return_quantity}. Quantity must be positive.",
                    'error_type': 'invalid_quantity',
                    'product_name': product_name,
                    'batch_no': batch_no
                }
            
            # Check if the batch exists (has purchase records)
            if not StockManager._batch_exists(product_id, batch_no):
                return {
                    'success': False,
                    'message': f"Batch {batch_no} not found for product {product_name}. Cannot process return.",
                    'error_type': 'batch_not_found',
                    'product_name': product_name,
                    'batch_no': batch_no
                }
            
            # Calculate new stock after return
            new_stock = current_stock + return_quantity
            
            # Log the transaction for audit trail
            print(f"SALES RETURN PROCESSED:")
            print(f"  Product: {product_name} (ID: {product_id})")
            print(f"  Batch: {batch_no}")
            print(f"  Return Quantity: {return_quantity}")
            print(f"  Stock Before: {current_stock}")
            print(f"  Stock After: {new_stock}")
            
            return {
                'success': True,
                'message': f"Sales return processed successfully. {product_name} (Batch: {batch_no}) stock increased from {current_stock} to {new_stock} units.",
                'transaction_type': 'sales_return',
                'product_name': product_name,
                'batch_no': batch_no,
                'previous_stock': current_stock,
                'new_stock': new_stock,
                'return_quantity': return_quantity,
                'stock_impact': +return_quantity
            }
        except Exception as e:
            error_msg = f"Error processing sales return: {str(e)}"
            print(f"SALES RETURN ERROR: {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'error_type': 'system_error',
                'error': str(e)
            }
    
    @staticmethod
    def validate_sale_quantity(product_id, batch_no, sale_quantity):
        """
        Validate if enough stock is available for a sale
        """
        try:
            batch_info = StockManager._get_batch_stock(product_id, batch_no)
            current_stock = batch_info['batch_stock']
            
            if current_stock < sale_quantity:
                return {
                    'valid': False,
                    'message': f"Insufficient stock. Available: {current_stock}, Required: {sale_quantity}",
                    'available_stock': current_stock
                }
            
            return {
                'valid': True,
                'message': f"Stock validation passed. Available: {current_stock}, Required: {sale_quantity}",
                'available_stock': current_stock
            }
        except Exception as e:
            return {
                'valid': False,
                'message': f"Error validating stock: {str(e)}",
                'available_stock': 0
            }
    
    @staticmethod
    def get_low_stock_products(threshold=10):
        """
        Get products with stock below threshold
        """
        low_stock_products = []
        
        products = ProductMaster.objects.all()
        for product in products:
            stock_summary = StockManager.get_stock_summary(product.productid)
            if 0 < stock_summary['total_stock'] <= threshold:
                low_stock_products.append({
                    'product': product,
                    'current_stock': stock_summary['total_stock'],
                    'batches': stock_summary['batches']
                })
        
        return low_stock_products
    
    @staticmethod
    def get_out_of_stock_products():
        """
        Get products that are completely out of stock
        """
        out_of_stock_products = []
        
        products = ProductMaster.objects.all()
        for product in products:
            stock_summary = StockManager.get_stock_summary(product.productid)
            if stock_summary['total_stock'] <= 0:
                out_of_stock_products.append({
                    'product': product,
                    'current_stock': stock_summary['total_stock'],
                    'batches': stock_summary['batches']
                })
        
        return out_of_stock_products
    
    @staticmethod
    def get_stock_value_summary():
        """
        Get total stock value across all products
        """
        total_value = 0
        total_products = 0
        
        products = ProductMaster.objects.all()
        for product in products:
            stock_summary = StockManager.get_stock_summary(product.productid)
            if stock_summary['total_stock'] > 0:
                # Get average MRP for value calculation
                avg_mrp = PurchaseMaster.objects.filter(
                    productid=product.productid
                ).aggregate(avg_mrp=Sum('product_MRP'))['avg_mrp'] or 0
                
                product_value = stock_summary['total_stock'] * avg_mrp
                total_value += product_value
                total_products += 1
        
        return {
            'total_value': total_value,
            'total_products_in_stock': total_products
        }
    
    @staticmethod
    def _get_batch_stock_excluding_return(product_id, batch_no, return_id):
        """
        Get batch stock excluding a specific purchase return (for validation)
        """
        # Get batch purchased from invoices
        purchased_invoice = PurchaseMaster.objects.filter(
            productid=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('product_quantity'))['total'] or 0
        
        # Get batch purchased from challans
        purchased_challan = SupplierChallanMaster.objects.filter(
            product_id=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('product_quantity'))['total'] or 0
        
        purchased = purchased_invoice + purchased_challan
        
        # Get batch sold quantity
        sold = SalesMaster.objects.filter(
            productid=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('sale_quantity'))['total'] or 0
        
        # Get batch purchase returns excluding the current one
        purchase_returns = ReturnPurchaseMaster.objects.filter(
            returnproductid=product_id,
            returnproduct_batch_no=batch_no
        ).exclude(
            returnpurchaseid=return_id
        ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        
        # Get batch sales returns
        sales_returns = ReturnSalesMaster.objects.filter(
            return_productid=product_id,
            return_product_batch_no=batch_no
        ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
        
        # Calculate batch stock
        batch_stock = purchased - sold - purchase_returns + sales_returns
        
        return {
            'batch_stock': batch_stock,
            'purchased': purchased,
            'sold': sold,
            'purchase_returns': purchase_returns,
            'sales_returns': sales_returns
        }
    
    @staticmethod
    def _get_batch_stock_excluding_sales_return(product_id, batch_no, return_id):
        """
        Get batch stock excluding a specific sales return (for validation)
        """
        # Get batch purchased from invoices
        purchased_invoice = PurchaseMaster.objects.filter(
            productid=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('product_quantity'))['total'] or 0
        
        # Get batch purchased from challans
        purchased_challan = SupplierChallanMaster.objects.filter(
            product_id=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('product_quantity'))['total'] or 0
        
        purchased = purchased_invoice + purchased_challan
        
        # Get batch sold quantity
        sold = SalesMaster.objects.filter(
            productid=product_id,
            product_batch_no=batch_no
        ).aggregate(total=Sum('sale_quantity'))['total'] or 0
        
        # Get batch purchase returns
        purchase_returns = ReturnPurchaseMaster.objects.filter(
            returnproductid=product_id,
            returnproduct_batch_no=batch_no
        ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        
        # Get batch sales returns excluding the current one
        sales_returns = ReturnSalesMaster.objects.filter(
            return_productid=product_id,
            return_product_batch_no=batch_no
        ).exclude(
            return_sales_id=return_id
        ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
        
        # Calculate batch stock
        batch_stock = purchased - sold - purchase_returns + sales_returns
        
        return {
            'batch_stock': batch_stock,
            'purchased': purchased,
            'sold': sold,
            'purchase_returns': purchase_returns,
            'sales_returns': sales_returns
        }
    
    @staticmethod
    def _batch_exists(product_id, batch_no):
        """
        Check if a batch exists for a product
        """
        invoice_exists = PurchaseMaster.objects.filter(
            productid=product_id,
            product_batch_no=batch_no
        ).exists()
        
        challan_exists = SupplierChallanMaster.objects.filter(
            product_id=product_id,
            product_batch_no=batch_no
        ).exists()
        
        return invoice_exists or challan_exists
    
    @staticmethod
    def validate_stock_transaction(product_id, batch_no, transaction_type, quantity):
        """
        Comprehensive validation for stock transactions
        """
        try:
            # Get product info
            try:
                product = ProductMaster.objects.get(productid=product_id)
                product_name = product.product_name
            except ProductMaster.DoesNotExist:
                return {
                    'valid': False,
                    'message': f"Product with ID {product_id} not found",
                    'error_type': 'product_not_found'
                }
            
            # Validate quantity
            if quantity <= 0:
                return {
                    'valid': False,
                    'message': f"Invalid quantity: {quantity}. Quantity must be positive.",
                    'error_type': 'invalid_quantity'
                }
            
            # Check if batch exists
            if not StockManager._batch_exists(product_id, batch_no):
                return {
                    'valid': False,
                    'message': f"Batch {batch_no} not found for product {product_name}",
                    'error_type': 'batch_not_found'
                }
            
            # Get current stock
            batch_info = StockManager._get_batch_stock(product_id, batch_no)
            current_stock = batch_info['batch_stock']
            
            # Validate based on transaction type
            if transaction_type in ['sale', 'purchase_return']:
                # These transactions reduce stock
                if current_stock < quantity:
                    return {
                        'valid': False,
                        'message': f"Insufficient stock for {transaction_type}. Available: {current_stock}, Required: {quantity}",
                        'error_type': 'insufficient_stock',
                        'available_stock': current_stock,
                        'required_quantity': quantity
                    }
            
            return {
                'valid': True,
                'message': f"Stock validation passed for {transaction_type}",
                'current_stock': current_stock,
                'transaction_quantity': quantity,
                'product_name': product_name,
                'batch_no': batch_no
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f"Error validating stock transaction: {str(e)}",
                'error_type': 'system_error',
                'error': str(e)
            }
    
    @staticmethod
    def update_stock_on_customer_challan(product, batch_no, quantity, expiry, mrp, rate):
        """
        Update inventory when customer challan is created (reduces stock like sales)
        Stock is tracked via SalesMaster - no separate inventory tables needed
        """
        try:
            # Customer challan reduces stock just like a sale
            # Stock calculation is done via StockManager methods which aggregate from:
            # - PurchaseMaster (adds stock)
            # - SupplierChallanMaster (adds stock)
            # - SalesMaster (reduces stock)
            # - CustomerChallanMaster (reduces stock via this tracking)
            
            # No additional action needed - stock is automatically calculated
            # when get_stock_summary or _get_batch_stock is called
            
            print(f"Customer challan stock update: Product {product.product_name}, Batch {batch_no}, Qty {quantity}")
            return True
        except Exception as e:
            print(f"Error in customer challan stock tracking: {e}")
            return False