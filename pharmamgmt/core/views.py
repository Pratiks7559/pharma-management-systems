from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q, Func, Value
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse
from datetime import datetime, timedelta
import json
import csv

from .models import (
    Web_User, Pharmacy_Details, ProductMaster, SupplierMaster, CustomerMaster,
    InvoiceMaster, InvoicePaid, PurchaseMaster, SalesInvoiceMaster, SalesMaster,
    SalesInvoicePaid, ProductRateMaster, ReturnInvoiceMaster, PurchaseReturnInvoicePaid,
    ReturnPurchaseMaster, ReturnSalesInvoiceMaster, ReturnSalesInvoicePaid, ReturnSalesMaster,
    SaleRateMaster
)
from .forms import (
    LoginForm, UserRegistrationForm, UserUpdateForm, PharmacyDetailsForm, ProductForm,
    SupplierForm, CustomerForm, InvoiceForm, InvoicePaymentForm, PurchaseForm,
    SalesInvoiceForm, SalesForm, SalesPaymentForm, ProductRateForm,
    PurchaseReturnInvoiceForm, PurchaseReturnForm, SalesReturnInvoiceForm, SalesReturnForm
)
from .utils import get_stock_status, get_batch_stock_status, generate_invoice_pdf, generate_sales_invoice_pdf, get_avg_mrp

# Authentication views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name()}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
        
    context = {
        'form': form,
        'title': 'Login'
    }
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')

@login_required
def register_user(request):
    if not request.user.user_type == 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}!")
            return redirect('user_list')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Register User'
    }
    return render(request, 'profile.html', context)

@login_required
def user_list(request):
    if not request.user.user_type == 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    users = Web_User.objects.all().order_by('username')
    
    context = {
        'users': users,
        'title': 'User List'
    }
    return render(request, 'user_list.html', context)

@login_required
def update_user(request, pk):
    if not request.user.user_type == 'admin' and not request.user.id == pk:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    user = get_object_or_404(Web_User, id=pk)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Account updated for {user.username}!")
            if request.user.user_type == 'admin':
                return redirect('user_list')
            else:
                return redirect('profile')
    else:
        form = UserUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'title': 'Update User'
    }
    return render(request, 'profile.html', context)

@login_required
def profile(request):
    return update_user(request, request.user.id)

# Dashboard
@login_required
def dashboard(request):
    # Get counts for dashboard cards
    product_count = ProductMaster.objects.count()
    supplier_count = SupplierMaster.objects.count()
    customer_count = CustomerMaster.objects.count()
    
    # Get recent sales
    recent_sales = SalesInvoiceMaster.objects.order_by('-sales_invoice_date')[:5]
    
    # Get recent purchases
    recent_purchases = InvoiceMaster.objects.order_by('-invoice_date')[:5]
    
    # Get low stock products
    low_stock_products = []
    products = ProductMaster.objects.all()
    
    for product in products:
        stock_info = get_stock_status(product.productid)
        if stock_info['current_stock'] <= 10:  # Threshold for low stock
            low_stock_products.append({
                'product': product,
                'current_stock': stock_info['current_stock']
            })
    
    # Get expired or near-expiry products
    today = timezone.now().date()
    expiry_threshold = today + timedelta(days=90)  # 3 months threshold
    
    expired_products = PurchaseMaster.objects.filter(
        product_expiry__lte=expiry_threshold
    ).order_by('product_expiry')[:10]
    
    # Calculate financial overview
    current_month_start = today.replace(day=1)
    
    # Monthly sales
    monthly_sales_invoices = SalesInvoiceMaster.objects.filter(
        sales_invoice_date__gte=current_month_start
    )
    monthly_sales = SalesMaster.objects.filter(
        sales_invoice_no__in=monthly_sales_invoices
    ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
    
    # Monthly purchases
    monthly_purchases = InvoiceMaster.objects.filter(
        invoice_date__gte=current_month_start
    ).aggregate(total=Sum('invoice_total'))['total'] or 0
    
    # Total outstanding payments from customers
    # Calculate total sales amounts
    sales_totals = SalesMaster.objects.values('sales_invoice_no').annotate(
        invoice_total=Sum('sale_total_amount')
    )
    
    # Create a dictionary mapping invoice numbers to their total amounts
    invoice_totals = {item['sales_invoice_no']: item['invoice_total'] for item in sales_totals}
    
    # Calculate total receivable
    total_receivable = 0
    for invoice in SalesInvoiceMaster.objects.all():
        invoice_total = invoice_totals.get(invoice.sales_invoice_no, 0)
        total_receivable += (invoice_total - invoice.sales_invoice_paid)
    
    # Total outstanding payments to suppliers
    total_payable = InvoiceMaster.objects.aggregate(
        total=Sum(F('invoice_total') - F('invoice_paid'))
    )['total'] or 0
    
    context = {
        'title': 'Dashboard',
        'product_count': product_count,
        'supplier_count': supplier_count,
        'customer_count': customer_count,
        'recent_sales': recent_sales,
        'recent_purchases': recent_purchases,
        'low_stock_products': low_stock_products,
        'expired_products': expired_products,
        'monthly_sales': monthly_sales,
        'monthly_purchases': monthly_purchases,
        'total_receivable': total_receivable,
        'total_payable': total_payable
    }
    return render(request, 'dashboard.html', context)

# Pharmacy Details
@login_required
def pharmacy_details(request):
    if not request.user.user_type == 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
        
    try:
        pharmacy = Pharmacy_Details.objects.first()
        form = PharmacyDetailsForm(instance=pharmacy)
    except Pharmacy_Details.DoesNotExist:
        pharmacy = None
        form = PharmacyDetailsForm()
    
    if request.method == 'POST':
        if pharmacy:
            form = PharmacyDetailsForm(request.POST, instance=pharmacy)
        else:
            form = PharmacyDetailsForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Pharmacy details updated successfully!")
            return redirect('pharmacy_details')
    
    context = {
        'form': form,
        'pharmacy': pharmacy,
        'title': 'Pharmacy Details'
    }
    return render(request, 'pharmacy_details.html', context)

# Product views
@login_required
def product_list(request):
    products = ProductMaster.objects.all().order_by('product_name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(product_company__icontains=search_query) |
            Q(product_salt__icontains=search_query)
        )
    
    # Get products with stock data for display
    products_with_stock = []
    for product in products:
        stock_info = get_stock_status(product.productid)
        product.stock_level = stock_info['current_stock']
        products_with_stock.append(product)
    
    # Pagination
    paginator = Paginator(products_with_stock, 10)  # 10 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'search_query': search_query,
        'title': 'Product List'
    }
    return render(request, 'products/product_list.html', context)

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.product_name}' added successfully!")
            return redirect('product_list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add Product'
    }
    return render(request, 'products/product_form.html', context)

@login_required
def update_product(request, pk):
    product = get_object_or_404(ProductMaster, productid=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.product_name}' updated successfully!")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': 'Update Product'
    }
    return render(request, 'products/product_form.html', context)

@login_required
def product_detail(request, pk):
    product = get_object_or_404(ProductMaster, productid=pk)
    
    # Get stock status
    stock_info = get_stock_status(pk)
    
    # Get purchase history
    purchases = PurchaseMaster.objects.filter(productid=pk).order_by('-purchase_entry_date')
    
    # Get sales history
    sales = SalesMaster.objects.filter(productid=pk).order_by('-sale_entry_date')
    
    # Get rate history
    rates = ProductRateMaster.objects.filter(rate_productid=pk).order_by('-rate_date')
    
    context = {
        'product': product,
        'stock_info': stock_info,
        'purchases': purchases,
        'sales': sales,
        'rates': rates,
        'title': f'Product: {product.product_name}'
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def bulk_upload_products(request):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('product_list')
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file:
            messages.error(request, "Please select a CSV file.")
            return redirect('bulk_upload_products')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "File must be a CSV.")
            return redirect('bulk_upload_products')
        
        # Process CSV file
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            success_count = 0
            error_count = 0
            errors = []
            
            for row in reader:
                try:
                    # Create or update product
                    product, created = ProductMaster.objects.update_or_create(
                        product_name=row.get('product_name', '').strip(),
                        product_company=row.get('product_company', '').strip(),
                        defaults={
                            'product_packing': row.get('product_packing', '').strip(),
                            'product_salt': row.get('product_salt', '').strip(),
                            'product_category': row.get('product_category', '').strip(),
                            'product_hsn': row.get('product_hsn', '').strip(),
                            'product_hsn_percent': row.get('product_hsn_percent', '').strip(),
                        }
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Error on row {reader.line_num}: {str(e)}")
            
            if success_count > 0:
                messages.success(request, f"Successfully processed {success_count} products.")
            
            if error_count > 0:
                messages.warning(request, f"Encountered {error_count} errors during import.")
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)
                if len(errors) > 10:
                    messages.error(request, f"... and {len(errors) - 10} more errors.")
            
            return redirect('product_list')
            
        except Exception as e:
            messages.error(request, f"Error processing CSV file: {str(e)}")
            return redirect('bulk_upload_products')
    
    # Generate a sample CSV for download
    if request.GET.get('sample'):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_template.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'product_name', 'product_company', 'product_packing', 
            'product_salt', 'product_category', 'product_hsn', 
            'product_hsn_percent'
        ])
        
        # Add sample row
        writer.writerow([
            'Paracetamol 500mg', 'ABC Pharma', '10x10',
            'Paracetamol', 'Analgesic', '30049099',
            '12'
        ])
        
        return response
    
    context = {
        'title': 'Bulk Upload Products'
    }
    return render(request, 'products/bulk_upload.html', context)

@login_required
def delete_product(request, pk):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('product_list')
        
    product = get_object_or_404(ProductMaster, productid=pk)
    
    if request.method == 'POST':
        product_name = product.product_name
        try:
            product.delete()
            messages.success(request, f"Product '{product_name}' deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete product. It is referenced by other records. Error: {str(e)}")
        return redirect('product_list')
    
    context = {
        'product': product,
        'title': 'Delete Product'
    }
    return render(request, 'products/product_confirm_delete.html', context)

