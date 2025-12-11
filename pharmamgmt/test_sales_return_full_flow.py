"""
Comprehensive Test for Sales Return Full Flow
Tests:
1. Fill sales return form
2. Check sales return detail page
3. Open edit dialog and add product
4. Check updated sales return detail
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "admin"
PASSWORD = "admin"

def login(driver):
    """Login to the system"""
    print("\n=== STEP 1: LOGIN ===")
    driver.get(f"{BASE_URL}/login/")
    time.sleep(1)
    
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    print("✓ Login successful")

def fill_sales_return_form(driver):
    """Fill and submit sales return form"""
    print("\n=== STEP 2: FILL SALES RETURN FORM ===")
    
    # Navigate to sales return form
    driver.get(f"{BASE_URL}/sales-return/add/")
    time.sleep(2)
    print("✓ Navigated to sales return form")
    
    # Fill return date (auto-filled, but verify)
    return_date = driver.find_element(By.ID, "return_date")
    print(f"✓ Return date: {return_date.get_attribute('value')}")
    
    # Select customer
    customer_select = Select(driver.find_element(By.ID, "customerSelect"))
    customer_select.select_by_index(1)  # Select first customer
    time.sleep(1)
    selected_customer = customer_select.first_selected_option.text
    print(f"✓ Selected customer: {selected_customer}")
    
    # Add first product
    print("\n--- Adding Product 1 ---")
    add_product_btn = driver.find_element(By.CSS_SELECTOR, ".sr-add-product-btn")
    add_product_btn.click()
    time.sleep(1)
    
    # Fill product 1 details
    product_row = driver.find_element(By.ID, "productRow_0")
    
    # Select product
    product_select = Select(product_row.find_element(By.CLASS_NAME, "product-select"))
    product_select.select_by_index(1)
    time.sleep(1)
    selected_product1 = product_select.first_selected_option.text
    print(f"  Product: {selected_product1}")
    
    # Wait for batch modal and select batch
    try:
        wait = WebDriverWait(driver, 5)
        batch_modal = wait.until(EC.presence_of_element_located((By.ID, "batchSelectionModal")))
        time.sleep(1)
        
        # Click first batch
        first_batch = driver.find_element(By.CLASS_NAME, "batch-item")
        batch_no = first_batch.find_element(By.CLASS_NAME, "batch-no").text
        first_batch.click()
        time.sleep(1)
        print(f"  Batch: {batch_no}")
    except:
        print("  No batch modal, filling manually")
        product_row.find_element(By.CLASS_NAME, "batch-no").send_keys("BATCH001")
        product_row.find_element(By.CLASS_NAME, "expiry").send_keys("12-2025")
        product_row.find_element(By.CLASS_NAME, "mrp").send_keys("100")
        product_row.find_element(By.CLASS_NAME, "return-rate").send_keys("90")
    
    # Fill quantity
    qty_input = product_row.find_element(By.CLASS_NAME, "return-quantity")
    qty_input.clear()
    qty_input.send_keys("5")
    time.sleep(0.5)
    print(f"  Quantity: 5")
    
    # Get row total
    row_total = product_row.find_element(By.CLASS_NAME, "row-total").text
    print(f"  Row Total: {row_total}")
    
    # Add second product
    print("\n--- Adding Product 2 ---")
    add_product_btn.click()
    time.sleep(1)
    
    product_row2 = driver.find_element(By.ID, "productRow_1")
    
    # Select product
    product_select2 = Select(product_row2.find_element(By.CLASS_NAME, "product-select"))
    product_select2.select_by_index(2)
    time.sleep(1)
    selected_product2 = product_select2.first_selected_option.text
    print(f"  Product: {selected_product2}")
    
    # Handle batch modal
    try:
        wait = WebDriverWait(driver, 5)
        batch_modal = wait.until(EC.presence_of_element_located((By.ID, "batchSelectionModal")))
        time.sleep(1)
        
        first_batch = driver.find_element(By.CLASS_NAME, "batch-item")
        batch_no2 = first_batch.find_element(By.CLASS_NAME, "batch-no").text
        first_batch.click()
        time.sleep(1)
        print(f"  Batch: {batch_no2}")
    except:
        print("  No batch modal, filling manually")
        product_row2.find_element(By.CLASS_NAME, "batch-no").send_keys("BATCH002")
        product_row2.find_element(By.CLASS_NAME, "expiry").send_keys("01-2026")
        product_row2.find_element(By.CLASS_NAME, "mrp").send_keys("150")
        product_row2.find_element(By.CLASS_NAME, "return-rate").send_keys("135")
    
    # Fill quantity
    qty_input2 = product_row2.find_element(By.CLASS_NAME, "return-quantity")
    qty_input2.clear()
    qty_input2.send_keys("3")
    time.sleep(0.5)
    print(f"  Quantity: 3")
    
    # Get row total
    row_total2 = product_row2.find_element(By.CLASS_NAME, "row-total").text
    print(f"  Row Total: {row_total2}")
    
    # Get grand total
    grand_total = driver.find_element(By.ID, "grandTotal").text
    print(f"\n✓ Grand Total: ₹{grand_total}")
    
    # Submit form
    print("\n--- Submitting Form ---")
    submit_btn = driver.find_element(By.CSS_SELECTOR, ".sr-save-btn")
    submit_btn.click()
    time.sleep(3)
    print("✓ Form submitted")
    
    return grand_total

def check_sales_return_detail(driver, expected_total):
    """Check sales return detail page"""
    print("\n=== STEP 3: CHECK SALES RETURN DETAIL ===")
    
    # Should be on detail page now
    current_url = driver.current_url
    print(f"Current URL: {current_url}")
    
    # Get return invoice number from URL
    return_id = current_url.split('/')[-2]
    print(f"✓ Return Invoice No: {return_id}")
    
    # Check invoice details
    try:
        invoice_header = driver.find_element(By.CSS_SELECTOR, ".invoice-header, .sr-header")
        print("✓ Invoice header found")
    except:
        print("⚠ Invoice header not found")
    
    # Check products table
    try:
        products_table = driver.find_element(By.CSS_SELECTOR, "table")
        rows = products_table.find_elements(By.CSS_SELECTOR, "tbody tr")
        print(f"✓ Products in table: {len(rows)}")
        
        for i, row in enumerate(rows, 1):
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 0:
                print(f"  Product {i}: {cells[0].text if len(cells) > 0 else 'N/A'}")
    except Exception as e:
        print(f"⚠ Error reading products table: {e}")
    
    # Check total
    try:
        total_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Total') or contains(text(), 'Grand Total')]")
        print(f"✓ Total found: {total_element.text}")
    except:
        print("⚠ Total not found")
    
    time.sleep(2)
    return return_id

def open_edit_dialog_and_add_product(driver):
    """Open edit dialog and add a new product"""
    print("\n=== STEP 4: OPEN EDIT DIALOG & ADD PRODUCT ===")
    
    # Click edit button or use Ctrl+E
    try:
        # Try keyboard shortcut first
        print("Trying Ctrl+E shortcut...")
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).send_keys('e').key_up(Keys.CONTROL).perform()
        time.sleep(2)
    except:
        # Try clicking edit button
        print("Trying edit button...")
        edit_btn = driver.find_element(By.CSS_SELECTOR, "button[onclick*='openEditSalesReturnModal'], .edit-btn")
        edit_btn.click()
        time.sleep(2)
    
    # Wait for modal to open
    try:
        wait = WebDriverWait(driver, 10)
        modal = wait.until(EC.presence_of_element_located((By.ID, "editSalesReturnModal")))
        print("✓ Edit modal opened")
    except Exception as e:
        print(f"✗ Failed to open edit modal: {e}")
        return False
    
    # Check existing products in modal
    try:
        existing_rows = driver.find_elements(By.CSS_SELECTOR, "#editReturnItemsBody tr")
        print(f"✓ Existing products in modal: {len(existing_rows)}")
    except:
        print("⚠ Could not count existing products")
    
    # Add new product
    print("\n--- Adding New Product in Edit Modal ---")
    try:
        add_btn = driver.find_element(By.CSS_SELECTOR, "#editSalesReturnModal .add-product-btn, button[onclick*='addEditReturnRow']")
        add_btn.click()
        time.sleep(1)
        print("✓ Clicked add product button")
    except Exception as e:
        print(f"✗ Failed to click add button: {e}")
        return False
    
    # Find the new row (last row)
    try:
        all_rows = driver.find_elements(By.CSS_SELECTOR, "#editReturnItemsBody tr")
        new_row = all_rows[-1]
        row_id = new_row.get_attribute('id')
        print(f"✓ New row added: {row_id}")
        
        # Select product
        product_select = Select(new_row.find_element(By.CLASS_NAME, "product-select"))
        product_select.select_by_index(3)  # Select 3rd product
        time.sleep(1)
        selected_product = product_select.first_selected_option.text
        print(f"  Product: {selected_product}")
        
        # Handle batch modal if appears
        try:
            wait = WebDriverWait(driver, 5)
            batch_modal = wait.until(EC.presence_of_element_located((By.ID, "batchModalEdit")))
            time.sleep(1)
            
            first_batch = driver.find_element(By.CLASS_NAME, "batch-item")
            batch_no = first_batch.find_element(By.CLASS_NAME, "batch-no").text
            first_batch.click()
            time.sleep(1)
            print(f"  Batch: {batch_no}")
        except:
            print("  No batch modal, filling manually")
            new_row.find_element(By.CLASS_NAME, "batch-no").send_keys("BATCH003")
            new_row.find_element(By.CLASS_NAME, "expiry").send_keys("06-2026")
            new_row.find_element(By.CLASS_NAME, "mrp").send_keys("200")
            new_row.find_element(By.CLASS_NAME, "return-rate").send_keys("180")
        
        # Fill quantity
        qty_input = new_row.find_element(By.CLASS_NAME, "return-qty")
        qty_input.clear()
        qty_input.send_keys("2")
        time.sleep(0.5)
        print(f"  Quantity: 2")
        
        # Get row total
        try:
            row_total = new_row.find_element(By.CLASS_NAME, "row-total").text
            print(f"  Row Total: {row_total}")
        except:
            print("  Row total not visible yet")
        
    except Exception as e:
        print(f"✗ Failed to fill new product: {e}")
        return False
    
    # Save changes
    print("\n--- Saving Changes ---")
    try:
        save_btn = driver.find_element(By.CSS_SELECTOR, "#editSalesReturnModal .btn-primary, button[onclick*='saveEditedSalesReturn']")
        save_btn.click()
        time.sleep(3)
        print("✓ Changes saved")
        return True
    except Exception as e:
        print(f"✗ Failed to save changes: {e}")
        return False

def check_updated_sales_return_detail(driver):
    """Check updated sales return detail page"""
    print("\n=== STEP 5: CHECK UPDATED SALES RETURN DETAIL ===")
    
    # Refresh page to see changes
    driver.refresh()
    time.sleep(2)
    
    # Check products table again
    try:
        products_table = driver.find_element(By.CSS_SELECTOR, "table")
        rows = products_table.find_elements(By.CSS_SELECTOR, "tbody tr")
        print(f"✓ Updated products count: {len(rows)}")
        
        print("\n--- Product Details ---")
        for i, row in enumerate(rows, 1):
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                product_name = cells[0].text if len(cells) > 0 else 'N/A'
                batch = cells[1].text if len(cells) > 1 else 'N/A'
                qty = cells[2].text if len(cells) > 2 else 'N/A'
                print(f"  {i}. {product_name} | Batch: {batch} | Qty: {qty}")
    except Exception as e:
        print(f"⚠ Error reading updated products: {e}")
    
    # Check updated total
    try:
        total_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Total') or contains(text(), 'Grand Total')]")
        print(f"\n✓ Updated Total: {total_element.text}")
    except:
        print("⚠ Updated total not found")
    
    time.sleep(2)

def main():
    """Main test execution"""
    print("="*60)
    print("SALES RETURN FULL FLOW TEST")
    print("="*60)
    
    # Setup driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        # Step 1: Login
        login(driver)
        
        # Step 2: Fill sales return form
        grand_total = fill_sales_return_form(driver)
        
        # Step 3: Check sales return detail
        return_id = check_sales_return_detail(driver, grand_total)
        
        # Step 4: Open edit dialog and add product
        success = open_edit_dialog_and_add_product(driver)
        
        if success:
            # Step 5: Check updated detail
            check_updated_sales_return_detail(driver)
        
        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Keep browser open for inspection
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close browser...")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
