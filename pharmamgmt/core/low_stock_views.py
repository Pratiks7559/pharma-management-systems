from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum
from datetime import datetime
import json

from .models import ProductMaster, SupplierMaster, InvoiceMaster, PurchaseMaster, SalesMaster

@login_required
def low_stock_update(request):
    # Get low stock items
    low_stock_items = []
    products = ProductMaster.objects.all()
    
    for product in products:
        purchases = PurchaseMaster.objects.filter(productid=product)
        
        # Skip products with no purchase history
        if not purchases.exists():
            continue
            
        sales = SalesMaster.objects.filter(productid=product)
        
        total_purchased = purchases.aggregate(total=Sum('product_quantity'))['total'] or 0
        total_sold = sales.aggregate(total=Sum('sale_quantity'))['total'] or 0
        current_stock = total_purchased - total_sold
        
        if current_stock <= 10:
            # Get latest batch info
            latest_purchase = purchases.order_by('-purchase_entry_date').first()
            low_stock_items.append({
                'product': product,
                'current_stock': current_stock,
                'batch_no': latest_purchase.product_batch_no if latest_purchase else '',
                'expiry': latest_purchase.product_expiry if latest_purchase and latest_purchase.product_expiry else '',
                'mrp': latest_purchase.product_MRP if latest_purchase else 0
            })
    
    suppliers = SupplierMaster.objects.all().order_by('supplier_name')
    
    return render(request, 'inventory/low_stock_update.html', {
        'low_stock_items': low_stock_items,
        'suppliers': suppliers
    })

@login_required
def update_low_stock_item(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        supplier_id = data.get('supplier_id')
        batch_no = data.get('batch_no')
        expiry = data.get('expiry')
        purchase_rate = data.get('purchase_rate')
        mrp = data.get('mrp')
        quantity = data.get('quantity')
        discount = data.get('discount', 0)
        gst = data.get('gst', 0)
        
        product = ProductMaster.objects.get(productid=product_id)
        supplier = SupplierMaster.objects.get(supplierid=supplier_id)
        
        # Find existing purchase entry for this batch
        existing_purchase = PurchaseMaster.objects.filter(
            productid=product,
            product_batch_no=batch_no,
            product_expiry=expiry
        ).first()
        
        if existing_purchase:
            # Update existing purchase quantity
            existing_purchase.product_quantity += quantity
            existing_purchase.save()
            return JsonResponse({'success': True, 'message': 'Stock updated in existing batch'})
        else:
            # Create new purchase entry
            invoice_no = f"LSU-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            invoice, created = InvoiceMaster.objects.get_or_create(
                invoice_no=invoice_no,
                defaults={
                    'supplierid': supplier,
                    'invoice_date': datetime.now(),
                    'transport_charges': 0,
                    'invoice_total': 0,
                    'invoice_paid': 0
                }
            )
            
            cgst = sgst = gst / 2
            
            PurchaseMaster.objects.create(
                product_invoiceid=invoice,
                productid=product,
                product_supplierid=supplier,
                product_invoice_no=invoice_no,
                product_name=product.product_name,
                product_company=product.product_company,
                product_packing=product.product_packing,
                product_batch_no=batch_no,
                product_expiry=expiry,
                product_MRP=mrp,
                product_purchase_rate=purchase_rate,
                product_quantity=quantity,
                product_discount_got=discount,
                product_transportation_charges=0,
                CGST=cgst,
                SGST=sgst,
                purchase_entry_date=datetime.now()
            )
            
            return JsonResponse({'success': True, 'message': 'Stock updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def bulk_update_low_stock(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        updates = data.get('updates', [])
        updated_count = 0
        
        with transaction.atomic():
            for update in updates:
                product_id = update.get('product_id')
                supplier_id = update.get('supplier_id')
                batch_no = update.get('batch_no')
                expiry = update.get('expiry')
                purchase_rate = update.get('purchase_rate')
                mrp = update.get('mrp')
                quantity = update.get('quantity')
                discount = update.get('discount', 0)
                gst = update.get('gst', 0)
                
                product = ProductMaster.objects.get(productid=product_id)
                supplier = SupplierMaster.objects.get(supplierid=supplier_id)
                
                # Find existing purchase entry for this batch
                existing_purchase = PurchaseMaster.objects.filter(
                    productid=product,
                    product_batch_no=batch_no,
                    product_expiry=expiry
                ).first()
                
                if existing_purchase:
                    # Update existing purchase quantity
                    existing_purchase.product_quantity += quantity
                    existing_purchase.save()
                else:
                    # Create new purchase entry
                    invoice_no = f"LSU-{datetime.now().strftime('%Y%m%d%H%M%S')}-{updated_count}"
                    invoice, created = InvoiceMaster.objects.get_or_create(
                        invoice_no=invoice_no,
                        defaults={
                            'supplierid': supplier,
                            'invoice_date': datetime.now(),
                            'transport_charges': 0,
                            'invoice_total': 0,
                            'invoice_paid': 0
                        }
                    )
                    
                    cgst = sgst = gst / 2
                    
                    PurchaseMaster.objects.create(
                        product_invoiceid=invoice,
                        productid=product,
                        product_supplierid=supplier,
                        product_invoice_no=invoice_no,
                        product_name=product.product_name,
                        product_company=product.product_company,
                        product_packing=product.product_packing,
                        product_batch_no=batch_no,
                        product_expiry=expiry,
                        product_MRP=mrp,
                        product_purchase_rate=purchase_rate,
                        product_quantity=quantity,
                        product_discount_got=discount,
                        product_transportation_charges=0,
                        CGST=cgst,
                        SGST=sgst,
                        purchase_entry_date=datetime.now()
                    )
                
                updated_count += 1
        
        return JsonResponse({'success': True, 'updated_count': updated_count})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def get_batch_suggestions(request):
    product_id = request.GET.get('product_id')
    
    if not product_id:
        return JsonResponse({'success': False, 'error': 'Product ID required'})
    
    try:
        batches = PurchaseMaster.objects.filter(
            productid_id=product_id
        ).values('product_batch_no', 'product_expiry').distinct().order_by('-purchase_entry_date')[:10]
        
        batch_list = []
        for batch in batches:
            if batch['product_expiry']:
                batch_list.append({
                    'batch_no': batch['product_batch_no'],
                    'expiry': batch['product_expiry'].strftime('%m-%Y')
                })
        
        return JsonResponse({'success': True, 'batches': batch_list})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
