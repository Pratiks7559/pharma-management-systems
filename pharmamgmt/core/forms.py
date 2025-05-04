from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    Web_User, Pharmacy_Details, ProductMaster, SupplierMaster, CustomerMaster,
    InvoiceMaster, InvoicePaid, PurchaseMaster, SalesInvoiceMaster, SalesMaster,
    SalesInvoicePaid, ProductRateMaster, ReturnInvoiceMaster, PurchaseReturnInvoicePaid,
    ReturnPurchaseMaster, ReturnSalesInvoiceMaster, ReturnSalesInvoicePaid, ReturnSalesMaster,
    SaleRateMaster
)

class DateInput(forms.DateInput):
    input_type = 'date'

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class UserRegistrationForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]
    
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    user_contact = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    path = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Web_User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'user_type', 'user_contact', 'path']

class UserUpdateForm(forms.ModelForm):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]
    
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    user_contact = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    path = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Web_User
        fields = ['first_name', 'last_name', 'email', 'user_type', 'user_contact', 'path']

class PharmacyDetailsForm(forms.ModelForm):
    pharmaname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    pharmaweburl = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    proprietorname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    proprietorcontact = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    proprietoremail = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Pharmacy_Details
        fields = '__all__'

class ProductForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('powder', 'Powder'),
        ('drops', 'Drops'),
        ('other', 'Other'),
    ]
    
    product_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_packing = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_salt = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    product_hsn = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_hsn_percent = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = ProductMaster
        fields = ['product_name', 'product_company', 'product_packing', 'product_salt', 
                  'product_category', 'product_hsn', 'product_hsn_percent', 'product_image']

class SupplierForm(forms.ModelForm):
    supplier_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_type = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    supplier_mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_whatsapp = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_emailid = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    supplier_spoc = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_dlno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_gstno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_bank = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_bankaccountno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_bankifsc = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    supplier_upi = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = SupplierMaster
        fields = '__all__'

class CustomerForm(forms.ModelForm):
    CUSTOMER_TYPE_CHOICES = [
        ('TYPE-A', 'Type A'),
        ('TYPE-B', 'Type B'),
        ('TYPE-C', 'Type C'),
    ]
    
    customer_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_type = forms.ChoiceField(choices=CUSTOMER_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    customer_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    customer_mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_whatsapp = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_emailid = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    customer_spoc = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_dlno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_gstno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_bank = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_bankaccountno = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_bankifsc = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_upi = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_credit_days = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = CustomerMaster
        fields = '__all__'

class InvoiceForm(forms.ModelForm):
    invoice_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    invoice_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    supplierid = forms.ModelChoiceField(queryset=SupplierMaster.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    transport_charges = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    invoice_total = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    
    class Meta:
        model = InvoiceMaster
        fields = ['invoice_no', 'invoice_date', 'supplierid', 'transport_charges', 'invoice_total']

class InvoicePaymentForm(forms.ModelForm):
    payment_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    payment_amount = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    payment_mode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    payment_ref_no = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = InvoicePaid
        fields = ['payment_date', 'payment_amount', 'payment_mode', 'payment_ref_no']
        exclude = ['ip_invoiceid']

class PurchaseForm(forms.ModelForm):
    product_batch_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_expiry = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    product_MRP = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    product_purchase_rate = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    product_quantity = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    product_scheme = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    product_discount_got = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    IGST = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    CALC_MODE_CHOICES = [
        ('flat', 'Flat Amount'),
        ('perc', 'Percentage'),
    ]
    purchase_calculation_mode = forms.ChoiceField(choices=CALC_MODE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    # Fields for batch-specific sale rates
    rate_A = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), required=False)
    rate_B = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), required=False)
    rate_C = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), required=False)
    
    class Meta:
        model = PurchaseMaster
        fields = ['productid', 'product_batch_no', 'product_expiry', 'product_MRP',
                 'product_purchase_rate', 'product_quantity', 'product_scheme',
                 'product_discount_got', 'IGST', 'purchase_calculation_mode',
                 'rate_A', 'rate_B', 'rate_C']
        exclude = ['product_supplierid', 'product_invoiceid', 'product_invoice_no',
                  'product_name', 'product_company', 'product_packing',
                  'product_transportation_charges', 'actual_rate_per_qty',
                  'product_actual_rate', 'total_amount', 'purchase_entry_date']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['productid'].queryset = ProductMaster.objects.all()
        self.fields['productid'].widget.attrs.update({'class': 'form-control'})
        self.fields['productid'].label = 'Product'

class SalesInvoiceForm(forms.ModelForm):
    sales_invoice_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    customerid = forms.ModelChoiceField(queryset=CustomerMaster.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    sales_transport_charges = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), initial=0)
    
    class Meta:
        model = SalesInvoiceMaster
        fields = ['sales_invoice_date', 'customerid', 'sales_transport_charges']

