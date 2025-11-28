# Script to remove Inventory models from models.py
with open('core/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all lines between "# REMOVED: InventoryMaster" and "# REMOVED: InventoryTransaction"
import re

# Find and remove InventoryMaster model
pattern1 = r'# REMOVED: InventoryMaster.*?(?=class StockIssueMaster|# REMOVED: InventoryTransaction|$)'
content = re.sub(pattern1, '', content, flags=re.DOTALL)

# Find and remove InventoryTransaction model  
pattern2 = r'# REMOVED: InventoryTransaction.*?(?=class StockIssueMaster|# REMOVED: BatchStockSummary|$)'
content = re.sub(pattern2, '', content, flags=re.DOTALL)

# Find and remove BatchStockSummary model
pattern3 = r'# REMOVED: BatchStockSummary.*?(?=class StockIssueMaster|$)'
content = re.sub(pattern3, '', content, flags=re.DOTALL)

# Write back
with open('core/models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Models removed successfully!")
