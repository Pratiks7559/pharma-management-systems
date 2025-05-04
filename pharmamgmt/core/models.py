from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime 

# Create your models here.
class Web_User(AbstractUser):
    # firstname=models.CharField(max_length=150, null=False, blank=False )
    # lastname=models.CharField(max_length=150, null=False, blank=False)
    username=models.CharField(max_length=150, unique=True, null=False, blank=False)
    password=models.CharField(max_length=100)
    user_type=models.CharField(max_length=50)
    user_contact=models.CharField(max_length=100)
    # path = models.ImageField(upload_to='images/')
    path = models.ImageField(upload_to='images/',default='images/default.png')
    def __str__(self):  
        return self.username
    # profile_picture = models.ImageField(upload_to='images/', blank=True, null=True)    
    # user_isactive=models.DecimalField(max_digits=1,decimal_places=0, default=0)
    # add additional fields in here
  
    
class Pharmacy_Details(models.Model):
    pharmaname=models.CharField(max_length=300)
    pharmaweburl=models.CharField(max_length=150)
    proprietorname=models.CharField(max_length=100)
    proprietorcontact=models.CharField(max_length=12)
    proprietoremail=models.CharField(max_length=100)
    
    def __str__(self):
        return self.pharmaname

class ProductMaster(models.Model):
    productid=models.BigAutoField(primary_key=True, auto_created=True)
    product_name=models.CharField(max_length=200)
    product_company=models.CharField(max_length=200)
    product_packing=models.CharField(max_length=20)
    product_image=models.ImageField(upload_to='images/',default='images/medicine_default.png', null=True)
    product_salt=models.CharField(max_length=300, default=None)
    product_category=models.CharField(max_length=30, default=None)
    product_hsn=models.CharField(max_length=20, default=None)
    product_hsn_percent=models.CharField(max_length=20, default=None)
    
    def __str__(self):
        return f"{self.product_name} ({self.product_company})"
    
class SupplierMaster(models.Model):
    supplierid=models.BigAutoField(primary_key=True, auto_created=True)
    supplier_name=models.CharField(max_length=200)
    supplier_type=models.CharField(max_length=200)
    supplier_address=models.CharField(max_length=200)
    supplier_mobile=models.CharField(max_length=15)
    supplier_whatsapp=models.CharField(max_length=15)
    supplier_emailid=models.CharField(max_length=60)
    supplier_spoc=models.CharField(max_length=100)
    supplier_dlno=models.CharField(max_length=30)
    supplier_gstno=models.CharField(max_length=20)
    supplier_bank=models.CharField(max_length=200)
    supplier_bankaccountno=models.CharField(max_length=30)
    supplier_bankifsc=models.CharField(max_length=20)
    supplier_upi=models.CharField(max_length=50, null=True)
    
    def __str__(self):
        return self.supplier_name

class CustomerMaster(models.Model):
    customerid=models.BigAutoField(primary_key=True, auto_created=True)
    customer_name=models.CharField(max_length=200, default='NA')
    customer_type=models.CharField(max_length=200, blank=True, default='TYPE-A')
    customer_address=models.CharField(max_length=200, blank=True, default='NA')
    customer_mobile=models.CharField(max_length=15, blank=True, default='NA')
    customer_whatsapp=models.CharField(max_length=15, blank=True, default='NA')
    customer_emailid=models.CharField(max_length=60, blank=True, default='NA')
    customer_spoc=models.CharField(max_length=100, blank=True, default='NA')
    customer_dlno=models.CharField(max_length=30, blank=True, default='NA')
    customer_gstno=models.CharField(max_length=20, blank=True, default='NA')
    customer_bank=models.CharField(max_length=200,blank=True, default='NA')
    customer_bankaccountno=models.CharField(max_length=30,blank=True, default='NA')
    customer_bankifsc=models.CharField(max_length=20, blank=True, default='NA')
    customer_upi=models.CharField(max_length=50, blank=True)
    customer_credit_days=models.IntegerField(blank=True, default=0)
    
    def __str__(self):
        return self.customer_name

