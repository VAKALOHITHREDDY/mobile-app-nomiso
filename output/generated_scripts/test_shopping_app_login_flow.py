import os
import logging
import pytest
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCREENSHOT_DIR = "output/screenshots/shopping_app_login_flow/"

def take_screenshot(driver, step_name):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{step_name}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    driver.save_screenshot(filepath)
    logging.info(f"Screenshot saved: {filepath}")


def find_element_with_fallback(driver, element_name, locators):
    """Find element with intelligent fallback: ID → XPath → Accessibility ID → Text"""
    element_data = locators[element_name]
    
    # Define fallback strategy order
    fallback_strategies = ['id', 'xpath', 'accessibility_id', 'class_name', 'android_uiautomator']
    
    # Try primary locator first
    primary_locator = element_data["primary_locator"]
    try:
        element = driver.find_element(by=primary_locator["strategy"], value=primary_locator["value"])
        logging.info(f"Element found using primary {primary_locator['strategy']} locator")
        return element
    except Exception as e:
        logging.warning(f"Primary locator failed: {e}")
    
    # Try fallback locators in order
    for fallback in element_data.get("fallback_locators", []):
        try:
            element = driver.find_element(by=fallback["strategy"], value=fallback["value"])
            logging.info(f"Element found using fallback {fallback['strategy']} locator")
            return element
        except Exception as e:
            logging.warning(f"Fallback {fallback['strategy']} failed: {e}")
            continue
    
    # Final text-based fallback
    try:
        element = driver.find_element(AppiumBy.XPATH, f"//*[contains(@text, '{element_name}')]")
        logging.info("Element found using text fallback")
        return element
    except Exception as e:
        logging.error(f"All locator strategies failed for {element_name}: {e}")
        raise e


@pytest.fixture(scope="module")
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


def test_shopping_app_login_flow(driver):
    steps = [
        {"step_number": 1, "action": "click", "element": "login_button", "input_data": "", "expected_result": "Login screen opens", "screenshot_required": True},
        {"step_number": 2, "action": "send_keys", "element": "username_field", "input_data": "testuser@example.com", "expected_result": "Username entered", "screenshot_required": False},
        {"step_number": 3, "action": "send_keys", "element": "password_field", "input_data": "password123", "expected_result": "Password entered", "screenshot_required": False},
        {"step_number": 4, "action": "click", "element": "submit_button", "input_data": "", "expected_result": "User logged in successfully", "screenshot_required": True}
    ]
    locators = {
        "login_button": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/login_button"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.Button[@text='Login']"}},
        "username_field": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/username_field"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.EditText[@hint='Username']"}},
        "password_field": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/password_field"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.EditText[@hint='Password']"}},
        "submit_button": {"primary_locator": {"strategy": "id", "value": "com.example.shoppingapp:id/submit_button"}, "secondary_locator": {"strategy": "xpath", "value": "//android.widget.Button[@text='Submit']"}}
    }

    for step in steps:
        try:
            element = find_element(driver, step["element"], locators)
            if step["action"] == "click":
                element.click()
            elif step["action"] == "send_keys":
                element.send_keys(step["input_data"])
            logging.info(f"Step {step['step_number']} - {step['expected_result']}")
            if step["screenshot_required"]:
                take_screenshot(driver, f"step_{step['step_number']}")
        except Exception as e:
            logging.error(f"Error in step {step['step_number']}: {e}")
            take_screenshot(driver, f"step_{step['step_number']}_failed")
            pytest.fail(f"Test failed in step {step['step_number']}")