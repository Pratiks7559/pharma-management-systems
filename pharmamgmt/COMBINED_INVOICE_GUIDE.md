# Combined Invoice and Products Functionality

This guide explains how to use the combined invoice and products functionality in your pharmacy management system.

## Features

### Purchase Invoices with Products
- Create purchase invoices and add multiple products in a single page
- Automatic calculation of totals, discounts, and transport charges
- Batch-specific sale rate management
- Real-time validation and error handling

### Sales Invoices with Products
- Create sales invoices and add multiple products in a single page
- Stock availability checking
- Automatic rate selection based on customer type
- Real-time total calculations

## How to Use

### Purchase Invoice with Products

1. **Navigate to Purchase Invoices**
   - Go to "Invoices" from the main menu
   - Click "Add Invoice with Products" button

2. **Fill Invoice Details**
   - Invoice Number: Enter unique invoice number
   - Invoice Date: Select the invoice date
   - Supplier: Choose from dropdown
   - Transport Charges: Enter if applicable
   - Invoice Total: Will be auto-calculated

3. **Add Products**
   - Click "Add Product" button to add product rows
   - Select Product from dropdown
   - Enter Batch Number and Expiry (MM-YYYY format)
   - Fill MRP, Purchase Rate, Quantity
   - Set Scheme and Discount if applicable
   - Choose discount type (Flat Amount or Percentage)
   - Enter IGST percentage
   - Optionally set Sale Rates A, B, C for future sales

4. **Save**
   - Review the calculated totals
   - Click "Save Invoice with Products"

### Sales Invoice with Products

1. **Navigate to Sales Invoices**
   - Go to "Sales" from the main menu
   - Click "Quick Invoice + Products" button

2. **Fill Invoice Details**
   - Invoice Date: Select the date
   - Customer: Choose from dropdown
   - Transport Charges: Enter if applicable

3. **Add Products**
   - Click "Add Product" button
   - Select Product from dropdown
   - Enter Batch Number (auto-fills details if available)
   - Verify MRP, Expiry, and available stock
   - Set Sale Rate and Quantity
   - Add Discount and IGST if needed

4. **Save**
   - Review totals and stock availability
   - Click "Save Sales Invoice"

## Key Features

### Automatic Calculations
- Row totals calculated automatically
- Grand total updates in real-time
- Transport charges distributed proportionally
- Tax calculations included

### Validation
- Stock availability checking for sales
- Duplicate batch validation
- Required field validation
- Numeric value validation

### Error Handling
- Clear error messages for validation failures
- Transaction rollback on errors
- Graceful handling of missing data

### Keyboard Shortcuts (Sales Invoice)
- `Ctrl + Enter`: Add new product row
- `Ctrl + S`: Save form

## Benefits

1. **Time Saving**: Create invoices and add products in one step
2. **Accuracy**: Automatic calculations reduce errors
3. **Stock Management**: Real-time stock checking prevents overselling
4. **User Friendly**: Intuitive interface with helpful feedback
5. **Data Integrity**: Transaction management ensures consistent data

## Troubleshooting

### Common Issues

1. **"Product not found" error**
   - Ensure the product exists in the system
   - Check if the product ID is correct

2. **"Insufficient stock" error**
   - Verify available stock for the batch
   - Check if the batch number is correct

3. **"Invalid numeric values" error**
   - Ensure all numeric fields contain valid numbers
   - Check for special characters in numeric fields

4. **Transport charges not distributing**
   - Ensure at least one product is added
   - Check if transport charges field has a valid value

### Best Practices

1. **Data Entry**
   - Double-check batch numbers and expiry dates
   - Verify customer/supplier selection
   - Review calculations before saving

2. **Stock Management**
   - Regularly update purchase records
   - Monitor stock levels
   - Use consistent batch numbering

3. **Error Prevention**
   - Fill required fields completely
   - Use proper date formats (MM-YYYY for expiry)
   - Validate numeric inputs

## Technical Notes

- Uses JavaScript for real-time calculations
- Database transactions ensure data consistency
- Bulk operations for better performance
- Responsive design works on all devices

For technical support or feature requests, contact your system administrator.