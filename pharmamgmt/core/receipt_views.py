from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
import json

from .models import SalesInvoiceMaster, SalesInvoicePaid, CustomerMaster

@login_required
def add_receipt(request):
    """Add receipt form similar to payment form with customer/invoice search"""
    
    if request.method == 'POST':
        # Handle AJAX request for adding receipt
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Get form data
                customer_id = request.POST.get('customer_id')
                invoice_no = request.POST.get('invoice_no')
                receipt_date = request.POST.get('receipt_date')
                receipt_amount_str = request.POST.get('receipt_amount')
                payment_mode = request.POST.get('payment_mode')
                bank_name = request.POST.get('bank_name', '')
                reference_no = request.POST.get('reference_no', '')
                
                # Validate required fields
                if not all([customer_id, invoice_no, receipt_date, receipt_amount_str, payment_mode]):
                    return JsonResponse({
                        'success': False,
                        'error': 'All required fields must be filled'
                    })
                
                # Validate amount
                try:
                    receipt_amount = float(receipt_amount_str)
                    if receipt_amount <= 0:
                        return JsonResponse({
                            'success': False,
                            'error': 'Receipt amount must be greater than 0'
                        })
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid receipt amount'
                    })
                
                # Get invoice
                try:
                    invoice = SalesInvoiceMaster.objects.get(sales_invoice_no=invoice_no)
                except SalesInvoiceMaster.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invoice not found'
                    })
                
                # Check if amount exceeds balance
                balance = invoice.sales_invoice_total - invoice.sales_invoice_paid
                if receipt_amount > balance + 0.01:  # Small tolerance for floating point
                    return JsonResponse({
                        'success': False,
                        'error': f'Receipt amount cannot exceed balance due of ₹{balance:.2f}'
                    })
                
                # Parse date
                try:
                    parsed_date = datetime.strptime(receipt_date, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid date format'
                    })
                
                # Handle bank name for bank transfer
                final_payment_mode = payment_mode
                if payment_mode == 'bank_transfer' and bank_name:
                    final_payment_mode = f'Bank Transfer - {bank_name}'
                
                # Create receipt record using SalesInvoicePaid
                receipt = SalesInvoicePaid.objects.create(
                    sales_ip_invoice_no=invoice,
                    sales_payment_date=parsed_date,
                    sales_payment_amount=receipt_amount,
                    sales_payment_mode=final_payment_mode,
                    sales_payment_ref_no=reference_no
                )
                
                # Update invoice paid amount
                invoice.sales_invoice_paid += receipt_amount
                invoice.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Receipt of ₹{receipt_amount:.2f} added successfully!',
                    'receipt_id': receipt.sales_payment_id
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Server error: {str(e)}'
                })
    
    # Get all customers for dropdown
    customers = CustomerMaster.objects.all().order_by('customer_name')
    
    context = {
        'customers': customers,
        'title': 'Add Receipt'
    }
    return render(request, 'receipts/receipt_form.html', context)

@login_required
def get_customer_invoices_api(request):
    """API to get invoices for selected customer"""
    customer_id = request.GET.get('customer_id')
    
    if not customer_id:
        return JsonResponse({'success': False, 'error': 'Customer ID is required'})
    
    try:
        # Get unpaid or partially paid invoices for the customer
        invoices = SalesInvoiceMaster.objects.filter(
            customerid=customer_id
        ).order_by('-sales_invoice_date')
        
        invoice_list = []
        for invoice in invoices:
            balance = invoice.sales_invoice_total - invoice.sales_invoice_paid
            if balance > 0.01:  # Only show invoices with outstanding balance
                invoice_list.append({
                    'invoice_no': invoice.sales_invoice_no,
                    'invoice_date': invoice.sales_invoice_date.strftime('%Y-%m-%d'),
                    'total_amount': float(invoice.sales_invoice_total),
                    'paid_amount': float(invoice.sales_invoice_paid),
                    'balance_amount': float(balance)
                })
        
        return JsonResponse({
            'success': True,
            'invoices': invoice_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def search_customers_api(request):
    """API to search customers by name or mobile"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'success': False, 'error': 'Query too short'})
    
    try:
        customers = CustomerMaster.objects.filter(
            Q(customer_name__icontains=query) |
            Q(customer_mobile__icontains=query)
        ).order_by('customer_name')[:10]
        
        customer_list = []
        for customer in customers:
            customer_list.append({
                'customer_id': customer.customerid,
                'customer_name': customer.customer_name,
                'customer_mobile': customer.customer_mobile,
                'customer_type': customer.customer_type
            })
        
        return JsonResponse({
            'success': True,
            'customers': customer_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def receipt_list(request):
    """List all receipts"""
    receipts = SalesInvoicePaid.objects.all().order_by('-sales_payment_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        receipts = receipts.filter(
            Q(sales_ip_invoice_no__sales_invoice_no__icontains=search_query) |
            Q(sales_ip_invoice_no__customerid__customer_name__icontains=search_query) |
            Q(sales_payment_ref_no__icontains=search_query)
        )
    
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            receipts = receipts.filter(sales_payment_date__range=[start_date, end_date])
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    context = {
        'receipts': receipts,
        'search_query': search_query,
        'start_date': start_date if 'start_date' in locals() else '',
        'end_date': end_date if 'end_date' in locals() else '',
        'title': 'Receipt List'
    }
    return render(request, 'receipts/receipt_list.html', context)