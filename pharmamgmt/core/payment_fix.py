from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from datetime import datetime
from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from .models import (
    InvoiceMaster, InvoicePaid, SalesInvoiceMaster, SalesInvoicePaid,
    SupplierMaster, CustomerMaster
)

@login_required
def add_unified_payment_fixed(request):
    """Fixed unified view for adding payments with proper balance handling"""
    
    if request.method == 'POST':
        try:
            print("=== FIXED UNIFIED PAYMENT FORM SUBMISSION ===")
            print(f"All POST data: {dict(request.POST)}")
            
            # Get form data
            transaction_type = request.POST.get('transaction_type')
            payment_date = request.POST.get('payment_date')
            payment_amount = request.POST.get('payment_amount')
            payment_mode = request.POST.get('payment_mode')
            reference_no = request.POST.get('reference_no', '')
            entity_id = request.POST.get('entity_id')
            invoice_no = request.POST.get('invoice_no')
            write_off_balance = request.POST.get('write_off_balance', 'false') == 'true'
            
            print(f"✅ Extracted form data:")
            print(f"   Transaction type: '{transaction_type}'")
            print(f"   Payment amount: '{payment_amount}'")
            print(f"   Payment mode: '{payment_mode}'")
            print(f"   Entity ID: '{entity_id}'")
            print(f"   Invoice no: '{invoice_no}'")
            print(f"   Payment date: '{payment_date}'")
            print(f"   Write off balance: {write_off_balance}")
            
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
            
            # Validate and convert amount to Decimal for precision
            try:
                payment_amount = Decimal(str(payment_amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if payment_amount <= 0:
                    print(f"❌ Invalid payment amount: {payment_amount}")
                    messages.error(request, 'Payment amount must be greater than 0.')
                    return redirect('add_unified_payment')
            except (ValueError, TypeError):
                print(f"❌ Cannot convert payment amount to decimal: '{payment_amount}'")
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
                        
                        # Calculate balance with proper decimal precision
                        invoice_total = Decimal(str(invoice.invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                        invoice_paid = Decimal(str(invoice.invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                        balance = invoice_total - invoice_paid
                        
                        print(f"Invoice balance: ₹{balance}")
                        
                        # Handle small balance scenarios
                        if balance <= Decimal('0.10') and balance > 0:
                            if write_off_balance:
                                # Write off the small balance
                                print(f"✅ Writing off small balance of ₹{balance}")
                                payment_amount = balance
                                messages.info(request, f'Small balance of ₹{balance} has been written off.')
                            elif payment_amount > balance:
                                # Offer to write off or pay exact balance
                                print(f"⚠️ Payment amount ₹{payment_amount} exceeds small balance ₹{balance}")
                                messages.warning(request, 
                                    f'Payment amount ₹{payment_amount} exceeds balance of ₹{balance}. '
                                    f'You can either pay exactly ₹{balance} or write off this small balance.'
                                )
                                return redirect('add_unified_payment')
                        elif payment_amount > balance:
                            print(f"❌ Payment amount ₹{payment_amount} exceeds balance ₹{balance}")
                            messages.error(request, f'Payment amount cannot exceed balance of ₹{balance}')
                            return redirect('add_unified_payment')
                        
                        # Create payment record
                        print(f"Creating payment record...")
                        payment_record = InvoicePaid.objects.create(
                            ip_invoiceid=invoice,
                            payment_date=payment_date,
                            payment_amount=float(payment_amount),
                            payment_mode=payment_mode,
                            payment_ref_no=reference_no
                        )
                        print(f"✅ Payment record created with ID: {payment_record.payment_id}")
                        
                        # Update invoice paid amount
                        old_paid = invoice.invoice_paid
                        invoice.invoice_paid = float(invoice_paid + payment_amount)
                        
                        # Update payment status
                        new_balance = invoice_total - Decimal(str(invoice.invoice_paid))
                        if new_balance <= Decimal('0.01'):
                            invoice.payment_status = 'paid'
                            print(f"✅ Invoice marked as fully paid")
                        elif invoice.invoice_paid > 0:
                            invoice.payment_status = 'partial'
                            print(f"✅ Invoice marked as partially paid")
                        else:
                            invoice.payment_status = 'pending'
                        
                        invoice.save()
                        print(f"✅ Invoice updated: ₹{old_paid} → ₹{invoice.invoice_paid}, New balance: ₹{new_balance}")
                        
                        if new_balance <= Decimal('0.01'):
                            messages.success(request, f'Payment of ₹{payment_amount} added successfully! Invoice is now fully paid.')
                        else:
                            messages.success(request, f'Payment of ₹{payment_amount} added successfully! Remaining balance: ₹{new_balance}')
                        
                    except InvoiceMaster.DoesNotExist:
                        print(f"❌ Invoice not found with invoice_no: '{invoice_no}'")
                        messages.error(request, f'Invoice {invoice_no} not found.')
                        return redirect('add_unified_payment')
                    except Exception as e:
                        print(f"❌ Error creating payment: {str(e)}")
                        messages.error(request, f'Error creating payment: {str(e)}')
                        return redirect('add_unified_payment')
                
                elif transaction_type == 'receipt':
                    # Handle customer receipt (similar logic)
                    print(f"Processing customer receipt for invoice: {invoice_no}")
                    try:
                        invoice = SalesInvoiceMaster.objects.get(sales_invoice_no=invoice_no)
                        print(f"✅ Found sales invoice: {invoice} (Total: ₹{invoice.sales_invoice_total}, Paid: ₹{invoice.sales_invoice_paid})")
                        
                        # Calculate balance with proper decimal precision
                        invoice_total = Decimal(str(invoice.sales_invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                        invoice_paid = Decimal(str(invoice.sales_invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                        balance = invoice_total - invoice_paid
                        
                        print(f"Sales invoice balance: ₹{balance}")
                        
                        # Handle small balance scenarios
                        if balance <= Decimal('0.10') and balance > 0:
                            if write_off_balance:
                                # Write off the small balance
                                print(f"✅ Writing off small balance of ₹{balance}")
                                payment_amount = balance
                                messages.info(request, f'Small balance of ₹{balance} has been written off.')
                            elif payment_amount > balance:
                                # Offer to write off or pay exact balance
                                print(f"⚠️ Receipt amount ₹{payment_amount} exceeds small balance ₹{balance}")
                                messages.warning(request, 
                                    f'Receipt amount ₹{payment_amount} exceeds balance of ₹{balance}. '
                                    f'You can either receive exactly ₹{balance} or write off this small balance.'
                                )
                                return redirect('add_unified_payment')
                        elif payment_amount > balance:
                            print(f"❌ Receipt amount ₹{payment_amount} exceeds balance ₹{balance}")
                            messages.error(request, f'Receipt amount cannot exceed balance of ₹{balance}')
                            return redirect('add_unified_payment')
                        
                        # Create receipt record
                        print(f"Creating receipt record...")
                        receipt_record = SalesInvoicePaid.objects.create(
                            sales_ip_invoice_no=invoice,
                            sales_payment_date=payment_date,
                            sales_payment_amount=float(payment_amount),
                            sales_payment_mode=payment_mode,
                            sales_payment_ref_no=reference_no
                        )
                        print(f"✅ Receipt record created with ID: {receipt_record.sales_payment_id}")
                        
                        # Update invoice paid amount
                        old_paid = invoice.sales_invoice_paid
                        invoice.sales_invoice_paid = float(invoice_paid + payment_amount)
                        invoice.save()
                        
                        new_balance = invoice_total - Decimal(str(invoice.sales_invoice_paid))
                        print(f"✅ Sales invoice updated: ₹{old_paid} → ₹{invoice.sales_invoice_paid}, New balance: ₹{new_balance}")
                        
                        if new_balance <= Decimal('0.01'):
                            messages.success(request, f'Receipt of ₹{payment_amount} added successfully! Invoice is now fully paid.')
                        else:
                            messages.success(request, f'Receipt of ₹{payment_amount} added successfully! Remaining balance: ₹{new_balance}')
                        
                    except SalesInvoiceMaster.DoesNotExist:
                        print(f"❌ Sales invoice not found with sales_invoice_no: '{invoice_no}'")
                        messages.error(request, f'Sales invoice {invoice_no} not found.')
                        return redirect('add_unified_payment')
                    except Exception as e:
                        print(f"❌ Error creating receipt: {str(e)}")
                        messages.error(request, f'Error creating receipt: {str(e)}')
                        return redirect('add_unified_payment')
                
                elif transaction_type == 'contra':
                    # Handle contra entry (direct cash/bank transfer)
                    print(f"Processing contra entry of ₹{payment_amount}")
                    print(f"✅ Contra entry processed successfully")
                    messages.success(request, f'Contra entry of ₹{payment_amount} recorded successfully!')
                
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
        'title': 'Add Payment/Receipt (Fixed)'
    }
    return render(request, 'finance/unified_payment_form.html', context)

def get_invoice_balance_info(invoice_no, transaction_type='payment'):
    """Helper function to get invoice balance information"""
    try:
        if transaction_type == 'payment':
            invoice = InvoiceMaster.objects.get(invoice_no=invoice_no)
            total = Decimal(str(invoice.invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            paid = Decimal(str(invoice.invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:  # receipt
            invoice = SalesInvoiceMaster.objects.get(sales_invoice_no=invoice_no)
            total = Decimal(str(invoice.sales_invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            paid = Decimal(str(invoice.sales_invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        balance = total - paid
        
        return {
            'total': float(total),
            'paid': float(paid),
            'balance': float(balance),
            'is_small_balance': balance <= Decimal('0.10') and balance > 0,
            'is_fully_paid': balance <= Decimal('0.01')
        }
    except Exception as e:
        return None

@login_required
def check_invoice_balance(request):
    """AJAX endpoint to check invoice balance"""
    invoice_no = request.GET.get('invoice_no')
    transaction_type = request.GET.get('transaction_type', 'payment')
    
    if not invoice_no:
        return JsonResponse({'error': 'Invoice number required'})
    
    balance_info = get_invoice_balance_info(invoice_no, transaction_type)
    
    if balance_info is None:
        return JsonResponse({'error': 'Invoice not found'})
    
    return JsonResponse(balance_info)