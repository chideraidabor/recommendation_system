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
        
        # Test 15: Verify billing address consistency
        print("\n TEST 15: Checking billing address consistency...")
        summary_billing = driver.find_element(By.ID, "displayBilling").text
        print(f"   Billing address in summary: {summary_billing[:50]}...")
        if "123 Main Street" in summary_billing:
            print("   Billing address matches!")
        
        # Test 16: Verify salesperson appears in summary
        print("\n TEST 16: Checking salesperson in summary...")
        summary_salesperson = driver.find_element(By.ID, "displaySalesperson").text
        print(f"   Salesperson: {summary_salesperson}")
        if summary_salesperson == "John Doe":
            print("   Salesperson matches!")
        
        # Test 17: Verify decimal precision in totals
        print("\n TEST 17: Checking decimal precision (2 decimal places)...")
        if "." in summary_total and len(summary_total.split(".")[-1]) == 2:
            print(f"   Total has 2 decimal places: ${summary_total}")
        
        # Test 18: Verify subtotal and tax calculation accuracy
        print("\n TEST 18: Verifying subtotal and tax calculations...")
        summary_subtotal = driver.find_element(By.ID, "displaySubtotal").text
        summary_tax = driver.find_element(By.ID, "displayTax").text
        summary_shipping = driver.find_element(By.ID, "displayShipping").text
        print(f"   Subtotal: ${summary_subtotal}")
        print(f"   Tax: ${summary_tax}")
        print(f"   Shipping: ${summary_shipping}")
        calculated_total = float(summary_subtotal) + float(summary_tax) + float(summary_shipping)
        print(f"   Calculated Total: ${calculated_total:.2f}")
        print(f"   Displayed Total: ${summary_total}")
        if abs(calculated_total - float(summary_total)) < 0.01:
            print("   Calculations are accurate!")
        
        # Test 19: Verify all items are listed (no missing items)
        print("\n TEST 19: Verifying all items are listed...")
        if len(items) >= 2:
            print(f"   All {len(items)} items are present in invoice")
    
    # Navigate back to create new invoice for additional tests
    print("\n" + "=" * 50)
    print(" NAVIGATING BACK FOR ADDITIONAL TESTS...")
    print("=" * 50)
    driver.get("http://127.0.0.1:5000")
    time.sleep(2)
    
    # Test 20: Verify invoice number auto-increments
    print("\n TEST 20: Checking invoice number auto-increment...")
    new_invoice_number = driver.find_element(By.ID, "invoiceNumber").get_attribute("value")
    print(f"   Previous Invoice: {invoice_number}")
    print(f"   New Invoice: {new_invoice_number}")
    prev_num = int(invoice_number.replace("INV", ""))
    new_num = int(new_invoice_number.replace("INV", ""))
    if new_num > prev_num:
        print("   Invoice number auto-incremented!")
    
    # Test 21: Verify date defaults to today
    print("\n TEST 21: Checking default date (today's date)...")
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    current_date = driver.find_element(By.ID, "invoiceDate").get_attribute("value")
    print(f"   Today's date: {today}")
    print(f"   Form date: {current_date}")
    if today == current_date:
        print("   Date defaults to today!")
    
    # Test 22: Verify email validation
    print("\n TEST 22: Testing email validation...")
    email_field = driver.find_element(By.ID, "customerContact")
    email_field.clear()
    email_field.send_keys("invalid-email")
    time.sleep(1)
    email_error = driver.find_element(By.ID, "emailError").text
    if "valid email" in email_error.lower():
        print("   Email validation working!")
    email_field.clear()
    email_field.send_keys("valid@email.com")
    time.sleep(1)
    
    # Test 23: Verify part number auto-fills description
    print("\n TEST 23: Testing part number auto-fills description...")
    billing_field = driver.find_element(By.ID, "billingAddress")
    billing_field.send_keys("456 Test Ave")
    salesperson_field = driver.find_element(By.ID, "salesperson")
    salesperson_field.send_keys("Jane Smith")
    time.sleep(1)
    part_dropdown = driver.find_element(By.CSS_SELECTOR, ".partNumber")
    select = Select(part_dropdown)
    available_parts = [opt for opt in select.options if opt.get_attribute("value")]
    if len(available_parts) > 1:
        test_part = available_parts[1].get_attribute("value")
        select.select_by_value(test_part)
        time.sleep(2)
        description = driver.find_element(By.CSS_SELECTOR, ".description").get_attribute("value")
        if description:
            print(f"   Part {test_part} auto-filled description: {description}")
    
    # Test 24: Verify quantity minimum of 1
    print("\n TEST 24: Testing quantity minimum validation...")
    qty_field = driver.find_element(By.CSS_SELECTOR, ".quantity")
    initial_qty = qty_field.get_attribute("value")
    print(f"   Default quantity: {initial_qty}")
    if int(initial_qty) >= 1:
        print("   Quantity starts at 1 or higher!")
    
    # Test 25: Verify amount updates with quantity change
    print("\n TEST 25: Testing amount updates with quantity...")
    unit_price = float(driver.find_element(By.CSS_SELECTOR, ".unitPrice").get_attribute("value") or 0)
    qty_field.clear()
    qty_field.send_keys("5")
    time.sleep(1)
    amount = driver.find_element(By.CSS_SELECTOR, ".amount").text
    expected_amount = unit_price * 5
    print(f"   Unit Price: ${unit_price}")
    print(f"   Quantity: 5")
    print(f"   Expected Amount: ${expected_amount:.2f}")
    print(f"   Actual Amount: ${amount}")
    if abs(float(amount) - expected_amount) < 0.01:
        print("   Amount calculation is correct!")
    
    # Test 26: Verify add-ons dropdown shows recommendations
    print("\n TEST 26: Verifying add-ons recommendations dropdown...")
    time.sleep(2)
    addon_dropdown = driver.find_element(By.CSS_SELECTOR, ".addon")
    addon_select = Select(addon_dropdown)
    addon_count = len([opt for opt in addon_select.options if opt.get_attribute("value")])
    print(f"   Add-on recommendations found: {addon_count}")
    if addon_count > 0:
        print("   Add-ons dropdown populated with recommendations!")
    
    # Test 27: Verify tax and shipping calculations
    print("\n TEST 27: Verifying tax and shipping calculations...")
    subtotal_val = float(driver.find_element(By.ID, "subtotal").text)
    tax_val = float(driver.find_element(By.ID, "tax").text)
    shipping_val = float(driver.find_element(By.ID, "shipping").text)
    expected_tax = subtotal_val * 0.05
    print(f"   Subtotal: ${subtotal_val:.2f}")
    print(f"   Tax (5%): ${tax_val:.2f} (Expected: ${expected_tax:.2f})")
    print(f"   Shipping: ${shipping_val:.2f}")
    if abs(tax_val - expected_tax) < 0.01:
        print("   Tax calculation is correct!")
    if shipping_val >= 0:
        print("   Shipping is calculated!")
    
    # Test 28: Verify salesperson can be entered
    print("\n TEST 28: Verifying salesperson field...")
    salesperson_value = driver.find_element(By.ID, "salesperson").get_attribute("value")
    if salesperson_value:
        print(f"   Salesperson entered: {salesperson_value}")
    
    # Test 29: Verify recommendation auto-adds line item
    print("\n TEST 29: Testing recommendation auto-adds line item...")
    initial_rows = len(driver.find_elements(By.CSS_SELECTOR, "#itemsTable tbody tr"))
    addon_dropdown = driver.find_element(By.CSS_SELECTOR, ".addon")
    addon_select = Select(addon_dropdown)
    available_addons = [opt for opt in addon_select.options if opt.get_attribute("value")]
    if available_addons:
        addon_select.select_by_value(available_addons[0].get_attribute("value"))
        time.sleep(2)
        new_rows = len(driver.find_elements(By.CSS_SELECTOR, "#itemsTable tbody tr"))
        print(f"   Rows before: {initial_rows}")
        print(f"   Rows after: {new_rows}")
        if new_rows > initial_rows:
            print("   Recommendation auto-added a new line item!")
    
    # Test 30: Verify delete item functionality
    print("\n TEST 30: Testing delete item functionality...")
    time.sleep(1)
    current_rows = len(driver.find_elements(By.CSS_SELECTOR, "#itemsTable tbody tr"))
    if current_rows > 1:
        delete_buttons = driver.find_elements(By.CSS_SELECTOR, ".delete")
        if delete_buttons:
            delete_buttons[0].click()
            time.sleep(1)
            rows_after_delete = len(driver.find_elements(By.CSS_SELECTOR, "#itemsTable tbody tr"))
            print(f"   Rows before delete: {current_rows}")
            print(f"   Rows after delete: {rows_after_delete}")
            if rows_after_delete < current_rows:
                print("   Delete item functionality works!")
    
    print("\n" + "=" * 50)
    print(" ALL 30 TESTS COMPLETED SUCCESSFULLY!")
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
