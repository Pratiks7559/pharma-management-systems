import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, Q
from .models import ProductMaster, SupplierMaster, PurchaseMaster, SaleRateMaster, InvoiceMaster, SalesMaster
from .forms import InvoiceForm
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple file logging for debugging
import os
log_file = os.path.join(os.path.dirname(__file__), 'invoice_debug.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

@login_required
def add_invoice_with_products(request):
    if request.method == 'POST':
        try:
            # Debug: Log the POST data
            logger.info(f"POST data received: {request.POST}")
            
            # Handle form submission
            invoice_form = InvoiceForm(request.POST)
            
            # Debug: Check form validation
            if not invoice_form.is_valid():
                logger.error(f"Invoice form validation errors: {invoice_form.errors}")
                messages.error(request, f"Invoice form validation failed: {invoice_form.errors}")
                # Return to form with errors
                suppliers = SupplierMaster.objects.all().order_by('supplier_name')
                products = ProductMaster.objects.all().order_by('product_name')
                context = {
                    'invoice_form': invoice_form,
                    'suppliers': suppliers,
                    'products': products,
                    'title': 'Add Invoice with Products'
                }
                return render(request, 'purchases/combined_invoice_form.html', context)
            
            # Process products data from JavaScript
            products_data = request.POST.get('products_data')
            logger.info(f"Products data received: {products_data}")
            
            if not products_data:
                messages.error(request, "No products data provided. Please add at least one product.")
                suppliers = SupplierMaster.objects.all().order_by('supplier_name')
                products = ProductMaster.objects.all().order_by('product_name')
                context = {
                    'invoice_form': invoice_form,
                    'suppliers': suppliers,
                    'products': products,
                    'title': 'Add Invoice with Products'
                }
                return render(request, 'purchases/combined_invoice_form.html', context)
            
            try:
                products = json.loads(products_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                messages.error(request, "Invalid products data format. Please try again.")
                suppliers = SupplierMaster.objects.all().order_by('supplier_name')
                products_list = ProductMaster.objects.all().order_by('product_name')
                context = {
                    'invoice_form': invoice_form,
                    'suppliers': suppliers,
                    'products': products_list,
                    'title': 'Add Invoice with Products'
                }
                return render(request, 'purchases/combined_invoice_form.html', context)
            
            if not products:
                messages.error(request, "Please add at least one product to the invoice.")
                suppliers = SupplierMaster.objects.all().order_by('supplier_name')
                products_list = ProductMaster.objects.all().order_by('product_name')
                context = {
                    'invoice_form': invoice_form,
                    'suppliers': suppliers,
                    'products': products_list,
                    'title': 'Add Invoice with Products'
                }
                return render(request, 'purchases/combined_invoice_form.html', context)
            
            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Create invoice
                invoice = invoice_form.save(commit=False)
                invoice.invoice_paid = 0
                invoice.save()
                logger.info(f"Invoice created with ID: {invoice.invoiceid}")
                
                total_amount = 0
                products_added = 0
                errors = []
                
                for i, product_data in enumerate(products):
                    if product_data.get('productid'):
                        try:
                            # Get product details
                            product = ProductMaster.objects.get(productid=product_data['productid'])
                            
                            # Validate required fields
                            batch_no = product_data.get('batch_no', '').strip()
                            expiry = product_data.get('expiry', '').strip()
                            
                            if not batch_no:
                                errors.append(f"Row {i+1}: Batch number is required for {product.product_name}")
                                continue
                            
                            if not expiry:
                                errors.append(f"Row {i+1}: Expiry date is required for {product.product_name}")
                                continue
                            
                            # Validate and normalize expiry date to MM-YYYY format
                            try:
                                import re
                                expiry = expiry.strip()
                                
                                # Handle different input formats and convert to MM-YYYY
                                if len(expiry) == 4 and expiry.isdigit():
                                    month = expiry[:2]
                                    year = '20' + expiry[2:4]
                                    expiry = f"{month}-{year}"
                                elif len(expiry) == 6 and expiry.isdigit():
                                    month = expiry[:2]
                                    year = expiry[2:6]
                                    expiry = f"{month}-{year}"
                                elif '/' in expiry:
                                    expiry = expiry.replace('/', '-')
                                elif len(expiry) == 7 and expiry.count('-') == 1:
                                    pass
                                elif not expiry:
                                    raise ValueError("Empty expiry date")
                                else:
                                    digits = re.sub(r'[^0-9]', '', expiry)
                                    if len(digits) == 4:
                                        expiry = f"{digits[:2]}-20{digits[2:4]}"
                                    elif len(digits) == 6:
                                        expiry = f"{digits[:2]}-{digits[2:6]}"
                                    else:
                                        raise ValueError("Invalid format")
                                
                                if not re.match(r'^(0[1-9]|1[0-2])-\d{4}$', expiry):
                                    raise ValueError("Invalid MM-YYYY format")
                                
                                month, year = expiry.split('-')
                                month = int(month)
                                year = int(year)
                                
                                if month < 1 or month > 12:
                                    raise ValueError("Invalid month")
                                if year < 2020 or year > 2100:
                                    raise ValueError("Invalid year")
                                
                            except (ValueError, IndexError) as e:
                                errors.append(f"Row {i+1}: Invalid expiry date format for {product.product_name}. Use MM-YYYY format (e.g., 12-2025). Got: '{product_data.get('expiry', '')}'. Error: {str(e)}")
                                continue
                            
                            # Convert and validate numeric fields
                            try:
                                mrp = float(product_data.get('mrp', 0))
                                purchase_rate = float(product_data.get('purchase_rate', 0))
                                quantity = float(product_data.get('quantity', 0))
                                scheme = float(product_data.get('scheme', 0))
                                discount = float(product_data.get('discount', 0))
                                cgst = float(product_data.get('cgst', 0))
                                sgst = float(product_data.get('sgst', 0))
                            except (ValueError, TypeError) as e:
                                errors.append(f"Row {i+1}: Invalid numeric values for {product.product_name}: {e}")
                                continue
                            
                            if quantity <= 0:
                                errors.append(f"Row {i+1}: Quantity must be greater than 0 for {product.product_name}")
                                continue
                            
                            if purchase_rate <= 0:
                                errors.append(f"Row {i+1}: Purchase rate must be greater than 0 for {product.product_name}")
                                continue
                            
                            # Create purchase entry
                            purchase = PurchaseMaster()
                            purchase.product_supplierid = invoice.supplierid
                            purchase.product_invoiceid = invoice
                            purchase.product_invoice_no = invoice.invoice_no
                            purchase.productid = product
                            purchase.product_name = product.product_name
                            purchase.product_company = product.product_company
                            purchase.product_packing = product.product_packing
                            purchase.product_batch_no = batch_no
                            purchase.product_expiry = expiry
                            purchase.product_MRP = mrp
                            purchase.product_purchase_rate = purchase_rate
                            purchase.product_quantity = quantity
                            purchase.product_scheme = scheme
                            purchase.product_discount_got = discount
                            purchase.CGST = cgst
                            purchase.SGST = sgst
                            purchase.purchase_calculation_mode = product_data.get('calculation_mode', 'flat')
                            
                            # Calculate actual rate
                            if purchase.purchase_calculation_mode == 'flat':
                                if discount > purchase_rate * quantity:
                                    errors.append(f"Row {i+1}: Flat discount cannot exceed total amount for {product.product_name}")
                                    continue
                                purchase.actual_rate_per_qty = purchase_rate - (discount / quantity) if quantity > 0 else purchase_rate
                            else:
                                if discount > 100:
                                    errors.append(f"Row {i+1}: Percentage discount cannot exceed 100% for {product.product_name}")
                                    continue
                                purchase.actual_rate_per_qty = purchase_rate * (1 - (discount / 100))
                            
                            purchase.product_actual_rate = purchase.actual_rate_per_qty
                            purchase.total_amount = purchase.product_actual_rate * quantity
                            purchase.product_transportation_charges = 0  # Will be calculated later
                            
                            total_amount += purchase.total_amount
                            purchase.save()
                            products_added += 1
                            logger.info(f"Product {product.product_name} added to invoice")
                            
                            # Save sale rates if provided
                            rate_A = product_data.get('rate_A')
                            rate_B = product_data.get('rate_B')
                            rate_C = product_data.get('rate_C')
                            
                            if rate_A or rate_B or rate_C:
                                try:
                                    SaleRateMaster.objects.update_or_create(
                                        productid=product,
                                        product_batch_no=batch_no,
                                        defaults={
                                            'rate_A': float(rate_A) if rate_A else 0,
                                            'rate_B': float(rate_B) if rate_B else 0,
                                            'rate_C': float(rate_C) if rate_C else 0
                                        }
                                    )
                                except (ValueError, TypeError):
                                    logger.warning(f"Invalid sale rates for {product.product_name}, skipping rate setup")
                            
                        except ProductMaster.DoesNotExist:
                            errors.append(f"Row {i+1}: Product with ID {product_data['productid']} not found")
                            continue
                        except Exception as e:
                            errors.append(f"Row {i+1}: Error processing product: {str(e)}")
                            logger.error(f"Error processing product {i+1}: {e}")
                            continue
                
                # Check if any products were added
                if products_added == 0:
                    error_msg = "No valid products were added to the invoice."
                    if errors:
                        error_msg += " Errors: " + "; ".join(errors[:5])  # Show first 5 errors
                    messages.error(request, error_msg)
                    # Delete the invoice since no products were added
                    invoice.delete()
                    suppliers = SupplierMaster.objects.all().order_by('supplier_name')
                    products_list = ProductMaster.objects.all().order_by('product_name')
                    context = {
                        'invoice_form': InvoiceForm(),
                        'suppliers': suppliers,
                        'products': products_list,
                        'title': 'Add Invoice with Products'
                    }
                    return render(request, 'purchases/combined_invoice_form.html', context)
                
                # Distribute transport charges if any
                if invoice.transport_charges > 0 and products_added > 0:
                    transport_per_product = invoice.transport_charges / products_added
                    purchases = PurchaseMaster.objects.filter(product_invoiceid=invoice)
                    
                    for purchase in purchases:
                        purchase.product_transportation_charges = transport_per_product
                        transport_per_unit = transport_per_product / purchase.product_quantity
                        purchase.product_actual_rate = purchase.actual_rate_per_qty + transport_per_unit
                        purchase.total_amount = purchase.product_actual_rate * purchase.product_quantity
                        purchase.save()
                    
                    # Recalculate total with transport charges
                    total_amount = sum(p.total_amount for p in purchases)
                
                # Update invoice total if calculated total differs significantly
                if abs(total_amount - invoice.invoice_total) > 0.01:
                    logger.info(f"Updating invoice total from {invoice.invoice_total} to {total_amount}")
                    invoice.invoice_total = total_amount
                    invoice.save()
                
                # Show any non-critical errors as warnings
                if errors:
                    for error in errors[:3]:  # Show first 3 errors
                        messages.warning(request, error)
                
                messages.success(request, f"Purchase Invoice #{invoice.invoice_no} with {products_added} products added successfully!")
                logger.info(f"Invoice {invoice.invoice_no} created successfully with {products_added} products")
                return redirect('invoice_detail', pk=invoice.invoiceid)
                
        except Exception as e:
            logger.error(f"Unexpected error creating invoice: {e}")
            messages.error(request, f"Error creating invoice: {str(e)}")
            # Return to form
            suppliers = SupplierMaster.objects.all().order_by('supplier_name')
            products = ProductMaster.objects.all().order_by('product_name')
            context = {
                'invoice_form': InvoiceForm(),
                'suppliers': suppliers,
                'products': products,
                'title': 'Add Invoice with Products'
            }
            return render(request, 'purchases/combined_invoice_form.html', context)
    else:
        # GET request - show the form
        invoice_form = InvoiceForm()
    
    # Get suppliers and products for dropdowns
    suppliers = SupplierMaster.objects.all().order_by('supplier_name')
    products = ProductMaster.objects.all().order_by('product_name')
    
    context = {
        'invoice_form': invoice_form,
        'suppliers': suppliers,
        'products': products,
        'title': 'Add Invoice with Products'
    }
    return render(request, 'purchases/combined_invoice_form.html', context)



@login_required
def get_existing_batches(request):
    """API endpoint to get batches from both Purchase and Supplier Challan entries"""
    try:
        product_id = request.GET.get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'error': 'Product ID required'})
        
        from .stock_manager import StockManager
        from .models import ReturnPurchaseMaster, ReturnSalesMaster, SupplierChallanMaster
        
        batches_dict = {}
        
        # 1. Get batches from PurchaseMaster
        purchase_batches = PurchaseMaster.objects.filter(productid=product_id).values(
            'product_batch_no', 'product_expiry', 'product_MRP', 'product_purchase_rate'
        ).distinct()
        
        for batch in purchase_batches:
            batch_no = batch['product_batch_no']
            try:
                batch_stock_info = StockManager._get_batch_stock(product_id, batch_no)
                current_stock = batch_stock_info['batch_stock']
            except Exception:
                total_purchased = PurchaseMaster.objects.filter(
                    productid=product_id, product_batch_no=batch_no
                ).aggregate(total=Sum('product_quantity'))['total'] or 0
                total_sold = SalesMaster.objects.filter(
                    productid=product_id, product_batch_no=batch_no
                ).aggregate(total=Sum('sale_quantity'))['total'] or 0
                purchase_returns = ReturnPurchaseMaster.objects.filter(
                    returnproductid=product_id, returnproduct_batch_no=batch_no
                ).aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
                sales_returns = ReturnSalesMaster.objects.filter(
                    return_productid=product_id, return_product_batch_no=batch_no
                ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
                current_stock = total_purchased - total_sold - purchase_returns + sales_returns
            
            if current_stock >= 0:
                latest_purchase = PurchaseMaster.objects.filter(
                    productid=product_id, product_batch_no=batch_no
                ).select_related('product_invoiceid', 'product_supplierid').order_by('-purchase_entry_date').first()
                
                supplier_challan = None
                if latest_purchase:
                    try:
                        challan = SupplierChallanMaster.objects.filter(
                            product_id=product_id, product_batch_no=batch_no
                        ).select_related('product_challan_id').order_by('-challan_entry_date').first()
                        if challan:
                            supplier_challan = {
                                'challan_no': challan.product_challan_no,
                                'challan_date': challan.product_challan_id.challan_date.strftime('%d-%m-%Y')
                            }
                    except Exception:
                        pass
                
                batches_dict[batch_no] = {
                    'batch_no': batch_no,
                    'expiry': batch['product_expiry'],
                    'mrp': batch['product_MRP'],
                    'purchase_rate': latest_purchase.product_purchase_rate if latest_purchase else batch['product_purchase_rate'],
                    'stock': current_stock,
                    'supplier_name': latest_purchase.product_supplierid.supplier_name if latest_purchase else 'N/A',
                    'invoice_no': latest_purchase.product_invoice_no if latest_purchase else 'N/A',
                    'supplier_challan': supplier_challan
                }
        
        # 2. Get batches from SupplierChallanMaster
        challan_batches = SupplierChallanMaster.objects.filter(product_id=product_id).values(
            'product_batch_no', 'product_expiry', 'product_mrp', 'product_purchase_rate'
        ).distinct()
        
        for batch in challan_batches:
            batch_no = batch['product_batch_no']
            if batch_no in batches_dict:
                continue
            
            try:
                batch_stock_info = StockManager._get_batch_stock(product_id, batch_no)
                current_stock = batch_stock_info['batch_stock']
            except Exception:
                total_challan = SupplierChallanMaster.objects.filter(
                    product_id=product_id, product_batch_no=batch_no
                ).aggregate(total=Sum('product_quantity'))['total'] or 0
                total_sold = SalesMaster.objects.filter(
                    productid=product_id, product_batch_no=batch_no
                ).aggregate(total=Sum('sale_quantity'))['total'] or 0
                sales_returns = ReturnSalesMaster.objects.filter(
                    return_productid=product_id, return_product_batch_no=batch_no
                ).aggregate(total=Sum('return_sale_quantity'))['total'] or 0
                current_stock = total_challan - total_sold + sales_returns
            
            if current_stock >= 0:
                latest_challan = SupplierChallanMaster.objects.filter(
                    product_id=product_id, product_batch_no=batch_no
                ).select_related('product_challan_id', 'product_suppliername').order_by('-challan_entry_date').first()
                
                batches_dict[batch_no] = {
                    'batch_no': batch_no,
                    'expiry': batch['product_expiry'],
                    'mrp': batch['product_mrp'],
                    'purchase_rate': latest_challan.product_purchase_rate if latest_challan else batch['product_purchase_rate'],
                    'stock': current_stock,
                    'supplier_name': latest_challan.product_suppliername.supplier_name if latest_challan else 'N/A',
                    'invoice_no': 'N/A',
                    'supplier_challan': {
                        'challan_no': latest_challan.product_challan_no,
                        'challan_date': latest_challan.product_challan_id.challan_date.strftime('%d-%m-%Y')
                    } if latest_challan else None
                }
        
        return JsonResponse({'success': True, 'batches': list(batches_dict.values())})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})




