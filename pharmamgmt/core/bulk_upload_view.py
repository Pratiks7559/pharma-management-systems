import pandas as pd
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from datetime import datetime
from .models import InvoiceMaster, PurchaseMaster, SupplierMaster, ProductMaster

@login_required
def bulk_upload_invoices(request):
    if request.method == 'POST' and request.FILES.get('bulk_file'):
        file = request.FILES['bulk_file']
        file_ext = file.name.split('.')[-1].lower()
        
        try:
            # Parse file based on extension
            if file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(file)
            elif file_ext == 'csv':
                df = pd.read_csv(file)
            else:
                messages.error(request, 'Unsupported file format. Please upload Excel or CSV file.')
                return redirect('invoice_list')
            
            # Validate required columns
            required_cols = ['Invoice No', 'Invoice Date', 'Supplier Name', 'Product Name', 
                           'Batch No', 'Expiry', 'MRP', 'Purchase Rate', 'Quantity']
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                messages.error(request, f'Missing columns: {", ".join(missing_cols)}')
                return redirect('invoice_list')
            
            # Process invoices
            invoices_created = 0
            products_added = 0
            errors = []
            
            # Group by Invoice No
            grouped = df.groupby('Invoice No')
            
            with transaction.atomic():
                for invoice_no, group in grouped:
                    try:
                        # Get first row for invoice details
                        first_row = group.iloc[0]
                        
                        # Find or create supplier
                        supplier_name = str(first_row['Supplier Name']).strip()
                        supplier = SupplierMaster.objects.filter(supplier_name__iexact=supplier_name).first()
                        
                        if not supplier:
                            errors.append(f"Invoice {invoice_no}: Supplier '{supplier_name}' not found")
                            continue
                        
                        # Parse invoice date
                        try:
                            invoice_date = pd.to_datetime(first_row['Invoice Date']).date()
                        except:
                            invoice_date = datetime.now().date()
                        
                        # Calculate invoice total
                        invoice_total = 0
                        for _, row in group.iterrows():
                            rate = float(row['Purchase Rate'])
                            qty = float(row['Quantity'])
                            discount = float(row.get('Discount', 0))
                            gst = float(row.get('GST%', 0))
                            
                            subtotal = rate * qty - discount
                            total = subtotal * (1 + gst/100)
                            invoice_total += total
                        
                        # Create invoice
                        invoice = InvoiceMaster.objects.create(
                            invoice_no=str(invoice_no),
                            invoice_date=invoice_date,
                            supplierid=supplier,
                            invoice_total=round(invoice_total, 2),
                            invoice_paid=0,
                            transport_charges=0
                        )
                        
                        invoices_created += 1
                        
                        # Add products
                        for _, row in group.iterrows():
                            try:
                                # Find product
                                product_name = str(row['Product Name']).strip()
                                product = ProductMaster.objects.filter(product_name__iexact=product_name).first()
                                
                                if not product:
                                    errors.append(f"Invoice {invoice_no}: Product '{product_name}' not found")
                                    continue
                                
                                # Create purchase entry
                                PurchaseMaster.objects.create(
                                    invoice_no=invoice,
                                    productid=product,
                                    product_batch_no=str(row['Batch No']),
                                    product_expiry=str(row['Expiry']),
                                    product_MRP=float(row['MRP']),
                                    product_purchase_rate=float(row['Purchase Rate']),
                                    product_quantity=float(row['Quantity']),
                                    product_discount_got=float(row.get('Discount', 0)),
                                    IGST=float(row.get('GST%', 0)),
                                    purchase_calculation_mode='flat',
                                    rate_A=float(row.get('Rate A', 0)),
                                    rate_B=float(row.get('Rate B', 0)),
                                    rate_C=float(row.get('Rate C', 0))
                                )
                                
                                products_added += 1
                                
                            except Exception as e:
                                errors.append(f"Invoice {invoice_no}, Product {product_name}: {str(e)}")
                    
                    except Exception as e:
                        errors.append(f"Invoice {invoice_no}: {str(e)}")
            
            # Show results
            if invoices_created > 0:
                messages.success(request, f'Successfully created {invoices_created} invoices with {products_added} products!')
            
            if errors:
                error_msg = '<br>'.join(errors[:10])  # Show first 10 errors
                if len(errors) > 10:
                    error_msg += f'<br>...and {len(errors)-10} more errors'
                messages.warning(request, f'Errors encountered:<br>{error_msg}')
            
            return redirect('invoice_list')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('invoice_list')
    
    return render(request, 'purchases/bulk_upload.html')