class InvoiceMaster(models.Model):
    invoiceid=models.BigAutoField(primary_key=True, auto_created=True)
    invoice_no=models.CharField(max_length=20)
    invoice_date=models.DateField(null=False, blank=False, default=datetime.now)
    supplierid=models.ForeignKey(SupplierMaster, on_delete=models.CASCADE)
    transport_charges=models.FloatField()
    invoice_total=models.FloatField(null=False, blank=False)
    invoice_paid=models.FloatField(null=False, blank=False, default=0)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['invoice_no', 'supplierid'], name='unique_invoiceno_supplierid')
        ]
    
    def __str__(self):
        return f"Invoice #{self.invoice_no} - {self.supplierid.supplier_name}"
    
    @property
    def balance_due(self):
        return self.invoice_total - self.invoice_paid

class InvoicePaid(models.Model):
    payment_id=models.BigAutoField(primary_key=True, auto_created=True)
    ip_invoiceid=models.ForeignKey(InvoiceMaster, on_delete=models.CASCADE)
    payment_date=models.DateField(null=False, blank=False, default=datetime.now)
    payment_amount=models.FloatField()
    payment_mode=models.CharField(max_length=30, null=True)
    payment_ref_no=models.CharField(max_length=30, null=True)
    
    def __str__(self):
        return f"Payment of {self.payment_amount} for Invoice #{self.ip_invoiceid.invoice_no}"

class PurchaseMaster(models.Model):
    purchaseid=models.BigAutoField(primary_key=True, auto_created=True) 
    product_supplierid=models.ForeignKey(SupplierMaster, on_delete=models.CASCADE)
    product_invoiceid=models.ForeignKey(InvoiceMaster, on_delete=models.CASCADE, default=1)
    product_invoice_no=models.CharField(max_length=20)
    productid=models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    product_name=models.CharField(max_length=200)
    product_company=models.CharField(max_length=200)
    product_packing=models.CharField(max_length=20)
    product_batch_no=models.CharField(max_length=20)
    product_expiry=models.DateField(default=datetime.now) 
    product_MRP=models.FloatField()
    product_purchase_rate=models.FloatField()  
    product_quantity=models.FloatField()
    product_scheme=models.FloatField(default=0.0)
    product_discount_got=models.FloatField()
    product_transportation_charges=models.FloatField()   
    actual_rate_per_qty=models.FloatField(default=0.0)  
    product_actual_rate=models.FloatField(default=0.0)
    total_amount=models.FloatField(default=0.0)  
    purchase_entry_date=models.DateTimeField(default=datetime.now)
    IGST=models.FloatField(default=0.0)
    purchase_calculation_mode=models.CharField(max_length=5, default='flat') 
    #calculation_mode indicates how discount is calculated by flat-rupees or %-percent
    
    def __str__(self):
        return f"{self.product_name} - {self.product_batch_no} - {self.product_quantity}"

class SalesInvoiceMaster(models.Model):
    sales_invoice_no=models.CharField(primary_key=True, max_length=20)
    sales_invoice_date=models.DateField(null=False, blank=False)
    customerid=models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    sales_transport_charges=models.FloatField(default=0)
    sales_invoice_paid=models.FloatField(null=False, blank=False, default=0)
    
    def __str__(self):
        return f"Sales Invoice #{self.sales_invoice_no} - {self.customerid.customer_name}"
    
    @property
    def sales_invoice_total(self):
        """Calculate total from the sum of all sales items"""
        from django.db.models import Sum
        sales_total = SalesMaster.objects.filter(sales_invoice_no=self.sales_invoice_no).aggregate(Sum('sale_total_amount'))
        return sales_total['sale_total_amount__sum'] or 0
    
    @property
    def balance_due(self):
        return self.sales_invoice_total - self.sales_invoice_paid

