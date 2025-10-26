from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from datetime import datetime
import json

from .models import (
    ProductMaster, SupplierMaster, InvoiceMaster, PurchaseMaster, SaleRateMaster, SalesMaster
)
from .utils import get_stock_status

@login_required
def low_stock_update(request):
    """Fast view for updating low stock items with batch details"""
    from django.db.models import Sum, Q
    
    # Get products with recent purchases
    recent_products = ProductMaster.objects.filter(
        purchasemaster__isnull=False
    ).distinct().order_by('product_name')[:30]
    
    low_stock_items = []
    
    for product in recent_products:
        # Get all batches for this product with stock calculation
        batches = PurchaseMaster.objects.filter(
            productid=product.productid
        ).values('product_batch_no', 'product_expiry').annotate(
            purchased_qty=Sum('product_quantity')
        ).distinct()
        
        for batch in batches:
            # Calculate sold quantity for this specific batch
            sold_qty = SalesMaster.objects.filter(
                productid=product.productid,
                product_batch_no=batch['product_batch_no']
            ).aggregate(Sum('sale_quantity'))['sale_quantity__sum'] or 0
            
            current_stock = batch['purchased_qty'] - sold_qty
            
            # Only include low stock batches
            if 0 < current_stock <= 10:
                # Get MRP from existing purchase records for this batch
                existing_mrp = PurchaseMaster.objects.filter(
                    productid=product,
                    product_batch_no=batch['product_batch_no']
                ).first()
                
                low_stock_items.append({
                    'product': product,
                    'batch_no': batch['product_batch_no'],
                    'expiry': batch['product_expiry'],
                    'current_stock': current_stock,
                    'mrp': existing_mrp.product_MRP if existing_mrp else 0,
                    'status': 'Low Stock'
                })
                
                # Stop after finding 30 low stock batch items
                if len(low_stock_items) >= 30:
                    break
        
        if len(low_stock_items) >= 30:
            break
    
    # Get all suppliers for dropdown
    suppliers = SupplierMaster.objects.all().order_by('supplier_name')
    
    context = {
        'low_stock_items': low_stock_items,
        'suppliers': suppliers,
        'title': 'Low Stock Update'
    }
    return render(request, 'inventory/low_stock_update.html', context)