# Supplier views
@login_required
def supplier_list(request):
    suppliers = SupplierMaster.objects.all().order_by('supplier_name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        suppliers = suppliers.filter(
            Q(supplier_name__icontains=search_query) | 
            Q(supplier_mobile__icontains=search_query) |
            Q(supplier_emailid__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(suppliers, 10)  # 10 suppliers per page
    page_number = request.GET.get('page')
    suppliers = paginator.get_page(page_number)
    
    context = {
        'suppliers': suppliers,
        'search_query': search_query,
        'title': 'Supplier List'
    }
    return render(request, 'suppliers/supplier_list.html', context)

@login_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f"Supplier '{supplier.supplier_name}' added successfully!")
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    
    context = {
        'form': form,
        'title': 'Add Supplier'
    }
    return render(request, 'suppliers/supplier_form.html', context)

@login_required
def update_supplier(request, pk):
    supplier = get_object_or_404(SupplierMaster, supplierid=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Supplier '{supplier.supplier_name}' updated successfully!")
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    context = {
        'form': form,
        'supplier': supplier,
        'title': 'Update Supplier'
    }
    return render(request, 'suppliers/supplier_form.html', context)

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(SupplierMaster, supplierid=pk)
    
    # Get invoices for this supplier
    invoices = InvoiceMaster.objects.filter(supplierid=pk).order_by('-invoice_date')
    
    # Calculate total purchase and payment amounts
    total_purchase = invoices.aggregate(Sum('invoice_total'))['invoice_total__sum'] or 0
    total_paid = invoices.aggregate(Sum('invoice_paid'))['invoice_paid__sum'] or 0
    balance = total_purchase - total_paid
    
    context = {
        'supplier': supplier,
        'invoices': invoices,
        'total_purchase': total_purchase,
        'total_paid': total_paid,
        'balance': balance,
        'title': f'Supplier: {supplier.supplier_name}'
    }
    return render(request, 'suppliers/supplier_detail.html', context)

@login_required
def delete_supplier(request, pk):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('supplier_list')
        
    supplier = get_object_or_404(SupplierMaster, supplierid=pk)
    
    if request.method == 'POST':
        supplier_name = supplier.supplier_name
        try:
            supplier.delete()
            messages.success(request, f"Supplier '{supplier_name}' deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete supplier. It is referenced by other records. Error: {str(e)}")
        return redirect('supplier_list')
    
    context = {
        'supplier': supplier,
        'title': 'Delete Supplier'
    }
    return render(request, 'suppliers/supplier_confirm_delete.html', context)

# Customer views
@login_required
def customer_list(request):
    customers = CustomerMaster.objects.all().order_by('customer_name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(customer_name__icontains=search_query) | 
            Q(customer_mobile__icontains=search_query) |
            Q(customer_emailid__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(customers, 10)  # 10 customers per page
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)
    
    context = {
        'customers': customers,
        'search_query': search_query,
        'title': 'Customer List'
    }
    return render(request, 'customers/customer_list.html', context)

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f"Customer '{customer.customer_name}' added successfully!")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': 'Add Customer'
    }
    return render(request, 'customers/customer_form.html', context)

@login_required
def update_customer(request, pk):
    customer = get_object_or_404(CustomerMaster, customerid=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer '{customer.customer_name}' updated successfully!")
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'title': 'Update Customer'
    }
    return render(request, 'customers/customer_form.html', context)

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(CustomerMaster, customerid=pk)
    
    # Get invoices for this customer
    invoices = SalesInvoiceMaster.objects.filter(customerid=pk).order_by('-sales_invoice_date')
    
    # Calculate total sales and payment amounts
    total_sales = invoices.aggregate(Sum('sales_invoice_total'))['sales_invoice_total__sum'] or 0
    total_paid = invoices.aggregate(Sum('sales_invoice_paid'))['sales_invoice_paid__sum'] or 0
    balance = total_sales - total_paid
    
    context = {
        'customer': customer,
        'invoices': invoices,
        'total_sales': total_sales,
        'total_paid': total_paid,
        'balance': balance,
        'title': f'Customer: {customer.customer_name}'
    }
    return render(request, 'customers/customer_detail.html', context)

@login_required
def delete_customer(request, pk):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('customer_list')
        
    customer = get_object_or_404(CustomerMaster, customerid=pk)
    
    if request.method == 'POST':
        customer_name = customer.customer_name
        try:
            customer.delete()
            messages.success(request, f"Customer '{customer_name}' deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete customer. It is referenced by other records. Error: {str(e)}")
        return redirect('customer_list')
    
    context = {
        'customer': customer,
        'title': 'Delete Customer'
    }
    return render(request, 'customers/customer_confirm_delete.html', context)

# Purchase Invoice views
@login_required
def invoice_list(request):
    invoices = InvoiceMaster.objects.all().order_by('-invoice_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        invoices = invoices.filter(
            Q(invoice_no__icontains=search_query) | 
            Q(supplierid__supplier_name__icontains=search_query)
        )
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            invoices = invoices.filter(invoice_date__range=[start_date, end_date])
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    # Pagination
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)
    
    context = {
        'invoices': invoices,
        'search_query': search_query,
        'start_date': start_date if 'start_date' in locals() else '',
        'end_date': end_date if 'end_date' in locals() else '',
        'title': 'Purchase Invoice List'
    }
    return render(request, 'purchases/invoice_list.html', context)

@login_required
def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_paid = 0  # Initialize paid amount to 0
            invoice.save()
            messages.success(request, f"Purchase Invoice #{invoice.invoice_no} added successfully!")
            return redirect('invoice_detail', pk=invoice.invoiceid)
    else:
        form = InvoiceForm()
    
    context = {
        'form': form,
        'title': 'Add Purchase Invoice'
    }
    return render(request, 'purchases/invoice_form.html', context)

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(InvoiceMaster, invoiceid=pk)
    
    # Get all purchases under this invoice
    purchases = PurchaseMaster.objects.filter(product_invoiceid=pk)
    
    # Calculate the sum of all purchase entries
    purchases_total = purchases.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Calculate the difference between invoice total and sum of purchases
    # Transport charges should NOT be included in the invoice total
    invoice_pending = invoice.invoice_total - purchases_total
    
    # Get all payments for this invoice
    payments = InvoicePaid.objects.filter(ip_invoiceid=pk).order_by('-payment_date')
    
    context = {
        'invoice': invoice,
        'purchases': purchases,
        'payments': payments,
        'purchases_total': purchases_total,
        'invoice_pending': invoice_pending,
        'has_pending_entries': abs(invoice_pending) > 0.01,  # Using a small threshold to account for floating-point errors
        'title': f'Purchase Invoice #{invoice.invoice_no}'
    }
    return render(request, 'purchases/invoice_detail.html', context)

