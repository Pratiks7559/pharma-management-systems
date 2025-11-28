from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models
from .models import (
    InvoicePaid, InvoiceMaster, SalesInvoicePaid, SalesInvoiceMaster,
    SupplierChallanMaster, PurchaseMaster, SalesMaster
)
# REMOVED: InventoryMaster, InventoryTransaction - no longer needed

@receiver(post_save, sender=InvoicePaid)
def update_invoice_payment_status_on_save(sender, instance, **kwargs):
    """Update invoice payment status when a payment is added or modified"""
    invoice = instance.ip_invoiceid
    
    # Recalculate total paid amount from all payments
    total_paid = InvoicePaid.objects.filter(ip_invoiceid=invoice).aggregate(
        total=models.Sum('payment_amount')
    )['total'] or 0
    
    # Update invoice paid amount
    invoice.invoice_paid = total_paid
    
    # Update payment status based on balance
    balance = invoice.invoice_total - invoice.invoice_paid
    if balance <= 0.01:
        invoice.payment_status = 'paid'
    elif invoice.invoice_paid > 0:
        invoice.payment_status = 'partial'
    else:
        invoice.payment_status = 'pending'
    
    invoice.save()

@receiver(post_delete, sender=InvoicePaid)
def update_invoice_payment_status_on_delete(sender, instance, **kwargs):
    """Update invoice payment status when a payment is deleted"""
    invoice = instance.ip_invoiceid
    
    # Recalculate total paid amount from remaining payments
    total_paid = InvoicePaid.objects.filter(ip_invoiceid=invoice).aggregate(
        total=models.Sum('payment_amount')
    )['total'] or 0
    
    # Update invoice paid amount
    invoice.invoice_paid = total_paid
    
    # Update payment status based on balance
    balance = invoice.invoice_total - invoice.invoice_paid
    if balance <= 0.01:
        invoice.payment_status = 'paid'
    elif invoice.invoice_paid > 0:
        invoice.payment_status = 'partial'
    else:
        invoice.payment_status = 'pending'
    
    invoice.save()

# Sales Invoice Payment Signals
@receiver(post_save, sender=SalesInvoicePaid)
def update_sales_invoice_payment_on_save(sender, instance, **kwargs):
    """Update sales invoice payment total when a payment is added or modified"""
    invoice = instance.sales_ip_invoice_no
    
    # Recalculate total paid amount from all payments
    total_paid = SalesInvoicePaid.objects.filter(sales_ip_invoice_no=invoice).aggregate(
        total=models.Sum('sales_payment_amount')
    )['total'] or 0
    
    # Update invoice paid amount
    invoice.sales_invoice_paid = total_paid
    invoice.save()

@receiver(post_delete, sender=SalesInvoicePaid)
def update_sales_invoice_payment_on_delete(sender, instance, **kwargs):
    """Update sales invoice payment total when a payment is deleted"""
    invoice = instance.sales_ip_invoice_no
    
    # Recalculate total paid amount from remaining payments
    total_paid = SalesInvoicePaid.objects.filter(sales_ip_invoice_no=invoice).aggregate(
        total=models.Sum('sales_payment_amount')
    )['total'] or 0
    
    # Update invoice paid amount
    invoice.sales_invoice_paid = total_paid
    invoice.save()

# REMOVED: Inventory Management Signals - no longer needed
# Inventory is now tracked through PurchaseMaster and SalesMaster tables directly