"""
Financial Analytics Module
Provides advanced financial analysis and reporting capabilities
"""

from django.db.models import Sum, Count, Q, F, Avg, Max, Min
from django.db.models.functions import TruncMonth, TruncDate, Extract
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    SalesInvoiceMaster, SalesMaster, SalesInvoicePaid,
    InvoiceMaster, PurchaseMaster, InvoicePaid,
    ReturnSalesInvoiceMaster, ReturnSalesMaster,
    ReturnInvoiceMaster, ReturnPurchaseMaster,
    CustomerMaster, SupplierMaster, ProductMaster,
    InventoryMaster, InventoryTransaction
)

class FinancialAnalytics:
    """Advanced financial analytics and reporting"""
    
    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date or (timezone.now().date() - timedelta(days=30))
        self.end_date = end_date or timezone.now().date()
    
    def get_comprehensive_report(self):
        """Get comprehensive financial report with all metrics"""
        return {
            'period': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'days': (self.end_date - self.start_date).days
            },
            'revenue_analysis': self.get_revenue_analysis(),
            'cost_analysis': self.get_cost_analysis(),
            'profitability_analysis': self.get_profitability_analysis(),
            'cash_flow_analysis': self.get_cash_flow_analysis(),
            'customer_analysis': self.get_customer_analysis(),
            'supplier_analysis': self.get_supplier_analysis(),
            'product_analysis': self.get_product_analysis(),
            'inventory_analysis': self.get_inventory_analysis(),
            'financial_ratios': self.get_financial_ratios(),
            'trends': self.get_trend_analysis(),
            'forecasts': self.get_forecasts()
        }
    
    def get_revenue_analysis(self):
        """Analyze revenue streams and patterns"""
        
        # Regular sales
        regular_sales = SalesMaster.objects.filter(
            sale_entry_date__date__range=[self.start_date, self.end_date]
        ).aggregate(
            total_revenue=Sum('sale_total_amount'),
            total_quantity=Sum('sale_quantity'),
            avg_order_value=Avg('sale_total_amount'),
            transaction_count=Count('id')
        )
        
        # Monthly revenue breakdown
        monthly_revenue = SalesMaster.objects.filter(
            sale_entry_date__date__range=[self.start_date, self.end_date]
        ).annotate(
            month=TruncMonth('sale_entry_date')
        ).values('month').annotate(
            revenue=Sum('sale_total_amount'),
            transactions=Count('id')
        ).order_by('month')
        
        # Revenue by customer type
        customer_type_revenue = SalesMaster.objects.filter(
            sale_entry_date__date__range=[self.start_date, self.end_date]
        ).values('customerid__customer_type').annotate(
            revenue=Sum('sale_total_amount'),
            customers=Count('customerid', distinct=True)
        ).order_by('-revenue')
        
        # Revenue growth rate
        prev_period_start = self.start_date - timedelta(days=(self.end_date - self.start_date).days)
        prev_period_end = self.start_date
        
        prev_revenue = SalesMaster.objects.filter(
            sale_entry_date__date__range=[prev_period_start, prev_period_end]
        ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
        
        current_revenue = regular_sales['total_revenue'] or 0
        growth_rate = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        return {
            'total_revenue': current_revenue,
            'total_quantity': regular_sales['total_quantity'] or 0,
            'avg_order_value': regular_sales['avg_order_value'] or 0,
            'transaction_count': regular_sales['transaction_count'] or 0,
            'growth_rate': growth_rate,
            'monthly_breakdown': list(monthly_revenue),
            'customer_type_breakdown': list(customer_type_revenue),
            'revenue_per_day': current_revenue / max(1, (self.end_date - self.start_date).days)
        }
    
    def get_cost_analysis(self):
        """Analyze cost structure and patterns"""
        
        # Purchase costs
        purchase_costs = PurchaseMaster.objects.filter(
            purchase_entry_date__date__range=[self.start_date, self.end_date]
        ).aggregate(
            total_cost=Sum('total_amount'),
            total_quantity=Sum('product_quantity'),
            avg_cost_per_unit=Avg('product_actual_rate'),
            transaction_count=Count('purchaseid')
        )
        
        # Cost by supplier
        supplier_costs = PurchaseMaster.objects.filter(
            purchase_entry_date__date__range=[self.start_date, self.end_date]
        ).values('product_supplierid__supplier_name').annotate(
            cost=Sum('total_amount'),
            transactions=Count('purchaseid')
        ).order_by('-cost')[:10]
        
        # Cost by product category
        category_costs = PurchaseMaster.objects.filter(
            purchase_entry_date__date__range=[self.start_date, self.end_date]
        ).values('productid__product_category').annotate(
            cost=Sum('total_amount'),
            quantity=Sum('product_quantity')
        ).order_by('-cost')
        
        # Monthly cost breakdown
        monthly_costs = PurchaseMaster.objects.filter(
            purchase_entry_date__date__range=[self.start_date, self.end_date]
        ).annotate(
            month=TruncMonth('purchase_entry_date')
        ).values('month').annotate(
            cost=Sum('total_amount')
        ).order_by('month')
        
        return {
            'total_cost': purchase_costs['total_cost'] or 0,
            'total_quantity': purchase_costs['total_quantity'] or 0,
            'avg_cost_per_unit': purchase_costs['avg_cost_per_unit'] or 0,
            'transaction_count': purchase_costs['transaction_count'] or 0,
            'supplier_breakdown': list(supplier_costs),
            'category_breakdown': list(category_costs),
            'monthly_breakdown': list(monthly_costs),
            'cost_per_day': (purchase_costs['total_cost'] or 0) / max(1, (self.end_date - self.start_date).days)
        }
    
    def get_profitability_analysis(self):
        """Analyze profitability metrics"""
        
        revenue_data = self.get_revenue_analysis()
        cost_data = self.get_cost_analysis()
        
        gross_profit = revenue_data['total_revenue'] - cost_data['total_cost']
        gross_margin = (gross_profit / revenue_data['total_revenue'] * 100) if revenue_data['total_revenue'] > 0 else 0
        
        # Product profitability
        product_profitability = []
        products = ProductMaster.objects.all()[:20]  # Top 20 products
        
        for product in products:
            sales = SalesMaster.objects.filter(
                productid=product,
                sale_entry_date__date__range=[self.start_date, self.end_date]
            ).aggregate(
                revenue=Sum('sale_total_amount'),
                quantity=Sum('sale_quantity')
            )
            
            purchases = PurchaseMaster.objects.filter(
                productid=product,
                purchase_entry_date__date__range=[self.start_date, self.end_date]
            ).aggregate(
                cost=Sum('total_amount'),
                quantity=Sum('product_quantity')
            )
            
            if sales['revenue'] and purchases['cost']:
                profit = sales['revenue'] - purchases['cost']
                margin = (profit / sales['revenue'] * 100) if sales['revenue'] > 0 else 0
                
                product_profitability.append({
                    'product_name': product.product_name,
                    'revenue': sales['revenue'],
                    'cost': purchases['cost'],
                    'profit': profit,
                    'margin': margin,
                    'quantity_sold': sales['quantity'] or 0
                })
        
        # Sort by profit descending
        product_profitability.sort(key=lambda x: x['profit'], reverse=True)
        
        return {
            'gross_profit': gross_profit,
            'gross_margin': gross_margin,
            'product_profitability': product_profitability[:10],
            'profit_per_day': gross_profit / max(1, (self.end_date - self.start_date).days),
            'break_even_point': cost_data['total_cost'] / max(1, revenue_data['avg_order_value']) if revenue_data['avg_order_value'] > 0 else 0
        }
    
    def get_cash_flow_analysis(self):
        """Analyze cash flow patterns"""
        
        # Daily cash inflows (payments received)
        daily_inflows = SalesInvoicePaid.objects.filter(
            sales_payment_date__range=[self.start_date, self.end_date]
        ).annotate(
            date=TruncDate('sales_payment_date')
        ).values('date').annotate(
            amount=Sum('sales_payment_amount')
        ).order_by('date')
        
        # Daily cash outflows (payments made)
        daily_outflows = InvoicePaid.objects.filter(
            payment_date__range=[self.start_date, self.end_date]
        ).annotate(
            date=TruncDate('payment_date')
        ).values('date').annotate(
            amount=Sum('payment_amount')
        ).order_by('date')
        
        # Net cash flow
        total_inflow = sum(item['amount'] for item in daily_inflows)
        total_outflow = sum(item['amount'] for item in daily_outflows)
        net_cash_flow = total_inflow - total_outflow
        
        # Cash flow by payment method
        inflow_by_method = SalesInvoicePaid.objects.filter(
            sales_payment_date__range=[self.start_date, self.end_date]
        ).values('sales_payment_mode').annotate(
            amount=Sum('sales_payment_amount')
        ).order_by('-amount')
        
        return {
            'total_inflow': total_inflow,
            'total_outflow': total_outflow,
            'net_cash_flow': net_cash_flow,
            'daily_inflows': list(daily_inflows),
            'daily_outflows': list(daily_outflows),
            'inflow_by_method': list(inflow_by_method),
            'cash_conversion_cycle': self.calculate_cash_conversion_cycle()
        }
    
    def get_customer_analysis(self):
        """Analyze customer behavior and value"""
        
        # Top customers by revenue
        top_customers = SalesMaster.objects.filter(
            sale_entry_date__date__range=[self.start_date, self.end_date]
        ).values('customerid__customer_name').annotate(
            revenue=Sum('sale_total_amount'),
            transactions=Count('sales_invoice_no', distinct=True),
            avg_order_value=Avg('sale_total_amount')
        ).order_by('-revenue')[:10]
        
        # Customer acquisition and retention
        new_customers = CustomerMaster.objects.filter(
            salesmaster__sale_entry_date__date__range=[self.start_date, self.end_date]
        ).distinct().count()
        
        # Customer lifetime value (simplified)
        customer_ltv = []
        for customer in CustomerMaster.objects.all()[:20]:
            total_revenue = SalesMaster.objects.filter(
                customerid=customer
            ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
            
            first_purchase = SalesMaster.objects.filter(
                customerid=customer
            ).order_by('sale_entry_date').first()
            
            if first_purchase:
                days_active = (timezone.now().date() - first_purchase.sale_entry_date.date()).days
                if days_active > 0:
                    customer_ltv.append({
                        'customer_name': customer.customer_name,
                        'total_revenue': total_revenue,
                        'days_active': days_active,
                        'avg_revenue_per_day': total_revenue / days_active
                    })
        
        customer_ltv.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        return {
            'top_customers': list(top_customers),
            'new_customers': new_customers,
            'customer_ltv': customer_ltv[:10],
            'avg_customer_value': sum(c['revenue'] for c in top_customers) / len(top_customers) if top_customers else 0
        }
    
    def get_supplier_analysis(self):
        """Analyze supplier performance and costs"""
        
        # Top suppliers by purchase volume
        top_suppliers = PurchaseMaster.objects.filter(
            purchase_entry_date__date__range=[self.start_date, self.end_date]
        ).values('product_supplierid__supplier_name').annotate(
            total_cost=Sum('total_amount'),
            transactions=Count('purchaseid'),
            avg_order_value=Avg('total_amount')
        ).order_by('-total_cost')[:10]
        
        # Supplier payment analysis
        supplier_payments = InvoicePaid.objects.filter(
            payment_date__range=[self.start_date, self.end_date]
        ).values('ip_invoiceid__supplierid__supplier_name').annotate(
            total_paid=Sum('payment_amount'),
            payment_count=Count('payment_id')
        ).order_by('-total_paid')[:10]
        
        return {
            'top_suppliers': list(top_suppliers),
            'supplier_payments': list(supplier_payments),
            'supplier_diversity': len(set(s['product_supplierid__supplier_name'] for s in top_suppliers))
        }
    
    def get_product_analysis(self):
        """Analyze product performance"""
        
        # Best selling products
        best_sellers = SalesMaster.objects.filter(
            sale_entry_date__date__range=[self.start_date, self.end_date]
        ).values('productid__product_name', 'productid__product_company').annotate(
            quantity_sold=Sum('sale_quantity'),
            revenue=Sum('sale_total_amount'),
            avg_price=Avg('sale_rate')
        ).order_by('-quantity_sold')[:10]
        
        # Most profitable products
        most_profitable = []
        for product in ProductMaster.objects.all()[:50]:
            sales_data = SalesMaster.objects.filter(
                productid=product,
                sale_entry_date__date__range=[self.start_date, self.end_date]
            ).aggregate(
                revenue=Sum('sale_total_amount'),
                quantity=Sum('sale_quantity')
            )
            
            purchase_data = PurchaseMaster.objects.filter(
                productid=product,
                purchase_entry_date__date__range=[self.start_date, self.end_date]
            ).aggregate(
                cost=Sum('total_amount')
            )
            
            if sales_data['revenue'] and purchase_data['cost']:
                profit = sales_data['revenue'] - purchase_data['cost']
                most_profitable.append({
                    'product_name': product.product_name,
                    'profit': profit,
                    'revenue': sales_data['revenue'],
                    'cost': purchase_data['cost']
                })
        
        most_profitable.sort(key=lambda x: x['profit'], reverse=True)
        
        return {
            'best_sellers': list(best_sellers),
            'most_profitable': most_profitable[:10],
            'product_diversity': ProductMaster.objects.count()
        }
    
    def get_inventory_analysis(self):
        """Analyze inventory metrics"""
        
        # Current inventory value
        inventory_value = InventoryMaster.objects.filter(
            is_active=True
        ).aggregate(
            total_value=Sum(F('current_stock') * F('purchase_rate')),
            total_items=Count('inventory_id'),
            total_stock=Sum('current_stock')
        )
        
        # Inventory turnover
        avg_inventory = inventory_value['total_value'] or 0
        cogs = self.get_cost_analysis()['total_cost']
        inventory_turnover = (cogs / avg_inventory) if avg_inventory > 0 else 0
        
        # Fast and slow moving items
        fast_moving = SalesMaster.objects.filter(
            sale_entry_date__date__range=[self.start_date, self.end_date]
        ).values('productid__product_name').annotate(
            quantity_sold=Sum('sale_quantity')
        ).order_by('-quantity_sold')[:10]
        
        return {
            'inventory_value': inventory_value['total_value'] or 0,
            'total_items': inventory_value['total_items'] or 0,
            'total_stock': inventory_value['total_stock'] or 0,
            'inventory_turnover': inventory_turnover,
            'fast_moving_items': list(fast_moving),
            'days_inventory_outstanding': (avg_inventory / cogs * 365) if cogs > 0 else 0
        }
    
    def get_financial_ratios(self):
        """Calculate key financial ratios"""
        
        revenue_data = self.get_revenue_analysis()
        cost_data = self.get_cost_analysis()
        cash_flow_data = self.get_cash_flow_analysis()
        inventory_data = self.get_inventory_analysis()
        
        # Profitability ratios
        gross_profit_margin = ((revenue_data['total_revenue'] - cost_data['total_cost']) / revenue_data['total_revenue'] * 100) if revenue_data['total_revenue'] > 0 else 0
        
        # Efficiency ratios
        asset_turnover = revenue_data['total_revenue'] / inventory_data['inventory_value'] if inventory_data['inventory_value'] > 0 else 0
        
        # Liquidity ratios (simplified)
        current_ratio = cash_flow_data['total_inflow'] / cash_flow_data['total_outflow'] if cash_flow_data['total_outflow'] > 0 else 0
        
        return {
            'gross_profit_margin': gross_profit_margin,
            'asset_turnover': asset_turnover,
            'current_ratio': current_ratio,
            'inventory_turnover': inventory_data['inventory_turnover'],
            'days_sales_outstanding': self.calculate_days_sales_outstanding(),
            'return_on_assets': (revenue_data['total_revenue'] - cost_data['total_cost']) / inventory_data['inventory_value'] * 100 if inventory_data['inventory_value'] > 0 else 0
        }
    
    def get_trend_analysis(self):
        """Analyze trends over time"""
        
        # Monthly trends
        monthly_data = []
        current_date = self.start_date.replace(day=1)
        
        while current_date <= self.end_date:
            month_end = (current_date.replace(month=current_date.month + 1) if current_date.month < 12 else current_date.replace(year=current_date.year + 1, month=1)) - timedelta(days=1)
            
            month_sales = SalesMaster.objects.filter(
                sale_entry_date__date__range=[current_date, month_end]
            ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
            
            month_purchases = PurchaseMaster.objects.filter(
                purchase_entry_date__date__range=[current_date, month_end]
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            monthly_data.append({
                'month': current_date,
                'sales': month_sales,
                'purchases': month_purchases,
                'profit': month_sales - month_purchases
            })
            
            current_date = current_date.replace(month=current_date.month + 1) if current_date.month < 12 else current_date.replace(year=current_date.year + 1, month=1)
        
        return {
            'monthly_data': monthly_data,
            'sales_trend': 'increasing' if len(monthly_data) > 1 and monthly_data[-1]['sales'] > monthly_data[0]['sales'] else 'decreasing',
            'profit_trend': 'increasing' if len(monthly_data) > 1 and monthly_data[-1]['profit'] > monthly_data[0]['profit'] else 'decreasing'
        }
    
    def get_forecasts(self):
        """Generate simple forecasts based on trends"""
        
        trends = self.get_trend_analysis()
        monthly_data = trends['monthly_data']
        
        if len(monthly_data) < 2:
            return {'sales_forecast': 0, 'profit_forecast': 0}
        
        # Simple linear regression for forecasting
        sales_values = [month['sales'] for month in monthly_data]
        profit_values = [month['profit'] for month in monthly_data]
        
        # Calculate average growth rate
        sales_growth = (sales_values[-1] - sales_values[0]) / len(sales_values) if sales_values[0] > 0 else 0
        profit_growth = (profit_values[-1] - profit_values[0]) / len(profit_values) if profit_values[0] > 0 else 0
        
        return {
            'sales_forecast': sales_values[-1] + sales_growth,
            'profit_forecast': profit_values[-1] + profit_growth,
            'confidence_level': 'low'  # Simple forecast has low confidence
        }
    
    def calculate_days_sales_outstanding(self):
        """Calculate days sales outstanding (DSO)"""
        
        # Get outstanding receivables
        outstanding = 0
        sales_invoices = SalesInvoiceMaster.objects.all()
        
        for invoice in sales_invoices:
            invoice_total = SalesMaster.objects.filter(
                sales_invoice_no=invoice
            ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
            
            balance = invoice_total - invoice.sales_invoice_paid
            if balance > 0:
                outstanding += balance
        
        # Calculate average daily sales
        revenue_data = self.get_revenue_analysis()
        avg_daily_sales = revenue_data['revenue_per_day']
        
        return outstanding / avg_daily_sales if avg_daily_sales > 0 else 0
    
    def calculate_cash_conversion_cycle(self):
        """Calculate cash conversion cycle"""
        
        inventory_data = self.get_inventory_analysis()
        dso = self.calculate_days_sales_outstanding()
        
        # Days payable outstanding (simplified)
        dpo = 30  # Assume 30 days average payment terms
        
        return inventory_data['days_inventory_outstanding'] + dso - dpo
    
    def export_to_json(self):
        """Export comprehensive report to JSON"""
        
        report = self.get_comprehensive_report()
        
        # Convert Decimal and datetime objects to JSON serializable format
        def json_serializer(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, 'date'):
                return obj.date().isoformat()
            return str(obj)
        
        return json.dumps(report, default=json_serializer, indent=2)