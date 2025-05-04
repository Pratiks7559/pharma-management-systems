from django.urls import path
from . import views

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
    path('products/bulk-upload/', views.bulk_upload_products, name='bulk_upload_products'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/update/', views.update_product, name='update_product'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    
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
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
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
    path('sales/<str:pk>/', views.sales_invoice_detail, name='sales_invoice_detail'),
    path('sales/<str:pk>/print/', views.print_sales_bill, name='print_sales_bill'),
    path('sales/<str:pk>/delete/', views.delete_sales_invoice, name='delete_sales_invoice'),
    path('sales/<str:invoice_id>/add-sale/', views.add_sale, name='add_sale'),
    path('sales/<str:invoice_id>/edit-sale/<int:sale_id>/', views.edit_sale, name='edit_sale'),
    path('sales/<str:invoice_id>/delete-sale/<int:sale_id>/', views.delete_sale, name='delete_sale'),
    path('sales/<str:invoice_id>/add-payment/', views.add_sales_payment, name='add_sales_payment'),
    
    # Purchase Returns
    path('purchase-returns/', views.purchase_return_list, name='purchase_return_list'),
    path('purchase-returns/add/', views.add_purchase_return, name='add_purchase_return'),
    path('purchase-returns/<str:pk>/', views.purchase_return_detail, name='purchase_return_detail'),
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
    
    # Reports
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/inventory/batch/', views.batch_inventory_report, name='batch_inventory_report'),
    path('reports/inventory/expiry/', views.dateexpiry_inventory_report, name='dateexpiry_inventory_report'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/purchases/', views.purchase_report, name='purchase_report'),
    path('reports/financial/', views.financial_report, name='financial_report'),
    
    # API endpoints for AJAX calls
    path('api/product-info/', views.get_product_info, name='get_product_info'),
    path('api/export-inventory/', views.export_inventory_csv, name='export_inventory_csv'),
    
    # Sale Rate Management
    path('rates/', views.sale_rate_list, name='sale_rate_list'),
    path('rates/add/', views.add_sale_rate, name='add_sale_rate'),
    path('rates/<int:pk>/update/', views.update_sale_rate, name='update_sale_rate'),
    path('rates/<int:pk>/delete/', views.delete_sale_rate, name='delete_sale_rate'),
]
