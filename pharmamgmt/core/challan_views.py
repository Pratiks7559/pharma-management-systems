from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

@login_required
def supplier_challan_list(request):
    """View for supplier challan list"""
    from core.models import Challan1, SupplierMaster
    
    # Only show challans that haven't been invoiced yet
    challans = Challan1.objects.select_related('supplier').filter(is_invoiced=False).order_by('-challan_date', '-challan_id')
    suppliers = SupplierMaster.objects.all().order_by('supplier_name')
    
    context = {
        'title': 'Supplier Challan List',
        'challans': challans,
        'suppliers': suppliers
    }
    return render(request, 'challan/supplier_challan_list.html', context)

@login_required
def add_supplier_challan(request):
    """View for adding supplier challan with products"""
    from core.models import SupplierMaster, ProductMaster, Challan1, SupplierChallanMaster
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.db import transaction
    import json
    from decimal import Decimal
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                challan_no = request.POST.get('challan_no')
                challan_date = request.POST.get('challan_date')
                supplier_id = request.POST.get('supplierid')
                transport_charges = Decimal(request.POST.get('transport_charges', 0))
                challan_total = Decimal(request.POST.get('challan_total', 0))
                products_data = json.loads(request.POST.get('products_data', '[]'))
                
                if not products_data:
                    messages.error(request, 'Please add at least one product')
                    return redirect('add_supplier_challan')
                
                supplier = SupplierMaster.objects.get(supplierid=supplier_id)
                
                challan = Challan1.objects.create(
                    challan_no=challan_no,
                    challan_date=challan_date,
                    supplier=supplier,
                    challan_total=float(challan_total),
                    transport_charges=float(transport_charges),
                    challan_paid=0.0
                )
                
                for product_data in products_data:
                    from core.models import PurchaseMaster, SaleRateMaster
                    
                    product = ProductMaster.objects.get(productid=product_data['productid'])
                    
                    rate = Decimal(product_data.get('challan_rate', 0))
                    qty = Decimal(product_data.get('quantity', 0))
                    discount = Decimal(product_data.get('discount', 0))
                    cgst = Decimal(product_data.get('cgst', 2.5))
                    sgst = Decimal(product_data.get('sgst', 2.5))
                    batch_no = product_data.get('batch_no', '')
                    expiry = product_data.get('expiry', '')
                    
                    subtotal = rate * qty
                    after_discount = subtotal - discount
                    cgst_amount = (after_discount * cgst) / 100
                    sgst_amount = (after_discount * sgst) / 100
                    total = after_discount + cgst_amount + sgst_amount
                    
                    # Create challan entry - Inventory auto-updates via StockManager
                    SupplierChallanMaster.objects.create(
                        product_suppliername=supplier,
                        product_challan_id=challan,
                        product_challan_no=challan_no,
                        product_id=product,
                        product_name=product.product_name,
                        product_company=product.product_company,
                        product_packing=product.product_packing,
                        product_batch_no=batch_no,
                        product_expiry=expiry,
                        product_mrp=float(product_data.get('mrp', 0)),
                        product_purchase_rate=float(rate),
                        product_quantity=float(qty),
                        product_scheme=float(product_data.get('scheme', 0)),
                        product_discount=float(discount),
                        cgst=float(cgst),
                        sgst=float(sgst),
                        total_amount=float(total),
                        challan_calculation_mode=product_data.get('calculation_mode', 'flat')
                    )
                    
                    # Update sale rates if provided
                    rate_A = product_data.get('rate_A')
                    rate_B = product_data.get('rate_B')
                    rate_C = product_data.get('rate_C')
                    
                    if rate_A or rate_B or rate_C:
                        SaleRateMaster.objects.update_or_create(
                            productid=product,
                            product_batch_no=batch_no,
                            defaults={
                                'rate_A': float(rate_A) if rate_A else 0,
                                'rate_B': float(rate_B) if rate_B else 0,
                                'rate_C': float(rate_C) if rate_C else 0
                            }
                        )
                
                messages.success(request, f'Challan {challan_no} created successfully! Inventory has been updated.')
                return redirect('supplier_challan_list')
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR in challan creation: {error_details}")
            messages.error(request, f'Error: {str(e)}')
            return redirect('add_supplier_challan')
    
    suppliers = SupplierMaster.objects.all().order_by('supplier_name')
    products = ProductMaster.objects.all().order_by('product_name')
    
    context = {
        'suppliers': suppliers,
        'products': products,
        'title': 'Add Supplier Challan with Products'
    }
    return render(request, 'challan/supplier_challan_form.html', context)

