from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Web_User, Pharmacy_Details, ProductMaster, SupplierMaster, CustomerMaster,
    InvoiceMaster, InvoicePaid, PurchaseMaster, SalesInvoiceMaster, SalesMaster,
    SalesInvoicePaid, ProductRateMaster, ReturnInvoiceMaster, PurchaseReturnInvoicePaid,
    ReturnPurchaseMaster, ReturnSalesInvoiceMaster, ReturnSalesInvoicePaid, ReturnSalesMaster
)

# Define custom admin classes

class Web_UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'user_contact', 'path')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'user_contact', 'path')}),
    )

class PharmacyDetailsAdmin(admin.ModelAdmin):
    list_display = ('pharmaname', 'proprietorname', 'proprietorcontact', 'proprietoremail')

class ProductMasterAdmin(admin.ModelAdmin):
    list_display = ('productid', 'product_name', 'product_company', 'product_packing', 'product_category', 'product_barcode')
    search_fields = ('product_name', 'product_company', 'product_salt', 'product_barcode')
    list_filter = ('product_category',)

class SupplierMasterAdmin(admin.ModelAdmin):
    list_display = ('supplierid', 'supplier_name', 'supplier_type', 'supplier_mobile', 'supplier_emailid')
    search_fields = ('supplier_name', 'supplier_mobile', 'supplier_emailid')

class CustomerMasterAdmin(admin.ModelAdmin):
    list_display = ('customerid', 'customer_name', 'customer_type', 'customer_mobile', 'customer_emailid')
    search_fields = ('customer_name', 'customer_mobile', 'customer_emailid')
    list_filter = ('customer_type',)

class InvoiceMasterAdmin(admin.ModelAdmin):
    list_display = ('invoiceid', 'invoice_no', 'invoice_date', 'supplierid', 'invoice_total', 'invoice_paid')
    list_filter = ('invoice_date',)
    search_fields = ('invoice_no', 'supplierid__supplier_name')

class PurchaseMasterAdmin(admin.ModelAdmin):
    list_display = ('purchaseid', 'product_name', 'product_company', 'product_batch_no', 
                    'product_quantity', 'product_expiry', 'total_amount')
    list_filter = ('purchase_entry_date', 'product_company')
    search_fields = ('product_name', 'product_batch_no', 'product_company')

class SalesInvoiceMasterAdmin(admin.ModelAdmin):
    list_display = ('sales_invoice_no', 'sales_invoice_date', 'customerid', 
                    'sales_invoice_total', 'sales_invoice_paid')
    list_filter = ('sales_invoice_date',)
    search_fields = ('sales_invoice_no', 'customerid__customer_name')

class SalesMasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'sales_invoice_no', 'product_name', 'product_batch_no', 
                   'sale_quantity', 'sale_rate', 'sale_total_amount')
    list_filter = ('sale_entry_date',)
    search_fields = ('product_name', 'product_batch_no', 'sales_invoice_no__sales_invoice_no')

# Register models with admin site
admin.site.register(Web_User, Web_UserAdmin)
admin.site.register(Pharmacy_Details, PharmacyDetailsAdmin)
admin.site.register(ProductMaster, ProductMasterAdmin)
admin.site.register(SupplierMaster, SupplierMasterAdmin)
admin.site.register(CustomerMaster, CustomerMasterAdmin)
admin.site.register(InvoiceMaster, InvoiceMasterAdmin)
admin.site.register(InvoicePaid)
admin.site.register(PurchaseMaster, PurchaseMasterAdmin)
admin.site.register(SalesInvoiceMaster, SalesInvoiceMasterAdmin)
admin.site.register(SalesMaster, SalesMasterAdmin)
admin.site.register(SalesInvoicePaid)
admin.site.register(ProductRateMaster)
admin.site.register(ReturnInvoiceMaster)
admin.site.register(PurchaseReturnInvoicePaid)
admin.site.register(ReturnPurchaseMaster)
admin.site.register(ReturnSalesInvoiceMaster)
admin.site.register(ReturnSalesInvoicePaid)
admin.site.register(ReturnSalesMaster)
