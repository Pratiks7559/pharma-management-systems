# Script to remove InventoryMaster imports from all Python files
import os
import re

files_to_fix = [
    'core/financial_report_views.py',
    'core/inventory_export_views.py',
    'core/low_stock_views.py',
    'core/stock_report_views.py',
    'core/stock_issue_views.py',
    'core/views.py',
]

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove InventoryMaster and InventoryTransaction from imports
    content = re.sub(r',\s*InventoryMaster', '', content)
    content = re.sub(r'InventoryMaster\s*,', '', content)
    content = re.sub(r',\s*InventoryTransaction', '', content)
    content = re.sub(r'InventoryTransaction\s*,', '', content)
    content = re.sub(r',\s*BatchStockSummary', '', content)
    content = re.sub(r'BatchStockSummary\s*,', '', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed: {filepath}")

print("All imports fixed!")
