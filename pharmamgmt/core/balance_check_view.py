from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal, ROUND_HALF_UP
from .models import InvoiceMaster, SalesInvoiceMaster

@login_required
def check_invoice_balance(request):
    """AJAX endpoint to check invoice balance for payment forms"""
    invoice_no = request.GET.get('invoice_no')
    transaction_type = request.GET.get('transaction_type', 'payment')
    
    if not invoice_no:
        return JsonResponse({'error': 'Invoice number required'})
    
    try:
        if transaction_type == 'payment':
            # Supplier invoice
            invoice = InvoiceMaster.objects.get(invoice_no=invoice_no)
            total = Decimal(str(invoice.invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            paid = Decimal(str(invoice.invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            # Customer invoice (receipt)
            invoice = SalesInvoiceMaster.objects.get(sales_invoice_no=invoice_no)
            total = Decimal(str(invoice.sales_invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            paid = Decimal(str(invoice.sales_invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        balance = total - paid
        
        return JsonResponse({
            'total': float(total),
            'paid': float(paid),
            'balance': float(balance),
            'is_small_balance': balance <= Decimal('0.10') and balance > 0,
            'is_fully_paid': balance <= Decimal('0.01'),
            'payment_status': getattr(invoice, 'payment_status', 'unknown')
        })
        
    except (InvoiceMaster.DoesNotExist, SalesInvoiceMaster.DoesNotExist):
        return JsonResponse({'error': f'Invoice {invoice_no} not found'})
    except Exception as e:
        return JsonResponse({'error': f'Error checking balance: {str(e)}'})

@login_required 
def fix_small_balance(request):
    """AJAX endpoint to fix a specific invoice's small balance"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'})
    
    invoice_no = request.POST.get('invoice_no')
    transaction_type = request.POST.get('transaction_type', 'payment')
    
    if not invoice_no:
        return JsonResponse({'error': 'Invoice number required'})
    
    try:
        if transaction_type == 'payment':
            # Supplier invoice
            invoice = InvoiceMaster.objects.get(invoice_no=invoice_no)
            total = Decimal(str(invoice.invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            paid = Decimal(str(invoice.invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            balance = total - paid
            
            if 0 < balance <= Decimal('0.10'):
                invoice.invoice_paid = float(total)
                invoice.payment_status = 'paid'
                invoice.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Small balance of ₹{balance} written off for invoice {invoice_no}',
                    'balance_written_off': float(balance)
                })
            else:
                return JsonResponse({'error': 'Invoice does not have a small balance to write off'})
                
        else:
            # Customer invoice (receipt)
            invoice = SalesInvoiceMaster.objects.get(sales_invoice_no=invoice_no)
            total = Decimal(str(invoice.sales_invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            paid = Decimal(str(invoice.sales_invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            balance = total - paid
            
            if 0 < balance <= Decimal('0.10'):
                invoice.sales_invoice_paid = float(total)
                invoice.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Small balance of ₹{balance} written off for sales invoice {invoice_no}',
                    'balance_written_off': float(balance)
                })
            else:
                return JsonResponse({'error': 'Invoice does not have a small balance to write off'})
        
    except (InvoiceMaster.DoesNotExist, SalesInvoiceMaster.DoesNotExist):
        return JsonResponse({'error': f'Invoice {invoice_no} not found'})
    except Exception as e:
        return JsonResponse({'error': f'Error fixing balance: {str(e)}'})