@login_required
def update_low_stock_item(request):
    """API endpoint to update single low stock item"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        supplier_id = data.get('supplier_id')
        batch_no = data.get('batch_no')
        expiry = data.get('expiry')
        purchase_rate = data.get('purchase_rate')
        mrp = data.get('mrp')
        discount = data.get('discount', 0)
        gst = data.get('gst', 0)
        quantity = data.get('quantity')
        
        # Validate required fields
        if not all([product_id, supplier_id, batch_no, expiry, purchase_rate, mrp, quantity]):
            return JsonResponse({
                'success': False,
                'error': 'All fields including supplier and MRP are required'
            })
        
        # Validate expiry format (MM-YYYY)
        import re
        if not re.match(r'^\d{2}-\d{4}$', expiry):
            return JsonResponse({
                'success': False,
                'error': 'Expiry must be in MM-YYYY format'
            })
        
        # Get product
        try:
            product = ProductMaster.objects.get(productid=product_id)
        except ProductMaster.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Product not found'
            })
        
        # Get selected supplier
        try:
            supplier = SupplierMaster.objects.get(supplierid=supplier_id)
        except SupplierMaster.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Supplier not found'
            })
        
        # Create a unique invoice for each stock update
        today = datetime.now()
        invoice_no = f'STK-{today.strftime("%Y%m%d%H%M%S%f")}-{product_id}'
        
        dummy_invoice = InvoiceMaster.objects.create(
            invoice_no=invoice_no,
            supplierid=supplier,
            invoice_date=today.date(),
            transport_charges=0,
            invoice_total=float(purchase_rate) * int(quantity),
            invoice_paid=0
        )
        
        with transaction.atomic():
            # Create purchase entry to increase stock
            purchase = PurchaseMaster.objects.create(
                product_supplierid=supplier,
                product_invoiceid=dummy_invoice,
                product_invoice_no=invoice_no,
                productid=product,
                product_name=product.product_name,
                product_company=product.product_company,
                product_packing=product.product_packing,
                product_batch_no=batch_no,
                product_expiry=expiry,
                product_MRP=float(mrp),
                product_purchase_rate=float(purchase_rate),
                product_quantity=int(quantity),
                product_scheme=0,
                product_discount_got=float(discount),
                product_transportation_charges=0,
                actual_rate_per_qty=float(purchase_rate),
                product_actual_rate=float(purchase_rate),
                total_amount=float(purchase_rate) * int(quantity),
                IGST=float(gst),
                purchase_calculation_mode='flat'
            )
            
            # Create default sale rates for the batch
            SaleRateMaster.objects.update_or_create(
                productid=product,
                product_batch_no=batch_no,
                defaults={
                    'rate_A': float(purchase_rate) * 1.15,  # 15% markup
                    'rate_B': float(purchase_rate) * 1.10,  # 10% markup
                    'rate_C': float(purchase_rate) * 1.05   # 5% markup
                }
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully added {quantity} units of {product.product_name}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def bulk_update_low_stock(request):
    """API endpoint to bulk update multiple low stock items"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        updates = data.get('updates', [])
        
        if not updates:
            return JsonResponse({
                'success': False,
                'error': 'No updates provided'
            })
        
        # Create a dummy supplier for stock updates
        dummy_supplier, created = SupplierMaster.objects.get_or_create(
            supplier_name='Stock Update Supplier',
            defaults={
                'supplier_type': 'Local',
                'supplier_address': 'N/A',
                'supplier_mobile': '0000000000',
                'supplier_whatsapp': '0000000000',
                'supplier_emailid': 'noreply@pharmacy.com',
                'supplier_spoc': 'System',
                'supplier_dlno': 'N/A',
                'supplier_gstno': 'N/A',
                'supplier_bank': 'N/A',
                'supplier_bankaccountno': 'N/A',
                'supplier_bankifsc': 'N/A'
            }
        )
        
        today = datetime.now()
        bulk_invoice_no = f'BULK-STK-{today.strftime("%Y%m%d%H%M%S%f")}-{len(updates)}'
        
        # Calculate total amount
        total_amount = sum(float(update['purchase_rate']) * int(update['quantity']) for update in updates)
        
        # Create bulk invoice
        bulk_invoice = InvoiceMaster.objects.create(
            invoice_no=bulk_invoice_no,
            supplierid=dummy_supplier,
            invoice_date=today.date(),
            transport_charges=0,
            invoice_total=total_amount,
            invoice_paid=0
        )
        
        updated_count = 0
        
        with transaction.atomic():
            for update in updates:
                try:
                    product_id = update.get('product_id')
                    supplier_id = update.get('supplier_id')
                    batch_no = update.get('batch_no')
                    expiry = update.get('expiry')
                    purchase_rate = update.get('purchase_rate')
                    mrp = update.get('mrp')
                    discount = update.get('discount', 0)
                    gst = update.get('gst', 0)
                    quantity = update.get('quantity')
                    
                    # Validate fields
                    if not all([product_id, supplier_id, batch_no, expiry, purchase_rate, mrp, quantity]):
                        continue
                    
                    # Validate expiry format
                    import re
                    if not re.match(r'^\d{2}-\d{4}$', expiry):
                        continue
                    
                    # Get product and supplier
                    try:
                        product = ProductMaster.objects.get(productid=product_id)
                        item_supplier = SupplierMaster.objects.get(supplierid=supplier_id)
                    except (ProductMaster.DoesNotExist, SupplierMaster.DoesNotExist):
                        continue
                    
                    # Create purchase entry
                    purchase = PurchaseMaster.objects.create(
                        product_supplierid=item_supplier,
                        product_invoiceid=bulk_invoice,
                        product_invoice_no=bulk_invoice_no,
                        productid=product,
                        product_name=product.product_name,
                        product_company=product.product_company,
                        product_packing=product.product_packing,
                        product_batch_no=batch_no,
                        product_expiry=expiry,
                        product_MRP=float(mrp),
                        product_purchase_rate=float(purchase_rate),
                        product_quantity=int(quantity),
                        product_scheme=0,
                        product_discount_got=float(discount),
                        product_transportation_charges=0,
                        actual_rate_per_qty=float(purchase_rate),
                        product_actual_rate=float(purchase_rate),
                        total_amount=float(purchase_rate) * int(quantity),
                        IGST=float(gst),
                        purchase_calculation_mode='flat'
                    )
                    
                    # Create sale rates
                    SaleRateMaster.objects.update_or_create(
                        productid=product,
                        product_batch_no=batch_no,
                        defaults={
                            'rate_A': float(purchase_rate) * 1.15,
                            'rate_B': float(purchase_rate) * 1.10,
                            'rate_C': float(purchase_rate) * 1.05
                        }
                    )
                    
                    updated_count += 1
                    
                except Exception as e:
                    print(f"Error updating product {product_id}: {e}")
                    continue
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully updated {updated_count} products',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def get_batch_suggestions(request):
    """API endpoint to get batch suggestions for a product"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        product_id = request.GET.get('product_id')
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'error': 'Product ID is required'
            })
        
        # Get product
        try:
            product = ProductMaster.objects.get(productid=product_id)
        except ProductMaster.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Product not found'
            })
        
        # Get all unique batches for this product
        batches = PurchaseMaster.objects.filter(
            productid=product
        ).values('product_batch_no', 'product_expiry').distinct().order_by('-product_expiry')
        
        batch_suggestions = []
        for batch in batches:
            batch_suggestions.append({
                'batch_no': batch['product_batch_no'],
                'expiry': batch['product_expiry']
            })
        
        return JsonResponse({
            'success': True,
            'batches': batch_suggestions
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)