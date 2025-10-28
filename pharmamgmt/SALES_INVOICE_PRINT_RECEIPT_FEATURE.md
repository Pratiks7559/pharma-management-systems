# Sales Invoice Print Receipt Feature

## Overview
Sales section mein jab user naya invoice banaye, toh automatically invoice detail page par redirect hota hai. Wahan Print Receipt button hai jo Ctrl+P shortcut ke saath kaam karta hai.

## Changes Made

### 1. Views (core/views.py)
- **Modified `add_sales_invoice_with_products`**: Invoice create hone ke baad automatically `sales_invoice_detail` page par redirect hota hai
- **Added `print_receipt` view**: Naya view jo landscape format mein receipt print karta hai

### 2. Template (templates/sales/print_receipt.html)
**New File Created** - Landscape format receipt with:
- **Paper Format**: A4 Landscape
- **Header Section**:
  - Pharmacy name (bold, uppercase)
  - Proprietor name
  - Contact number
  - Website URL
  - Email address
  - Address
  - DL No & GST No (if available)

- **Invoice Info Section**:
  - Customer name
  - Current date (DD-MM-YYYY format)
  - Invoice number
  - Time

- **Products Table**:
  - Sr. No
  - Product Name (with company & packing)
  - Batch No
  - Expiry
  - MRP
  - Rate
  - Quantity
  - Discount
  - Total

- **Total Section**:
  - Subtotal
  - Transport Charges (if any)
  - Grand Total
  - Amount Paid
  - Balance Due

- **Features**:
  - Print button with Ctrl+P shortcut
  - Auto-print on Ctrl+P keypress
  - Structured table format
  - Professional styling
  - Print-optimized CSS

### 3. URLs (core/urls.py)
- **Added route**: `path('sales/<str:pk>/print-receipt/', views.print_receipt, name='print_receipt')`

### 4. Invoice Detail Page (templates/sales/sales_invoice_detail.html)
- **Added Print Receipt button** in page actions with:
  - Icon: Receipt icon (fas fa-receipt)
  - Text: "Print Receipt (Ctrl+P)"
  - Opens in new tab
  - Tooltip showing shortcut

- **Added Ctrl+P keyboard shortcut**:
  - Prevents default browser print
  - Opens print receipt page in new tab
  - Works from invoice detail page

## User Flow

1. **Create Invoice**:
   - User sales section mein jata hai
   - "Add Sales Invoice with Products" par click karta hai
   - Invoice details aur products add karta hai
   - "Save Sales Invoice" button click karta hai

2. **Automatic Redirect**:
   - Invoice successfully create hone ke baad
   - Automatically invoice detail page par redirect hota hai
   - Success message show hota hai

3. **Print Receipt**:
   - Invoice detail page par "Print Receipt (Ctrl+P)" button dikhta hai
   - User button click kar sakta hai YA
   - Ctrl+P shortcut use kar sakta hai
   - New tab mein landscape format receipt open hota hai
   - Receipt mein pharmacy details, customer info, products table, aur totals dikhte hain

## Keyboard Shortcuts

- **Ctrl+P**: Print Receipt (from invoice detail page)
- **Ctrl+E**: Edit Invoice (existing)

## Print Receipt Format

```
┌─────────────────────────────────────────────────────────────┐
│                    PHARMACY NAME                             │
│              Proprietor: [Name]                              │
│         Contact: [Phone] | Website: [URL]                    │
│              Email: [Email]                                  │
│              Address: [Address]                              │
│         DL No: [DL] | GST No: [GST]                         │
├─────────────────────────────────────────────────────────────┤
│ Customer: [Name]              Invoice No: [INV-001]         │
│ Contact: [Phone]              Date: 15-01-2025              │
│ Address: [Address]            Time: 14:30                   │
├─────────────────────────────────────────────────────────────┤
│ Sr. │ Product Name    │ Batch │ Expiry │ MRP │ Rate │ Qty │
│  1  │ Paracetamol 500 │ B001  │ 12-25  │ 10  │ 9.5  │ 10  │
│     │ ABC Pharma-10x10│       │        │     │      │     │
├─────────────────────────────────────────────────────────────┤
│                                    Subtotal: ₹1,000.00      │
│                           Transport Charges: ₹50.00         │
│                              GRAND TOTAL: ₹1,050.00         │
│                                Amount Paid: ₹500.00         │
│                               Balance Due: ₹550.00          │
├─────────────────────────────────────────────────────────────┤
│              Thank you for your business!                    │
│   This is a computer-generated receipt.                     │
└─────────────────────────────────────────────────────────────┘
```

## Technical Details

### CSS Features
- `@page { size: A4 landscape; }` - Landscape orientation
- Print-optimized styling
- No-print class for buttons
- Professional table design
- Color-coded balance (red for due, green for paid)

### JavaScript Features
- Ctrl+P event listener
- Prevents default browser print dialog
- Opens receipt in new tab
- Auto-focus for immediate printing

### Django Template Features
- Uses `{% load static %}` for assets
- Conditional rendering for pharmacy details
- Date formatting: `|date:"d-m-Y"`
- Float formatting: `|floatformat:2`
- Loop counter: `{{ forloop.counter }}`

## Benefits

1. **User-Friendly**: Automatic redirect to invoice detail
2. **Quick Access**: Ctrl+P shortcut for fast printing
3. **Professional**: Structured landscape format
4. **Complete Info**: All pharmacy and customer details
5. **Print-Ready**: Optimized for printing
6. **Flexible**: Works with or without pharmacy details

## Testing Checklist

- [ ] Create new sales invoice
- [ ] Verify automatic redirect to detail page
- [ ] Click "Print Receipt" button
- [ ] Test Ctrl+P shortcut
- [ ] Verify landscape orientation
- [ ] Check all pharmacy details display
- [ ] Verify customer information
- [ ] Check products table formatting
- [ ] Verify totals calculation
- [ ] Test print functionality
- [ ] Check with/without pharmacy details
- [ ] Test with/without transport charges

## Future Enhancements

1. Add company logo in header
2. Add barcode/QR code for invoice
3. Add terms & conditions section
4. Add signature section
5. Multiple receipt templates
6. Email receipt option
7. Download as PDF option
8. Customizable receipt format

## Notes

- Receipt automatically opens in new tab
- Landscape format ensures all details fit properly
- Print button visible on screen, hidden in print
- Ctrl+P shortcut works only on invoice detail page
- Receipt includes current date/time stamp
- Professional styling with proper spacing
