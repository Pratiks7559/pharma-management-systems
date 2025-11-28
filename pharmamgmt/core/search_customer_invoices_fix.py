def search_customer_invoices(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if len(query) >= 2:
        # Search customers and their invoices
        customers = CustomerMaster.objects.filter(
            customer_name__icontains=query
        )[:10]
        
        for customer in customers:
            # Get all invoices for this customer (we'll filter by balance later)
            invoices = SalesInvoiceMaster.objects.filter(
                customerid=customer
            ).order_by('-sales_invoice_date')[:10]  # Get more to filter from
            
            for invoice in invoices:
                # Calculate balance using the property
                total_amount = invoice.sales_invoice_total
                paid_amount = invoice.sales_invoice_paid
                balance = total_amount - paid_amount
                
                # Only show invoices with outstanding balance
                if balance > 0.01:  # Use small threshold for floating point comparison
                    results.append({
                        'invoice_no': invoice.sales_invoice_no,
                        'customer_id': customer.customerid,
                        'customer_name': customer.customer_name,
                        'invoice_date': invoice.sales_invoice_date.strftime('%d-%m-%Y'),
                        'total_amount': float(total_amount),
                        'paid_amount': float(paid_amount),
                        'balance_amount': float(balance)
                    })
                    
                    # Limit results per customer to avoid too many results
                    if len([r for r in results if r['customer_id'] == customer.customerid]) >= 5:
                        break
    
    return JsonResponse(results, safe=False)