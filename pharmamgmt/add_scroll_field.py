#!/usr/bin/env python
"""
Script to properly add scroll_no field to InvoiceMaster model
Run this after confirming the website is working
"""
import os
import sys

print("=== Adding Scroll No Field to Invoice Master ===")
print("1. First, ensure your website is running properly")
print("2. Then run this script to add the scroll_no field")
print()

choice = input("Is your website running properly now? (y/n): ").lower().strip()

if choice == 'y':
    print("\nStep 1: Adding scroll_no field to models.py...")
    
    # Read the current models.py
    with open('core/models.py', 'r') as f:
        content = f.read()
    
    # Add scroll_no field
    old_line = "    invoice_no=models.CharField(max_length=20)\n    invoice_date=models.DateField(null=False, blank=False, default=datetime.now)"
    new_line = "    invoice_no=models.CharField(max_length=20)\n    scroll_no=models.CharField(max_length=50, blank=True, null=True, help_text=\"Manual scroll number for invoice tracking\")\n    invoice_date=models.DateField(null=False, blank=False, default=datetime.now)"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        with open('core/models.py', 'w') as f:
            f.write(content)
        print("✓ Added scroll_no field to InvoiceMaster model")
    else:
        print("✗ Could not find the right location in models.py")
        sys.exit(1)
    
    print("\nStep 2: Adding scroll_no field to forms.py...")
    
    # Read the current forms.py
    with open('core/forms.py', 'r') as f:
        content = f.read()
    
    # Add scroll_no field to form
    old_form = "    invoice_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))\n    invoice_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))"
    new_form = "    invoice_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))\n    scroll_no = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter scroll number (optional)'}))\n    invoice_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))"
    
    old_fields = "        fields = ['invoice_no', 'invoice_date', 'supplierid', 'transport_charges', 'invoice_total']"
    new_fields = "        fields = ['invoice_no', 'scroll_no', 'invoice_date', 'supplierid', 'transport_charges', 'invoice_total']"
    
    if old_form in content and old_fields in content:
        content = content.replace(old_form, new_form)
        content = content.replace(old_fields, new_fields)
        
        with open('core/forms.py', 'w') as f:
            f.write(content)
        print("✓ Added scroll_no field to InvoiceForm")
    else:
        print("✗ Could not find the right location in forms.py")
        sys.exit(1)
    
    print("\nStep 3: Creating migration...")
    os.system("python manage.py makemigrations core --name add_scroll_no_field")
    
    print("\nStep 4: Applying migration...")
    os.system("python manage.py migrate")
    
    print("\n✓ Scroll No field has been successfully added!")
    print("You can now use the scroll_no field in your purchase invoices.")
    
else:
    print("Please fix any website issues first, then run this script.")