# Rate Applied Fix - Combined Sales Invoice Form

## Problem
Jab bhi sales create hota hai combined sales invoice form se, customer ka jo rate type hota hai (TYPE-A, TYPE-B, TYPE-C) usi ke hisab se rate apply hota hai. Lekin database mein SalesMaster table ke `rate_applied` column mein sirf 'A' save ho raha hai, chahe customer ka type kuch bhi ho.

## Root Cause
File: `core/views.py`
Lines: 2293 and 2565

```python
rate_applied=product_data.get('rate_applied', 'A'),  # ❌ Hardcoded default 'A'
```

Yahan `product_data.get('rate_applied', 'A')` mein default value 'A' set hai. Agar frontend se `rate_applied` nahi aata, toh automatically 'A' set ho jata hai.

## Solution
Customer ka `customer_type` field se rate type extract karke use karna chahiye:

```python
# Customer type se rate extract karo
customer_rate_type = invoice.customerid.customer_type  # 'TYPE-A', 'TYPE-B', or 'TYPE-C'
rate_letter = customer_rate_type.split('-')[1] if '-' in customer_rate_type else 'A'  # Extract 'A', 'B', or 'C'

# Use in SalesMaster creation
rate_applied=product_data.get('rate_applied', rate_letter),  # ✅ Customer ke type ke hisab se
```

## Files to Modify
1. `core/views.py` - Line 2293 (in add_sales_invoice_with_products function)
2. `core/views.py` - Line 2565 (in add_sales_invoice_with_products function - seems duplicate)

## Implementation Steps
1. Customer ka type fetch karo: `invoice.customerid.customer_type`
2. Type se letter extract karo: 'TYPE-A' → 'A', 'TYPE-B' → 'B', 'TYPE-C' → 'C'
3. Default value ko 'A' ki jagah extracted letter use karo
4. Dono jagah (line 2293 aur 2565) fix apply karo

## Testing
1. TYPE-A customer se sale create karo → rate_applied = 'A' hona chahiye
2. TYPE-B customer se sale create karo → rate_applied = 'B' hona chahiye  
3. TYPE-C customer se sale create karo → rate_applied = 'C' hona chahiye
4. Database mein SalesMaster table check karo ki sahi rate_applied save ho raha hai
