#!/usr/bin/env python
import os
import sys
import django

# Setup Django
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.db import models
from core.models import SalesInvoiceMaster, SalesInvoicePaid, InvoiceMaster, InvoicePaid

def fix_payment_totals():
    print("🔄 Fixing payment totals...")
    
    # Fix Sales Invoices
    sales_fixed = 0
    for invoice in SalesInvoiceMaster.objects.all():
        actual_paid = SalesInvoicePaid.objects.filter(
            sales_ip_invoice_no=invoice
        ).aggregate(total=models.Sum('sales_payment_amount'))['total'] or 0
        
        if invoice.sales_invoice_paid != actual_paid:
            print(f"📋 Sales Invoice {invoice.sales_invoice_no}: ₹{invoice.sales_invoice_paid} → ₹{actual_paid}")
            invoice.sales_invoice_paid = actual_paid
            invoice.save()
            sales_fixed += 1
    
    # Fix Purchase Invoices  
    purchase_fixed = 0
    for invoice in InvoiceMaster.objects.all():
        actual_paid = InvoicePaid.objects.filter(
            ip_invoiceid=invoice
        ).aggregate(total=models.Sum('payment_amount'))['total'] or 0
        
        if invoice.invoice_paid != actual_paid:
            print(f"📋 Purchase Invoice {invoice.invoice_no}: ₹{invoice.invoice_paid} → ₹{actual_paid}")
            invoice.invoice_paid = actual_paid
            invoice.save()
            purchase_fixed += 1
    
    print(f"✅ Fixed {sales_fixed} sales invoices and {purchase_fixed} purchase invoices")

if __name__ == "__main__":
    fix_payment_totals()