import csv
import random
from datetime import datetime, timedelta

suppliers = ['ABC Pharma', 'XYZ Medical', 'Global Drugs', 'MediSupply Co', 'HealthCare Ltd']
products = ['Paracetamol 500mg', 'Amoxicillin 250mg', 'Ibuprofen 400mg', 'Cetirizine 10mg', 
            'Azithromycin 500mg', 'Metformin 500mg', 'Omeprazole 20mg', 'Aspirin 75mg', 
            'Vitamin D3 1000IU', 'Calcium 500mg']

with open('sample_invoice_bulk_upload.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Invoice No', 'Invoice Date', 'Supplier Name', 'Product Name', 'Batch No', 
                     'Expiry', 'MRP', 'Purchase Rate', 'Quantity', 'Discount', 'GST%', 
                     'Rate A', 'Rate B', 'Rate C'])
    
    base_date = datetime(2024, 1, 1)
    for i in range(1000):
        invoice_no = f'INV{str(i//10 + 1).zfill(4)}'
        invoice_date = (base_date + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        supplier = random.choice(suppliers)
        product = random.choice(products)
        batch_no = f'BATCH{random.randint(1000, 9999)}'
        expiry = (datetime.now() + timedelta(days=random.randint(365, 1095))).strftime('%m/%Y')
        mrp = round(random.uniform(50, 500), 2)
        purchase_rate = round(random.uniform(30, 400), 2)
        quantity = random.randint(10, 500)
        discount = round(random.uniform(0, 50), 2)
        gst = random.choice([5, 12, 18])
        rate_a = round(random.uniform(40, 450), 2)
        rate_b = round(random.uniform(45, 480), 2)
        rate_c = round(random.uniform(50, 500), 2)
        
        writer.writerow([invoice_no, invoice_date, supplier, product, batch_no, expiry, 
                        mrp, purchase_rate, quantity, discount, gst, rate_a, rate_b, rate_c])

print('Sample CSV created: sample_invoice_bulk_upload.csv with 1000 records')