class SalesMaster(models.Model):
    sales_invoice_no=models.ForeignKey(SalesInvoiceMaster, on_delete=models.CASCADE)
    customerid=models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    productid=models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    product_name=models.CharField(max_length=200, default='NA')
    product_company=models.CharField(max_length=200, blank=True, default='NA')
    product_packing=models.CharField(max_length=20, blank=True, default='NA')
    product_batch_no=models.CharField(max_length=20)
    product_expiry=models.DateField(default=datetime.now)
    product_MRP=models.FloatField(default=0.0)
    sale_rate=models.FloatField(default=0.0)
    sale_quantity=models.FloatField(default=0.0)
    sale_scheme=models.FloatField(default=0.0)
    sale_discount=models.FloatField(default=0.0)
    sale_igst=models.FloatField(default=0.0)
    sale_total_amount=models.FloatField(default=0.0)
    sale_entry_date=models.DateTimeField(default=datetime.now)
    rate_applied=models.CharField(max_length=10, blank=True, default='NA')
    sale_calculation_mode=models.CharField(max_length=5, default='flat') 
    #calculation_mode indicates how discount is calculated by flat-rupees or %-percent
   
    def __str__(self):
        return f"{self.product_name} - {self.product_batch_no} - {self.sale_quantity}"

class SalesInvoicePaid(models.Model):
    sales_payment_id=models.BigAutoField(primary_key=True, auto_created=True)
    sales_ip_invoice_no=models.ForeignKey(SalesInvoiceMaster, on_delete=models.CASCADE)
    sales_payment_date=models.DateTimeField(default=datetime.now)
    sales_payment_amount=models.FloatField()
    sales_payment_mode=models.CharField(max_length=30, default='NA')
    sales_payment_ref_no=models.CharField(max_length=30,default='NA')
    
    def __str__(self):
        return f"Payment of {self.sales_payment_amount} for Sales Invoice #{self.sales_ip_invoice_no.sales_invoice_no}"

class ProductRateMaster(models.Model):
    rate_productid=models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    rate_A=models.FloatField(default=0.0)
    rate_B=models.FloatField(default=0.0)
    rate_C=models.FloatField(default=0.0)
    rate_date=models.DateField(null=False, blank=False, default=datetime.now)
    
    def __str__(self):
        return f"Rates for {self.rate_productid.product_name} as of {self.rate_date}"

class ReturnInvoiceMaster(models.Model):
    returninvoiceid=models.CharField(primary_key=True, max_length=20)
    returninvoice_date=models.DateField(null=False, blank=False, default=datetime.now)
    returnsupplierid=models.ForeignKey(SupplierMaster, on_delete=models.CASCADE)
    return_charges=models.FloatField(default=0)
    returninvoice_total=models.FloatField(null=False, blank=False)
    returninvoice_paid=models.FloatField(null=False, blank=False, default=0)
    
    def __str__(self):
        return f"Return Invoice #{self.returninvoiceid} - {self.returnsupplierid.supplier_name}"
    
    @property
    def balance_due(self):
        return self.returninvoice_total - self.returninvoice_paid

class PurchaseReturnInvoicePaid(models.Model):
    pr_payment_id=models.BigAutoField(primary_key=True, auto_created=True)
    pr_ip_returninvoiceid=models.ForeignKey(ReturnInvoiceMaster, on_delete=models.CASCADE)
    pr_payment_date=models.DateField(null=False, blank=False, default=datetime.now)
    pr_payment_amount=models.FloatField()
    pr_payment_mode=models.CharField(max_length=30, null=True)
    pr_payment_ref_no=models.CharField(max_length=30, null=True)
    
    def __str__(self):
        return f"Return Payment of {self.pr_payment_amount} for Return Invoice #{self.pr_ip_returninvoiceid.returninvoiceid}"

