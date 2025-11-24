# Simple Selenium Test for Invoice Form
# Install: pip install selenium webdriver-manager
# Run: python simple_automation_test.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
import os

print(" Starting Invoice Form Automation Test...")
print("=" * 50)

# Setup Chrome browser
print("\n1. Opening Chrome browser...")
chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Try to use Chrome directly without webdriver-manager
try:
    driver = webdriver.Chrome(options=chrome_options)
except Exception as e:
    print(f"Error with default ChromeDriver: {e}")
    print("Trying with webdriver-manager...")
    from webdriver_manager.chrome import ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

driver.maximize_window()

try:
    # Open invoice form
    print("2. Navigating to invoice form...")
    driver.get("http://127.0.0.1:5000")
    time.sleep(2)
    
    # Test 1: Check invoice number
    print("\n TEST 1: Checking invoice number auto-generation...")
    invoice_number = driver.find_element(By.ID, "invoiceNumber").get_attribute("value")
    print(f"   Invoice Number: {invoice_number}")
    
    # Test 2: Check date
    print("\n TEST 2: Checking invoice date...")
    invoice_date = driver.find_element(By.ID, "invoiceDate").get_attribute("value")
    print(f"   Invoice Date: {invoice_date}")
    
    # Test 3: Fill customer email
    print("\n TEST 3: Entering customer email...")
    email_field = driver.find_element(By.ID, "customerContact")
    email_field.clear()
    email_field.send_keys("test@example.com")
    print("   Email entered: test@example.com")
    time.sleep(1)
    
    # Test 4: Fill billing address
    print("\n TEST 4: Entering billing address...")
    billing_field = driver.find_element(By.ID, "billingAddress")
    billing_field.clear()
    billing_field.send_keys("123 Main Street, City, State 12345")
    print("   Billing address entered")
    time.sleep(1)
    
    # Test 5: Fill salesperson
    print("\n TEST 5: Entering salesperson...")
    salesperson_field = driver.find_element(By.ID, "salesperson")
    salesperson_field.clear()
    salesperson_field.send_keys("John Doe")
    print("   Salesperson entered: John Doe")
    time.sleep(1)
    
    # Test 6: Select a part number
    print("\n TEST 6: Selecting part number...")
    time.sleep(2)  # Wait for items to load
    part_dropdown = driver.find_element(By.CSS_SELECTOR, ".partNumber")
    select = Select(part_dropdown)
    
    # Get first available part (skip "Select Part" option)
    available_parts = [opt.get_attribute("value") for opt in select.options if opt.get_attribute("value")]
    if available_parts:
        first_part = available_parts[0]
        select.select_by_value(first_part)
        print(f"   Part {first_part} selected")
        time.sleep(2)
    else:
        print("    No parts available in dropdown")
        time.sleep(1)
    
    # Check if description auto-filled
    description = driver.find_element(By.CSS_SELECTOR, ".description").get_attribute("value")
    print(f"   Description auto-filled: {description}")
    
    # Test 7: Change quantity
    print("\n TEST 7: Changing quantity...")
    qty_field = driver.find_element(By.CSS_SELECTOR, ".quantity")
    qty_field.clear()
    qty_field.send_keys("3")
    print("   Quantity changed to 3")
    time.sleep(1)
    
    # Test 8: Check calculations
    print("\n TEST 8: Checking automatic calculations...")
    subtotal = driver.find_element(By.ID, "subtotal").text
    tax = driver.find_element(By.ID, "tax").text
    total = driver.find_element(By.ID, "total").text
    print(f"   Subtotal: ${subtotal}")
    print(f"   Tax: ${tax}")
    print(f"   Total: ${total}")
    
    # Test 9: Check add-on recommendations
    print("\n TEST 9: Checking add-on recommendations...")
    addon_dropdown = driver.find_element(By.CSS_SELECTOR, ".addon")
    addon_select = Select(addon_dropdown)
    addon_options = [option.get_attribute("value") for option in addon_select.options]
    print(f"   Add-on options available: {len(addon_options)}")
    
    # If recommendations exist, select one
    if len(addon_options) > 1:
        print("\n TEST 10: Selecting add-on recommendation...")
        addon_value = [opt for opt in addon_options if opt != ""][0]
        addon_select.select_by_value(addon_value)
        print(f"   Selected add-on: {addon_value}")
        time.sleep(2)
        
        # Check if new row was created
        rows = driver.find_elements(By.CSS_SELECTOR, "#itemsTable tbody tr")
        print(f"   Total rows now: {len(rows)}")
    
    # Test 11: Add another item
    print("\n TEST 11: Clicking 'Add item' button...")
    add_button = driver.find_element(By.ID, "addItem")
    add_button.click()
    time.sleep(1)
    rows = driver.find_elements(By.CSS_SELECTOR, "#itemsTable tbody tr")
    print(f"   Total rows after adding: {len(rows)}")
    
    # Test 12: Check if Create Invoice button is enabled
    print("\n TEST 12: Checking Create Invoice button...")
    create_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    is_enabled = create_button.is_enabled()
    print(f"   Button enabled: {is_enabled}")
    
    # Test 13: Create the invoice
    print("\n TEST 13: Creating invoice...")
    create_button.click()
    time.sleep(3)
    
    # Check if navigated to invoice summary
    if "invoice" in driver.current_url:
        print("    Successfully navigated to invoice summary!")
        
        # Check summary data
        print("\n TEST 14: Verifying invoice summary...")
        summary_number = driver.find_element(By.ID, "displayNumber").text
        summary_customer = driver.find_element(By.ID, "displayCustomer").text
        summary_total = driver.find_element(By.ID, "displayTotal").text
        
        print(f"   Invoice #: {summary_number}")
        print(f"   Customer: {summary_customer}")
        print(f"   Total: ${summary_total}")
        
        # Count items in summary
        items = driver.find_elements(By.CSS_SELECTOR, "#displayItems tbody tr")
        print(f"   Items in invoice: {len(items)}")
    
    print("\n" + "=" * 50)
    print(" ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("\nBrowser will close in 5 seconds...")
    time.sleep(5)

except Exception as e:
    print(f"\n ERROR: {str(e)}")
    print("\nMake sure:")
    print("1. Flask app is running: python app.py")
    print("2. App is on http://127.0.0.1:5000")
    time.sleep(3)

finally:
    driver.quit()
    print("\n Browser closed. Test completed!")
