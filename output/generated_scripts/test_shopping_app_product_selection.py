import os
import logging
import pytest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def take_screenshot(driver, test_name, step_number):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    screenshot_dir = "output/screenshots/shopping_app_product_selection/"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, f"{test_name}_step_{step_number}_{timestamp}.png")
    driver.save_screenshot(screenshot_path)
    logging.info(f"Screenshot saved: {screenshot_path}")

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

def test_shopping_app_product_selection(driver):
    test_name = "shopping_app_product_selection"
    steps = [
        {"step_number": 1, "action": "click", "element": "products_menu", "input_data": "", "expected_result": "Products screen opens", "screenshot_required": True},
        {"step_number": 2, "action": "click", "element": "first_product", "input_data": "", "expected_result": "Product details screen opens", "screenshot_required": True},
        {"step_number": 3, "action": "click", "element": "add_to_cart_button", "input_data": "", "expected_result": "Product added to cart", "screenshot_required": True}
    ]
    locators = {
        "products_menu": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/products_menu"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.Button[@text='Products']"}},
        "first_product": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/product_item_0"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.RecyclerView[@resource-id='com.example.shoppingapp:id/products_list']/android.widget.LinearLayout[1]"}},
        "add_to_cart_button": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/add_to_cart_button"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.Button[@text='Add to Cart']"}}
    }

    for step in steps:
        try:
            locator = locators[step["element"]]["primary_locator"]
            if locator["strategy"] == "id":
                element = driver.find_element(AppiumBy.ID, locator["value"])
            elif locator["strategy"] == "xpath":
                element = driver.find_element(AppiumBy.XPATH, locator["value"])
            else:
                raise ValueError(f"Unsupported locator strategy: {locator['strategy']}")

            if step["action"] == "click":
                element.click()

            if step["screenshot_required"]:
                take_screenshot(driver, test_name, step["step_number"])

        except Exception as e:
            logging.error(f"Error in step {step['step_number']}: {e}")
            take_screenshot(driver, test_name, f"{step['step_number']}_error") # Screenshot on error
            pytest.fail(f"Test failed in step {step['step_number']}: {e}")