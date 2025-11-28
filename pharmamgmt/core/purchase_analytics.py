from django.db.models import Sum, Count, Avg, Max, Min
from datetime import datetime, timedelta
from .models import (
    InvoiceMaster, PurchaseMaster, SupplierMaster, ProductMaster, 
    InvoicePaid
)

class PurchaseAnalytics:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        
        # Get filtered invoices for the period
        self.invoices = InvoiceMaster.objects.filter(
            invoice_date__range=[start_date, end_date]
        ).select_related('supplierid').order_by('-invoice_date')
        
        # Get purchase items for the period
        self.purchase_items = PurchaseMaster.objects.filter(
            product_invoiceid__in=self.invoices
        ).select_related('productid', 'product_supplierid')
    
    def get_core_metrics(self):
        """Calculate core purchase metrics"""
        total_purchases = self.invoices.aggregate(Sum('invoice_total'))['invoice_total__sum'] or 0
        total_paid = self.invoices.aggregate(Sum('invoice_paid'))['invoice_paid__sum'] or 0
        total_pending = total_purchases - total_paid
        total_invoices = self.invoices.count()
        
        # Calculate payment rate
        payment_rate = (total_paid / total_purchases * 100) if total_purchases > 0 else 0
        pending_rate = (total_pending / total_purchases * 100) if total_purchases > 0 else 0
        
        # Average invoice value
        avg_invoice_value = total_purchases / total_invoices if total_invoices > 0 else 0
        
        return {
            'total_purchases': total_purchases,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'total_invoices': total_invoices,
            'payment_rate': payment_rate,
            'pending_rate': pending_rate,
            'avg_invoice_value': avg_invoice_value
        }
    
    def get_invoice_analysis(self):
        """Analyze invoice payment status"""
        paid_invoices = 0
        partial_paid = 0
        unpaid_invoices = 0
        largest_invoice = 0
        smallest_invoice = float('inf')
        
        for invoice in self.invoices:
            if invoice.invoice_paid >= invoice.invoice_total:
                paid_invoices += 1
            elif invoice.invoice_paid > 0:
                partial_paid += 1
            else:
                unpaid_invoices += 1
            
            if invoice.invoice_total > largest_invoice:
                largest_invoice = invoice.invoice_total
            if invoice.invoice_total < smallest_invoice:
                smallest_invoice = invoice.invoice_total
        
        if smallest_invoice == float('inf'):
            smallest_invoice = 0
        
        return {
            'paid_invoices': paid_invoices,
            'partial_paid': partial_paid,
            'unpaid_invoices': unpaid_invoices,
            'largest_invoice': largest_invoice,
            'smallest_invoice': smallest_invoice
        }
    
    def get_realtime_stats(self):
        """Calculate real-time purchase statistics"""
        unique_suppliers = len(set(invoice.supplierid.supplierid for invoice in self.invoices))
        unique_products = len(set(item.productid.productid for item in self.purchase_items))
        
        total_products_purchased = sum(item.product_quantity or 0 for item in self.purchase_items)
        total_discount_received = sum(item.product_discount_got or 0 for item in self.purchase_items)
        
        # Calculate total purchase value
        total_purchase_value = sum(
            (item.product_purchase_rate or 0) * (item.product_quantity or 0) 
            for item in self.purchase_items
        )
        
        avg_discount_rate = (total_discount_received / total_purchase_value * 100) if total_purchase_value > 0 else 0
        
        # Average items per invoice
        avg_items_per_invoice = total_products_purchased / self.invoices.count() if self.invoices.count() > 0 else 0
        
        # Total transport charges
        total_transport_charges = sum(invoice.transport_charges or 0 for invoice in self.invoices)
        
        return {
            'unique_suppliers': unique_suppliers,
            'unique_products': unique_products,
            'total_products_purchased': total_products_purchased,
            'total_discount_received': total_discount_received,
            'avg_discount_rate': avg_discount_rate,
            'avg_items_per_invoice': avg_items_per_invoice,
            'total_transport_charges': total_transport_charges
        }
    
    def get_product_analytics(self):
        """Get product-wise purchase analysis"""
        # Simple aggregation without complex functions
        product_data = {}
        for item in self.purchase_items:
            key = f"{item.productid.product_name}_{item.productid.product_company}"
            if key not in product_data:
                product_data[key] = {
                    'productid__product_name': item.productid.product_name,
                    'productid__product_company': item.productid.product_company,
                    'productid__product_category': item.productid.product_category,
                    'total_quantity': 0,
                    'total_amount': 0,
                    'rates': [],
                    'invoice_count': set(),
                    'batch_count': set(),
                    'discounts': [],
                    'last_purchase_date': None
                }
            
            product_data[key]['total_quantity'] += item.product_quantity or 0
            product_data[key]['total_amount'] += item.total_amount or 0
            product_data[key]['rates'].append(item.product_actual_rate or 0)
            product_data[key]['invoice_count'].add(item.product_invoiceid.invoiceid)
            product_data[key]['batch_count'].add(item.product_batch_no)
            product_data[key]['discounts'].append(item.product_discount_got or 0)
            
            if not product_data[key]['last_purchase_date'] or item.product_invoiceid.invoice_date > product_data[key]['last_purchase_date']:
                product_data[key]['last_purchase_date'] = item.product_invoiceid.invoice_date
        
        # Calculate averages
        result = []
        for key, data in product_data.items():
            data['avg_rate'] = sum(data['rates']) / len(data['rates']) if data['rates'] else 0
            data['invoice_count'] = len(data['invoice_count'])
            data['batch_count'] = len(data['batch_count'])
            data['avg_discount'] = sum(data['discounts']) / len(data['discounts']) if data['discounts'] else 0
            # Remove helper fields
            del data['rates']
            del data['discounts']
            result.append(data)
        
        return sorted(result, key=lambda x: x['total_amount'], reverse=True)
    
    def get_supplier_analytics(self):
        """Get supplier-wise purchase analysis"""
        # Simple calculation without complex aggregations
        supplier_data = {}
        for invoice in self.invoices:
            supplier_name = invoice.supplierid.supplier_name
            if supplier_name not in supplier_data:
                supplier_data[supplier_name] = {
                    'supplierid__supplier_name': supplier_name,
                    'supplierid__supplier_type': invoice.supplierid.supplier_type,
                    'supplierid__supplier_mobile': invoice.supplierid.supplier_mobile,
                    'supplierid__supplier_emailid': invoice.supplierid.supplier_emailid,
                    'total_amount': 0,
                    'total_paid': 0,
                    'invoice_count': 0,
                    'invoice_values': [],
                    'last_purchase_date': None
                }
            
            supplier_data[supplier_name]['total_amount'] += invoice.invoice_total or 0
            supplier_data[supplier_name]['total_paid'] += invoice.invoice_paid or 0
            supplier_data[supplier_name]['invoice_count'] += 1
            supplier_data[supplier_name]['invoice_values'].append(invoice.invoice_total or 0)
            
            if not supplier_data[supplier_name]['last_purchase_date'] or invoice.invoice_date > supplier_data[supplier_name]['last_purchase_date']:
                supplier_data[supplier_name]['last_purchase_date'] = invoice.invoice_date
        
        # Calculate derived values
        result = []
        for supplier_name, data in supplier_data.items():
            data['pending_amount'] = data['total_amount'] - data['total_paid']
            data['payment_rate'] = (data['total_paid'] / data['total_amount'] * 100) if data['total_amount'] > 0 else 0
            data['avg_invoice_value'] = sum(data['invoice_values']) / len(data['invoice_values']) if data['invoice_values'] else 0
            del data['invoice_values']
            result.append(data)
        
        return sorted(result, key=lambda x: x['total_amount'], reverse=True)
    
    def get_category_analytics(self):
        """Get category-wise purchase analysis"""
        category_data = {}
        for item in self.purchase_items:
            category = item.productid.product_category or 'Uncategorized'
            if category not in category_data:
                category_data[category] = {
                    'productid__product_category': category,
                    'total_quantity': 0,
                    'total_amount': 0,
                    'rates': [],
                    'products': set(),
                    'invoices': set()
                }
            
            category_data[category]['total_quantity'] += item.product_quantity or 0
            category_data[category]['total_amount'] += item.total_amount or 0
            category_data[category]['rates'].append(item.product_actual_rate or 0)
            category_data[category]['products'].add(item.productid.productid)
            category_data[category]['invoices'].add(item.product_invoiceid.invoiceid)
        
        result = []
        for category, data in category_data.items():
            data['avg_rate'] = sum(data['rates']) / len(data['rates']) if data['rates'] else 0
            data['product_count'] = len(data['products'])
            data['invoice_count'] = len(data['invoices'])
            del data['rates']
            del data['products']
            del data['invoices']
            result.append(data)
        
        return sorted(result, key=lambda x: x['total_amount'], reverse=True)
    
    def get_daily_trend(self):
        """Get daily purchase trend"""
        daily_data = {}
        for invoice in self.invoices:
            day = invoice.invoice_date
            if day not in daily_data:
                daily_data[day] = {
                    'day': day,
                    'daily_total': 0,
                    'invoice_count': 0
                }
            daily_data[day]['daily_total'] += invoice.invoice_total or 0
            daily_data[day]['invoice_count'] += 1
        
        return sorted(daily_data.values(), key=lambda x: x['day'])
    
    def get_monthly_trend(self):
        """Get monthly purchase trend"""
        monthly_data = {}
        for invoice in self.invoices:
            month = invoice.invoice_date.replace(day=1)
            if month not in monthly_data:
                monthly_data[month] = {
                    'month': month,
                    'monthly_total': 0,
                    'invoice_count': 0
                }
            monthly_data[month]['monthly_total'] += invoice.invoice_total or 0
            monthly_data[month]['invoice_count'] += 1
        
        return sorted(monthly_data.values(), key=lambda x: x['month'])
    
    def get_top_performers(self):
        """Get top performing products and suppliers"""
        top_products = self.get_product_analytics()[:10]
        top_suppliers = self.get_supplier_analytics()[:10]
        
        return {
            'top_products': top_products,
            'top_suppliers': top_suppliers
        }
    
    def get_payment_analysis(self):
        """Analyze payment patterns"""
        # Simple payment mode analysis
        payment_data = {}
        payments = InvoicePaid.objects.filter(ip_invoiceid__in=self.invoices)
        
        for payment in payments:
            mode = payment.payment_mode or 'Unknown'
            if mode not in payment_data:
                payment_data[mode] = {
                    'payment_mode': mode,
                    'total_amount': 0,
                    'payment_count': 0
                }
            payment_data[mode]['total_amount'] += payment.payment_amount or 0
            payment_data[mode]['payment_count'] += 1
        
        payment_modes = sorted(payment_data.values(), key=lambda x: x['total_amount'], reverse=True)
        core_metrics = self.get_core_metrics()
        
        return {
            'payment_rate': core_metrics['payment_rate'],
            'pending_rate': core_metrics['pending_rate'],
            'payment_modes': payment_modes,
            'avg_payment_days': 0
        }
    
    def get_comprehensive_report(self):
        """Get complete purchase analytics report"""
        # Prepare invoice data with calculated totals
        invoices_data = []
        for invoice in self.invoices:
            invoices_data.append({
                'invoiceid': invoice.invoiceid,
                'invoice_no': invoice.invoice_no,
                'invoice_date': invoice.invoice_date,
                'supplier_name': invoice.supplierid.supplier_name,
                'supplier_type': invoice.supplierid.supplier_type,
                'invoice_total': invoice.invoice_total,
                'invoice_paid': invoice.invoice_paid,
                'transport_charges': invoice.transport_charges
            })
        
        return {
            'invoices': invoices_data,
            'core_metrics': self.get_core_metrics(),
            'invoice_analysis': self.get_invoice_analysis(),
            'realtime_stats': self.get_realtime_stats(),
            'product_analytics': list(self.get_product_analytics()),
            'supplier_analytics': list(self.get_supplier_analytics()),
            'category_analytics': list(self.get_category_analytics()),
            'daily_trend': list(self.get_daily_trend()),
            'monthly_trend': list(self.get_monthly_trend()),
            'top_performers': self.get_top_performers(),
            'payment_analysis': self.get_payment_analysis()
        }