@login_required
def add_purchase(request, invoice_id):
    invoice = get_object_or_404(InvoiceMaster, invoiceid=invoice_id)
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            
            # Set additional fields
            purchase.product_supplierid = invoice.supplierid
            purchase.product_invoiceid = invoice
            purchase.product_invoice_no = invoice.invoice_no
            
            # Get product details from the selected product
            product = purchase.productid
            purchase.product_name = product.product_name
            purchase.product_company = product.product_company
            purchase.product_packing = product.product_packing
            
            # Calculate actual rate based on discount and quantity
            if purchase.purchase_calculation_mode == 'flat':
                # Flat discount amount
                purchase.actual_rate_per_qty = purchase.product_purchase_rate - (purchase.product_discount_got / purchase.product_quantity)
            else:
                # Percentage discount
                purchase.actual_rate_per_qty = purchase.product_purchase_rate * (1 - (purchase.product_discount_got / 100))
            
            purchase.product_actual_rate = purchase.actual_rate_per_qty
            
            # Calculate total amount before transport charges
            purchase.total_amount = purchase.product_actual_rate * purchase.product_quantity
            
            # Check if adding this product would exceed the invoice total
            existing_purchases_total = PurchaseMaster.objects.filter(
                product_invoiceid=invoice
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            new_total = existing_purchases_total + purchase.total_amount
            
            if new_total > invoice.invoice_total:
                messages.error(
                    request, 
                    f"Adding this product would exceed the invoice total amount of ₹{invoice.invoice_total}. "
                    f"Current total: ₹{existing_purchases_total:.2f}, This product: ₹{purchase.total_amount:.2f}, "
                    f"New total would be: ₹{new_total:.2f}"
                )
                context = {
                    'form': form,
                    'invoice': invoice,
                    'title': 'Add Purchase'
                }
                return render(request, 'purchases/purchase_form.html', context)
            
            # Calculate and distribute transport charges
            if invoice.transport_charges > 0:
                # Count existing products plus this new one
                existing_purchases = list(PurchaseMaster.objects.filter(product_invoiceid=invoice))
                total_products = len(existing_purchases) + 1
                
                # Calculate transport share per product
                transport_share_per_product = invoice.transport_charges / total_products
                
                # Update this product's transport charges
                purchase.product_transportation_charges = transport_share_per_product
                
                # Add the transport share to the actual rate
                transport_per_unit = transport_share_per_product / purchase.product_quantity
                purchase.product_actual_rate = purchase.actual_rate_per_qty + transport_per_unit
                
                # Recalculate total amount with transport charges included
                purchase.total_amount = purchase.product_actual_rate * purchase.product_quantity
                
                # Update existing products to redistribute transport charges
                for prev_purchase in existing_purchases:
                    prev_purchase.product_transportation_charges = transport_share_per_product
                    transport_per_unit = transport_share_per_product / prev_purchase.product_quantity
                    prev_purchase.product_actual_rate = prev_purchase.actual_rate_per_qty + transport_per_unit
                    prev_purchase.total_amount = prev_purchase.product_actual_rate * prev_purchase.product_quantity
                    prev_purchase.save()
            else:
                purchase.product_transportation_charges = 0
            
            purchase.save()
            
            # Save batch-specific sale rates to SaleRateMaster
            rate_A = form.cleaned_data.get('rate_A')
            rate_B = form.cleaned_data.get('rate_B')
            rate_C = form.cleaned_data.get('rate_C')
            
            # Check if any of the rates were specified
            if rate_A is not None or rate_B is not None or rate_C is not None:
                
                # Check if a rate entry already exists for this product batch
                try:
                    batch_rate = SaleRateMaster.objects.get(
                        productid=product,
                        product_batch_no=purchase.product_batch_no
                    )
                    # Update existing entry
                    batch_rate.rate_A = rate_A
                    batch_rate.rate_B = rate_B
                    batch_rate.rate_C = rate_C
                    batch_rate.save()
                except SaleRateMaster.DoesNotExist:
                    # Create new entry
                    SaleRateMaster.objects.create(
                        productid=product,
                        product_batch_no=purchase.product_batch_no,
                        rate_A=rate_A,
                        rate_B=rate_B,
                        rate_C=rate_C
                    )
            
            messages.success(request, f"Purchase for {purchase.product_name} added successfully!")
            return redirect('invoice_detail', pk=invoice_id)
    else:
        form = PurchaseForm()
    
    context = {
        'form': form,
        'invoice': invoice,
        'title': 'Add Purchase'
    }
    return render(request, 'purchases/purchase_form.html', context)

@login_required
def edit_purchase(request, invoice_id, purchase_id):
    invoice = get_object_or_404(InvoiceMaster, invoiceid=invoice_id)
    purchase = get_object_or_404(PurchaseMaster, purchaseid=purchase_id)
    
    # Ensure this purchase belongs to the specified invoice
    if purchase.product_invoiceid.invoiceid != invoice.invoiceid:
        messages.error(request, "This purchase does not belong to the specified invoice.")
        return redirect('invoice_detail', pk=invoice_id)
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            purchase = form.save(commit=False)
            
            # Get product details from the selected product
            product = purchase.productid
            purchase.product_name = product.product_name
            purchase.product_company = product.product_company
            purchase.product_packing = product.product_packing
            
            # Store old quantity for comparison
            old_purchase = PurchaseMaster.objects.get(purchaseid=purchase_id)
            old_total = old_purchase.total_amount
            
            # Calculate actual rate based on discount and quantity
            if purchase.purchase_calculation_mode == 'flat':
                # Flat discount amount
                purchase.actual_rate_per_qty = purchase.product_purchase_rate - (purchase.product_discount_got / purchase.product_quantity)
            else:
                # Percentage discount
                purchase.actual_rate_per_qty = purchase.product_purchase_rate * (1 - (purchase.product_discount_got / 100))
            
            purchase.product_actual_rate = purchase.actual_rate_per_qty
            
            # Calculate total amount without transport charges
            base_total = purchase.product_actual_rate * purchase.product_quantity
            
            # Check if updating this product would exceed the invoice total
            # Get the sum of all purchases for this invoice excluding the current one
            other_purchases_total = PurchaseMaster.objects.filter(
                product_invoiceid=invoice
            ).exclude(
                purchaseid=purchase_id
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            new_total = other_purchases_total + base_total
            
            if new_total > invoice.invoice_total:
                messages.error(
                    request, 
                    f"Updating this product would exceed the invoice total amount of ₹{invoice.invoice_total}. "
                    f"Other products total: ₹{other_purchases_total:.2f}, This product: ₹{base_total:.2f}, "
                    f"New total would be: ₹{new_total:.2f}"
                )
                # Restore form with current values
                try:
                    batch_rate = SaleRateMaster.objects.get(
                        productid=old_purchase.productid,
                        product_batch_no=old_purchase.product_batch_no
                    )
                    form = PurchaseForm(instance=old_purchase, initial={
                        'rate_A': batch_rate.rate_A,
                        'rate_B': batch_rate.rate_B,
                        'rate_C': batch_rate.rate_C
                    })
                except SaleRateMaster.DoesNotExist:
                    form = PurchaseForm(instance=old_purchase)
                
                context = {
                    'form': form,
                    'invoice': invoice,
                    'purchase': old_purchase,
                    'title': 'Edit Purchase',
                    'is_edit': True
                }
                return render(request, 'purchases/purchase_form.html', context)
            
            # Calculate and distribute transport charges
            if invoice.transport_charges > 0:
                # Get all purchases for this invoice excluding the current one
                other_purchases = list(PurchaseMaster.objects.filter(
                    product_invoiceid=invoice
                ).exclude(
                    purchaseid=purchase_id
                ))
                
                total_products = len(other_purchases) + 1
                
                # Calculate transport share per product
                transport_share_per_product = invoice.transport_charges / total_products
                
                # Update this product's transport charges
                purchase.product_transportation_charges = transport_share_per_product
                
                # Add transport share to actual rate
                transport_per_unit = transport_share_per_product / purchase.product_quantity
                purchase.product_actual_rate = purchase.actual_rate_per_qty + transport_per_unit
                
                # Recalculate total amount with transport charges included
                purchase.total_amount = purchase.product_actual_rate * purchase.product_quantity
                
                # Update other products to redistribute transport charges
                for other_purchase in other_purchases:
                    other_purchase.product_transportation_charges = transport_share_per_product
                    other_transport_per_unit = transport_share_per_product / other_purchase.product_quantity
                    other_purchase.product_actual_rate = other_purchase.actual_rate_per_qty + other_transport_per_unit
                    other_purchase.total_amount = other_purchase.product_actual_rate * other_purchase.product_quantity
                    other_purchase.save()
            else:
                purchase.product_transportation_charges = 0
                purchase.total_amount = base_total
            
            purchase.save()
            
            # Save batch-specific sale rates to SaleRateMaster
            rate_A = form.cleaned_data.get('rate_A')
            rate_B = form.cleaned_data.get('rate_B')
            rate_C = form.cleaned_data.get('rate_C')
            
            # Check if any of the rates were specified
            if rate_A is not None or rate_B is not None or rate_C is not None:
                # Default to product master rates if not specified
                if rate_A is None:
                    # Get rates from SaleRateMaster or default values
                    rate_A = 0.0
                    rate_B = 0.0
                    rate_C = 0.0
                
                # Check if a rate entry already exists for this product batch
                try:
                    batch_rate = SaleRateMaster.objects.get(
                        productid=product,
                        product_batch_no=purchase.product_batch_no
                    )
                    # Update existing entry
                    batch_rate.rate_A = rate_A
                    batch_rate.rate_B = rate_B
                    batch_rate.rate_C = rate_C
                    batch_rate.save()
                except SaleRateMaster.DoesNotExist:
                    # Create new entry
                    SaleRateMaster.objects.create(
                        productid=product,
                        product_batch_no=purchase.product_batch_no,
                        rate_A=rate_A,
                        rate_B=rate_B,
                        rate_C=rate_C
                    )
            
            messages.success(request, f"Purchase for {purchase.product_name} updated successfully!")
            return redirect('invoice_detail', pk=invoice_id)
    else:
        # Try to get current rates for this product and batch
        try:
            batch_rate = SaleRateMaster.objects.get(
                productid=purchase.productid,
                product_batch_no=purchase.product_batch_no
            )
            
            # Initialize the form with current values including rates
            form = PurchaseForm(instance=purchase, initial={
                'rate_A': batch_rate.rate_A,
                'rate_B': batch_rate.rate_B,
                'rate_C': batch_rate.rate_C
            })
        except SaleRateMaster.DoesNotExist:
            # No batch-specific rates found, use default form
            form = PurchaseForm(instance=purchase)
    
    context = {
        'form': form,
        'invoice': invoice,
        'purchase': purchase,
        'title': 'Edit Purchase',
        'is_edit': True
    }
    return render(request, 'purchases/purchase_form.html', context)

@login_required
def delete_purchase(request, invoice_id, purchase_id):
    invoice = get_object_or_404(InvoiceMaster, invoiceid=invoice_id)
    purchase = get_object_or_404(PurchaseMaster, purchaseid=purchase_id)
    
    # Ensure this purchase belongs to the specified invoice
    if purchase.product_invoiceid.invoiceid != invoice.invoiceid:
        messages.error(request, "This purchase does not belong to the specified invoice.")
        return redirect('invoice_detail', pk=invoice_id)
    
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('invoice_detail', pk=invoice_id)
    
    if request.method == 'POST':
        product_name = purchase.product_name
        try:
            # Before deleting, check if we need to redistribute transport charges
            if invoice.transport_charges > 0:
                # Get all other purchases for this invoice
                other_purchases = list(PurchaseMaster.objects.filter(
                    product_invoiceid=invoice
                ).exclude(
                    purchaseid=purchase_id
                ))
                
                # If there are other purchases, redistribute transport charges
                if other_purchases:
                    # Calculate new transport share per product
                    transport_share_per_product = invoice.transport_charges / len(other_purchases)
                    
                    # Update all other products with new transport charges
                    for other_purchase in other_purchases:
                        other_purchase.product_transportation_charges = transport_share_per_product
                        transport_per_unit = transport_share_per_product / other_purchase.product_quantity
                        other_purchase.product_actual_rate = other_purchase.actual_rate_per_qty + transport_per_unit
                        other_purchase.total_amount = other_purchase.product_actual_rate * other_purchase.product_quantity
                        other_purchase.save()
            
            # Now delete the purchase
            purchase.delete()
            messages.success(request, f"Purchase for {product_name} deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete purchase. Error: {str(e)}")
        return redirect('invoice_detail', pk=invoice_id)
    
    context = {
        'invoice': invoice,
        'purchase': purchase,
        'title': 'Delete Purchase'
    }
    return render(request, 'purchases/purchase_confirm_delete.html', context)

@login_required
def add_invoice_payment(request, invoice_id):
    invoice = get_object_or_404(InvoiceMaster, invoiceid=invoice_id)
    
    if request.method == 'POST':
        form = InvoicePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.ip_invoiceid = invoice
            
            # Check if payment amount is valid
            if payment.payment_amount > (invoice.invoice_total - invoice.invoice_paid):
                messages.error(request, "Payment amount cannot exceed the remaining balance.")
                return redirect('add_invoice_payment', invoice_id=invoice_id)
            
            payment.save()
            
            # Update invoice paid amount
            invoice.invoice_paid += payment.payment_amount
            invoice.save()
            
            messages.success(request, f"Payment of {payment.payment_amount} added successfully!")
            return redirect('invoice_detail', pk=invoice_id)
    else:
        form = InvoicePaymentForm()
    
    context = {
        'form': form,
        'invoice': invoice,
        'balance': invoice.invoice_total - invoice.invoice_paid,
        'title': 'Add Invoice Payment'
    }
    return render(request, 'purchases/payment_form.html', context)

@login_required
def edit_invoice_payment(request, invoice_id, payment_id):
    invoice = get_object_or_404(InvoiceMaster, invoiceid=invoice_id)
    payment = get_object_or_404(InvoicePaid, payment_id=payment_id, ip_invoiceid=invoice_id)
    
    # Store original payment amount to calculate difference
    original_amount = payment.payment_amount
    
    if request.method == 'POST':
        form = InvoicePaymentForm(request.POST, instance=payment)
        if form.is_valid():
            # Calculate the difference between new and old payment amount
            new_payment = form.save(commit=False)
            difference = new_payment.payment_amount - original_amount
            
            # Check if new amount would exceed the invoice total
            if invoice.invoice_paid + difference > invoice.invoice_total:
                messages.error(request, "Payment amount cannot exceed the invoice total.")
                return redirect('edit_invoice_payment', invoice_id=invoice_id, payment_id=payment_id)
            
            # Update payment
            new_payment.save()
            
            # Update invoice paid amount
            invoice.invoice_paid += difference
            invoice.save()
            
            messages.success(request, f"Payment updated successfully!")
            return redirect('invoice_detail', pk=invoice_id)
    else:
        form = InvoicePaymentForm(instance=payment)
    
    context = {
        'form': form,
        'invoice': invoice,
        'payment': payment,
        'balance': invoice.invoice_total - invoice.invoice_paid + payment.payment_amount,
        'is_edit': True,
        'title': 'Edit Invoice Payment'
    }
    return render(request, 'purchases/payment_form.html', context)

@login_required
def delete_invoice_payment(request, invoice_id, payment_id):
    invoice = get_object_or_404(InvoiceMaster, invoiceid=invoice_id)
    payment = get_object_or_404(InvoicePaid, payment_id=payment_id, ip_invoiceid=invoice_id)
    
    if request.method == 'POST':
        # Update invoice paid amount
        invoice.invoice_paid -= payment.payment_amount
        invoice.save()
        
        # Delete payment
        payment.delete()
        
        messages.success(request, "Payment deleted successfully!")
        return redirect('invoice_detail', pk=invoice_id)
    
    context = {
        'payment': payment,
        'invoice': invoice,
        'title': 'Delete Invoice Payment'
    }
    return render(request, 'purchases/payment_confirm_delete.html', context)

@login_required
def delete_invoice(request, pk):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('invoice_list')
        
    invoice = get_object_or_404(InvoiceMaster, invoiceid=pk)
    
    if request.method == 'POST':
        try:
            invoice.delete()
            messages.success(request, f"Purchase Invoice #{invoice.invoice_no} deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete invoice. Error: {str(e)}")
        return redirect('invoice_list')
    
    context = {
        'invoice': invoice,
        'title': 'Delete Purchase Invoice'
    }
    return render(request, 'purchases/invoice_confirm_delete.html', context)

# Sales Invoice views
@login_required
def sales_invoice_list(request):
    invoices = SalesInvoiceMaster.objects.all().order_by('-sales_invoice_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        invoices = invoices.filter(
            Q(sales_invoice_no__icontains=search_query) | 
            Q(customerid__customer_name__icontains=search_query)
        )
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            invoices = invoices.filter(sales_invoice_date__range=[start_date, end_date])
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    # Pagination
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)
    
    context = {
        'invoices': invoices,
        'search_query': search_query,
        'start_date': start_date if 'start_date' in locals() else '',
        'end_date': end_date if 'end_date' in locals() else '',
        'title': 'Sales Invoice List'
    }
    return render(request, 'sales/sales_invoice_list.html', context)

@login_required
def add_sales_invoice(request):
    # Generate the invoice number format that will be used
    # Format: SINV-YYYYMMDD-XXX where XXX is a sequential number
    today = datetime.now()
    date_prefix = today.strftime('%Y%m%d')
    invoice_prefix = f"SINV-{date_prefix}-"
    
    # Find the highest invoice number for today
    latest_invoices = SalesInvoiceMaster.objects.filter(
        sales_invoice_no__startswith=invoice_prefix
    ).order_by('-sales_invoice_no')
    
    if latest_invoices.exists():
        # Extract the last sequential number and increment it
        latest_number = latest_invoices.first().sales_invoice_no
        sequence = int(latest_number.split('-')[-1]) + 1
    else:
        # Start with 1 if no invoices exist for today
        sequence = 1
        
    # Create the preview invoice number
    preview_invoice_no = f"{invoice_prefix}{sequence:03d}"
    
    if request.method == 'POST':
        form = SalesInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            
            # Set the generated invoice number
            invoice.sales_invoice_no = preview_invoice_no
            
            # Initialize paid amount to 0
            invoice.sales_invoice_paid = 0
            
            # Note: We don't need to set sales_invoice_total anymore as it's now calculated dynamically from sales items
            
            invoice.save()
            messages.success(request, f"Sales Invoice #{invoice.sales_invoice_no} added successfully!")
            return redirect('sales_invoice_detail', pk=invoice.sales_invoice_no)
    else:
        form = SalesInvoiceForm()
    
    context = {
        'form': form,
        'title': 'Add Sales Invoice',
        'preview_invoice_no': preview_invoice_no
    }
    return render(request, 'sales/sales_invoice_form.html', context)

@login_required
def sales_invoice_detail(request, pk):
    invoice = get_object_or_404(SalesInvoiceMaster, sales_invoice_no=pk)
    
    # Get all sales under this invoice
    sales = SalesMaster.objects.filter(sales_invoice_no=pk)
    
    # Get all payments for this invoice
    payments = SalesInvoicePaid.objects.filter(sales_ip_invoice_no=pk).order_by('-sales_payment_date')
    
    context = {
        'invoice': invoice,
        'sales': sales,
        'payments': payments,
        'title': f'Sales Invoice #{invoice.sales_invoice_no}'
    }
    return render(request, 'sales/sales_invoice_detail.html', context)

@login_required
def print_sales_bill(request, pk):
    invoice = get_object_or_404(SalesInvoiceMaster, sales_invoice_no=pk)
    
    # Get all sales under this invoice
    sales = SalesMaster.objects.filter(sales_invoice_no=pk)
    
    # Get all payments for this invoice
    payments = SalesInvoicePaid.objects.filter(sales_ip_invoice_no=pk).order_by('-sales_payment_date')
    
    # Get pharmacy details for the bill header
    try:
        pharmacy = Pharmacy_Details.objects.first()
    except Pharmacy_Details.DoesNotExist:
        pharmacy = None
    
    # Calculate totals and tax amounts
    subtotal = 0
    total_tax = 0
    
    for sale in sales:
        # Base price before tax
        base_price = sale.sale_rate * sale.sale_quantity
        
        # Apply discount
        if sale.sale_calculation_mode == 'flat':
            # Flat discount in rupees
            base_price_after_discount = base_price - sale.sale_discount
        else:
            # Percentage discount
            base_price_after_discount = base_price - (base_price * sale.sale_discount / 100)
        
        # Calculate tax amount
        tax_amount = base_price_after_discount * (sale.sale_igst / 100)
        
        subtotal += base_price_after_discount
        total_tax += tax_amount
    
    context = {
        'invoice': invoice,
        'sales': sales,
        'payments': payments,
        'pharmacy': pharmacy,
        'subtotal': subtotal,
        'total_tax': total_tax,
        'total': invoice.sales_invoice_total,
        'balance': invoice.balance_due,
        'title': f'Print Bill: {invoice.sales_invoice_no}'
    }
    return render(request, 'sales/print_sales_bill.html', context)

@login_required
def add_sale(request, invoice_id):
    invoice = get_object_or_404(SalesInvoiceMaster, sales_invoice_no=invoice_id)
    
    if request.method == 'POST':
        form = SalesForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            
            # Set additional fields
            sale.sales_invoice_no = invoice
            sale.customerid = invoice.customerid
            
            # Check stock availability first
            from .utils import get_batch_stock_status
            batch_quantity, is_available = get_batch_stock_status(
                sale.productid.productid, sale.product_batch_no
            )
            
            # If product is out of stock, show an error and don't save
            if not is_available:
                messages.error(request, f"Cannot add sale. Product {sale.productid.product_name} with batch {sale.product_batch_no} is out of stock.")
                context = {
                    'form': form,
                    'invoice': invoice,
                    'title': 'Add Sale'
                }
                return render(request, 'sales/sales_form.html', context)
            
            # If not enough quantity available, show error and don't save
            if batch_quantity < sale.sale_quantity:
                messages.error(request, f"Cannot add sale. Only {batch_quantity} units available for product {sale.productid.product_name} with batch {sale.product_batch_no}.")
                context = {
                    'form': form,
                    'invoice': invoice,
                    'title': 'Add Sale'
                }
                return render(request, 'sales/sales_form.html', context)
            
            # Get product details from the selected product
            product = sale.productid
            sale.product_name = product.product_name
            sale.product_company = product.product_company
            sale.product_packing = product.product_packing
            
            # Get batch-specific rates if available
            batch_specific_rate = None
            if sale.product_batch_no:
                try:
                    batch_specific_rate = SaleRateMaster.objects.get(
                        productid=product, 
                        product_batch_no=sale.product_batch_no
                    )
                except SaleRateMaster.DoesNotExist:
                    batch_specific_rate = None
            
            # Set appropriate rate based on customer type and selected rate type
            if form.cleaned_data.get('custom_rate') and sale.rate_applied == 'custom':
                # Use the custom rate provided
                sale.sale_rate = form.cleaned_data.get('custom_rate')
            elif sale.rate_applied == 'A':
                if batch_specific_rate:
                    sale.sale_rate = batch_specific_rate.rate_A
                else:
                    sale.sale_rate = purchase.product_MRP  # Fallback to MRP
            elif sale.rate_applied == 'B':
                if batch_specific_rate:
                    sale.sale_rate = batch_specific_rate.rate_B
                else:
                    sale.sale_rate = purchase.product_MRP  # Fallback to MRP
            elif sale.rate_applied == 'C':
                if batch_specific_rate:
                    sale.sale_rate = batch_specific_rate.rate_C
                else:
                    sale.sale_rate = purchase.product_MRP  # Fallback to MRP
            
            # Calculate base price for all units
            base_price = sale.sale_rate * sale.sale_quantity
            
            # Apply discount first
            if sale.sale_calculation_mode == 'flat':
                # Flat discount amount
                discounted_amount = base_price - sale.sale_discount
            else:
                # Percentage discount
                discounted_amount = base_price * (1 - (sale.sale_discount / 100))
            
            # Then add GST to the discounted amount
            sale.sale_total_amount = discounted_amount * (1 + (sale.sale_igst / 100))
            
            sale.save()
            
            messages.success(request, f"Sale for {sale.product_name} added successfully!")
            return redirect('sales_invoice_detail', pk=invoice_id)
    else:
        form = SalesForm()
    
    context = {
        'form': form,
        'invoice': invoice,
        'title': 'Add Sale'
    }
    return render(request, 'sales/sales_form.html', context)

@login_required
def edit_sale(request, invoice_id, sale_id):
    invoice = get_object_or_404(SalesInvoiceMaster, sales_invoice_no=invoice_id)
    sale = get_object_or_404(SalesMaster, id=sale_id)
    
    # Ensure this sale belongs to the specified invoice
    if sale.sales_invoice_no.sales_invoice_no != invoice.sales_invoice_no:
        messages.error(request, "This sale does not belong to the specified invoice.")
        return redirect('sales_invoice_detail', pk=invoice_id)
    
    if request.method == 'POST':
        form = SalesForm(request.POST, instance=sale)
        if form.is_valid():
            sale = form.save(commit=False)
            
            # Check stock availability first
            from .utils import get_batch_stock_status
            batch_quantity, is_available = get_batch_stock_status(
                sale.productid.productid, sale.product_batch_no
            )
            
            # For edit, we need to consider current quantity of this sale item
            current_sale = SalesMaster.objects.get(id=sale_id)
            additional_qty_needed = sale.sale_quantity - current_sale.sale_quantity
            
            # If product is out of stock, show an error and don't save
            if not is_available and additional_qty_needed > 0:
                messages.error(request, f"Cannot update sale. Product {sale.productid.product_name} with batch {sale.product_batch_no} is out of stock.")
                context = {
                    'form': form,
                    'invoice': invoice,
                    'sale': sale,
                    'title': 'Edit Sale',
                    'is_edit': True
                }
                return render(request, 'sales/sales_form.html', context)
            
            # If not enough quantity available, show error and don't save
            if batch_quantity < additional_qty_needed:
                messages.error(request, f"Cannot update sale. Only {batch_quantity} additional units available for product {sale.productid.product_name} with batch {sale.product_batch_no}.")
                context = {
                    'form': form,
                    'invoice': invoice,
                    'sale': sale,
                    'title': 'Edit Sale',
                    'is_edit': True
                }
                return render(request, 'sales/sales_form.html', context)
            
            # Get product details from the selected product
            product = sale.productid
            sale.product_name = product.product_name
            sale.product_company = product.product_company
            sale.product_packing = product.product_packing
            
            # Get batch-specific rates if available
            batch_specific_rate = None
            if sale.product_batch_no:
                try:
                    batch_specific_rate = SaleRateMaster.objects.get(
                        productid=product, 
                        product_batch_no=sale.product_batch_no
                    )
                except SaleRateMaster.DoesNotExist:
                    batch_specific_rate = None
            
            # Set appropriate rate based on customer type and selected rate type
            if form.cleaned_data.get('custom_rate') and sale.rate_applied == 'custom':
                # Use the custom rate provided
                sale.sale_rate = form.cleaned_data.get('custom_rate')
            elif sale.rate_applied == 'A':
                if batch_specific_rate:
                    sale.sale_rate = batch_specific_rate.rate_A
                else:
                    sale.sale_rate = purchase.product_MRP  # Fallback to MRP
            elif sale.rate_applied == 'B':
                if batch_specific_rate:
                    sale.sale_rate = batch_specific_rate.rate_B
                else:
                    sale.sale_rate = purchase.product_MRP  # Fallback to MRP
            elif sale.rate_applied == 'C':
                if batch_specific_rate:
                    sale.sale_rate = batch_specific_rate.rate_C
                else:
                    sale.sale_rate = purchase.product_MRP  # Fallback to MRP
            
            # Calculate base price for all units
            base_price = sale.sale_rate * sale.sale_quantity
            
            # Apply discount first
            if sale.sale_calculation_mode == 'flat':
                # Flat discount amount
                discounted_amount = base_price - sale.sale_discount
            else:
                # Percentage discount
                discounted_amount = base_price * (1 - (sale.sale_discount / 100))
            
            # Then add GST to the discounted amount
            sale.sale_total_amount = discounted_amount * (1 + (sale.sale_igst / 100))
            
            sale.save()
            
            messages.success(request, f"Sale for {sale.product_name} updated successfully!")
            return redirect('sales_invoice_detail', pk=invoice_id)
    else:
        # Initialize form with existing data
        form = SalesForm(instance=sale)
        
        # For custom rate, we need to set the initial value
        if sale.rate_applied == 'custom':
            form.fields['custom_rate'].initial = sale.sale_rate
    
    context = {
        'form': form,
        'invoice': invoice,
        'sale': sale,
        'title': 'Edit Sale',
        'is_edit': True
    }
    return render(request, 'sales/sales_form.html', context)

@login_required
def delete_sale(request, invoice_id, sale_id):
    invoice = get_object_or_404(SalesInvoiceMaster, sales_invoice_no=invoice_id)
    sale = get_object_or_404(SalesMaster, id=sale_id)
    
    # Ensure this sale belongs to the specified invoice
    if sale.sales_invoice_no.sales_invoice_no != invoice.sales_invoice_no:
        messages.error(request, "This sale does not belong to the specified invoice.")
        return redirect('sales_invoice_detail', pk=invoice_id)
    
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('sales_invoice_detail', pk=invoice_id)
    
    if request.method == 'POST':
        product_name = sale.product_name
        try:
            sale.delete()
            messages.success(request, f"Sale for {product_name} deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete sale. Error: {str(e)}")
        return redirect('sales_invoice_detail', pk=invoice_id)
    
    context = {
        'invoice': invoice,
        'sale': sale,
        'title': 'Delete Sale'
    }
    return render(request, 'sales/sale_confirm_delete.html', context)

@login_required
def add_sales_payment(request, invoice_id):
    invoice = get_object_or_404(SalesInvoiceMaster, sales_invoice_no=invoice_id)
    
    if request.method == 'POST':
        form = SalesPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.sales_ip_invoice_no = invoice
            
            # Calculate invoice total from sale items
            invoice_total = SalesMaster.objects.filter(
                sales_invoice_no=invoice.sales_invoice_no
            ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
            
            # Check if payment amount is valid
            if payment.sales_payment_amount > (invoice_total - invoice.sales_invoice_paid):
                messages.error(request, "Payment amount cannot exceed the remaining balance.")
                return redirect('add_sales_payment', invoice_id=invoice_id)
            
            payment.save()
            
            # Update invoice paid amount
            invoice.sales_invoice_paid += payment.sales_payment_amount
            invoice.save()
            
            messages.success(request, f"Payment of {payment.sales_payment_amount} added successfully!")
            return redirect('sales_invoice_detail', pk=invoice_id)
    else:
        form = SalesPaymentForm()
    
    # Calculate invoice total from sale items for context
    invoice_total = SalesMaster.objects.filter(
        sales_invoice_no=invoice.sales_invoice_no
    ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
    
    context = {
        'form': form,
        'invoice': invoice,
        'balance': invoice_total - invoice.sales_invoice_paid,
        'title': 'Add Sales Payment'
    }
    return render(request, 'sales/payment_form.html', context)

@login_required
def delete_sales_invoice(request, pk):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('sales_invoice_list')
        
    invoice = get_object_or_404(SalesInvoiceMaster, sales_invoice_no=pk)
    
    if request.method == 'POST':
        try:
            invoice.delete()
            messages.success(request, f"Sales Invoice #{invoice.sales_invoice_no} deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete invoice. Error: {str(e)}")
        return redirect('sales_invoice_list')
    
    context = {
        'invoice': invoice,
        'title': 'Delete Sales Invoice'
    }
    return render(request, 'sales/sales_invoice_confirm_delete.html', context)

# Purchase Return views
@login_required
def purchase_return_list(request):
    returns = ReturnInvoiceMaster.objects.all().order_by('-returninvoice_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        returns = returns.filter(
            Q(returninvoiceid__icontains=search_query) | 
            Q(returnsupplierid__supplier_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(returns, 10)
    page_number = request.GET.get('page')
    returns = paginator.get_page(page_number)
    
    context = {
        'returns': returns,
        'search_query': search_query,
        'title': 'Purchase Return List'
    }
    return render(request, 'returns/purchase_return_list.html', context)

@login_required
def add_purchase_return(request):
    # Generate the return invoice number format that will be used
    # Format: PURR-YYYYMMDD-XXX where XXX is a sequential number
    today = datetime.now()
    date_prefix = today.strftime('%Y%m%d')
    invoice_prefix = f"PURR-{date_prefix}-"
    
    # Find the highest return invoice number for today
    latest_returns = ReturnInvoiceMaster.objects.filter(
        returninvoiceid__startswith=invoice_prefix
    ).order_by('-returninvoiceid')
    
    if latest_returns.exists():
        # Extract the last sequential number and increment it
        latest_number = latest_returns.first().returninvoiceid
        sequence = int(latest_number.split('-')[-1]) + 1
    else:
        # Start with 1 if no returns exist for today
        sequence = 1
        
    # Create the new return invoice number
    new_return_id = f"{invoice_prefix}{sequence:03d}"

    if request.method == 'POST':
        form = PurchaseReturnInvoiceForm(request.POST)
        if form.is_valid():
            return_invoice = form.save(commit=False)
            # Set the generated return invoice number
            return_invoice.returninvoiceid = new_return_id
            return_invoice.returninvoice_paid = 0  # Initialize paid amount to 0
            return_invoice.save()
            messages.success(request, f"Purchase Return #{return_invoice.returninvoiceid} added successfully!")
            return redirect('purchase_return_detail', pk=return_invoice.returninvoiceid)
    else:
        # Pre-fill the form with initial values
        initial_data = {
            'returninvoice_date': today.date(),
        }
        form = PurchaseReturnInvoiceForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Add Purchase Return',
        'preview_id': new_return_id
    }
    return render(request, 'returns/purchase_return_form.html', context)

@login_required
def purchase_return_detail(request, pk):
    return_invoice = get_object_or_404(ReturnInvoiceMaster, returninvoiceid=pk)
    
    # Get all returns under this invoice
    returns = ReturnPurchaseMaster.objects.filter(returninvoiceid=pk)
    
    # Get all payments for this return invoice
    payments = PurchaseReturnInvoicePaid.objects.filter(pr_ip_returninvoiceid=pk).order_by('-pr_payment_date')
    
    context = {
        'return_invoice': return_invoice,
        'returns': returns,
        'payments': payments,
        'title': f'Purchase Return #{return_invoice.returninvoiceid}'
    }
    return render(request, 'returns/purchase_return_detail.html', context)

@login_required
def delete_purchase_return(request, pk):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('purchase_return_list')
        
    return_invoice = get_object_or_404(ReturnInvoiceMaster, returninvoiceid=pk)
    
    if request.method == 'POST':
        try:
            return_invoice.delete()
            messages.success(request, f"Purchase Return #{pk} deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete return invoice. Error: {str(e)}")
        return redirect('purchase_return_list')
    
    context = {
        'return_invoice': return_invoice,
        'title': 'Delete Purchase Return'
    }
    return render(request, 'returns/purchase_return_confirm_delete.html', context)

@login_required
def edit_purchase_return_item(request, return_id, item_id):
    # Check if user is admin or manager (case-insensitive)
    if not request.user.user_type.lower() in ['admin', 'manager']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('purchase_return_detail', pk=return_id)
        
    return_item = get_object_or_404(ReturnPurchaseMaster, pk=item_id)
    return_invoice = return_item.returninvoiceid
    
    if request.method == 'POST':
        form = PurchaseReturnForm(request.POST, instance=return_item)
        if form.is_valid():
            # Store the original amount to calculate difference
            original_amount = return_item.returntotal_amount
            
            # Update the item without saving yet
            updated_item = form.save(commit=False)
            
            # Set additional fields
            updated_item.returninvoiceid = return_invoice
            updated_item.returnproduct_supplierid = return_invoice.returnsupplierid
            
            # The product details are accessed via the returnproductid foreign key relation
            # No need to set additional fields as they'll be accessed through the relation
            
            # Verify stock availability for increased quantity
            if updated_item.returnproduct_quantity > return_item.returnproduct_quantity:
                batch_stock, is_available = get_batch_stock_status(
                    product.productid, 
                    updated_item.returnproduct_batch_no
                )
                
                additional_qty = updated_item.returnproduct_quantity - return_item.returnproduct_quantity
                
                if batch_stock < additional_qty:
                    messages.error(request, f"Error: Insufficient stock! Available: {batch_stock}, Attempted to add: {additional_qty}")
                    context = {
                        'form': form,
                        'return_invoice': return_invoice,
                        'return_item': return_item,
                        'title': 'Edit Return Item'
                    }
                    return render(request, 'returns/purchase_return_item_edit_form.html', context)
            
            # Calculate total amount (including charges)
            updated_item.returntotal_amount = (updated_item.returnproduct_purchase_rate * updated_item.returnproduct_quantity) + updated_item.returnproduct_charges
            
            # Save the updated item
            updated_item.save()
            
            # Update the return invoice total
            total_amount = ReturnPurchaseMaster.objects.filter(returninvoiceid=return_id).aggregate(
                total=Sum('returntotal_amount'))['total'] or 0
            return_invoice.returninvoice_total = total_amount + return_invoice.return_charges
            return_invoice.save()
            
            messages.success(request, "Return item updated successfully!")
            return redirect('purchase_return_detail', pk=return_id)
    else:
        form = PurchaseReturnForm(instance=return_item)
    
    context = {
        'form': form,
        'return_invoice': return_invoice,
        'return_item': return_item,
        'title': 'Edit Return Item'
    }
    return render(request, 'returns/purchase_return_item_edit_form.html', context)

@login_required
def delete_purchase_return_item(request, return_id, item_id):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('purchase_return_detail', pk=return_id)
        
    return_item = get_object_or_404(ReturnPurchaseMaster, pk=item_id)
    return_invoice = return_item.returninvoiceid
    
    if request.method == 'POST':
        try:
            # Store the item amount to adjust the invoice total
            item_amount = return_item.returntotal_amount
            
            # Delete the item
            return_item.delete()
            
            # Update the invoice total
            total_amount = ReturnPurchaseMaster.objects.filter(returninvoiceid=return_id).aggregate(
                total=Sum('returntotal_amount'))['total'] or 0
            return_invoice.returninvoice_total = total_amount + return_invoice.return_charges
            return_invoice.save()
            
            messages.success(request, "Return item deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete return item. Error: {str(e)}")
        return redirect('purchase_return_detail', pk=return_id)
    
    context = {
        'return_item': return_item,
        'return_invoice': return_invoice,
        'title': 'Delete Return Item'
    }
    return render(request, 'returns/purchase_return_item_confirm_delete.html', context)

@login_required
def add_purchase_return_item(request, return_id):
    return_invoice = get_object_or_404(ReturnInvoiceMaster, returninvoiceid=return_id)
    
    # For AJAX request to get batch info
    if request.method == 'GET' and 'product_id' in request.GET:
        print("*** AJAX Request Detected for Purchase Return ***")
        product_id = request.GET.get('product_id')
        batch_no = request.GET.get('batch_no')
        print(f"*** Requested: Product ID: {product_id}, Batch: {batch_no} ***")
        
        if product_id and batch_no:
            # Check if the product was purchased with this batch from this supplier
            purchase_data = PurchaseMaster.objects.filter(
                productid_id=product_id, 
                product_batch_no=batch_no,
                product_supplierid=return_invoice.returnsupplierid
            ).first()
            
            if purchase_data:
                # Check current stock for this batch
                batch_stock, is_available = get_batch_stock_status(product_id, batch_no)
                print(f"*** Found Purchase Data: Expiry: {purchase_data.product_expiry}, Rate: {purchase_data.product_purchase_rate}, MRP: {purchase_data.product_MRP} ***")
                print(f"*** Stock Status: Available Qty: {batch_stock}, Is Available: {is_available} ***")
                
                if batch_stock <= 0:
                    response_data = {
                        'exists': True,
                        'expiry': purchase_data.product_expiry.strftime('%Y-%m-%d'),
                        'rate': purchase_data.product_purchase_rate,
                        'mrp': purchase_data.product_MRP,
                        'available_qty': 0,
                        'message': 'Warning: No stock available for return!'
                    }
                    print(f"*** Sending Response: {response_data} ***")
                    return JsonResponse(response_data)
                
                # Return product details including expiry
                response_data = {
                    'exists': True,
                    'expiry': purchase_data.product_expiry.strftime('%Y-%m-%d'),
                    'rate': purchase_data.product_purchase_rate,
                    'mrp': purchase_data.product_MRP,
                    'available_qty': batch_stock,
                    'message': f'Product found in purchase records. Current stock: {batch_stock}'
                }
                print(f"*** Sending Response: {response_data} ***")
                return JsonResponse(response_data)
            else:
                print("*** No purchase data found for this supplier/batch combination ***")
                return JsonResponse({
                    'exists': False,
                    'message': 'Error: This product with this batch was not purchased from this supplier!'
                })
        
        print("*** Invalid product or batch number ***")
        return JsonResponse({'exists': False, 'message': 'Invalid product or batch number'})
    
    if request.method == 'POST':
        form = PurchaseReturnForm(request.POST)
        if form.is_valid():
            return_item = form.save(commit=False)
            
            # Verify product was purchased from this supplier
            purchase_exists = PurchaseMaster.objects.filter(
                productid=return_item.returnproductid,
                product_batch_no=return_item.returnproduct_batch_no,
                product_supplierid=return_invoice.returnsupplierid
            ).exists()
            
            if not purchase_exists:
                messages.error(request, "Error: This product with this batch was not purchased from this supplier!")
                context = {
                    'form': form,
                    'return_invoice': return_invoice,
                    'title': 'Add Return Item'
                }
                return render(request, 'returns/purchase_return_item_form.html', context)
            
            # Check stock availability
            batch_stock, is_available = get_batch_stock_status(return_item.returnproductid.productid, return_item.returnproduct_batch_no)
            
            if batch_stock < return_item.returnproduct_quantity:
                messages.error(request, f"Error: Insufficient stock! Available: {batch_stock}, Attempted to return: {return_item.returnproduct_quantity}")
                context = {
                    'form': form,
                    'return_invoice': return_invoice,
                    'title': 'Add Return Item'
                }
                return render(request, 'returns/purchase_return_item_form.html', context)
            
            # Set additional fields
            return_item.returninvoiceid = return_invoice
            return_item.returnproduct_supplierid = return_invoice.returnsupplierid
            
            # The product details are accessed via the returnproductid foreign key relation
            # No need to set additional fields as they'll be accessed through the relation
            
            # Calculate total amount (including charges)
            return_item.returntotal_amount = (return_item.returnproduct_purchase_rate * return_item.returnproduct_quantity) + return_item.returnproduct_charges
            
            return_item.save()
            
            # Update the return invoice total
            total_amount = ReturnPurchaseMaster.objects.filter(returninvoiceid=return_id).aggregate(
                total=Sum('returntotal_amount'))['total'] or 0
            return_invoice.returninvoice_total = total_amount + return_invoice.return_charges
            return_invoice.save()
            
            messages.success(request, f"Return item added successfully!")
            return redirect('purchase_return_detail', pk=return_id)
    else:
        form = PurchaseReturnForm()
    
    context = {
        'form': form,
        'return_invoice': return_invoice,
        'title': 'Add Return Item'
    }
    return render(request, 'returns/purchase_return_item_form.html', context)

# Sales Return views
@login_required
def sales_return_list(request):
    returns = ReturnSalesInvoiceMaster.objects.all().order_by('-return_sales_invoice_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        returns = returns.filter(
            Q(return_sales_invoice_no__icontains=search_query) | 
            Q(return_sales_customerid__customer_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(returns, 10)
    page_number = request.GET.get('page')
    returns = paginator.get_page(page_number)
    
    context = {
        'returns': returns,
        'search_query': search_query,
        'title': 'Sales Return List'
    }
    return render(request, 'returns/sales_return_list.html', context)

@login_required
def add_sales_return(request):
    # Generate the sales return invoice number format that will be used
    # Format: SRET-YYYYMMDD-XXX where XXX is a sequential number
    today = datetime.now()
    date_prefix = today.strftime('%Y%m%d')
    invoice_prefix = f"SRET-{date_prefix}-"
    
    # Find the highest sales return invoice number for today
    latest_returns = ReturnSalesInvoiceMaster.objects.filter(
        return_sales_invoice_no__startswith=invoice_prefix
    ).order_by('-return_sales_invoice_no')
    
    if latest_returns.exists():
        # Extract the last sequential number and increment it
        latest_number = latest_returns.first().return_sales_invoice_no
        sequence = int(latest_number.split('-')[-1]) + 1
    else:
        # Start with 1 if no returns exist for today
        sequence = 1
        
    # Create the new return invoice number
    new_return_id = f"{invoice_prefix}{sequence:03d}"

    if request.method == 'POST':
        form = SalesReturnInvoiceForm(request.POST)
        if form.is_valid():
            return_invoice = form.save(commit=False)
            # Set the generated return invoice number
            return_invoice.return_sales_invoice_no = new_return_id
            return_invoice.return_sales_invoice_paid = 0  # Initialize paid amount to 0
            return_invoice.save()
            messages.success(request, f"Sales Return #{return_invoice.return_sales_invoice_no} added successfully!")
            return redirect('sales_return_detail', pk=return_invoice.return_sales_invoice_no)
    else:
        # Pre-fill the form with initial values
        initial_data = {
            'return_sales_invoice_date': today.date(),
        }
        form = SalesReturnInvoiceForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Add Sales Return',
        'preview_id': new_return_id
    }
    return render(request, 'returns/sales_return_form.html', context)

@login_required
def sales_return_detail(request, pk):
    return_invoice = get_object_or_404(ReturnSalesInvoiceMaster, return_sales_invoice_no=pk)
    
    # Get all returns under this invoice
    returns = ReturnSalesMaster.objects.filter(return_sales_invoice_no=pk)
    
    # Get all payments for this return invoice
    payments = ReturnSalesInvoicePaid.objects.filter(return_sales_ip_invoice_no=pk).order_by('-return_sales_payment_date')
    
    context = {
        'return_invoice': return_invoice,
        'returns': returns,
        'payments': payments,
        'title': f'Sales Return #{return_invoice.return_sales_invoice_no}'
    }
    return render(request, 'returns/sales_return_detail.html', context)

@login_required
def delete_sales_return(request, pk):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('sales_return_list')
        
    return_invoice = get_object_or_404(ReturnSalesInvoiceMaster, return_sales_invoice_no=pk)
    
    if request.method == 'POST':
        try:
            return_invoice.delete()
            messages.success(request, f"Sales Return #{pk} deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete return invoice. Error: {str(e)}")
        return redirect('sales_return_list')
    
    context = {
        'return_invoice': return_invoice,
        'title': 'Delete Sales Return'
    }
    return render(request, 'returns/sales_return_confirm_delete.html', context)

@login_required
def edit_sales_return_item(request, return_id, item_id):
    # Check if user is admin or manager (case-insensitive)
    if not request.user.user_type.lower() in ['admin', 'manager']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('sales_return_detail', pk=return_id)
        
    return_item = get_object_or_404(ReturnSalesMaster, pk=item_id)
    return_invoice = return_item.return_sales_invoice_no
    
    if request.method == 'POST':
        form = SalesReturnForm(request.POST, instance=return_item)
        if form.is_valid():
            # Store the original amount to calculate difference
            original_amount = return_item.return_sale_total_amount
            
            # Update the item without saving yet
            updated_item = form.save(commit=False)
            
            # Set additional fields
            updated_item.return_sales_invoice_no = return_invoice
            updated_item.return_customerid = return_invoice.return_sales_customerid
            
            # Get product details
            product = updated_item.return_productid
            updated_item.return_product_name = product.product_name
            updated_item.return_product_company = product.product_company
            updated_item.return_product_packing = product.product_packing
            
            # Calculate base amount
            base_amount = updated_item.return_sale_rate * updated_item.return_sale_quantity
            
            # Apply discount first
            discounted_amount = base_amount
            if updated_item.return_sale_discount > 0:
                if updated_item.return_sale_discount < 100:  # Assuming percentage discount
                    discounted_amount = base_amount * (1 - (updated_item.return_sale_discount / 100))
                else:  # Assuming flat discount
                    discounted_amount = base_amount - updated_item.return_sale_discount
            
            # Then apply GST to the discounted amount
            updated_item.return_sale_total_amount = discounted_amount * (1 + (updated_item.return_sale_igst / 100))
            
            # Save the updated item
            updated_item.save()
            
            # Update the invoice total
            total_amount = ReturnSalesMaster.objects.filter(return_sales_invoice_no=return_id).aggregate(
                total=Sum('return_sale_total_amount'))['total'] or 0
            return_invoice.return_sales_invoice_total = total_amount + return_invoice.return_sales_charges
            return_invoice.save()
            
            messages.success(request, "Return item updated successfully!")
            return redirect('sales_return_detail', pk=return_id)
    else:
        form = SalesReturnForm(instance=return_item)
    
    context = {
        'form': form,
        'return_invoice': return_invoice,
        'return_item': return_item,
        'title': 'Edit Return Item'
    }
    return render(request, 'returns/sales_return_item_edit_form.html', context)

@login_required
def delete_sales_return_item(request, return_id, item_id):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('sales_return_detail', pk=return_id)
        
    return_item = get_object_or_404(ReturnSalesMaster, pk=item_id)
    return_invoice = return_item.return_sales_invoice_no
    
    if request.method == 'POST':
        try:
            # Store the item amount to adjust the invoice total
            item_amount = return_item.return_sale_total_amount
            
            # Delete the item
            return_item.delete()
            
            # Update the invoice total
            total_amount = ReturnSalesMaster.objects.filter(return_sales_invoice_no=return_id).aggregate(
                total=Sum('return_sale_total_amount'))['total'] or 0
            return_invoice.return_sales_invoice_total = total_amount + return_invoice.return_sales_charges
            return_invoice.save()
            
            messages.success(request, "Return item deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete return item. Error: {str(e)}")
        return redirect('sales_return_detail', pk=return_id)
    
    context = {
        'return_item': return_item,
        'return_invoice': return_invoice,
        'title': 'Delete Return Item'
    }
    return render(request, 'returns/sales_return_item_confirm_delete.html', context)

@login_required
def add_sales_return_item(request, return_id):
    return_invoice = get_object_or_404(ReturnSalesInvoiceMaster, return_sales_invoice_no=return_id)
    
    # For AJAX request to get batch info
    if request.method == 'GET' and 'product_id' in request.GET:
        print("*** AJAX Request Detected for Sales Return ***")
        product_id = request.GET.get('product_id')
        batch_no = request.GET.get('batch_no')
        print(f"*** Requested: Product ID: {product_id}, Batch: {batch_no} ***")
        
        if product_id and batch_no:
            # Check if the product was sold with this batch
            sales_data = SalesMaster.objects.filter(
                productid_id=product_id, 
                product_batch_no=batch_no,
                customerid=return_invoice.return_sales_customerid
            ).first()
            
            if sales_data:
                print(f"*** Found Sales Data: Expiry: {sales_data.product_expiry}, Rate: {sales_data.sale_rate}, Quantity: {sales_data.sale_quantity} ***")
                
                # Get MRP from PurchaseMaster instead of sales data
                purchase_data = PurchaseMaster.objects.filter(
                    productid_id=product_id,
                    product_batch_no=batch_no
                ).first()
                
                # Use MRP from purchase data if available, otherwise fallback to sales data
                mrp = purchase_data.product_MRP if purchase_data else sales_data.product_MRP
                
                # Return product details including expiry, MRP, discount, and GST
                response_data = {
                    'exists': True,
                    'expiry': sales_data.product_expiry.strftime('%Y-%m-%d'),
                    'rate': sales_data.sale_rate,
                    'quantity': sales_data.sale_quantity,
                    'mrp': mrp,
                    'discount_type': sales_data.sale_calculation_mode or 'percentage',
                    'discount': sales_data.sale_discount or 0,
                    'igst': sales_data.sale_igst or 0,
                    'message': 'Product found in sales records.'
                }
                print(f"*** Sending Response: {response_data} ***")
                return JsonResponse(response_data)
            else:
                print("*** No sales data found for this customer/batch combination ***")
                
                # Verify product is in inventory with this batch
                purchase_data = PurchaseMaster.objects.filter(
                    productid_id=product_id,
                    product_batch_no=batch_no
                ).first()
                
                if purchase_data:
                    print(f"*** Found in inventory but not sold to this customer: Expiry: {purchase_data.product_expiry} ***")
                    response_data = {
                        'exists': False,
                        'expiry': purchase_data.product_expiry.strftime('%Y-%m-%d'),
                        'mrp': purchase_data.product_MRP,
                        'message': 'Warning: This product with this batch was not sold to this customer!'
                    }
                    print(f"*** Sending Response: {response_data} ***")
                    return JsonResponse(response_data)
                else:
                    print("*** Product not found in inventory with this batch number ***")
                    return JsonResponse({
                        'exists': False,
                        'message': 'Error: This product with this batch number does not exist in inventory!'
                    })
        
        print("*** Invalid product or batch number ***")
        return JsonResponse({'exists': False, 'message': 'Invalid product or batch number'})
    
    if request.method == 'POST':
        form = SalesReturnForm(request.POST)
        if form.is_valid():
            return_item = form.save(commit=False)
            
            # Verify product was actually sold to this customer
            sales_exist = SalesMaster.objects.filter(
                productid=return_item.return_productid,
                product_batch_no=return_item.return_product_batch_no,
                customerid=return_invoice.return_sales_customerid
            ).exists()
            
            if not sales_exist:
                messages.error(request, "Warning: This product with this batch was not sold to this customer!")
            
            # Set additional fields
            return_item.return_sales_invoice_no = return_invoice
            return_item.return_customerid = return_invoice.return_sales_customerid
            
            # Get product details
            product = return_item.return_productid
            return_item.return_product_name = product.product_name
            return_item.return_product_company = product.product_company
            return_item.return_product_packing = product.product_packing
            
            # Calculate base amount
            base_amount = return_item.return_sale_rate * return_item.return_sale_quantity
            
            # Apply discount first
            discounted_amount = base_amount
            if return_item.return_sale_discount > 0:
                if return_item.return_sale_discount < 100:  # Assuming percentage discount
                    discounted_amount = base_amount * (1 - (return_item.return_sale_discount / 100))
                else:  # Assuming flat discount
                    discounted_amount = base_amount - return_item.return_sale_discount
            
            # Then apply GST to the discounted amount
            return_item.return_sale_total_amount = discounted_amount * (1 + (return_item.return_sale_igst / 100))
            
            return_item.save()
            
            messages.success(request, f"Return item added successfully!")
            return redirect('sales_return_detail', pk=return_id)
    else:
        form = SalesReturnForm()
    
    context = {
        'form': form,
        'return_invoice': return_invoice,
        'title': 'Add Return Item'
    }
    return render(request, 'returns/sales_return_item_form.html', context)

# Product Wise Report
@login_required
def product_wise_report(request):
    """
    Generate a report showing total purchases, sales, purchase returns, and sales returns for each product
    """
    # Get all products
    products = ProductMaster.objects.all().order_by('product_name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(product_company__icontains=search_query) |
            Q(product_salt__icontains=search_query)
        )
    
    # Get product-wise data
    product_data = []
    for product in products:
        # Get total purchases
        purchases = PurchaseMaster.objects.filter(productid=product.productid)
        total_purchase_qty = purchases.aggregate(total=Sum('product_quantity'))['total'] or 0
        total_purchase_value = purchases.aggregate(
            total=Sum(F('product_quantity') * F('product_purchase_rate'))
        )['total'] or 0
        
        # Get total sales
        sales = SalesMaster.objects.filter(productid=product.productid)
        total_sale_qty = sales.aggregate(total=Sum('sale_quantity'))['total'] or 0
        total_sale_value = sales.aggregate(total=Sum('sale_total_amount'))['total'] or 0
        
        # Get total purchase returns
        purchase_returns = ReturnPurchaseMaster.objects.filter(returnproductid=product.productid)
        total_purchase_return_qty = purchase_returns.aggregate(total=Sum('returnproduct_quantity'))['total'] or 0
        total_purchase_return_value = purchase_returns.aggregate(
            total=Sum(F('returnproduct_quantity') * F('returnproduct_purchase_rate'))
        )['total'] or 0
        
        # Get total sales returns
        sales_returns = ReturnSalesMaster.objects.filter(return_productid=product.productid)
        total_sale_return_qty = sales_returns.aggregate(total=Sum('return_sale_quantity'))['total'] or 0
        total_sale_return_value = sales_returns.aggregate(total=Sum('return_sale_total_amount'))['total'] or 0
        
        # Calculate net quantities and values
        net_quantity = total_purchase_qty - total_sale_qty - total_purchase_return_qty + total_sale_return_qty
        net_purchase_value = total_purchase_value - total_purchase_return_value
        net_sale_value = total_sale_value - total_sale_return_value
        
        # Only include products with some transaction history
        if total_purchase_qty > 0 or total_sale_qty > 0 or total_purchase_return_qty > 0 or total_sale_return_qty > 0:
            product_data.append({
                'product': product,
                'total_purchase_qty': total_purchase_qty,
                'total_purchase_value': total_purchase_value,
                'total_sale_qty': total_sale_qty,
                'total_sale_value': total_sale_value,
                'total_purchase_return_qty': total_purchase_return_qty,
                'total_purchase_return_value': total_purchase_return_value,
                'total_sale_return_qty': total_sale_return_qty,
                'total_sale_return_value': total_sale_return_value,
                'net_quantity': net_quantity,
                'net_purchase_value': net_purchase_value,
                'net_sale_value': net_sale_value,
                'profit': net_sale_value - net_purchase_value,
            })
    
    # Calculate totals for all products
    grand_total = {
        'total_purchase_qty': sum(item['total_purchase_qty'] for item in product_data),
        'total_purchase_value': sum(item['total_purchase_value'] for item in product_data),
        'total_sale_qty': sum(item['total_sale_qty'] for item in product_data),
        'total_sale_value': sum(item['total_sale_value'] for item in product_data),
        'total_purchase_return_qty': sum(item['total_purchase_return_qty'] for item in product_data),
        'total_purchase_return_value': sum(item['total_purchase_return_value'] for item in product_data),
        'total_sale_return_qty': sum(item['total_sale_return_qty'] for item in product_data),
        'total_sale_return_value': sum(item['total_sale_return_value'] for item in product_data),
        'net_quantity': sum(item['net_quantity'] for item in product_data),
        'net_purchase_value': sum(item['net_purchase_value'] for item in product_data),
        'net_sale_value': sum(item['net_sale_value'] for item in product_data),
        'profit': sum(item['profit'] for item in product_data),
    }
    
    context = {
        'title': 'Product-wise Transaction Report',
        'product_data': product_data,
        'grand_total': grand_total,
        'search_query': search_query,
    }
    return render(request, 'reports/product_wise_report.html', context)

# Report views
@login_required
def inventory_report(request):
    products = ProductMaster.objects.all().order_by('product_name')
    
    inventory_data = []
    
    for product in products:
        stock_info = get_stock_status(product.productid)
        
        inventory_data.append({
            'product': product,
            'current_stock': stock_info['current_stock'],
            'value': stock_info['current_stock'] * get_avg_mrp(product.productid)  # Using avg MRP as base rate
        })
    
    # Calculate total inventory value
    total_value = sum(item['value'] for item in inventory_data)
    
    context = {
        'inventory_data': inventory_data,
        'total_value': total_value,
        'title': 'Inventory Report'
    }
    return render(request, 'reports/inventory_report.html', context)
    
@login_required
def batch_inventory_report(request):
    products = ProductMaster.objects.all().order_by('product_name')
    
    batch_inventory_data = []
    total_value = 0
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(product_company__icontains=search_query) |
            Q(product_category__icontains=search_query)
        )
    
    for product in products:
        stock_info = get_stock_status(product.productid)
        
        # Add batch details if there's stock
        if stock_info['current_stock'] > 0 and stock_info['expiry_stock']:
            for batch in stock_info['expiry_stock']:
                batch_value = batch['quantity'] * batch['mrp']
                total_value += batch_value
                
                days_to_expiry = (batch['expiry'] - timezone.now().date()).days if batch['expiry'] else 0
                
                batch_inventory_data.append({
                    'product': product,
                    'batch_no': batch['batch_no'],
                    'expiry': batch['expiry'],
                    'days_to_expiry': days_to_expiry,
                    'quantity': batch['quantity'],
                    'purchase_rate': batch['purchase_rate'],
                    'mrp': batch['mrp'],
                    'value': batch_value
                })
    
    # Sort by expiry date (ascending)
    batch_inventory_data.sort(key=lambda x: (x['expiry'] or datetime.max.date()))
    
    context = {
        'batch_inventory_data': batch_inventory_data,
        'total_value': total_value,
        'search_query': search_query,
        'title': 'Batch-wise Inventory Report'
    }
    return render(request, 'reports/batch_inventory_report.html', context)

@login_required
def dateexpiry_inventory_report(request):
    products = ProductMaster.objects.all().order_by('product_name')
    
    # Get date filters
    expiry_from = request.GET.get('expiry_from', '')
    expiry_to = request.GET.get('expiry_to', '')
    
    # Convert string dates to datetime objects
    try:
        expiry_from_date = datetime.strptime(expiry_from, '%Y-%m-%d').date() if expiry_from else None
        expiry_to_date = datetime.strptime(expiry_to, '%Y-%m-%d').date() if expiry_to else None
    except ValueError:
        expiry_from_date = None
        expiry_to_date = None
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(product_company__icontains=search_query) |
            Q(product_category__icontains=search_query)
        )
    
    # Group by expiry date
    expiry_grouped_data = {}
    total_value = 0
    
    for product in products:
        stock_info = get_stock_status(product.productid)
        
        if stock_info['current_stock'] > 0 and stock_info['expiry_stock']:
            for batch in stock_info['expiry_stock']:
                # Skip if outside the date range
                if expiry_from_date and batch['expiry'] < expiry_from_date:
                    continue
                if expiry_to_date and batch['expiry'] > expiry_to_date:
                    continue
                    
                expiry_date = batch['expiry']
                batch_value = batch['quantity'] * batch['mrp']
                total_value += batch_value
                
                # Group by expiry date
                if expiry_date not in expiry_grouped_data:
                    days_to_expiry = (expiry_date - timezone.now().date()).days if expiry_date else 0
                    expiry_grouped_data[expiry_date] = {
                        'expiry_date': expiry_date,
                        'days_to_expiry': days_to_expiry,
                        'products': [],
                        'total_value': 0
                    }
                
                expiry_grouped_data[expiry_date]['products'].append({
                    'product': product,
                    'batch_no': batch['batch_no'],
                    'quantity': batch['quantity'],
                    'purchase_rate': batch['purchase_rate'],
                    'mrp': batch['mrp'],
                    'value': batch_value
                })
                
                expiry_grouped_data[expiry_date]['total_value'] += batch_value
    
    # Convert to list and sort by expiry date
    expiry_data = list(expiry_grouped_data.values())
    expiry_data.sort(key=lambda x: x['expiry_date'] or datetime.max.date())
    
    context = {
        'expiry_data': expiry_data,
        'total_value': total_value,
        'search_query': search_query,
        'expiry_from': expiry_from,
        'expiry_to': expiry_to,
        'title': 'Expiry Date-wise Inventory Report'
    }
    return render(request, 'reports/dateexpiry_inventory_report.html', context)

@login_required
def sales_report(request):
    # Default to current month
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today
    
    # Get date range from request
    if request.method == 'GET' and 'start_date' in request.GET and 'end_date' in request.GET:
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    # Get sales for the selected period
    sales_invoices = SalesInvoiceMaster.objects.filter(
        sales_invoice_date__range=[start_date, end_date]
    ).order_by('-sales_invoice_date')
    
    # Get all sales for these invoices
    sales_items = SalesMaster.objects.filter(
        sales_invoice_no__in=sales_invoices
    )
    
    # Calculate totals
    total_sales = sales_items.aggregate(total=Sum('sale_total_amount'))['total'] or 0
    total_received = sales_invoices.aggregate(Sum('sales_invoice_paid'))['sales_invoice_paid__sum'] or 0
    total_pending = total_sales - total_received
    
    # Get product-wise sales
    product_sales = SalesMaster.objects.filter(
        sales_invoice_no__sales_invoice_date__range=[start_date, end_date]
    ).values('productid__product_name').annotate(
        total_quantity=Sum('sale_quantity'),
        total_amount=Sum('sale_total_amount')
    ).order_by('-total_amount')
    
    # Get customer-wise sales
    customer_sales = SalesMaster.objects.filter(
        sales_invoice_no__sales_invoice_date__range=[start_date, end_date]
    ).values('sales_invoice_no__customerid__customer_name').annotate(
        total_amount=Sum('sale_total_amount')
    ).order_by('-total_amount')
    
    context = {
        'sales_invoices': sales_invoices,
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_received': total_received,
        'total_pending': total_pending,
        'product_sales': product_sales,
        'customer_sales': customer_sales,
        'title': 'Sales Report'
    }
    return render(request, 'reports/sales_report.html', context)

@login_required
def purchase_report(request):
    # Default to current month
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today
    
    # Get date range from request
    if request.method == 'GET' and 'start_date' in request.GET and 'end_date' in request.GET:
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    # Get purchases for the selected period
    purchase_invoices = InvoiceMaster.objects.filter(
        invoice_date__range=[start_date, end_date]
    ).order_by('-invoice_date')
    
    # Calculate totals
    total_purchases = purchase_invoices.aggregate(Sum('invoice_total'))['invoice_total__sum'] or 0
    total_paid = purchase_invoices.aggregate(Sum('invoice_paid'))['invoice_paid__sum'] or 0
    total_pending = total_purchases - total_paid
    
    # Get product-wise purchases
    product_purchases = PurchaseMaster.objects.filter(
        product_invoiceid__invoice_date__range=[start_date, end_date]
    ).values('productid__product_name').annotate(
        total_quantity=Sum('product_quantity'),
        total_amount=Sum('total_amount')
    ).order_by('-total_amount')
    
    # Get supplier-wise purchases
    supplier_purchases = InvoiceMaster.objects.filter(
        invoice_date__range=[start_date, end_date]
    ).values('supplierid__supplier_name').annotate(
        total_amount=Sum('invoice_total')
    ).order_by('-total_amount')
    
    context = {
        'purchase_invoices': purchase_invoices,
        'start_date': start_date,
        'end_date': end_date,
        'total_purchases': total_purchases,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'product_purchases': product_purchases,
        'supplier_purchases': supplier_purchases,
        'title': 'Purchase Report'
    }
    return render(request, 'reports/purchase_report.html', context)

@login_required
def financial_report(request):
    # Default to current month
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today
    
    # Get date range from request
    if request.method == 'GET' and 'start_date' in request.GET and 'end_date' in request.GET:
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    # Get sales for the selected period
    # We need to calculate the sales total from SalesMaster since sales_invoice_total is a property
    sales_invoices = SalesInvoiceMaster.objects.filter(
        sales_invoice_date__range=[start_date, end_date]
    )
    
    # Get all sales invoice numbers for the filtered period
    sales_invoice_nos = sales_invoices.values_list('sales_invoice_no', flat=True)
    
    # Calculate total sales from SalesMaster
    sales = SalesMaster.objects.filter(
        sales_invoice_no__in=sales_invoice_nos
    ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
    
    # Get purchases for the selected period
    purchases = InvoiceMaster.objects.filter(
        invoice_date__range=[start_date, end_date]
    ).aggregate(total=Sum('invoice_total'))['total'] or 0
    
    # Get sales returns for the selected period
    sales_returns = ReturnSalesInvoiceMaster.objects.filter(
        return_sales_invoice_date__range=[start_date, end_date]
    ).aggregate(total=Sum('return_sales_invoice_total'))['total'] or 0
    
    # Get purchase returns for the selected period
    purchase_returns = ReturnInvoiceMaster.objects.filter(
        returninvoice_date__range=[start_date, end_date]
    ).aggregate(total=Sum('returninvoice_total'))['total'] or 0
    
    # Calculate net figures
    net_sales = sales - sales_returns
    net_purchases = purchases - purchase_returns
    
    # Calculate gross profit
    gross_profit = net_sales - net_purchases
    
    # Get monthly sales trend for the past 12 months
    end_month = timezone.now().date().replace(day=1)
    start_month = (end_month - timedelta(days=365)).replace(day=1)
    
    # Since sales_invoice_total is a property, we need to calculate monthly totals differently
    # First, get a list of all months in the period
    monthly_dates = []
    current = start_month
    while current <= end_month:
        monthly_dates.append((current, (current.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)))
        current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    # Initialize the monthly sales data structure
    monthly_sales = []
    
    # For each month, calculate the total sales
    for month_start, month_end in monthly_dates:
        # Get all sales invoices for this month
        month_invoices = SalesInvoiceMaster.objects.filter(
            sales_invoice_date__range=[month_start, month_end]
        )
        
        # Get all sales invoice numbers for this month
        month_invoice_nos = month_invoices.values_list('sales_invoice_no', flat=True)
        
        # Calculate total sales for this month from SalesMaster
        month_total = SalesMaster.objects.filter(
            sales_invoice_no__in=month_invoice_nos
        ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
        
        # Add to monthly_sales with the first day of the month
        if month_total > 0:  # Only add months with sales
            monthly_sales.append({
                'month': month_start,
                'total': month_total
            })
    
    monthly_purchases = InvoiceMaster.objects.filter(
        invoice_date__range=[start_month, end_month]
    ).annotate(
        month=TruncMonth('invoice_date')
    ).values('month').annotate(
        total=Sum('invoice_total')
    ).order_by('month')
    
    # Prepare data for chart
    months = []
    sales_data = []
    purchase_data = []
    
    # Convert query results to lists for easy access in the template
    monthly_sales_dict = {item['month']: item['total'] for item in monthly_sales}
    monthly_purchases_dict = {item['month']: item['total'] for item in monthly_purchases}
    
    # Generate all months in the range
    current_month = start_month
    while current_month <= end_month:
        month_name = current_month.strftime('%b %Y')
        months.append(month_name)
        
        # Get the values or default to 0
        sales_value = monthly_sales_dict.get(current_month, 0)
        purchase_value = monthly_purchases_dict.get(current_month, 0)
        
        sales_data.append(sales_value)
        purchase_data.append(purchase_value)
        
        # Move to next month
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year + 1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month + 1)
    
    # Calculate outstanding amounts
    # We need to calculate customer outstanding differently as sales_invoice_total is a property
    customer_outstanding = 0
    
    # Get all sales invoices
    all_sales_invoices = SalesInvoiceMaster.objects.all()
    
    # Calculate total outstanding by looping through each invoice
    for invoice in all_sales_invoices:
        # Calculate sales_invoice_total by querying SalesMaster
        invoice_total = SalesMaster.objects.filter(
            sales_invoice_no=invoice.sales_invoice_no
        ).aggregate(total=Sum('sale_total_amount'))['total'] or 0
        
        # Add the outstanding amount to the total
        customer_outstanding += (invoice_total - invoice.sales_invoice_paid)
    
    supplier_outstanding = InvoiceMaster.objects.aggregate(
        total=Sum(F('invoice_total') - F('invoice_paid'))
    )['total'] or 0
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'sales': sales,
        'purchases': purchases,
        'sales_returns': sales_returns,
        'purchase_returns': purchase_returns,
        'net_sales': net_sales,
        'net_purchases': net_purchases,
        'gross_profit': gross_profit,
        'months': json.dumps(months),
        'sales_data': json.dumps(sales_data),
        'purchase_data': json.dumps(purchase_data),
        'customer_outstanding': customer_outstanding,
        'supplier_outstanding': supplier_outstanding,
        'title': 'Financial Report'
    }
    return render(request, 'reports/financial_report.html', context)

# API views for AJAX requests
@login_required
def get_product_info(request):
    if request.method == 'GET' and 'product_id' in request.GET:
        product_id = request.GET.get('product_id')
        batch_no = request.GET.get('batch_no')
        
        try:
            product = ProductMaster.objects.get(productid=product_id)
            stock_info = get_stock_status(product_id)
            
            data = {
                'product_name': product.product_name,
                'product_company': product.product_company,
                'product_packing': product.product_packing,
                # Product data fields
                "id": product.productid,
                "name": product.product_name,
                "company": product.product_company,
                'product_hsn_percent': product.product_hsn_percent,
                'stock_quantity': stock_info['current_stock'],
                'product_expiry': None
            }
            
            # If batch number is provided
            if batch_no:
                # Try to get batch-specific rates
                try:
                    batch_rate = SaleRateMaster.objects.get(
                        productid=product,
                        product_batch_no=batch_no
                    )
                    # Override with batch-specific rates
                    data['rate_A'] = batch_rate.rate_A
                    data['rate_B'] = batch_rate.rate_B
                    data['rate_C'] = batch_rate.rate_C
                except SaleRateMaster.DoesNotExist:
                    # Keep using product default rates
                    pass
                
                # Get expiry date from purchases for this batch
                try:
                    purchase = PurchaseMaster.objects.filter(
                        productid=product,
                        product_batch_no=batch_no
                    ).order_by('-purchase_entry_date').first()
                    
                    if purchase and purchase.product_expiry:
                        data['product_expiry'] = purchase.product_expiry.strftime('%Y-%m-%d')
                except Exception as e:
                    # If there's any error, just continue without the expiry date
                    pass
                
                # Check stock availability for this batch
                from .utils import get_batch_stock_status
                batch_quantity, is_available = get_batch_stock_status(product_id, batch_no)
                data['batch_stock_quantity'] = batch_quantity
                data['batch_stock_available'] = is_available
            
            return JsonResponse(data)
        except ProductMaster.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def export_inventory_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Product ID', 'Product Name', 'Company', 'Packing', 'Category', 'Current Stock', 'Value'])
    
    products = ProductMaster.objects.all().order_by('product_name')
    
    for product in products:
        stock_info = get_stock_status(product.productid)
        writer.writerow([
            product.productid,
            product.product_name,
            product.product_company,
            product.product_packing,
            product.product_category,
            stock_info['current_stock'],
            stock_info['current_stock'] * get_avg_mrp(product.productid)  # Using avg MRP as base rate
        ])
    
    return response

# Sale Rate Management Views
@login_required
def sale_rate_list(request):
    # Fetch sale rates
    sale_rates = SaleRateMaster.objects.all().select_related('productid').order_by('productid__product_name', 'product_batch_no')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        sale_rates = sale_rates.filter(
            Q(productid__product_name__icontains=search_query) | 
            Q(product_batch_no__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(sale_rates, 10)  # 10 items per page
    page_number = request.GET.get('page')
    sale_rates = paginator.get_page(page_number)
    
    context = {
        'sale_rates': sale_rates,
        'search_query': search_query,
        'title': 'Sale Rate List'
    }
    return render(request, 'rates/sale_rate_list.html', context)

@login_required
def add_sale_rate(request):
    if request.method == 'POST':
        form = SaleRateForm(request.POST)
        if form.is_valid():
            # Check if a rate for this product and batch already exists
            try:
                # Try to get existing record
                existing_rate = SaleRateMaster.objects.get(
                    productid=form.cleaned_data['productid'],
                    product_batch_no=form.cleaned_data['product_batch_no']
                )
                # If found, show an error
                messages.error(request, f"A rate for this product and batch already exists. Please edit the existing record instead.")
                return redirect('sale_rate_list')
            except SaleRateMaster.DoesNotExist:
                # If not found, save the new rate
                sale_rate = form.save()
                messages.success(request, f"Sale rate for {sale_rate.productid.product_name} - Batch {sale_rate.product_batch_no} added successfully!")
                return redirect('sale_rate_list')
    else:
        form = SaleRateForm()
    
    context = {
        'form': form,
        'title': 'Add Sale Rate'
    }
    return render(request, 'rates/sale_rate_form.html', context)

@login_required
def update_sale_rate(request, pk):
    sale_rate = get_object_or_404(SaleRateMaster, pk=pk)
    
    if request.method == 'POST':
        form = SaleRateForm(request.POST, instance=sale_rate)
        if form.is_valid():
            form.save()
            messages.success(request, f"Sale rate for {sale_rate.productid.product_name} - Batch {sale_rate.product_batch_no} updated successfully!")
            return redirect('sale_rate_list')
    else:
        form = SaleRateForm(instance=sale_rate)
    
    context = {
        'form': form,
        'sale_rate': sale_rate,
        'title': 'Update Sale Rate'
    }
    return render(request, 'rates/sale_rate_form.html', context)

@login_required
def delete_sale_rate(request, pk):
    # Check if user is admin (case-insensitive)
    if not request.user.user_type.lower() in ['admin']:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('sale_rate_list')
        
    sale_rate = get_object_or_404(SaleRateMaster, pk=pk)
    
    if request.method == 'POST':
        product_name = sale_rate.productid.product_name
        batch_no = sale_rate.product_batch_no
        try:
            sale_rate.delete()
            messages.success(request, f"Sale rate for {product_name} - Batch {batch_no} deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete sale rate. Error: {str(e)}")
        return redirect('sale_rate_list')
    
    context = {
        'sale_rate': sale_rate,
        'title': 'Delete Sale Rate'
    }
    return render(request, 'rates/sale_rate_confirm_delete.html', context)

@login_required
def delete_user(request, pk):
    # Check if user is admin
    if not request.user.user_type.lower() == 'admin':
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('dashboard')
    
    # Prevent admin from deleting themselves
    if request.user.id == pk:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user_list')
    
    user = get_object_or_404(Web_User, id=pk)
    
    if request.method == 'POST':
        username = user.username
        try:
            user.delete()
            messages.success(request, f"User '{username}' deleted successfully!")
        except Exception as e:
            messages.error(request, f"Cannot delete user. Error: {str(e)}")
        return redirect('user_list')
    
    context = {
        'user_obj': user,  # Using user_obj to avoid conflict with request.user
        'title': 'Delete User'
    }
    return render(request, 'user_confirm_delete.html', context)
