from django.urls import path, include
from . import views
from .combined_invoice_view import add_invoice_with_products, get_existing_batches, cleanup_duplicate_batches
from .low_stock_views import low_stock_update, update_low_stock_item, bulk_update_low_stock, get_batch_suggestions
from .bulk_upload_views import bulk_upload_products, download_product_template

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User management
    path('register/', views.register_user, name='register'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/update/', views.update_user, name='update_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('profile/', views.profile, name='profile'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Pharmacy details
    path('pharmacy-details/', views.pharmacy_details, name='pharmacy_details'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/bulk-upload/', bulk_upload_products, name='bulk_upload_products'),
    path('products/download-template/', download_product_template, name='download_product_template'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/update/', views.update_product, name='update_product'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('products/export-pdf/', views.export_products_pdf, name='export_products_pdf'),
    path('products/export-excel/', views.export_products_excel, name='export_products_excel'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/update/', views.update_supplier, name='update_supplier'),
    path('suppliers/<int:pk>/delete/', views.delete_supplier, name='delete_supplier'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/update/', views.update_customer, name='update_customer'),
    path('customers/<int:pk>/delete/', views.delete_customer, name='delete_customer'),
    
    # Purchase Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/add/', views.add_invoice, name='add_invoice'),
    path('invoices/add-with-products/', views.add_invoice_with_products, name='add_invoice_with_products'),

    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.edit_invoice, name='edit_invoice'),
    path('invoices/<int:pk>/delete/', views.delete_invoice, name='delete_invoice'),
    path('invoices/<int:invoice_id>/add-purchase/', views.add_purchase, name='add_purchase'),
    path('invoices/<int:invoice_id>/edit-purchase/<int:purchase_id>/', views.edit_purchase, name='edit_purchase'),
    path('invoices/<int:invoice_id>/delete-purchase/<int:purchase_id>/', views.delete_purchase, name='delete_purchase'),
    path('invoices/<int:invoice_id>/add-payment/', views.add_invoice_payment, name='add_invoice_payment'),
    path('invoices/<int:invoice_id>/edit-payment/<int:payment_id>/', views.edit_invoice_payment, name='edit_invoice_payment'),
    path('invoices/<int:invoice_id>/delete-payment/<int:payment_id>/', views.delete_invoice_payment, name='delete_invoice_payment'),
    
    # Sales Invoices
    path('sales/', views.sales_invoice_list, name='sales_invoice_list'),
    path('sales/add/', views.add_sales_invoice, name='add_sales_invoice'),
    path('sales/add-with-products/', views.add_sales_invoice_with_products, name='add_sales_invoice_with_products'),
    path('sales/<str:pk>/', views.sales_invoice_detail, name='sales_invoice_detail'),
    path('sales/<str:pk>/edit/', views.edit_sales_invoice, name='edit_sales_invoice'),
    path('sales/<str:pk>/print/', views.print_sales_bill, name='print_sales_bill'),
    path('sales/<str:pk>/print-receipt/', views.print_receipt, name='print_receipt'),
    path('sales/<str:pk>/delete/', views.delete_sales_invoice, name='delete_sales_invoice'),
    path('sales/<str:invoice_id>/add-sale/', views.add_sale, name='add_sale'),
    path('sales/<str:invoice_id>/edit-sale/<int:sale_id>/', views.edit_sale, name='edit_sale'),
    path('sales/<str:invoice_id>/delete-sale/<int:sale_id>/', views.delete_sale, name='delete_sale'),
    path('sales/<str:invoice_id>/add-payment/', views.add_sales_payment, name='add_sales_payment'),
    path('sales/<str:invoice_id>/edit-payment/<int:payment_id>/', views.edit_sales_payment, name='edit_sales_payment'),
    path('sales/<str:invoice_id>/delete-payment/<int:payment_id>/', views.delete_sales_payment, name='delete_sales_payment'),
    
    # Purchase Returns
    path('purchase-returns/', views.purchase_return_list, name='purchase_return_list'),
    path('purchase-returns/add/', views.add_purchase_return, name='add_purchase_return'),
    path('purchase-returns/<str:pk>/', views.purchase_return_detail, name='purchase_return_detail'),
    path('purchase-returns/<str:pk>/edit/', views.edit_purchase_return, name='edit_purchase_return'),
    path('purchase-returns/<str:pk>/delete/', views.delete_purchase_return, name='delete_purchase_return'),
    path('purchase-returns/<str:return_id>/add-item/', views.add_purchase_return_item, name='add_purchase_return_item'),
    path('purchase-returns/<str:return_id>/edit-item/<int:item_id>/', views.edit_purchase_return_item, name='edit_purchase_return_item'),
    path('purchase-returns/<str:return_id>/delete-item/<int:item_id>/', views.delete_purchase_return_item, name='delete_purchase_return_item'),
    
    # Sales Returns
    path('sales-returns/', views.sales_return_list, name='sales_return_list'),
    path('sales-returns/add/', views.add_sales_return, name='add_sales_return'),
    path('sales-returns/<str:pk>/', views.sales_return_detail, name='sales_return_detail'),
    path('sales-returns/<str:pk>/delete/', views.delete_sales_return, name='delete_sales_return'),
    path('sales-returns/<str:return_id>/add-item/', views.add_sales_return_item, name='add_sales_return_item'),
    path('sales-returns/<str:return_id>/edit-item/<int:item_id>/', views.edit_sales_return_item, name='edit_sales_return_item'),
    path('sales-returns/<str:return_id>/delete-item/<int:item_id>/', views.delete_sales_return_item, name='delete_sales_return_item'),
    path('sales-returns/<str:return_id>/add-payment/', views.add_sales_return_payment, name='add_sales_return_payment'),
    path('sales-returns/<str:return_id>/edit-payment/<int:payment_id>/', views.edit_sales_return_payment, name='edit_sales_return_payment'),
    path('sales-returns/<str:return_id>/delete-payment/<int:payment_id>/', views.delete_sales_return_payment, name='delete_sales_return_payment'),
    
    # Sales Return API endpoints
    path('api/sales-invoices-for-customer/', views.get_sales_invoices_for_customer, name='get_sales_invoices_for_customer'),
    path('api/sales-invoice-items/', views.get_sales_invoice_items, name='get_sales_invoice_items'), 
    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    
    # Reports
    path('reports/inventory/batch/', views.batch_inventory_report, name='batch_inventory_report'),
    path('reports/inventory/expiry/', views.dateexpiry_inventory_report, name='dateexpiry_inventory_report'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/sales/analytics/', views.sales_report, name='enhanced_sales_analytics'),
    path('reports/purchases/', views.purchase_report, name='purchase_report'),
    path('reports/financial/', views.financial_report, name='financial_report'),
    
    # API endpoints for AJAX calls
    path('get-product-info/', views.get_product_info, name='get_product_info'),
    path('api/product-info/', views.get_product_info, name='get_product_info_api'),
    path('api/product-by-barcode/', views.get_product_by_barcode, name='get_product_by_barcode'),
    path('api/export-inventory/', views.export_inventory_csv, name='export_inventory_csv'),
    path('api/sales-analytics/', views.get_sales_analytics_api, name='get_sales_analytics_api'),

    
    # Export URLs
    path('export/inventory/pdf/', views.export_inventory_pdf, name='export_inventory_pdf'),
    path('export/inventory/excel/', views.export_inventory_excel, name='export_inventory_excel'),
    path('export/sales/pdf/', views.export_sales_pdf, name='export_sales_pdf'),
    path('export/sales/excel/', views.export_sales_excel, name='export_sales_excel'),
    path('export/purchases/pdf/', views.export_purchases_pdf, name='export_purchases_pdf'),
    # path('export/purchases/excel/', views.export_purchases_excel, name='export/financial/pdf/', views.export_financial_pdf, name='export_financial_pdf'),
    path('export/purchases/excel/', views.export_purchases_excel, name='export_purchases_excel'),
path('export/financial/pdf/', views.export_financial_pdf, name='export_financial_pdf'),

    path('export/financial/excel/', views.export_financial_excel, name='export_financial_excel'),
    
    # Sale Rate Management
    path('rates/', views.sale_rate_list, name='sale_rate_list'),
    path('rates/add/', views.add_sale_rate, name='add_sale_rate'),
    path('rates/<int:pk>/update/', views.update_sale_rate, name='update_sale_rate'),
    path('rates/<int:pk>/delete/', views.delete_sale_rate, name='delete_sale_rate'),
    
    # API endpoints for batch functionality
    path('api/product-batches/', views.get_product_batches, name='get_product_batches'),
    path('api/batch-details/', views.get_batch_details, name='get_batch_details'),
    path('api/product-batch-selector/', views.get_product_batch_selector, name='api_product_batch_selector'),
    path('api/search-products/', views.search_products_api, name='search_products_api'),
    path('api/customer-rate-info/', views.get_customer_rate_info, name='api_customer_rate_info'),
    path('api/get-batch-rates/', views.get_batch_rates, name='get_batch_rates'),
    path('api/update-purchase-return/', views.update_purchase_return_api, name='update_purchase_return_api'),
    path('api/update-sales-return/', views.update_sales_return_api, name='update_sales_return_api'),
    path('api/delete-sales-return-item/', views.delete_sales_return_item_api, name='delete_sales_return_item_api'),
    
    # Stock Management APIs
    path('api/existing-batches/', get_existing_batches, name='get_existing_batches'),
    path('api/cleanup-duplicate-batches/', cleanup_duplicate_batches, name='cleanup_duplicate_batches'),
    
    # Low Stock Update
    path('inventory/low-stock-update/', low_stock_update, name='low_stock_update'),
    path('api/update-low-stock-item/', update_low_stock_item, name='update_low_stock_item'),
    path('api/bulk-update-low-stock/', bulk_update_low_stock, name='bulk_update_low_stock'),
    path('get-batch-suggestions/', get_batch_suggestions, name='get_batch_suggestions'),
    
    # Finance - Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.add_payment, name='add_payment'),
    path('payments/<int:pk>/edit/', views.edit_payment, name='edit_payment'),
    path('payments/<int:pk>/delete/', views.delete_payment, name='delete_payment'),
    path('payments/export-pdf/', views.export_payments_pdf, name='export_payments_pdf'),
    path('payments/export-excel/', views.export_payments_excel, name='export_payments_excel'),
    
    # Finance - Receipts
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipts/add/', views.add_receipt, name='add_receipt'),
    path('receipts/<int:pk>/edit/', views.edit_receipt, name='edit_receipt'),
    path('receipts/<int:pk>/delete/', views.delete_receipt, name='delete_receipt'),
    path('receipts/export-pdf/', views.export_receipts_pdf, name='export_receipts_pdf'),
    path('receipts/export-excel/', views.export_receipts_excel, name='export_receipts_excel'),
    


]

