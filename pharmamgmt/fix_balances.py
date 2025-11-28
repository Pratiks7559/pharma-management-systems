#!/usr/bin/env python
"""
Quick script to fix small balance issues in the pharmacy management system.
Run this script to identify and fix invoices with small balances (≤ Rs.0.10).
"""

import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from core.models import InvoiceMaster, SalesInvoiceMaster

def fix_small_balances(dry_run=True, threshold=0.10):
    """
    Fix invoices with small balance issues
    
    Args:
        dry_run (bool): If True, only show what would be fixed without making changes
        threshold (float): Balance threshold for auto-fix (default: 0.10)
    """
    threshold_decimal = Decimal(str(threshold)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    print(f"🔍 Scanning for invoices with small balances ≤ Rs.{threshold}")
    if dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
    print("-" * 60)
    
    # Fix supplier invoices
    supplier_invoices_fixed = 0
    supplier_invoices = InvoiceMaster.objects.all()
    
    print("📋 SUPPLIER INVOICES:")
    for invoice in supplier_invoices:
        total = Decimal(str(invoice.invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        paid = Decimal(str(invoice.invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        balance = total - paid
        
        if 0 < balance <= threshold_decimal:
            print(f"   📄 Invoice {invoice.invoice_no} - Balance: Rs.{balance}")
            print(f"      Supplier: {invoice.supplierid.supplier_name}")
            print(f"      Total: Rs.{total}, Paid: Rs.{paid}")
            
            if not dry_run:
                with transaction.atomic():
                    # Mark as fully paid by adjusting paid amount
                    invoice.invoice_paid = float(total)
                    invoice.payment_status = 'paid'
                    invoice.save()
                    print(f"      ✅ FIXED: Rs.{balance} written off")
            else:
                print(f"      🔧 WOULD FIX: Write off Rs.{balance}")
            
            supplier_invoices_fixed += 1
            print()
    
    # Fix customer invoices
    customer_invoices_fixed = 0
    customer_invoices = SalesInvoiceMaster.objects.all()
    
    print("📋 CUSTOMER INVOICES:")
    for invoice in customer_invoices:
        total = Decimal(str(invoice.sales_invoice_total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        paid = Decimal(str(invoice.sales_invoice_paid)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        balance = total - paid
        
        if 0 < balance <= threshold_decimal:
            print(f"   📄 Invoice {invoice.sales_invoice_no} - Balance: Rs.{balance}")
            print(f"      Customer: {invoice.customerid.customer_name}")
            print(f"      Total: Rs.{total}, Paid: Rs.{paid}")
            
            if not dry_run:
                with transaction.atomic():
                    # Mark as fully paid by adjusting paid amount
                    invoice.sales_invoice_paid = float(total)
                    invoice.save()
                    print(f"      ✅ FIXED: Rs.{balance} written off")
            else:
                print(f"      🔧 WOULD FIX: Write off Rs.{balance}")
            
            customer_invoices_fixed += 1
            print()
    
    # Summary
    total_fixed = supplier_invoices_fixed + customer_invoices_fixed
    
    print("=" * 60)
    if dry_run:
        print("📊 DRY RUN SUMMARY:")
        print(f"   Would fix {supplier_invoices_fixed} supplier invoices")
        print(f"   Would fix {customer_invoices_fixed} customer invoices")
        print(f"   Total invoices that would be fixed: {total_fixed}")
        print("\n💡 Run with dry_run=False to apply fixes")
    else:
        print("📊 FIX SUMMARY:")
        print(f"   Fixed {supplier_invoices_fixed} supplier invoices")
        print(f"   Fixed {customer_invoices_fixed} customer invoices")
        print(f"   Total invoices fixed: {total_fixed}")
    
    if total_fixed == 0:
        print("✅ No invoices with small balances found!")
    
    return total_fixed

def main():
    """Main function to run the balance fix"""
    print("🏥 PHARMACY MANAGEMENT - SMALL BALANCE FIXER")
    print("=" * 60)
    
    # First run in dry-run mode to see what would be fixed
    print("Step 1: Scanning for issues...")
    issues_found = fix_small_balances(dry_run=True)
    
    if issues_found > 0:
        print(f"\n⚠️  Found {issues_found} invoices with small balance issues!")
        
        # Ask user if they want to proceed with fixes
        response = input("\nDo you want to fix these issues? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\nStep 2: Applying fixes...")
            fix_small_balances(dry_run=False)
            print("\n🎉 All small balance issues have been resolved!")
        else:
            print("\n❌ No changes made. Issues remain unfixed.")
    else:
        print("\n✅ No small balance issues found. System is clean!")

if __name__ == "__main__":
    main()