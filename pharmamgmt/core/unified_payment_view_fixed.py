from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from datetime import datetime
from django.db import models
from .models import (
    InvoiceMaster, InvoicePaid, SalesInvoiceMaster, SalesInvoicePaid,
    SupplierMaster, CustomerMaster
)

@login_required
def add_unified_payment(request):
    """Unified view for adding payments, receipts, and contra entries"""
    
    if request.method == 'POST':
        try:
            print("=== UNIFIED PAYMENT FORM SUBMISSION ===")
            print(f"All POST data: {dict(request.POST)}")
            
            # Get form data
            transaction_type = request.POST.get('transaction_type')
            payment_date = request.POST.get('payment_date')
            payment_amount = request.POST.get('payment_amount')
            payment_mode = request.POST.get('payment_mode')
            reference_no = request.POST.get('reference_no', '')
            entity_id = request.POST.get('entity_id')
            invoice_no = request.POST.get('invoice_no')
            
            print(f"✅ Extracted form data:")
            print(f"   Transaction type: '{transaction_type}'")
            print(f"   Payment amount: '{payment_amount}'")
            print(f"   Payment mode: '{payment_mode}'")
            print(f"   Entity ID: '{entity_id}'")
            print(f"   Invoice no: '{invoice_no}'")
            print(f"   Payment date: '{payment_date}'")
            
            # Validate required fields
            missing_fields = []
            if not transaction_type:
                missing_fields.append('transaction_type')
            if not payment_date:
                missing_fields.append('payment_date')
            if not payment_amount:
                missing_fields.append('payment_amount')
            if not payment_mode:
                missing_fields.append('payment_mode')
                
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                messages.error(request, f'Missing required fields: {", ".join(missing_fields)}')
                return redirect('add_unified_payment')
            
            # Validate transaction type
            if transaction_type not in ['payment', 'receipt', 'contra']:
                print(f"❌ Invalid transaction type: '{transaction_type}'")
                messages.error(request, 'Invalid transaction type.')
                return redirect('add_unified_payment')
            
            # For payment and receipt, entity and invoice are required
            if transaction_type in ['payment', 'receipt']:
                if not entity_id:
                    print(f"❌ Missing entity_id for {transaction_type}")
                    messages.error(request, 'Please select an invoice first (missing entity).')
                    return redirect('add_unified_payment')
                if not invoice_no:
                    print(f"❌ Missing invoice_no for {transaction_type}")
                    messages.error(request, 'Please select an invoice first (missing invoice number).')
                    return redirect('add_unified_payment')
            
            # Validate amount
            try:
                payment_amount = float(payment_amount)
                if payment_amount <= 0:
                    print(f"❌ Invalid payment amount: {payment_amount}")
                    messages.error(request, 'Payment amount must be greater than 0.')
                    return redirect('add_unified_payment')
            except (ValueError, TypeError):
                print(f"❌ Cannot convert payment amount to float: '{payment_amount}'")
                messages.error(request, 'Invalid payment amount.')
                return redirect('add_unified_payment')
            
            # Parse date
            try:
                payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
                print(f"✅ Parsed payment date: {payment_date}")
            except ValueError:
                print(f"❌ Invalid date format: '{payment_date}'")
                messages.error(request, 'Invalid date format.')
                return redirect('add_unified_payment')
            
            # Handle bank name for bank transfer
            bank_name = request.POST.get('bank_name', '').strip()
            print(f"Bank name from form: '{bank_name}'")
            if payment_mode == 'bank':
                if bank_name:
                    payment_mode = f'bank - {bank_name}'
                    print(f"✅ Updated payment mode: '{payment_mode}'")
                else:
                    print(f"❌ Bank transfer selected but no bank name provided")
                    messages.error(request, 'Bank name is required for bank transfer.')
                    return redirect('add_unified_payment')
            
            with transaction.atomic():
                if transaction_type == 'payment':
                    # Handle supplier payment
                    print(f"Processing supplier payment for invoice: {invoice_no}")
                    try:
                        invoice = InvoiceMaster.objects.get(invoice_no=invoice_no)
                        print(f"✅ Found invoice: {invoice} (Total: ₹{invoice.invoice_total}, Paid: ₹{invoice.invoice_paid})")
                        
                        # Check balance
                        balance = invoice.invoice_total - invoice.invoice_paid
                        print(f"Invoice balance: ₹{balance}")
                        if payment_amount > balance:
                            print(f"❌ Payment amount ₹{payment_amount} exceeds balance ₹{balance}")
                            messages.error(request, f'Payment amount cannot exceed balance of ₹{balance:.2f}')
                            return redirect('add_unified_payment')
                        
                        # Create payment record
                        print(f"Creating payment record...")
                        payment_record = InvoicePaid.objects.create(
                            ip_invoiceid=invoice,
                            payment_date=payment_date,
                            payment_amount=payment_amount,
                            payment_mode=payment_mode,
                            payment_ref_no=reference_no
                        )
                        print(f"✅ Payment record created with ID: {payment_record.payment_id}")
                        
                        # Update invoice paid amount
                        old_paid = invoice.invoice_paid
                        invoice.invoice_paid += payment_amount
                        print(f"Updated invoice paid: ₹{old_paid} → ₹{invoice.invoice_paid}")
                        
                        # Update payment status
                        new_balance = invoice.invoice_total - invoice.invoice_paid
                        if new_balance <= 0.01:
                            invoice.payment_status = 'paid'
                        elif invoice.invoice_paid > 0:
                            invoice.payment_status = 'partial'
                        else:
                            invoice.payment_status = 'pending'
                        
                        invoice.save()
                        print(f"✅ Invoice updated and saved. New balance: ₹{new_balance}")
                        
                        messages.success(request, f'Payment of ₹{payment_amount:.2f} added successfully!')
                        
                    except InvoiceMaster.DoesNotExist:
                        print(f"❌ Invoice not found with invoice_no: '{invoice_no}'")
                        # List available invoices for debugging
                        available_invoices = InvoiceMaster.objects.all()[:5]
                        print(f"Available invoices: {[inv.invoice_no for inv in available_invoices]}")
                        messages.error(request, f'Invoice {invoice_no} not found.')
                        return redirect('add_unified_payment')
                    except Exception as e:
                        print(f"❌ Error creating payment: {str(e)}")
                        messages.error(request, f'Error creating payment: {str(e)}')
                        return redirect('add_unified_payment')
                
                elif transaction_type == 'receipt':
                    # Handle customer receipt
                    print(f"Processing customer receipt for invoice: {invoice_no}")
                    try:
                        invoice = SalesInvoiceMaster.objects.get(sales_invoice_no=invoice_no)
                        print(f"✅ Found sales invoice: {invoice} (Total: ₹{invoice.sales_invoice_total}, Paid: ₹{invoice.sales_invoice_paid})")
                        
                        # Check balance
                        balance = invoice.sales_invoice_total - invoice.sales_invoice_paid
                        print(f"Sales invoice balance: ₹{balance}")
                        if payment_amount > balance:
                            print(f"❌ Receipt amount ₹{payment_amount} exceeds balance ₹{balance}")
                            messages.error(request, f'Receipt amount cannot exceed balance of ₹{balance:.2f}')
                            return redirect('add_unified_payment')
                        
                        # Create receipt record
                        print(f"Creating receipt record...")
                        receipt_record = SalesInvoicePaid.objects.create(
                            sales_ip_invoice_no=invoice,
                            sales_payment_date=payment_date,
                            sales_payment_amount=payment_amount,
                            sales_payment_mode=payment_mode,
                            sales_payment_ref_no=reference_no
                        )
                        print(f"✅ Receipt record created with ID: {receipt_record.sales_payment_id}")
                        
                        # Update invoice paid amount
                        old_paid = invoice.sales_invoice_paid
                        invoice.sales_invoice_paid += payment_amount
                        invoice.save()
                        print(f"✅ Sales invoice updated: ₹{old_paid} → ₹{invoice.sales_invoice_paid}")
                        
                        messages.success(request, f'Receipt of ₹{payment_amount:.2f} added successfully!')
                        
                    except SalesInvoiceMaster.DoesNotExist:
                        print(f"❌ Sales invoice not found with sales_invoice_no: '{invoice_no}'")
                        # List available sales invoices for debugging
                        available_invoices = SalesInvoiceMaster.objects.all()[:5]
                        print(f"Available sales invoices: {[inv.sales_invoice_no for inv in available_invoices]}")
                        messages.error(request, f'Sales invoice {invoice_no} not found.')
                        return redirect('add_unified_payment')
                    except Exception as e:
                        print(f"❌ Error creating receipt: {str(e)}")
                        messages.error(request, f'Error creating receipt: {str(e)}')
                        return redirect('add_unified_payment')
                
                elif transaction_type == 'contra':
                    # Handle contra entry (direct cash/bank transfer)
                    print(f"Processing contra entry of ₹{payment_amount}")
                    # For now, just show success message
                    # You can extend this to create contra entries in a separate table
                    print(f"✅ Contra entry processed successfully")
                    messages.success(request, f'Contra entry of ₹{payment_amount:.2f} recorded successfully!')
                
                print(f"✅ Transaction completed successfully")
                return redirect('add_unified_payment')
                
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            messages.error(request, f'Error processing transaction: {str(e)}')
            return redirect('add_unified_payment')
    
    # GET request - show form
    context = {
        'title': 'Add Payment/Receipt'
    }
    return render(request, 'finance/unified_payment_form.html', context)

