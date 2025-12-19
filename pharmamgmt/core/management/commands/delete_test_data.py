from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import *


class Command(BaseCommand):
    help = 'Delete all test data from database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete everything including Products, Customers, Suppliers',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING('⚠️  WARNING: This will delete test data!'))
            confirm = input('Type "DELETE" to confirm: ')
            if confirm != 'DELETE':
                self.stdout.write(self.style.ERROR('❌ Operation cancelled'))
                return

        self.stdout.write(self.style.SUCCESS('🗑️  Starting deletion...'))

        try:
            with transaction.atomic():
                # Delete in correct order
                counts = {}
                
                # Sales Returns
                counts['sales_return_items'] = ReturnSalesMaster.objects.all().count()
                ReturnSalesMaster.objects.all().delete()
                
                counts['sales_return_payments'] = ReturnSalesInvoicePaid.objects.all().count()
                ReturnSalesInvoicePaid.objects.all().delete()
                
                counts['sales_return_invoices'] = ReturnSalesInvoiceMaster.objects.all().count()
                ReturnSalesInvoiceMaster.objects.all().delete()
                
                # Purchase Returns
                counts['purchase_return_items'] = ReturnPurchaseMaster.objects.all().count()
                ReturnPurchaseMaster.objects.all().delete()
                
                counts['purchase_return_payments'] = PurchaseReturnInvoicePaid.objects.all().count()
                PurchaseReturnInvoicePaid.objects.all().delete()
                
                counts['purchase_return_invoices'] = ReturnInvoiceMaster.objects.all().count()
                ReturnInvoiceMaster.objects.all().delete()
                
                # Sales
                counts['sales_items'] = SalesMaster.objects.all().count()
                SalesMaster.objects.all().delete()
                
                counts['sales_payments'] = SalesInvoicePaid.objects.all().count()
                SalesInvoicePaid.objects.all().delete()
                
                counts['sales_invoices'] = SalesInvoiceMaster.objects.all().count()
                SalesInvoiceMaster.objects.all().delete()
                
                # Purchases
                counts['purchase_items'] = PurchaseMaster.objects.all().count()
                PurchaseMaster.objects.all().delete()
                
                counts['purchase_payments'] = InvoicePaid.objects.all().count()
                InvoicePaid.objects.all().delete()
                
                counts['purchase_invoices'] = InvoiceMaster.objects.all().count()
                InvoiceMaster.objects.all().delete()
                
                # Challans
                counts['customer_challan_items'] = CustomerChallanMaster.objects.all().count()
                CustomerChallanMaster.objects.all().delete()
                
                counts['customer_challan_items2'] = CustomerChallanMaster2.objects.all().count()
                CustomerChallanMaster2.objects.all().delete()
                
                counts['customer_challans'] = CustomerChallan.objects.all().count()
                CustomerChallan.objects.all().delete()
                
                counts['supplier_challan_items'] = SupplierChallanMaster.objects.all().count()
                SupplierChallanMaster.objects.all().delete()
                
                counts['supplier_challan_items2'] = SupplierChallanMaster2.objects.all().count()
                SupplierChallanMaster2.objects.all().delete()
                
                counts['supplier_challans'] = Challan1.objects.all().count()
                Challan1.objects.all().delete()
                
                # Stock Issues
                counts['stock_issue_details'] = StockIssueDetail.objects.all().count()
                StockIssueDetail.objects.all().delete()
                
                counts['stock_issues'] = StockIssueMaster.objects.all().count()
                StockIssueMaster.objects.all().delete()
                
                # Contra
                counts['contra_entries'] = ContraEntry.objects.all().count()
                ContraEntry.objects.all().delete()
                
                # Rates
                counts['sale_rates'] = SaleRateMaster.objects.all().count()
                SaleRateMaster.objects.all().delete()
                
                counts['product_rates'] = ProductRateMaster.objects.all().count()
                ProductRateMaster.objects.all().delete()
                
                # Optional: Delete Products, Customers, Suppliers
                if options['all']:
                    counts['products'] = ProductMaster.objects.all().count()
                    ProductMaster.objects.all().delete()
                    
                    counts['customers'] = CustomerMaster.objects.all().count()
                    CustomerMaster.objects.all().delete()
                    
                    counts['suppliers'] = SupplierMaster.objects.all().count()
                    SupplierMaster.objects.all().delete()
                
                # Display results
                self.stdout.write(self.style.SUCCESS('\n✅ Deletion Summary:'))
                total = 0
                for key, count in counts.items():
                    if count > 0:
                        self.stdout.write(f'   • {key.replace("_", " ").title()}: {count}')
                        total += count
                
                self.stdout.write(self.style.SUCCESS(f'\n🎯 Total records deleted: {total}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            raise
