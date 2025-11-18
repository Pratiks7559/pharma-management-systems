from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import (
    CustomerMaster, SupplierMaster, SalesInvoiceMaster, SalesMaster,
    SalesInvoicePaid, ReturnSalesInvoiceMaster, InvoiceMaster, InvoicePaid,
    ReturnInvoiceMaster, Pharmacy_Details
)

@login_required
def customer_ledger(request, customer_id=None):
    customers = CustomerMaster.objects.all().order_by('customer_name')
    
    if not customer_id:
        context = {'customers': customers, 'title': 'Select Customer'}
        return render(request, 'ledger/customer_select.html', context)
    
    customer = get_object_or_404(CustomerMaster, customerid=customer_id)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    transactions = []
    
    # Sales Invoices (Debit)
    sales = SalesInvoiceMaster.objects.filter(customerid=customer).order_by('sales_invoice_date')
    if start_date and end_date:
        sales = sales.filter(sales_invoice_date__range=[start_date, end_date])
    
    for sale in sales:
        total = SalesMaster.objects.filter(sales_invoice_no=sale.sales_invoice_no).aggregate(
            Sum('sale_total_amount'))['sale_total_amount__sum'] or 0
        transactions.append({
            'date': sale.sales_invoice_date,
            'type': 'Sales Invoice',
            'reference': sale.sales_invoice_no,
            'debit': total,
            'credit': 0
        })
    
    # Payments (Credit)
    payments = SalesInvoicePaid.objects.filter(
        sales_ip_invoice_no__customerid=customer
    ).order_by('sales_payment_date')
    if start_date and end_date:
        payments = payments.filter(sales_payment_date__range=[start_date, end_date])
    
    for payment in payments:
        transactions.append({
            'date': payment.sales_payment_date,
            'type': 'Payment',
            'reference': payment.sales_ip_invoice_no.sales_invoice_no,
            'debit': 0,
            'credit': payment.sales_payment_amount
        })
    
    # Sales Returns (Credit)
    returns = ReturnSalesInvoiceMaster.objects.filter(
        return_sales_customerid=customer
    ).order_by('return_sales_invoice_date')
    if start_date and end_date:
        returns = returns.filter(return_sales_invoice_date__range=[start_date, end_date])
    
    for ret in returns:
        transactions.append({
            'date': ret.return_sales_invoice_date,
            'type': 'Sales Return',
            'reference': ret.return_sales_invoice_no,
            'debit': 0,
            'credit': ret.return_sales_invoice_total
        })
    
    # Sort and calculate balance
    transactions.sort(key=lambda x: x['date'])
    balance = 0
    for trans in transactions:
        balance += trans['debit'] - trans['credit']
        trans['balance'] = balance
    
    total_debit = sum(t['debit'] for t in transactions)
    total_credit = sum(t['credit'] for t in transactions)
    
    # Get pharmacy details for print format
    try:
        pharmacy = Pharmacy_Details.objects.first()
    except Pharmacy_Details.DoesNotExist:
        pharmacy = None
    
    context = {
        'customer': customer,
        'transactions': transactions,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'closing_balance': balance,
        'customers': customers,
        'pharmacy': pharmacy,
        'current_date': timezone.now(),
        'start_date': start_date,
        'end_date': end_date,
        'title': f'Ledger - {customer.customer_name}'
    }
    return render(request, 'ledger/customer_ledger.html', context)


@login_required
def supplier_ledger(request, supplier_id=None):
    suppliers = SupplierMaster.objects.all().order_by('supplier_name')
    
    if not supplier_id:
        context = {'suppliers': suppliers, 'title': 'Select Supplier'}
        return render(request, 'ledger/supplier_select.html', context)
    
    supplier = get_object_or_404(SupplierMaster, supplierid=supplier_id)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    transactions = []
    
    # Purchase Invoices (Credit)
    purchases = InvoiceMaster.objects.filter(supplierid=supplier).order_by('invoice_date')
    if start_date and end_date:
        purchases = purchases.filter(invoice_date__range=[start_date, end_date])
    
    for purchase in purchases:
        transactions.append({
            'date': purchase.invoice_date,
            'type': 'Purchase Invoice',
            'reference': purchase.invoice_no,
            'debit': 0,
            'credit': purchase.invoice_total
        })
    
    # Payments (Debit)
    payments = InvoicePaid.objects.filter(
        ip_invoiceid__supplierid=supplier
    ).order_by('payment_date')
    if start_date and end_date:
        payments = payments.filter(payment_date__range=[start_date, end_date])
    
    for payment in payments:
        transactions.append({
            'date': payment.payment_date,
            'type': 'Payment',
            'reference': payment.ip_invoiceid.invoice_no,
            'debit': payment.payment_amount,
            'credit': 0
        })
    
    # Purchase Returns (Debit)
    returns = ReturnInvoiceMaster.objects.filter(
        returnsupplierid=supplier
    ).order_by('returninvoice_date')
    if start_date and end_date:
        returns = returns.filter(returninvoice_date__range=[start_date, end_date])
    
    for ret in returns:
        transactions.append({
            'date': ret.returninvoice_date,
            'type': 'Purchase Return',
            'reference': ret.returninvoiceid,
            'debit': ret.returninvoice_total,
            'credit': 0
        })
    
    # Sort and calculate balance
    transactions.sort(key=lambda x: x['date'])
    balance = 0
    for trans in transactions:
        balance += trans['credit'] - trans['debit']
        trans['balance'] = balance
    
    total_debit = sum(t['debit'] for t in transactions)
    total_credit = sum(t['credit'] for t in transactions)
    
    # Get pharmacy details for print format
    try:
        pharmacy = Pharmacy_Details.objects.first()
    except Pharmacy_Details.DoesNotExist:
        pharmacy = None
    
    context = {
        'supplier': supplier,
        'transactions': transactions,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'closing_balance': balance,
        'suppliers': suppliers,
        'pharmacy': pharmacy,
        'current_date': timezone.now(),
        'start_date': start_date,
        'end_date': end_date,
        'title': f'Ledger - {supplier.supplier_name}'
    }
    return render(request, 'ledger/supplier_ledger.html', context)
