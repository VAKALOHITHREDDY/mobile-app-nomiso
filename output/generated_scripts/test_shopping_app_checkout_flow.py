import os
import logging
from appium import webdriver
import pytest
from time import sleep

def take_screenshot(driver, test_name, step_number):
    screenshot_dir = "output/screenshots/" + test_name + "/"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = screenshot_dir + test_name + "_step_" + str(step_number) + ".png"
    driver.save_screenshot(screenshot_path)

def find_element(driver, locator):
    try:
        return driver.find_element(locator["primary_locator"]["strategy"], locator["primary_locator"]["value"])
    except Exception as e:
        logging.warning(f"Primary locator failed: {e}")
        try:
            return driver.find_element(locator["secondary_locator"]["strategy"], locator["secondary_locator"]["value"])
        except Exception as e:
            logging.error(f"Secondary locator failed: {e}")
            raise

@pytest.fixture(scope="function")
def driver():
    desired_caps = {
        "platformName": "Android",  # Replace with your platform
        "deviceName": "emulator-5554",  # Replace with your device name
        "app": "your_app.apk",  # Replace with your app path
        "automationName": "UiAutomator2" # Or Appium if needed
    }
    driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
    yield driver
    driver.quit()

def test_shopping_app_checkout_flow(driver):
    test_name = "shopping_app_checkout_flow"
    steps = [
        {"step_number": 1, "action": "click", "element": "cart_icon", "input_data": "", "expected_result": "Cart screen opens", "screenshot_required": True},
        {"step_number": 2, "action": "click", "element": "checkout_button", "input_data": "", "expected_result": "Checkout screen opens", "screenshot_required": True},
        {"step_number": 3, "action": "send_keys", "element": "shipping_address", "input_data": "123 Main St, City, State 12345", "expected_result": "Address entered", "screenshot_required": False},
        {"step_number": 4, "action": "click", "element": "place_order_button", "input_data": "", "expected_result": "Order placed successfully", "screenshot_required": True}
    ]
    locators = {
        "cart_icon": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/cart_icon"}, "secondary_locator": {"strategy": "accessibility_id", "value": "Shopping Cart"}},
        "checkout_button": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/checkout_button"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.Button[@text='Checkout']"}},
        "shipping_address": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/shipping_address"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.EditText[@hint='Shipping Address']"}},
        "place_order_button": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/place_order_button"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.Button[@text='Place Order']"}}
    }

    for step in steps:
        element_locator = locators[step["element"]]
        element = find_element(driver, element_locator)

        if step["action"] == "click":
            element.click()
        elif step["action"] == "send_keys":
            element.send_keys(step["input_data"])

        if step["screenshot_required"]:
            take_screenshot(driver, test_name, step["step_number"])
        sleep(1) # Short delay for visualization