@login_required
def view_supplier_challan(request, challan_id):
    """View for displaying supplier challan details"""
    from core.models import Challan1, SupplierChallanMaster
    from django.db.models import Sum
    
    challan = get_object_or_404(Challan1, challan_id=challan_id)
    challan_items = SupplierChallanMaster.objects.filter(product_challan_id=challan).select_related('product_id')
    
    products_total = challan_items.aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'challan': challan,
        'challan_items': challan_items,
        'products_total': products_total,
        'title': f'Challan {challan.challan_no}'
    }
    return render(request, 'challan/supplier_challan_detail.html', context)

@login_required
@require_POST
def delete_supplier_challan(request, challan_id):
    """Delete supplier challan"""
    from core.models import Challan1
    from django.db import transaction
    
    try:
        with transaction.atomic():
            challan = get_object_or_404(Challan1, challan_id=challan_id)
            challan_no = challan.challan_no
            challan.delete()
            return JsonResponse({'success': True, 'message': f'Challan {challan_no} deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Customer Challan Views
@login_required
def customer_challan_list(request):
    """View for customer challan list - only show non-invoiced challans"""
    from core.models import CustomerChallan, InvoiceSeries
    
    # Only show challans that haven't been invoiced yet
    challans = CustomerChallan.objects.select_related('customer_name').filter(is_invoiced=False).order_by('-customer_challan_date', '-customer_challan_id')
    
    # Get all active invoice series for the dropdown
    invoice_series = InvoiceSeries.objects.filter(is_active=True).order_by('series_name')
    
    context = {
        'title': 'Customer Challan List',
        'challans': challans,
        'invoice_series': invoice_series
    }
    return render(request, 'challan/customer_challan_list.html', context)

@login_required
def add_customer_challan(request):
    """View for adding customer challan with products"""
    from core.models import CustomerMaster, ProductMaster, CustomerChallan, CustomerChallanMaster, InvoiceSeries
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.db import transaction
    import json
    from decimal import Decimal
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                challan_date = request.POST.get('challan_date')
                customer_id = request.POST.get('customer_id')
                series_id = request.POST.get('challan_series')
                transport_charges = Decimal(request.POST.get('transport_charges', 0))
                products_data = json.loads(request.POST.get('products_data', '[]'))
                
                if not products_data:
                    messages.error(request, 'Please add at least one product')
                    return redirect('add_customer_challan')
                
                customer = CustomerMaster.objects.get(customerid=customer_id)
                
                # Get series and generate challan number with date
                series = None
                from datetime import datetime
                from core.models import ChallanSeries
                
                if series_id:
                    series = ChallanSeries.objects.get(series_id=series_id)
                    series_name = series.series_name
                    
                    # Parse challan date
                    challan_date_obj = datetime.strptime(challan_date, '%Y-%m-%d')
                    date_str = challan_date_obj.strftime('%d%m%Y')
                    
                    # Find last challan with same series and date
                    prefix = f'{series_name}{date_str}'
                    last_challan = CustomerChallan.objects.filter(
                        customer_challan_no__startswith=prefix
                    ).order_by('-customer_challan_no').first()
                    
                    if last_challan:
                        # Extract counter from last challan number
                        last_counter = int(last_challan.customer_challan_no[-3:])
                        new_counter = last_counter + 1
                    else:
                        # First challan for this date
                        new_counter = 1
                    
                    challan_no = f'{prefix}{new_counter:03d}'
                else:
                    # Fallback if no series selected
                    challan_date_obj = datetime.strptime(challan_date, '%Y-%m-%d')
                    date_str = challan_date_obj.strftime('%d%m%Y')
                    prefix = f'CH{date_str}'
                    
                    last_challan = CustomerChallan.objects.filter(
                        customer_challan_no__startswith=prefix
                    ).order_by('-customer_challan_no').first()
                    
                    if last_challan:
                        last_counter = int(last_challan.customer_challan_no[-3:])
                        new_counter = last_counter + 1
                    else:
                        new_counter = 1
                    
                    challan_no = f'{prefix}{new_counter:03d}'
                
                # Calculate products total
                products_total = sum(
                    Decimal(p.get('sale_rate', 0)) * Decimal(p.get('quantity', 0)) - 
                    Decimal(p.get('discount', 0)) + 
                    (Decimal(p.get('sale_rate', 0)) * Decimal(p.get('quantity', 0)) - Decimal(p.get('discount', 0))) * 
                    (Decimal(p.get('cgst', 0)) + Decimal(p.get('sgst', 0))) / 100
                    for p in products_data
                )
                challan_total = products_total + transport_charges
                
                challan = CustomerChallan.objects.create(
                    customer_challan_no=challan_no,
                    customer_challan_date=challan_date,
                    customer_name=customer,
                    challan_series=series,
                    customer_transport_charges=float(transport_charges),
                    challan_total=float(challan_total),
                    challan_invoice_paid=0.0
                )
                
                for product_data in products_data:
                    product = ProductMaster.objects.get(productid=product_data['productid'])
                    
                    rate = Decimal(product_data.get('sale_rate', 0))
                    qty = Decimal(product_data.get('quantity', 0))
                    discount = Decimal(product_data.get('discount', 0))
                    cgst = Decimal(product_data.get('cgst', 2.5))
                    sgst = Decimal(product_data.get('sgst', 2.5))
                    batch_no = product_data.get('batch_no', '')
                    expiry = product_data.get('expiry', '')
                    
                    subtotal = rate * qty
                    after_discount = subtotal - discount
                    cgst_amount = (after_discount * cgst) / 100
                    sgst_amount = (after_discount * sgst) / 100
                    total = after_discount + cgst_amount + sgst_amount
                    
                    CustomerChallanMaster.objects.create(
                        customer_challan_id=challan,
                        customer_challan_no=challan_no,
                        customer_name=customer,
                        product_id=product,
                        product_name=product.product_name,
                        product_company=product.product_company,
                        product_packing=product.product_packing,
                        product_batch_no=batch_no,
                        product_expiry=expiry,
                        product_mrp=float(product_data.get('mrp', 0)),
                        sale_rate=float(rate),
                        sale_quantity=float(qty),
                        sale_discount=float(discount),
                        sale_cgst=float(cgst),
                        sale_sgst=float(sgst),
                        sale_total_amount=float(total),
                        rate_applied=product_data.get('rate_applied', 'NA')
                    )
                    
                    from core.stock_manager import StockManager
                    StockManager.update_stock_on_customer_challan(
                        product=product,
                        batch_no=batch_no,
                        quantity=float(qty),
                        expiry=expiry,
                        mrp=float(product_data.get('mrp', 0)),
                        rate=float(rate)
                    )
                
                messages.success(request, f'Customer Challan {challan_no} created successfully! Inventory updated.')
                return redirect('view_customer_challan', challan_id=challan.customer_challan_id)
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR in customer challan creation: {error_details}")
            messages.error(request, f'Error: {str(e)}')
            return redirect('add_customer_challan')
    
    from core.models import ChallanSeries
    customers = CustomerMaster.objects.all().order_by('customer_name')
    products = ProductMaster.objects.all().order_by('product_name')
    invoice_series = ChallanSeries.objects.filter(is_active=True).order_by('series_name')
    
    context = {
        'customers': customers,
        'products': products,
        'invoice_series': invoice_series,
        'title': 'Add Customer Challan with Products'
    }
    return render(request, 'challan/customer_challan_form.html', context)

@login_required
def view_customer_challan(request, challan_id):
    """View for displaying customer challan details"""
    from core.models import CustomerChallan, CustomerChallanMaster
    from django.db.models import Sum
    
    challan = get_object_or_404(CustomerChallan, customer_challan_id=challan_id)
    challan_items = CustomerChallanMaster.objects.filter(customer_challan_id=challan).select_related('product_id')
    
    # Calculate grand total
    grand_total = challan_items.aggregate(total=Sum('sale_total_amount'))['total'] or 0
    final_total = grand_total + (challan.customer_transport_charges or 0)
    
    context = {
        'challan': challan,
        'challan_items': challan_items,
        'grand_total': grand_total,
        'final_total': final_total,
        'title': f'Challan {challan.customer_challan_no}'
    }
    return render(request, 'challan/customer_challan_detail.html', context)

@login_required
@require_POST
def delete_customer_challan(request, challan_id):
    """Delete customer challan"""
    from core.models import CustomerChallan
    from django.db import transaction
    
    try:
        with transaction.atomic():
            challan = get_object_or_404(CustomerChallan, customer_challan_id=challan_id)
            challan_no = challan.customer_challan_no
            challan.delete()
            return JsonResponse({'success': True, 'message': f'Challan {challan_no} deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_next_challan_number(request):
    """API endpoint to get next challan number preview"""
    from core.models import CustomerChallan
    from datetime import datetime
    
    try:
        series_name = request.GET.get('series_name', '')
        date_str = request.GET.get('date', '')
        
        if not series_name or not date_str:
            return JsonResponse({'success': False, 'error': 'Missing parameters'})
        
        # Parse date
        challan_date = datetime.strptime(date_str, '%Y-%m-%d')
        date_formatted = challan_date.strftime('%d%m%Y')
        
        # Generate prefix
        prefix = f'{series_name}{date_formatted}'
        
        # Find last challan with same prefix
        last_challan = CustomerChallan.objects.filter(
            customer_challan_no__startswith=prefix
        ).order_by('-customer_challan_no').first()
        
        if last_challan:
            last_counter = int(last_challan.customer_challan_no[-3:])
            new_counter = last_counter + 1
        else:
            new_counter = 1
        
        challan_number = f'{prefix}{new_counter:03d}'
        
        return JsonResponse({
            'success': True,
            'challan_number': challan_number
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def add_challan_series(request):
    """Add new challan series"""
    from core.models import ChallanSeries
    
    if request.method == 'POST':
        series_name = request.POST.get('series_name', '').strip().upper()
        
        if not series_name:
            return JsonResponse({'success': False, 'error': 'Series name is required'})
        
        if len(series_name) > 10:
            return JsonResponse({'success': False, 'error': 'Series name must be 10 characters or less'})
        
        try:
            if ChallanSeries.objects.filter(series_name=series_name).exists():
                return JsonResponse({'success': False, 'error': 'Series already exists'})
            
            series = ChallanSeries.objects.create(
                series_name=series_name,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'series_id': series.series_id,
                'series_name': series.series_name,
                'message': f'Series "{series_name}" added successfully!'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def challan_invoice_list(request):
    """View for challan invoice list"""
    from core.models import ChallanInvoice, SupplierMaster
    
    # Get actual challan invoices
    invoices = ChallanInvoice.objects.select_related('supplier').all().order_by('-invoice_date', '-challan_invoice_id')
    suppliers = SupplierMaster.objects.all().order_by('supplier_name')
    
    # Transform data for template
    invoice_data = []
    for invoice in invoices:
        invoice_data.append({
            'invoice_id': invoice.challan_invoice_id,
            'invoice_no': invoice.invoice_no,
            'invoice_date': invoice.invoice_date,
            'supplier_name': invoice.supplier.supplier_name,
            'total_amount': invoice.invoice_total,
            'paid_amount': invoice.invoice_paid,
            'balance_amount': invoice.balance_due
        })
    
    context = {
        'title': 'Challan Invoice List',
        'invoices': invoice_data,
        'suppliers': suppliers
    }
    return render(request, 'purchases/challan_invoice_list.html', context)

@login_required
@require_POST
def create_invoice_from_challans(request):
    """Create invoice from selected challans"""
    from core.models import Challan1, ChallanInvoice
    from django.db import transaction
    import json
    
    try:
        with transaction.atomic():
            invoice_no = request.POST.get('invoice_no')
            invoice_date = request.POST.get('invoice_date')
            challan_ids = json.loads(request.POST.get('challan_ids', '[]'))
            
            if not invoice_no or not challan_ids:
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            # Check if invoice number already exists
            if ChallanInvoice.objects.filter(invoice_no=invoice_no).exists():
                return JsonResponse({'success': False, 'error': 'Invoice number already exists'})
            
            # Get selected challans
            challans = Challan1.objects.filter(challan_id__in=challan_ids)
            if not challans.exists():
                return JsonResponse({'success': False, 'error': 'No valid challans found'})
            
            # Check if all challans are from same supplier
            suppliers = set(challan.supplier.supplierid for challan in challans)
            if len(suppliers) > 1:
                return JsonResponse({'success': False, 'error': 'All challans must be from the same supplier'})
            
            # Calculate total amount
            total_amount = sum(challan.challan_total for challan in challans)
            
            # Create challan invoice
            challan_invoice = ChallanInvoice.objects.create(
                invoice_no=invoice_no,
                invoice_date=invoice_date,
                supplier=challans.first().supplier,
                selected_challans=challan_ids,
                invoice_total=total_amount,
                invoice_paid=0.0
            )
            
            # Mark selected challans as invoiced
            challans.update(is_invoiced=True)
            
            return JsonResponse({
                'success': True,
                'message': f'Invoice {invoice_no} created successfully!',
                'invoice_id': challan_invoice.challan_invoice_id
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def challan_invoice_detail(request, invoice_id):
    """View for challan invoice detail"""
    from core.models import ChallanInvoice, Challan1
    
    invoice = get_object_or_404(ChallanInvoice, challan_invoice_id=invoice_id)
    
    # Get included challans
    challan_ids = invoice.selected_challans
    challans = Challan1.objects.filter(challan_id__in=challan_ids)
    
    # Calculate totals
    challans_total = sum(challan.challan_total for challan in challans)
    transport_total = sum(challan.transport_charges for challan in challans)
    
    # Calculate payment percentage
    payment_percentage = (invoice.invoice_paid / invoice.invoice_total * 100) if invoice.invoice_total > 0 else 0
    
    # Get payment history
    from core.models import ChallanInvoicePaid
    payments = ChallanInvoicePaid.objects.filter(challan_invoice=invoice).order_by('-payment_date')
    
    context = {
        'title': f'Challan Invoice {invoice.invoice_no}',
        'invoice': invoice,
        'challans': challans,
        'challans_total': challans_total,
        'transport_total': transport_total,
        'payment_percentage': payment_percentage,
        'payments': payments
    }
    return render(request, 'purchases/challan_invoice_detail.html', context)

@login_required
@require_POST
def add_challan_invoice_payment(request, invoice_id):
    """Add payment to challan invoice"""
    from core.models import ChallanInvoice, ChallanInvoicePaid
    from django.db import transaction
    
    try:
        with transaction.atomic():
            invoice = get_object_or_404(ChallanInvoice, challan_invoice_id=invoice_id)
            
            payment_date = request.POST.get('payment_date')
            payment_amount = float(request.POST.get('payment_amount', 0))
            payment_method = request.POST.get('payment_method', 'Cash')
            payment_reference = request.POST.get('payment_reference', 'NA')
            
            if payment_amount <= 0:
                return JsonResponse({'success': False, 'error': 'Payment amount must be greater than 0'})
            
            if payment_amount > invoice.balance_due:
                return JsonResponse({'success': False, 'error': 'Payment amount cannot exceed balance due'})
            
            # Create payment record
            ChallanInvoicePaid.objects.create(
                challan_invoice=invoice,
                payment_date=payment_date,
                payment_amount=payment_amount,
                payment_method=payment_method,
                payment_reference=payment_reference
            )
            
            # Update invoice paid amount
            invoice.invoice_paid += payment_amount
            invoice.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Payment of ₹{payment_amount} added successfully!'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def edit_challan_invoice_payment(request, payment_id):
    """Edit challan invoice payment"""
    from core.models import ChallanInvoicePaid
    from django.db import transaction
    
    try:
        with transaction.atomic():
            payment = get_object_or_404(ChallanInvoicePaid, payment_id=payment_id)
            old_amount = payment.payment_amount
            
            payment_date = request.POST.get('payment_date')
            payment_amount = float(request.POST.get('payment_amount', 0))
            payment_method = request.POST.get('payment_method', 'Cash')
            payment_reference = request.POST.get('payment_reference', 'NA')
            
            if payment_amount <= 0:
                return JsonResponse({'success': False, 'error': 'Payment amount must be greater than 0'})
            
            # Check if new amount is valid
            invoice = payment.challan_invoice
            available_balance = invoice.balance_due + old_amount  # Add back old amount
            
            if payment_amount > available_balance:
                return JsonResponse({'success': False, 'error': 'Payment amount cannot exceed available balance'})
            
            # Update payment record
            payment.payment_date = payment_date
            payment.payment_amount = payment_amount
            payment.payment_method = payment_method
            payment.payment_reference = payment_reference
            payment.save()
            
            # Update invoice paid amount
            invoice.invoice_paid = invoice.invoice_paid - old_amount + payment_amount
            invoice.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Payment updated successfully!'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def delete_challan_invoice_payment(request, payment_id):
    """Delete challan invoice payment"""
    from core.models import ChallanInvoicePaid
    from django.db import transaction
    
    try:
        with transaction.atomic():
            payment = get_object_or_404(ChallanInvoicePaid, payment_id=payment_id)
            payment_amount = payment.payment_amount
            invoice = payment.challan_invoice
            
            # Update invoice paid amount
            invoice.invoice_paid -= payment_amount
            invoice.save()
            
            # Delete payment record
            payment.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Payment of ₹{payment_amount} deleted successfully!'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_challan_invoice_payment(request, payment_id):
    """Get challan invoice payment details for editing"""
    from core.models import ChallanInvoicePaid
    
    try:
        payment = get_object_or_404(ChallanInvoicePaid, payment_id=payment_id)
        
        return JsonResponse({
            'success': True,
            'payment': {
                'payment_id': payment.payment_id,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'payment_amount': payment.payment_amount,
                'payment_method': payment.payment_method,
                'payment_reference': payment.payment_reference
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def create_customer_invoice_from_challans(request):
    """Create sales challan invoice from selected customer challans"""
    from core.models import CustomerChallan, SalesChallanInvoice, InvoiceSeries
    from django.db import transaction
    import json
    
    try:
        data = json.loads(request.body)
        series_id = data.get('series_id')
        invoice_date = data.get('invoice_date')
        challan_ids = data.get('challan_ids', [])
        
        if not series_id or not invoice_date or not challan_ids:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        with transaction.atomic():
            # Get invoice series and generate invoice number
            try:
                series = InvoiceSeries.objects.get(series_id=series_id, is_active=True)
                invoice_no = series.get_next_invoice_number()
            except InvoiceSeries.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid invoice series'})
            
            # Get selected challans
            challans = CustomerChallan.objects.filter(customer_challan_id__in=challan_ids, is_invoiced=False)
            if not challans.exists():
                return JsonResponse({'success': False, 'error': 'No valid challans found or already invoiced'})
            
            # Check if all challans are from same customer
            customers = set(challan.customer_name.customerid for challan in challans)
            if len(customers) > 1:
                return JsonResponse({'success': False, 'error': 'All challans must be from the same customer'})
            
            # Calculate total amount
            total_amount = sum(challan.challan_total for challan in challans)
            
            # Create sales challan invoice
            sales_challan_invoice = SalesChallanInvoice.objects.create(
                invoice_no=invoice_no,
                invoice_date=invoice_date,
                customer=challans.first().customer_name,
                invoice_series=series,
                selected_challans=challan_ids,
                invoice_total=total_amount,
                invoice_paid=0.0
            )
            
            # Mark selected challans as invoiced
            challans.update(is_invoiced=True)
            
            return JsonResponse({
                'success': True,
                'message': f'Sales Challan Invoice {invoice_no} created successfully!',
                'invoice_number': invoice_no,
                'invoice_id': sales_challan_invoice.sales_challan_invoice_id
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def sales_challan_invoice_list(request):
    """View for sales challan invoice list"""
    from core.models import SalesChallanInvoice, CustomerMaster
    from django.db.models import Q
    from django.core.paginator import Paginator
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Base queryset
    invoices = SalesChallanInvoice.objects.select_related('customer', 'invoice_series').all()
    
    # Apply filters
    if search_query:
        invoices = invoices.filter(
            Q(invoice_no__icontains=search_query) |
            Q(customer__customer_name__icontains=search_query)
        )
    
    if start_date:
        invoices = invoices.filter(invoice_date__gte=start_date)
    
    if end_date:
        invoices = invoices.filter(invoice_date__lte=end_date)
    
    invoices = invoices.order_by('-invoice_date', '-sales_challan_invoice_id')
    
    # Pagination
    paginator = Paginator(invoices, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Sales Challan Invoices',
        'invoices': page_obj,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'sales/sales_challan_invoice_list.html', context)

@login_required
def sales_challan_invoice_detail(request, invoice_id):
    """View for sales challan invoice detail"""
    from core.models import SalesChallanInvoice, CustomerChallan, SalesChallanInvoicePaid
    
    invoice = get_object_or_404(SalesChallanInvoice, sales_challan_invoice_id=invoice_id)
    
    # Get included challans
    challan_ids = invoice.selected_challans
    challans = CustomerChallan.objects.filter(customer_challan_id__in=challan_ids)
    
    # Get payment history
    payments = SalesChallanInvoicePaid.objects.filter(sales_challan_invoice=invoice).order_by('-payment_date')
    
    # Calculate payment percentage
    payment_percentage = (invoice.invoice_paid / invoice.invoice_total * 100) if invoice.invoice_total > 0 else 0
    
    context = {
        'title': f'Sales Challan Invoice {invoice.invoice_no}',
        'invoice': invoice,
        'challans': challans,
        'payments': payments,
        'payment_percentage': round(payment_percentage, 1)
    }
    return render(request, 'sales/sales_challan_invoice_detail.html', context)

@login_required
@require_POST
def add_sales_challan_invoice_payment(request, invoice_id):
    """Add payment to sales challan invoice"""
    from core.models import SalesChallanInvoice, SalesChallanInvoicePaid
    from django.db import transaction
    
    try:
        with transaction.atomic():
            invoice = get_object_or_404(SalesChallanInvoice, sales_challan_invoice_id=invoice_id)
            
            payment_date = request.POST.get('payment_date')
            payment_amount = float(request.POST.get('payment_amount', 0))
            payment_method = request.POST.get('payment_method', 'Cash')
            payment_reference = request.POST.get('payment_reference', 'NA')
            
            if payment_amount <= 0:
                return JsonResponse({'success': False, 'error': 'Payment amount must be greater than 0'})
            
            if payment_amount > invoice.balance_due:
                return JsonResponse({'success': False, 'error': 'Payment amount cannot exceed balance due'})
            
            # Create payment record
            SalesChallanInvoicePaid.objects.create(
                sales_challan_invoice=invoice,
                payment_date=payment_date,
                payment_amount=payment_amount,
                payment_method=payment_method,
                payment_reference=payment_reference
            )
            
            # Update invoice paid amount
            invoice.invoice_paid += payment_amount
            invoice.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Payment of ₹{payment_amount} added successfully!'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def edit_sales_challan_invoice_payment(request, payment_id):
    """Edit sales challan invoice payment"""
    from core.models import SalesChallanInvoicePaid
    from django.db import transaction
    
    try:
        with transaction.atomic():
            payment = get_object_or_404(SalesChallanInvoicePaid, payment_id=payment_id)
            old_amount = payment.payment_amount
            
            payment_date = request.POST.get('payment_date')
            payment_amount = float(request.POST.get('payment_amount', 0))
            payment_method = request.POST.get('payment_method', 'Cash')
            payment_reference = request.POST.get('payment_reference', 'NA')
            
            if payment_amount <= 0:
                return JsonResponse({'success': False, 'error': 'Payment amount must be greater than 0'})
            
            # Check if new amount is valid
            invoice = payment.sales_challan_invoice
            available_balance = invoice.balance_due + old_amount  # Add back old amount
            
            if payment_amount > available_balance:
                return JsonResponse({'success': False, 'error': 'Payment amount cannot exceed available balance'})
            
            # Update payment record
            payment.payment_date = payment_date
            payment.payment_amount = payment_amount
            payment.payment_method = payment_method
            payment.payment_reference = payment_reference
            payment.save()
            
            # Update invoice paid amount
            invoice.invoice_paid = invoice.invoice_paid - old_amount + payment_amount
            invoice.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Payment updated successfully!'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def delete_sales_challan_invoice_payment(request, payment_id):
    """Delete sales challan invoice payment"""
    from core.models import SalesChallanInvoicePaid
    from django.db import transaction
    
    try:
        with transaction.atomic():
            payment = get_object_or_404(SalesChallanInvoicePaid, payment_id=payment_id)
            payment_amount = payment.payment_amount
            invoice = payment.sales_challan_invoice
            
            # Update invoice paid amount
            invoice.invoice_paid -= payment_amount
            invoice.save()
            
            # Delete payment record
            payment.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Payment of ₹{payment_amount} deleted successfully!'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_sales_challan_invoice_payment(request, payment_id):
    """Get sales challan invoice payment details for editing"""
    from core.models import SalesChallanInvoicePaid
    
    try:
        payment = get_object_or_404(SalesChallanInvoicePaid, payment_id=payment_id)
        
        return JsonResponse({
            'success': True,
            'payment': {
                'payment_id': payment.payment_id,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'payment_amount': payment.payment_amount,
                'payment_method': payment.payment_method,
                'payment_reference': payment.payment_reference
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def delete_sales_challan_invoice(request, invoice_id):
    """Delete sales challan invoice"""
    from core.models import SalesChallanInvoice, CustomerChallan
    from django.db import transaction
    
    try:
        with transaction.atomic():
            invoice = get_object_or_404(SalesChallanInvoice, sales_challan_invoice_id=invoice_id)
            invoice_no = invoice.invoice_no
            
            # Mark associated challans as not invoiced
            challan_ids = invoice.selected_challans
            CustomerChallan.objects.filter(customer_challan_id__in=challan_ids).update(is_invoiced=False)
            
            # Delete the invoice (payments will be deleted due to CASCADE)
            invoice.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Sales Challan Invoice {invoice_no} deleted successfully!',
                'redirect_url': '/challan/customer/'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
@login_required
@require_POST
def delete_challan_invoice(request, invoice_id):
    """Delete challan invoice"""
    from core.models import ChallanInvoice, Challan1
    from django.db import transaction
    
    try:
        with transaction.atomic():
            invoice = get_object_or_404(ChallanInvoice, challan_invoice_id=invoice_id)
            invoice_no = invoice.invoice_no
            
            # Mark associated challans as not invoiced
            challan_ids = invoice.selected_challans
            Challan1.objects.filter(challan_id__in=challan_ids).update(is_invoiced=False)
            
            # Delete the invoice (payments will be deleted due to CASCADE)
            invoice.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Challan Invoice {invoice_no} deleted successfully!',
                'redirect_url': '/challan/supplier/'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})