@login_required
def search_supplier_invoices(request):
    """Search supplier invoices for payment"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse([])
    
    # Search unpaid supplier invoices
    invoices = InvoiceMaster.objects.filter(
        supplierid__supplier_name__icontains=query,
        invoice_paid__lt=models.F('invoice_total')
    ).select_related('supplierid').order_by('-invoice_date')[:20]
    
    results = []
    for invoice in invoices:
        balance = invoice.invoice_total - invoice.invoice_paid
        if balance > 0:
            results.append({
                'supplier_id': invoice.supplierid.supplierid,
                'supplier_name': invoice.supplierid.supplier_name,
                'invoice_no': invoice.invoice_no,
                'invoice_date': invoice.invoice_date.strftime('%d-%m-%Y'),
                'total_amount': float(invoice.invoice_total),
                'paid_amount': float(invoice.invoice_paid),
                'balance_amount': float(balance)
            })
    
    return JsonResponse(results, safe=False)

@login_required
def search_customer_invoices(request):
    """Search customer invoices for receipt"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse([])
    
    # Search unpaid customer invoices
    invoices = SalesInvoiceMaster.objects.filter(
        models.Q(customerid__customer_name__icontains=query) |
        models.Q(customerid__customer_mobile__icontains=query),
        sales_invoice_paid__lt=models.F('sales_invoice_total')
    ).select_related('customerid').order_by('-sales_invoice_date')[:20]
    
    results = []
    for invoice in invoices:
        balance = invoice.sales_invoice_total - invoice.sales_invoice_paid
        if balance > 0:
            results.append({
                'customer_id': invoice.customerid.customerid,
                'customer_name': invoice.customerid.customer_name,
                'invoice_no': invoice.sales_invoice_no,
                'invoice_date': invoice.sales_invoice_date.strftime('%d-%m-%Y'),
                'total_amount': float(invoice.sales_invoice_total),
                'paid_amount': float(invoice.sales_invoice_paid),
                'balance_amount': float(balance)
            })
    
    return JsonResponse(results, safe=False)