class ReturnPurchaseMaster(models.Model):
    returnpurchaseid=models.BigAutoField(primary_key=True, auto_created=True)
    returninvoiceid=models.ForeignKey(ReturnInvoiceMaster, on_delete=models.CASCADE, default=1) 
    returnproduct_supplierid=models.ForeignKey(SupplierMaster, on_delete=models.CASCADE)
    returnproductid=models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    returnproduct_batch_no=models.CharField(max_length=20)
    returnproduct_expiry=models.DateField(default=datetime.now)
    returnproduct_MRP=models.FloatField(default=0.0)  
    returnproduct_purchase_rate=models.FloatField()  
    returnproduct_quantity=models.FloatField()
    returnproduct_scheme=models.FloatField(default=0.0)
    returnproduct_charges=models.FloatField()
    returntotal_amount=models.FloatField(default=0.0)
    return_reason=models.CharField(max_length=200, blank=True, null=True)
    returnpurchase_entry_date=models.DateField(default=datetime.now)
    
    def __str__(self):
        return f"Return: {self.returnproductid.product_name} - {self.returnproduct_batch_no} - {self.returnproduct_quantity}"

class ReturnSalesInvoiceMaster(models.Model):
    return_sales_invoice_no=models.CharField(primary_key=True, max_length=20)
    return_sales_invoice_date=models.DateField(null=False, blank=False)
    return_sales_customerid=models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    return_sales_charges=models.FloatField(default=0)
    return_sales_invoice_total=models.FloatField(null=False, blank=False)
    return_sales_invoice_paid=models.FloatField(null=False, blank=False, default=0)
    
    def __str__(self):
        return f"Sales Return Invoice #{self.return_sales_invoice_no} - {self.return_sales_customerid.customer_name}"
    
    @property
    def balance_due(self):
        return self.return_sales_invoice_total - self.return_sales_invoice_paid

class ReturnSalesInvoicePaid(models.Model):
    return_sales_payment_id=models.BigAutoField(primary_key=True, auto_created=True)
    return_sales_ip_invoice_no=models.ForeignKey(ReturnSalesInvoiceMaster, on_delete=models.CASCADE)
    return_sales_payment_date=models.DateTimeField(default=datetime.now)
    return_sales_payment_amount=models.FloatField()
    return_sales_payment_mode=models.CharField(max_length=30, default='NA')
    return_sales_payment_ref_no=models.CharField(max_length=30,default='NA')
    
    def __str__(self):
        return f"Return Payment of {self.return_sales_payment_amount} for Return Sales Invoice #{self.return_sales_ip_invoice_no.return_sales_invoice_no}"

class ReturnSalesMaster(models.Model):
    return_sales_id=models.BigAutoField(primary_key=True, auto_created=True)
    return_sales_invoice_no=models.ForeignKey(ReturnSalesInvoiceMaster, on_delete=models.CASCADE)
    return_customerid=models.ForeignKey(CustomerMaster, on_delete=models.CASCADE)
    return_productid=models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    return_product_name=models.CharField(max_length=200, default='NA')
    return_product_company=models.CharField(max_length=200, blank=True, default='NA')
    return_product_packing=models.CharField(max_length=20, blank=True, default='NA')
    return_product_batch_no=models.CharField(max_length=20)
    return_product_expiry=models.DateField(default=datetime.now)
    return_product_MRP=models.FloatField(default=0.0)
    return_sale_rate=models.FloatField(default=0.0)
    return_sale_quantity=models.FloatField(default=0.0)
    return_sale_scheme=models.FloatField(default=0.0)
    return_sale_discount=models.FloatField(default=0.0)
    return_sale_igst=models.FloatField(default=0.0)
    return_sale_total_amount=models.FloatField(default=0.0)
    return_reason=models.CharField(max_length=200, blank=True, null=True)
    return_sale_entry_date=models.DateTimeField(default=datetime.now)
    return_sale_calculation_mode=models.CharField(max_length=20, default='percentage', choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')])
    
    def __str__(self):
        return f"Sales Return: {self.return_product_name} - {self.return_product_batch_no} - {self.return_sale_quantity}"

class SaleRateMaster(models.Model):
    productid=models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    product_batch_no=models.CharField(max_length=20)
    rate_A=models.FloatField(default=0.0)
    rate_B=models.FloatField(default=0.0)
    rate_C=models.FloatField(default=0.0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['productid', 'product_batch_no'], name='unique_productid_product_batch_no')
        ]
        
    def __str__(self):
        return f"Batch Rates for {self.productid.product_name} - Batch {self.product_batch_no}"
