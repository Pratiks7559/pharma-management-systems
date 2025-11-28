from django.urls import path
from .receipt_views import (
    add_receipt, 
    receipt_list, 
    get_customer_invoices_api, 
    search_customers_api
)
from . import views

urlpatterns = [
    path('', receipt_list, name='receipt_list'),
    path('add/', add_receipt, name='add_receipt'),
    path('api/customer-invoices/', get_customer_invoices_api, name='get_customer_invoices_api'),
    path('api/search-customers/', search_customers_api, name='search_customers_api'),
    path('api/search-customer-invoices/', views.search_customer_invoices, name='search_customer_invoices_api'),
]