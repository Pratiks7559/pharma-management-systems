"""
Enhanced Sales Analytics Module
Provides comprehensive real-time sales analysis and calculations
"""

from django.db.models import Sum, Count, Avg, Max, Min, F, Q, Case, When, FloatField
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    SalesInvoiceMaster, SalesMaster, CustomerMaster, 
    ProductMaster, SalesInvoicePaid
)

class SalesAnalytics:
    """Real-time sales analytics calculator"""
    
    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date or datetime.now().date().replace(day=1)
        self.end_date = end_date or datetime.now().date()
        self._invoices = None
        self._sales_details = None
    
    @property
    def invoices(self):
        """Cached invoice queryset"""
        if self._invoices is None:
            try:
                self._invoices = SalesInvoiceMaster.objects.filter(
                    sales_invoice_date__range=[self.start_date, self.end_date]
                ).select_related('customerid')
            except Exception:
                # Return empty queryset if there's an error
                self._invoices = SalesInvoiceMaster.objects.none()
        return self._invoices
    
    @property
    def sales_details(self):
        """Cached sales details queryset"""
        if self._sales_details is None:
            try:
                self._sales_details = SalesMaster.objects.filter(
                    sales_invoice_no__in=self.invoices
                ).select_related('productid', 'sales_invoice_no__customerid')
            except Exception:
                # Return empty queryset if there's an error
                self._sales_details = SalesMaster.objects.none()
        return self._sales_details
    
    def calculate_core_metrics(self):
        """Calculate core sales metrics"""
        # Calculate total sales from SalesMaster instead of property
        total_sales = self.sales_details.aggregate(Sum('sale_total_amount'))['sale_total_amount__sum'] or 0
        total_received = sum(inv.sales_invoice_paid or 0 for inv in self.invoices)
        total_pending = total_sales - total_received
        
        invoice_count = self.invoices.count()
        
        return {
            'total_sales': float(total_sales),
            'total_received': float(total_received),
            'total_pending': float(total_pending),
            'total_invoices': invoice_count,
            'collection_rate': float((total_received / total_sales * 100) if total_sales > 0 else 0),
            'pending_rate': float((total_pending / total_sales * 100) if total_sales > 0 else 0),
            'avg_invoice_value': float(total_sales / invoice_count if invoice_count > 0 else 0)
        }
    
    def calculate_invoice_analysis(self):
        """Analyze invoice payment status"""
        # Calculate invoice totals from sales details
        invoice_totals = {}
        for invoice in self.invoices:
            invoice_total = self.sales_details.filter(
                sales_invoice_no=invoice.sales_invoice_no
            ).aggregate(Sum('sale_total_amount'))['sale_total_amount__sum'] or 0
            invoice_totals[invoice.sales_invoice_no] = float(invoice_total)
        
        paid_invoices = sum(1 for inv in self.invoices 
                          if (inv.sales_invoice_paid or 0) >= invoice_totals.get(inv.sales_invoice_no, 0))
        partial_paid = sum(1 for inv in self.invoices 
                         if 0 < (inv.sales_invoice_paid or 0) < invoice_totals.get(inv.sales_invoice_no, 0))
        unpaid_invoices = sum(1 for inv in self.invoices if (inv.sales_invoice_paid or 0) == 0)
        
        totals_list = [total for total in invoice_totals.values() if total > 0]
        
        return {
            'paid_invoices': paid_invoices,
            'partial_paid': partial_paid,
            'unpaid_invoices': unpaid_invoices,
            'largest_invoice': float(max(totals_list)) if totals_list else 0,
            'smallest_invoice': float(min(totals_list)) if totals_list else 0
        }
    
    def calculate_product_analytics(self):
        """Calculate detailed product-wise sales analytics"""
        return self.sales_details.values(
            'productid__product_name',
            'productid__product_company',
            'productid__product_category'
        ).annotate(
            total_quantity=Sum('sale_quantity'),
            total_amount=Sum('sale_total_amount'),
            avg_rate=Avg('sale_rate'),
            max_rate=Max('sale_rate'),
            min_rate=Min('sale_rate'),
            invoice_count=Count('sales_invoice_no', distinct=True),
            total_discount=Sum('sale_discount'),
            avg_discount=Avg('sale_discount')
        ).order_by('-total_amount')
    
    def calculate_customer_analytics(self):
        """Calculate detailed customer-wise sales analytics"""
        return self.sales_details.values(
            'sales_invoice_no__customerid__customer_name',
            'sales_invoice_no__customerid__customer_type',
            'sales_invoice_no__customerid__customer_mobile'
        ).annotate(
            total_amount=Sum('sale_total_amount'),
            invoice_count=Count('sales_invoice_no', distinct=True),
            total_quantity=Sum('sale_quantity'),
            avg_invoice_value=Avg('sale_total_amount'),
            last_purchase_date=Max('sales_invoice_no__sales_invoice_date'),
            total_discount=Sum('sale_discount')
        ).order_by('-total_amount')
    
    def calculate_category_analytics(self):
        """Calculate category-wise sales distribution"""
        return self.sales_details.values(
            'productid__product_category'
        ).annotate(
            total_amount=Sum('sale_total_amount'),
            total_quantity=Sum('sale_quantity'),
            product_count=Count('productid', distinct=True),
            avg_rate=Avg('sale_rate')
        ).order_by('-total_amount')
    
    def calculate_daily_trend(self):
        """Calculate daily sales trend"""
        return self.sales_details.extra(
            select={'day': 'DATE(sales_invoice_no_id)'}
        ).values('day').annotate(
            daily_total=Sum('sale_total_amount'),
            daily_quantity=Sum('sale_quantity'),
            daily_invoices=Count('sales_invoice_no', distinct=True)
        ).order_by('day')
    
    def calculate_realtime_stats(self):
        """Calculate real-time statistics"""
        total_products_sold = self.sales_details.aggregate(
            total=Sum('sale_quantity')
        )['total'] or 0
        
        unique_products = self.sales_details.values('productid').distinct().count()
        unique_customers = self.invoices.values('customerid').distinct().count()
        
        total_items = self.sales_details.count()
        invoice_count = self.invoices.count()
        avg_items_per_invoice = total_items / invoice_count if invoice_count > 0 else 0
        
        total_discount = self.sales_details.aggregate(
            total=Sum('sale_discount')
        )['total'] or 0
        
        # Calculate tax more safely
        total_tax = 0
        for sale in self.sales_details:
            try:
                tax_amount = (sale.sale_total_amount or 0) * (sale.sale_igst or 0) / 100
                total_tax += tax_amount
            except (TypeError, AttributeError):
                continue
        
        return {
            'total_products_sold': float(total_products_sold),
            'unique_products': unique_products,
            'unique_customers': unique_customers,
            'avg_items_per_invoice': float(avg_items_per_invoice),
            'total_discount_given': float(total_discount),
            'total_tax_collected': float(total_tax)
        }
    
    def get_monthly_comparison(self, months=12):
        """Get monthly sales comparison for trend analysis"""
        monthly_data = []
        current_date = datetime.now().date()
        
        for i in range(months):
            if i == 0:
                month_start = current_date.replace(day=1)
            else:
                if month_start.month == 1:
                    month_start = month_start.replace(year=month_start.year-1, month=12, day=1)
                else:
                    month_start = month_start.replace(month=month_start.month-1, day=1)
            
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year+1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month+1, day=1) - timedelta(days=1)
            
            month_invoices = SalesInvoiceMaster.objects.filter(
                sales_invoice_date__range=[month_start, month_end]
            )
            
            # Calculate month total from sales details
            month_total = SalesMaster.objects.filter(
                sales_invoice_no__in=month_invoices
            ).aggregate(Sum('sale_total_amount'))['sale_total_amount__sum'] or 0
            
            monthly_data.insert(0, {
                'month': month_start.strftime('%b %Y'),
                'total': month_total,
                'invoice_count': month_invoices.count()
            })
        
        return monthly_data
    
    def get_top_performers(self, limit=10):
        """Get top performing products and customers"""
        top_products = list(self.calculate_product_analytics()[:limit])
        top_customers = list(self.calculate_customer_analytics()[:limit])
        
        return {
            'top_products': top_products,
            'top_customers': top_customers
        }
    
    def get_comprehensive_report(self):
        """Generate comprehensive sales analytics report"""
        return {
            'period': {
                'start_date': self.start_date,
                'end_date': self.end_date
            },
            'core_metrics': self.calculate_core_metrics(),
            'invoice_analysis': self.calculate_invoice_analysis(),
            'product_analytics': list(self.calculate_product_analytics()),
            'customer_analytics': list(self.calculate_customer_analytics()),
            'category_analytics': list(self.calculate_category_analytics()),
            'daily_trend': list(self.calculate_daily_trend()),
            'monthly_trend': self.get_monthly_comparison(),
            'realtime_stats': self.calculate_realtime_stats(),
            'top_performers': self.get_top_performers(),
            'invoices': [{
                'sales_invoice_no': inv.sales_invoice_no,
                'sales_invoice_date': inv.sales_invoice_date,
                'customer_name': inv.customerid.customer_name if inv.customerid else 'Unknown',
                'customer_type': inv.customerid.customer_type if inv.customerid else 'Unknown',
                'sales_invoice_paid': float(inv.sales_invoice_paid or 0),
                'sales_invoice_total': float(self.sales_details.filter(
                    sales_invoice_no=inv.sales_invoice_no
                ).aggregate(Sum('sale_total_amount'))['sale_total_amount__sum'] or 0)
            } for inv in self.invoices]
        }

