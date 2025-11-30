from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import ReturnInvoiceMaster, ReturnPurchaseMaster, ReturnSalesInvoiceMaster, ReturnSalesMaster, Pharmacy_Details

@login_required
def print_purchase_return_receipt(request, return_id):
    return_invoice = get_object_or_404(ReturnInvoiceMaster, returninvoiceid=return_id)
    return_items = ReturnPurchaseMaster.objects.filter(returninvoiceid=return_invoice)
    items_total = return_items.aggregate(Sum('returntotal_amount'))['returntotal_amount__sum'] or 0
    
    pharmacy = Pharmacy_Details.objects.first()
    
    context = {
        'return_invoice': return_invoice,
        'return_items': return_items,
        'items_total': items_total,
        'pharmacy': pharmacy,
        'today': timezone.now(),
        'title': f'Debit Note - {return_invoice.returninvoiceid}'
    }
    return render(request, 'returns/purchase_return_receipt.html', context)

@login_required
def print_sales_return_receipt(request, return_id):
    return_invoice = get_object_or_404(ReturnSalesInvoiceMaster, return_sales_invoice_no=return_id)
    return_items = ReturnSalesMaster.objects.filter(return_sales_invoice_no=return_invoice)
    items_total = return_items.aggregate(Sum('return_sale_total_amount'))['return_sale_total_amount__sum'] or 0
    
    pharmacy = Pharmacy_Details.objects.first()
    
    context = {
        'return_invoice': return_invoice,
        'return_items': return_items,
        'items_total': items_total,
        'pharmacy': pharmacy,
        'today': timezone.now(),
        'title': f'Credit Note - {return_invoice.return_sales_invoice_no}'
    }
    return render(request, 'returns/sales_return_receipt.html', context)
