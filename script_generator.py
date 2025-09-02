import google.generativeai as genai
import json
import os
import re
from typing import Dict, List, Any, Optional
import logging
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

class AIScriptGenerator:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            raise ValueError("GEMINI_API_KEY not configured. Please set your actual API key in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-1.5-pro'))
        self.logger = logging.getLogger(__name__)
        
        # Enhanced prompt for comprehensive flow generation
        self.COMPREHENSIVE_FLOW_PROMPT = """Persona:
You are a Senior Automation Architect specializing in Appium-based mobile automation for Android applications.  
You design scalable, reusable, and modular Python test scripts that integrate with helper modules and locators.json.  
You always prioritize:  
- Accuracy of locators by using get_locator() strictly with exact names from locators.json.  
- Clean modular workflows for login, product selection, and add-to-cart.  
- Structured logging using the existing logger.  
- Intelligent waits with wait_for_screen_transition().  
- Graceful error handling and fallback for resilient execution.  
- Test design in unittest style with setUp and tearDown.  
Your deliverable is always a single high-quality Python script file that follows PEP8, is well-documented, scalable for future flows like checkout/payment, and executable end-to-end without manual intervention.  

Task:
Generate a Python script that:
1. Automates end-to-end test cases for a Shopping App using Appium, importing helper functions and LOCATORS via:
   from helper import *
2. Initializes the driver by calling launch() and ensures reusability by setting reuse_existing=True when flows do not require login.
3. Organizes flows into structured functions covering:
   - Login
   - Product selection
   - Add to cart
4. Supports screenshot-based validation and XML parsing for accurate element recognition.
5. Reuses existing logger from helper for structured logging (INFO, DEBUG, ERROR).
6. Always use get_locator(screen_name, element_name) from helper to fetch locators dynamically.
   - Do not hardcode locators in the script.
   - Always pass exact names as they appear in locators.json without renaming or altering.
   - Example:
     locator_dict = get_locator("login_screen", "username_input")
     find_element_with_fallback(driver, locator_dict, "Username Input")
7. Use wait_for_screen_transition() to confirm readiness of each screen before performing interactions.
8. For login flow:
   - Input username and password using send_keys().
   - Validate login success by checking unique identifier of home_screen.
9. For product selection flow:
   - Navigate to product listing using get_locator() for category buttons.
   - Select a product by verifying presence via XML layout and screenshot match.
10. For add-to-cart flow:
    - Locate "Add to Cart" button via locator dictionary.
    - Confirm success with presence of "cart_badge" or cart screen identifier.
11. Test cases must be generated in unittest style:
    - Encapsulate flows inside TestShoppingApp class.
    - Use setUp / tearDown for driver lifecycle.
    - Modularize each test as a separate method (e.g., test_login, test_product_selection, test_add_to_cart).
12. Handle dynamic content with resilient fallback:
    - If locator not found, attempt close synonyms only inside post-failure fallback.
13. Ensure popup handling with handle_possible_popups() before or during navigation.
14. Expandable lists or accordions must be validated with is_element_expanded(element) before expanding.
15. Screenshots must be validated against expected state before asserting success.
16. Avoid retries unless necessary, and log locator usage clearly.
17. Scripts must gracefully handle failures and log structured error details.
18. Ensure OTP handling is skipped in this flow (only username/password login used).
19. Do not reimplement helper functions—reuse as provided.
20. Deliver output as a single Python .py file, runnable as test automation script.
21. Include inline comments explaining key workflows.
22. Code must be modular, reusable, and scalable for future flows like checkout and payment.
23. Use only necessary imports, avoid unused libraries.

Code Style Guide:
- PEP8 Compliance: Follow Python style guidelines strictly
- Documentation: Include comprehensive docstrings and inline comments
- Error Handling: Use try-except blocks with specific exception types
- Logging: Use structured logging with appropriate levels (INFO, DEBUG, ERROR)
- Modularity: Separate concerns into focused, reusable functions
- Naming: Use descriptive variable and function names (snake_case)
- Constants: Define constants at module level for reusability
- Type Hints: Use type annotations for better code clarity
- Imports: Organize imports (standard, third-party, local) with clear separation

Technical Requirements:
- Framework: unittest with setUp/tearDown methods
- Driver Management: Proper initialization and cleanup
- Locator Strategy: Dynamic locator fetching with fallback mechanisms
- Wait Strategies: Intelligent waits for element visibility and screen transitions
- Screenshot Management: Timestamped screenshots with descriptive naming
- XML Parsing: Page source analysis for element validation
- Popup Handling: Automatic popup detection and dismissal
- Error Recovery: Graceful failure handling with detailed logging

Evaluation Metrics:
- Reusability: Flows easily extended for future features
- Locator Accuracy: All locators resolve correctly from locators.json
- Readability: Clear, documented, PEP8 compliant code
- Scalability: Adaptable to future app features and flows
- Execution Validity: Must run end-to-end with minimal manual changes
- Error Resilience: Handles failures gracefully with proper logging
- Performance: Efficient execution with minimal unnecessary waits

Deliverable:
Generate a single high-quality Python script file that:
- Implements complete login → product selection → add to cart flow
- Uses unittest framework with proper test structure
- Follows all specified requirements and style guidelines
- Is production-ready and executable without manual intervention
- Includes comprehensive error handling and logging
- Is scalable for future automation needs

Return ONLY executable Python code wrapped in ```python``` blocks. Ensure the script is production-ready for Android mobile app testing with enterprise-grade quality standards."""
        
    def _extract_python_code_from_response(self, response_text: str) -> str:
        """Extract Python code from response text with enhanced pattern matching"""
        # Enhanced Python code extraction patterns
        patterns = [
            r'```python\s*(.*?)\s*```',  # Python-specific code blocks
            r'```\s*(.*?)\s*```',        # Generic code blocks
            r'# Python code:(.*?)(?=\n\n|\Z)',  # Code after "Python code:" marker
            r'def test_.*?(?=\n\n|\Z)',  # Test function definition onwards
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
        if matches:
                extracted = matches[0].strip()
                if len(extracted) > 100:  # Ensure meaningful content
                    return extracted
        
        # Fallback: return cleaned response text
        return re.sub(r'^[^#\n]*\n', '', response_text.strip())
        
    def generate_comprehensive_flow_script(self, test_case: Dict, locators: Dict, 
                                         page_source: str = '', flow_type: str = 'complete') -> str:
        """Generate comprehensive Appium test script combining multiple flows"""
        
        # Enhanced prompt with specific flow requirements
        flow_specific_prompt = f"""{self.COMPREHENSIVE_FLOW_PROMPT}

FLOW TYPE: {flow_type.upper()}
TEST CASE: {test_case.get('test_name', 'Comprehensive Flow Test')}
DESCRIPTION: {test_case.get('description', 'End-to-end user journey testing')}

LOCATORS DATA:
{json.dumps(locators, indent=2)}

PAGE SOURCE CONTEXT (First 2000 chars):
{page_source[:2000] if page_source else 'Page source not provided'}

ADDITIONAL REQUIREMENTS:
- Implement Android screenshot capture at each major step
- Parse Android XML page source for element validation
- Handle Android login authentication with proper error handling
- Navigate Android product catalog and select items
- Add products to Android cart with validation
- Include comprehensive Android logging and error handling
- Use Android-specific wait strategies and retry mechanisms
- Validate Android business logic at each step
- Handle Android dynamic content and user-specific scenarios
- Use Android-specific element interactions (tap, swipe, scroll)

Generate a production-ready Android mobile app test script that can be executed immediately."""
        
        try:
            response = self.model.generate_content(
                flow_specific_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=6000,  # Increased for comprehensive flows
                    temperature=0.1,         # Low temperature for consistent output
                    top_p=0.8,              # Focused creativity
                    top_k=40                # Diverse but relevant responses
                )
            )
            
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            # Extract and validate generated script
            generated_script = self._extract_python_code_from_response(response.text)
            
            # Enhanced validation for comprehensive flows
            required_elements = [
                'import unittest', 'from helper import', 'get_locator', 'launch()', 
                'wait_for_screen_transition', 'logger', 'setUp', 'tearDown', 
                'TestShoppingApp', 'test_login', 'test_product_selection', 'test_add_to_cart',
                'try:', 'except', 'screenshot', 'handle_possible_popups'
            ]
            
            missing_elements = [elem for elem in required_elements if elem.lower() not in generated_script.lower()]
            
            if missing_elements:
                self.logger.warning(f"Generated script missing elements: {missing_elements}")
            
            if len(generated_script) < 200:
                raise Exception("Generated script is too short for comprehensive flows")
            
            self.logger.info(f"Successfully generated comprehensive flow script for {test_case.get('test_name', 'Unknown')}")
            return generated_script
            
        except Exception as e:
            self.logger.error(f"Comprehensive flow script generation failed: {str(e)}")
            raise Exception(f"Failed to generate comprehensive flow script: {str(e)}")

    def generate_test_script(self, test_case: Dict, locators: Dict, page_source: str = '') -> str:
        """Generate standard Appium test script - maintained for backward compatibility"""
        return self.generate_comprehensive_flow_script(test_case, locators, page_source, 'standard')
        
    def save_script(self, script_content: str, test_name: str, flow_type: str = 'comprehensive') -> str:
        """Save generated script with enhanced naming and organization"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'test_{test_name}_{flow_type}_{timestamp}.py'
        file_path = os.path.join('output/generated_scripts', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Add header comment with generation metadata
        header_comment = f'''"""
Generated Appium Test Script
Test: {test_name}
Flow Type: {flow_type}
Generated: {datetime.now().isoformat()}
Framework: Appium + Python + Pytest
Features: Screenshot capture, XML parsing, Login, Product selection, Add to cart
"""

'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(header_comment + script_content)
            
        self.logger.info(f'Generated {flow_type} script saved: {file_path}')
        return file_path

    def generate_flow_specific_script(self, flow_name: str, locators: Dict, 
                                    page_source: str = '') -> str:
        """Generate script for specific flow types"""
        flow_configs = {
            'login': {
                'test_name': 'Login Flow Test',
                'description': 'Complete authentication flow with screenshot capture and XML parsing',
                'focus': 'Login, error handling, validation'
            },
            'product_selection': {
                'test_name': 'Product Selection Flow Test',
                'description': 'Product browsing, selection, and details with comprehensive validation',
                'focus': 'Catalog navigation, product selection, reviews'
            },
            'add_to_cart': {
                'test_name': 'Add to Cart Flow Test',
                'description': 'Cart management, product addition, and validation flows',
                'focus': 'Cart operations, quantity management, validation'
            },
            'complete_flow': {
                'test_name': 'Complete User Journey Test',
                'description': 'End-to-end user journey from login to cart completion',
                'focus': 'All flows combined with comprehensive validation'
            }
        }
        
        config = flow_configs.get(flow_name, flow_configs['complete_flow'])
        
        test_case = {
            'test_name': config['test_name'],
            'description': config['description'],
            'flow_type': flow_name,
            'focus': config['focus']
        }
        
        return self.generate_comprehensive_flow_script(test_case, locators, page_source, flow_name)

    def validate_generated_script(self, script_content: str) -> Dict[str, Any]:
        """Validate generated script for quality and completeness"""
        validation_result = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'score': 100
        }
        
        # Check for required imports
        required_imports = ['unittest', 'from helper import', 'get_locator']
        for imp in required_imports:
            if imp not in script_content:
                validation_result['issues'].append(f"Missing import: {imp}")
                validation_result['score'] -= 10
        
        # Check for required functions
        required_functions = ['def setUp', 'def tearDown', 'def test_login', 'def test_product_selection', 'def test_add_to_cart']
        for func in required_functions:
            if func not in script_content:
                validation_result['warnings'].append(f"Missing function: {func}")
                validation_result['score'] -= 5
        
        # Check for required features
        required_features = ['launch()', 'wait_for_screen_transition', 'logger', 'screenshot', 'handle_possible_popups', 'try:', 'except']
        for feature in required_features:
            if feature not in script_content:
                validation_result['warnings'].append(f"Missing feature: {feature}")
                validation_result['score'] -= 5
        
        # Check script length
        if len(script_content) < 300:
            validation_result['issues'].append("Script too short for comprehensive flows")
            validation_result['score'] -= 20
        
        # Determine validity
        if validation_result['score'] < 70:
            validation_result['is_valid'] = False
        
        return validation_result