def get_sales_analytics(start_date=None, end_date=None):
    """Factory function to get sales analytics"""
    try:
        analytics = SalesAnalytics(start_date, end_date)
        return analytics.get_comprehensive_report()
    except Exception as e:
        # Return empty report structure if there's an error
        return {
            'period': {'start_date': start_date, 'end_date': end_date},
            'core_metrics': {
                'total_sales': 0, 'total_received': 0, 'total_pending': 0,
                'total_invoices': 0, 'collection_rate': 0, 'pending_rate': 0, 'avg_invoice_value': 0
            },
            'invoice_analysis': {
                'paid_invoices': 0, 'partial_paid': 0, 'unpaid_invoices': 0,
                'largest_invoice': 0, 'smallest_invoice': 0
            },
            'product_analytics': [], 'customer_analytics': [], 'category_analytics': [],
            'daily_trend': [], 'monthly_trend': [], 'realtime_stats': {
                'total_products_sold': 0, 'unique_products': 0, 'unique_customers': 0,
                'avg_items_per_invoice': 0, 'total_discount_given': 0, 'total_tax_collected': 0
            },
            'top_performers': {'top_products': [], 'top_customers': []},
            'invoices': []
        }

def calculate_invoice_totals(invoices):
    """Calculate totals for a list of invoices"""
    total_sales = sum(inv.sales_invoice_total for inv in invoices)
    total_received = sum(inv.sales_invoice_paid for inv in invoices)
    return {
        'total_sales': total_sales,
        'total_received': total_received,
        'total_pending': total_sales - total_received
    }