class SalesForm(forms.ModelForm):
    product_batch_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    product_expiry = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    sale_rate = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}))
    sale_quantity = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    sale_scheme = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    sale_discount = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    sale_igst = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    custom_rate = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    RATE_CHOICES = [
        ('A', 'Rate A'),
        ('B', 'Rate B'),
        ('C', 'Rate C'),
        ('custom', 'Custom Rate'),
    ]
    rate_applied = forms.ChoiceField(choices=RATE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    CALC_MODE_CHOICES = [
        ('flat', 'Flat Amount'),
        ('perc', 'Percentage'),
    ]
    sale_calculation_mode = forms.ChoiceField(choices=CALC_MODE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = SalesMaster
        fields = ['productid', 'product_batch_no', 'product_expiry', 
                 'sale_rate', 'sale_quantity', 'sale_scheme',
                 'sale_discount', 'sale_igst', 'custom_rate', 'rate_applied', 'sale_calculation_mode']
        exclude = ['sales_invoice_no', 'customerid', 'product_name', 'product_company', 
                  'product_packing', 'product_MRP', 'sale_total_amount', 'sale_entry_date']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['productid'].queryset = ProductMaster.objects.all()
        self.fields['productid'].widget.attrs.update({'class': 'form-control'})
        self.fields['productid'].label = 'Product'

class SalesPaymentForm(forms.ModelForm):
    sales_payment_date = forms.DateTimeField(widget=DateInput(attrs={'class': 'form-control'}))
    sales_payment_amount = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('online', 'Online Transfer'),
        ('upi', 'UPI'),
    ]
    sales_payment_mode = forms.ChoiceField(choices=PAYMENT_MODE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    sales_payment_ref_no = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = SalesInvoicePaid
        fields = ['sales_payment_date', 'sales_payment_amount', 'sales_payment_mode', 'sales_payment_ref_no']
        exclude = ['sales_ip_invoice_no']

class ProductRateForm(forms.ModelForm):
    rate_A = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    rate_B = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    rate_C = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    rate_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = ProductRateMaster
        fields = ['rate_productid', 'rate_A', 'rate_B', 'rate_C', 'rate_date']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rate_productid'].queryset = ProductMaster.objects.all()
        self.fields['rate_productid'].widget.attrs.update({'class': 'form-control'})
        self.fields['rate_productid'].label = 'Product'

class PurchaseReturnInvoiceForm(forms.ModelForm):
    returninvoiceid = forms.CharField(required=False, widget=forms.HiddenInput())
    returninvoice_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    returnsupplierid = forms.ModelChoiceField(queryset=SupplierMaster.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    return_charges = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), initial=0.0)
    returninvoice_total = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), initial=0.0)
    
    class Meta:
        model = ReturnInvoiceMaster
        fields = ['returninvoiceid', 'returninvoice_date', 'returnsupplierid', 'return_charges', 'returninvoice_total']

class PurchaseReturnForm(forms.ModelForm):
    returnproduct_batch_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    returnproduct_expiry = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    returnproduct_MRP = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    returnproduct_purchase_rate = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    returnproduct_quantity = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    returnproduct_scheme = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    returnproduct_charges = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    return_reason = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    class Meta:
        model = ReturnPurchaseMaster
        fields = ['returnproductid', 'returnproduct_batch_no', 'returnproduct_expiry', 
                 'returnproduct_MRP', 'returnproduct_purchase_rate', 
                 'returnproduct_quantity', 'returnproduct_scheme', 'returnproduct_charges',
                 'return_reason']
        exclude = ['returninvoiceid', 'returnproduct_supplierid', 'returntotal_amount', 'returnpurchase_entry_date']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['returnproductid'].queryset = ProductMaster.objects.all()
        self.fields['returnproductid'].widget.attrs.update({'class': 'form-control'})
        self.fields['returnproductid'].label = 'Product'

class SalesReturnInvoiceForm(forms.ModelForm):
    return_sales_invoice_no = forms.CharField(required=False, widget=forms.HiddenInput())
    return_sales_invoice_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    return_sales_customerid = forms.ModelChoiceField(queryset=CustomerMaster.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    return_sales_charges = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), initial=0.0)
    return_sales_invoice_total = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), initial=0.0)
    
    class Meta:
        model = ReturnSalesInvoiceMaster
        fields = ['return_sales_invoice_no', 'return_sales_invoice_date', 'return_sales_customerid', 
                 'return_sales_charges', 'return_sales_invoice_total']

class SalesReturnForm(forms.ModelForm):
    return_product_batch_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    return_product_expiry = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    return_product_MRP = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    return_sale_rate = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    return_sale_quantity = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    return_sale_scheme = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}), required=False, initial=0)
    return_sale_discount = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    return_sale_igst = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    return_reason = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    return_sale_calculation_mode = forms.ChoiceField(
        choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='percentage'
    )
    
    class Meta:
        model = ReturnSalesMaster
        fields = ['return_productid', 'return_product_batch_no', 'return_product_expiry',
                 'return_product_MRP', 'return_sale_rate', 'return_sale_quantity', 'return_sale_scheme',
                 'return_sale_discount', 'return_sale_igst', 'return_reason',
                 'return_sale_calculation_mode']
        exclude = ['return_sales_invoice_no', 'return_customerid', 'return_product_name',
                  'return_product_company', 'return_product_packing',
                  'return_sale_total_amount', 'return_sale_entry_date']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['return_productid'].queryset = ProductMaster.objects.all()
        self.fields['return_productid'].widget.attrs.update({'class': 'form-control'})
        self.fields['return_productid'].label = 'Product'
        
class SaleRateForm(forms.ModelForm):
    productid = forms.ModelChoiceField(
        queryset=ProductMaster.objects.all().order_by('product_name'),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    product_batch_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    rate_A = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    rate_B = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    rate_C = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    
    class Meta:
        model = SaleRateMaster
        fields = ['productid', 'product_batch_no', 'rate_A', 'rate_B', 'rate_C']
