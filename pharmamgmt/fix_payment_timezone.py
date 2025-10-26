#!/usr/bin/env python
"""
Fix timezone issues in payment records
This script updates existing payment records to use proper timezone-aware datetime
"""

import os
import sys
import django
from datetime import datetime, time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from django.utils import timezone
from core.models import SalesInvoicePaid, ReturnSalesInvoicePaid, InvoicePaid

def fix_payment_timezones():
    """Fix timezone issues in payment records"""
    
    print("🔧 Starting payment timezone fix...")
    
    # Fix SalesInvoicePaid records
    print("\n📋 Fixing SalesInvoicePaid records...")
    sales_payments = SalesInvoicePaid.objects.all()
    sales_count = 0
    
    for payment in sales_payments:
        try:
            # Check if payment_date is naive (no timezone info)
            if payment.sales_payment_date and payment.sales_payment_date.tzinfo is None:
                # Convert to timezone-aware datetime with current time
                current_time = timezone.now().time()
                if hasattr(payment.sales_payment_date, 'date'):
                    # It's already a datetime, just make it timezone-aware
                    payment.sales_payment_date = timezone.make_aware(payment.sales_payment_date)
                else:
                    # It's a date, convert to datetime with current time
                    payment.sales_payment_date = timezone.make_aware(
                        datetime.combine(payment.sales_payment_date, current_time)
                    )
                payment.save()
                sales_count += 1
                print(f"  ✅ Fixed sales payment #{payment.sales_payment_id}")
        except Exception as e:
            print(f"  ❌ Error fixing sales payment #{payment.sales_payment_id}: {e}")
    
    print(f"📊 Fixed {sales_count} sales payment records")
    
    # Fix ReturnSalesInvoicePaid records
    print("\n📋 Fixing ReturnSalesInvoicePaid records...")
    return_payments = ReturnSalesInvoicePaid.objects.all()
    return_count = 0
    
    for payment in return_payments:
        try:
            # Check if payment_date is naive (no timezone info)
            if payment.return_sales_payment_date and payment.return_sales_payment_date.tzinfo is None:
                # Convert to timezone-aware datetime with current time
                current_time = timezone.now().time()
                if hasattr(payment.return_sales_payment_date, 'date'):
                    # It's already a datetime, just make it timezone-aware
                    payment.return_sales_payment_date = timezone.make_aware(payment.return_sales_payment_date)
                else:
                    # It's a date, convert to datetime with current time
                    payment.return_sales_payment_date = timezone.make_aware(
                        datetime.combine(payment.return_sales_payment_date, current_time)
                    )
                payment.save()
                return_count += 1
                print(f"  ✅ Fixed return payment #{payment.return_sales_payment_id}")
        except Exception as e:
            print(f"  ❌ Error fixing return payment #{payment.return_sales_payment_id}: {e}")
    
    print(f"📊 Fixed {return_count} return payment records")
    
    # Fix InvoicePaid records (purchase payments)
    print("\n📋 Fixing InvoicePaid records...")
    invoice_payments = InvoicePaid.objects.all()
    invoice_count = 0
    
    for payment in invoice_payments:
        try:
            # Check if payment_date is naive (no timezone info)
            if payment.payment_date and hasattr(payment.payment_date, 'date'):
                # Convert date to timezone-aware datetime with current time
                current_time = timezone.now().time()
                payment.payment_date = timezone.make_aware(
                    datetime.combine(payment.payment_date, current_time)
                )
                payment.save()
                invoice_count += 1
                print(f"  ✅ Fixed invoice payment #{payment.payment_id}")
        except Exception as e:
            print(f"  ❌ Error fixing invoice payment #{payment.payment_id}: {e}")
    
    print(f"📊 Fixed {invoice_count} invoice payment records")
    
    print(f"\n🎉 Payment timezone fix completed!")
    print(f"📈 Total records fixed: {sales_count + return_count + invoice_count}")

if __name__ == "__main__":
    fix_payment_timezones()