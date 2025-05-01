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
    ReturnPurchaseMaster, ReturnSalesInvoiceMaster, ReturnSalesInvoicePaid, ReturnSalesMaster
)
from .forms import (
    LoginForm, UserRegistrationForm, UserUpdateForm, PharmacyDetailsForm, ProductForm,
    SupplierForm, CustomerForm, InvoiceForm, InvoicePaymentForm, PurchaseForm,
    SalesInvoiceForm, SalesForm, SalesPaymentForm, ProductRateForm,
    PurchaseReturnInvoiceForm, PurchaseReturnForm, SalesReturnInvoiceForm, SalesReturnForm
)
from .utils import get_stock_status, generate_invoice_pdf, generate_sales_invoice_pdf

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
    monthly_sales = SalesInvoiceMaster.objects.filter(
        sales_invoice_date__gte=current_month_start
    ).aggregate(total=Sum('sales_invoice_total'))['total'] or 0
    
    # Monthly purchases
    monthly_purchases = InvoiceMaster.objects.filter(
        invoice_date__gte=current_month_start
    ).aggregate(total=Sum('invoice_total'))['total'] or 0
    
    # Total outstanding payments from customers
    total_receivable = SalesInvoiceMaster.objects.aggregate(
        total=Sum(F('sales_invoice_total') - F('sales_invoice_paid'))
    )['total'] or 0
    
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
    
    # Pagination
    paginator = Paginator(products, 10)  # 10 products per page
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
                            'rate_A': float(row.get('rate_A', 0) or 0),
                            'rate_B': float(row.get('rate_B', 0) or 0),
                            'rate_C': float(row.get('rate_C', 0) or 0),
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
            'product_hsn_percent', 'rate_A', 'rate_B', 'rate_C'
        ])
        
        # Add sample row
        writer.writerow([
            'Paracetamol 500mg', 'ABC Pharma', '10x10',
            'Paracetamol', 'Analgesic', '30049099',
            '12', '5.0', '4.5', '4.0'
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
            
            # Transport charges are not included in product calculations
            # They are additional charges separate from the invoice total
            purchase.product_transportation_charges = 0
            
            # Calculate actual rate based on discount and quantity
            if purchase.purchase_calculation_mode == 'flat':
                # Flat discount amount
                purchase.actual_rate_per_qty = purchase.product_purchase_rate - (purchase.product_discount_got / purchase.product_quantity)
            else:
                # Percentage discount
                purchase.actual_rate_per_qty = purchase.product_purchase_rate * (1 - (purchase.product_discount_got / 100))
            
            purchase.product_actual_rate = purchase.actual_rate_per_qty
            
            # Calculate total amount
            purchase.total_amount = purchase.product_actual_rate * purchase.product_quantity
            
            purchase.save()
            
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
def add_sale(request, invoice_id):
    invoice = get_object_or_404(SalesInvoiceMaster, sales_invoice_no=invoice_id)
    
    if request.method == 'POST':
        form = SalesForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            
            # Set additional fields
            sale.sales_invoice_no = invoice
            sale.customerid = invoice.customerid
            
            # Get product details from the selected product
            product = sale.productid
            sale.product_name = product.product_name
            sale.product_company = product.product_company
            sale.product_packing = product.product_packing
            
            # Set appropriate rate based on customer type and selected rate type
            if sale.rate_applied == 'A':
                sale.sale_rate = product.rate_A
            elif sale.rate_applied == 'B':
                sale.sale_rate = product.rate_B
            elif sale.rate_applied == 'C':
                sale.sale_rate = product.rate_C
            # Custom rate is already set in the form
            
            # Calculate total amount based on discount
            if sale.sale_calculation_mode == 'flat':
                # Flat discount amount
                actual_rate = sale.sale_rate - (sale.sale_discount / sale.sale_quantity if sale.sale_quantity else 0)
            else:
                # Percentage discount
                actual_rate = sale.sale_rate * (1 - (sale.sale_discount / 100))
            
            # Add GST if applicable
            sale.sale_total_amount = (actual_rate * sale.sale_quantity) * (1 + (sale.sale_igst / 100))
            
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
def add_sales_payment(request, invoice_id):
    invoice = get_object_or_404(SalesInvoiceMaster, sales_invoice_no=invoice_id)
    
    if request.method == 'POST':
        form = SalesPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.sales_ip_invoice_no = invoice
            
            # Check if payment amount is valid
            if payment.sales_payment_amount > (invoice.sales_invoice_total - invoice.sales_invoice_paid):
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
    
    context = {
        'form': form,
        'invoice': invoice,
        'balance': invoice.sales_invoice_total - invoice.sales_invoice_paid,
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
    if request.method == 'POST':
        form = PurchaseReturnInvoiceForm(request.POST)
        if form.is_valid():
            return_invoice = form.save(commit=False)
            return_invoice.returninvoice_paid = 0  # Initialize paid amount to 0
            return_invoice.save()
            messages.success(request, f"Purchase Return #{return_invoice.returninvoiceid} added successfully!")
            return redirect('purchase_return_detail', pk=return_invoice.returninvoiceid)
    else:
        form = PurchaseReturnInvoiceForm()
    
    context = {
        'form': form,
        'title': 'Add Purchase Return'
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
def add_purchase_return_item(request, return_id):
    return_invoice = get_object_or_404(ReturnInvoiceMaster, returninvoiceid=return_id)
    
    if request.method == 'POST':
        form = PurchaseReturnForm(request.POST)
        if form.is_valid():
            return_item = form.save(commit=False)
            
            # Set additional fields
            return_item.returninvoiceid = return_invoice
            return_item.returnproduct_supplierid = return_invoice.returnsupplierid
            
            # Calculate total amount
            return_item.returntotal_amount = return_item.returnproduct_purchase_rate * return_item.returnproduct_quantity
            
            return_item.save()
            
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
    if request.method == 'POST':
        form = SalesReturnInvoiceForm(request.POST)
        if form.is_valid():
            return_invoice = form.save(commit=False)
            return_invoice.return_sales_invoice_paid = 0  # Initialize paid amount to 0
            return_invoice.save()
            messages.success(request, f"Sales Return #{return_invoice.return_sales_invoice_no} added successfully!")
            return redirect('sales_return_detail', pk=return_invoice.return_sales_invoice_no)
    else:
        form = SalesReturnInvoiceForm()
    
    context = {
        'form': form,
        'title': 'Add Sales Return'
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
def add_sales_return_item(request, return_id):
    return_invoice = get_object_or_404(ReturnSalesInvoiceMaster, return_sales_invoice_no=return_id)
    
    if request.method == 'POST':
        form = SalesReturnForm(request.POST)
        if form.is_valid():
            return_item = form.save(commit=False)
            
            # Set additional fields
            return_item.return_sales_invoice_no = return_invoice
            return_item.return_customerid = return_invoice.return_sales_customerid
            
            # Get product details
            product = return_item.return_productid
            return_item.return_product_name = product.product_name
            return_item.return_product_company = product.product_company
            return_item.return_product_packing = product.product_packing
            
            # Calculate total amount
            base_amount = return_item.return_sale_rate * return_item.return_sale_quantity
            discount_amount = 0
            
            # Apply discount
            if return_item.return_sale_discount > 0:
                discount_amount = (return_item.return_sale_discount / 100) * base_amount
            
            # Apply GST
            gst_amount = ((base_amount - discount_amount) * return_item.return_sale_igst) / 100
            
            return_item.return_sale_total_amount = base_amount - discount_amount + gst_amount
            
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
            'value': stock_info['current_stock'] * product.rate_A  # Using rate_A as base rate
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
    
    # Calculate totals
    total_sales = sales_invoices.aggregate(Sum('sales_invoice_total'))['sales_invoice_total__sum'] or 0
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
    customer_sales = SalesInvoiceMaster.objects.filter(
        sales_invoice_date__range=[start_date, end_date]
    ).values('customerid__customer_name').annotate(
        total_amount=Sum('sales_invoice_total')
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
    sales = SalesInvoiceMaster.objects.filter(
        sales_invoice_date__range=[start_date, end_date]
    ).aggregate(total=Sum('sales_invoice_total'))['total'] or 0
    
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
    
    monthly_sales = SalesInvoiceMaster.objects.filter(
        sales_invoice_date__range=[start_month, end_month]
    ).annotate(
        month=TruncMonth('sales_invoice_date')
    ).values('month').annotate(
        total=Sum('sales_invoice_total')
    ).order_by('month')
    
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
    customer_outstanding = SalesInvoiceMaster.objects.aggregate(
        total=Sum(F('sales_invoice_total') - F('sales_invoice_paid'))
    )['total'] or 0
    
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
        try:
            product = ProductMaster.objects.get(productid=product_id)
            stock_info = get_stock_status(product_id)
            
            data = {
                'product_name': product.product_name,
                'product_company': product.product_company,
                'product_packing': product.product_packing,
                'rate_A': product.rate_A,
                'rate_B': product.rate_B,
                'rate_C': product.rate_C,
                'product_hsn': product.product_hsn,
                'product_hsn_percent': product.product_hsn_percent,
                'stock_quantity': stock_info['current_stock']
            }
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
            stock_info['current_stock'] * product.rate_A  # Using rate_A as base rate
        ])
    
    return response