@login_required
def cleanup_duplicate_batches(request):
    """Clean up duplicate SaleRateMaster entries to fix product list duplicates"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                from django.db.models import Count
                
                # Find all duplicate SaleRateMaster entries
                duplicates = SaleRateMaster.objects.values(
                    'productid', 'product_batch_no'
                ).annotate(
                    count=Count('id')
                ).filter(count__gt=1)
                
                cleaned_count = 0
                duplicate_groups = 0
                
                for duplicate in duplicates:
                    # Get all entries for this product-batch combination
                    entries = SaleRateMaster.objects.filter(
                        productid=duplicate['productid'],
                        product_batch_no=duplicate['product_batch_no']
                    ).order_by('id')
                    
                    if entries.count() > 1:
                        duplicate_groups += 1
                        # Keep the first entry, delete the rest
                        entries_to_delete = entries[1:]
                        
                        for entry in entries_to_delete:
                            entry.delete()
                            cleaned_count += 1
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully cleaned up {cleaned_count} duplicate entries from {duplicate_groups} product-batch combinations',
                    'cleaned_count': cleaned_count,
                    'duplicate_groups': duplicate_groups
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error during cleanup: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method. Use POST.'
    })

@login_required
def get_batch_inventory_status(request):
    """Get current inventory status for a specific batch"""
    if request.method == 'GET':
        try:
            product_id = request.GET.get('product_id')
            batch_no = request.GET.get('batch_no')
            
            if not product_id or not batch_no:
                return JsonResponse({
                    'success': False,
                    'error': 'Product ID and Batch Number are required'
                })
            
            # Get current stock for this batch
            from django.db.models import Sum
            
            # Total purchased quantity
            total_purchased = PurchaseMaster.objects.filter(
                productid=product_id,
                product_batch_no=batch_no
            ).aggregate(total=Sum('product_quantity'))['total'] or 0
            
            # Check if SaleRateMaster entry exists
            sale_rate_count = SaleRateMaster.objects.filter(
                productid_id=product_id,
                product_batch_no=batch_no
            ).count()
            
            return JsonResponse({
                'success': True,
                'product_id': product_id,
                'batch_no': batch_no,
                'total_stock': total_purchased,
                'sale_rate_entries': sale_rate_count,
                'has_duplicates': sale_rate_count > 1
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
def cleanup_product_duplicates(request):
    """Clean up duplicate entries for a specific product"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            batch_no = data.get('batch_no')
            
            if not product_id or not batch_no:
                return JsonResponse({
                    'success': False,
                    'error': 'Product ID and Batch Number are required'
                })
            
            with transaction.atomic():
                # Clean SaleRateMaster duplicates for this specific batch
                sale_rate_entries = SaleRateMaster.objects.filter(
                    productid_id=product_id,
                    product_batch_no=batch_no
                ).order_by('id')
                
                cleaned_count = 0
                if sale_rate_entries.count() > 1:
                    # Keep first entry, delete rest
                    entries_to_delete = sale_rate_entries[1:]
                    for entry in entries_to_delete:
                        entry.delete()
                        cleaned_count += 1
                
                return JsonResponse({
                    'success': True,
                    'message': f'Cleaned {cleaned_count} duplicate entries for batch {batch_no}',
                    'cleaned_count': cleaned_count
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })