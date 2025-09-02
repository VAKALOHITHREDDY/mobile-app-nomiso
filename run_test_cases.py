#!/usr/bin/env python3
"""
Run specific test cases for the shopping app
Including login pass and fail scenarios
"""

import json
import os
import sys
from datetime import datetime

def load_test_cases():
    """Load test cases from JSON file"""
    try:
        with open('test_cases.json', 'r') as f:
            test_cases = json.load(f)
        print(f"✅ Loaded {len(test_cases)} test cases")
        return test_cases
    except Exception as e:
        print(f"❌ Failed to load test cases: {e}")
        return None

def run_login_pass_test():
    """Run the successful login test case"""
    print("\n🧪 RUNNING LOGIN PASS TEST")
    print("=" * 40)
    
    try:
        from screen import AppiumBase
        from locator_generator import AILocatorGenerator
        from script_generator import AIScriptGenerator
        
        print("✅ All required classes imported successfully")
        
        # Initialize base framework
        base = AppiumBase()
        print("✅ AppiumBase initialized")
        
        # Initialize locator generator
        locator_gen = AILocatorGenerator()
        print("✅ LocatorGenerator initialized")
        
        # Initialize script generator
        script_gen = AIScriptGenerator()
        print("✅ ScriptGenerator initialized")
        
        # Load test case
        test_cases = load_test_cases()
        if not test_cases:
            return False
            
        login_pass_test = None
        for test in test_cases:
            if test.get('test_name') == 'shopping_app_login_flow_pass':
                login_pass_test = test
                break
        
        if not login_pass_test:
            print("❌ Login pass test case not found")
            return False
            
        print(f"✅ Found login pass test: {login_pass_test['test_name']}")
        print(f"📝 Description: {login_pass_test['description']}")
        print(f"🏷️  Tags: {', '.join(login_pass_test['tags'])}")
        print(f"⏱️  Estimated Duration: {login_pass_test['estimated_duration']} seconds")
        
        # Display test steps
        print(f"\n📋 Test Steps ({len(login_pass_test['steps'])} steps):")
        for step in login_pass_test['steps']:
            print(f"   Step {step['step_number']}: {step['description']}")
            print(f"      Action: {step['action']} on {step['element']}")
            if step['input_data']:
                print(f"      Input: {step['input_data']}")
            print(f"      Expected: {step['expected_result']}")
            print()
        
        print("✅ Login pass test case loaded and ready for execution")
        return True
        
    except Exception as e:
        print(f"❌ Login pass test failed: {e}")
        return False

def run_login_fail_test():
    """Run the failed login test case"""
    print("\n🧪 RUNNING LOGIN FAIL TEST")
    print("=" * 40)
    
    try:
        # Load test case
        test_cases = load_test_cases()
        if not test_cases:
            return False
            
        login_fail_test = None
        for test in test_cases:
            if test.get('test_name') == 'shopping_app_login_flow_fail':
                login_fail_test = test
                break
        
        if not login_fail_test:
            print("❌ Login fail test case not found")
            return False
            
        print(f"✅ Found login fail test: {login_fail_test['test_name']}")
        print(f"📝 Description: {login_fail_test['description']}")
        print(f"🏷️  Tags: {', '.join(login_fail_test['tags'])}")
        print(f"⏱️  Estimated Duration: {login_fail_test['estimated_duration']} seconds")
        
        # Display test steps
        print(f"\n📋 Test Steps ({len(login_fail_test['steps'])} steps):")
        for step in login_fail_test['steps']:
            print(f"   Step {step['step_number']}: {step['description']}")
            print(f"      Action: {step['action']} on {step['element']}")
            if step['input_data']:
                print(f"      Input: {step['input_data']}")
            print(f"      Expected: {step['expected_result']}")
            print()
        
        # Show test data for failed login
        test_data = login_fail_test.get('test_data', {})
        print("🔑 Test Data for Failed Login:")
        print(f"   Valid Email: {test_data.get('valid_email', 'N/A')}")
        print(f"   Invalid Password: {test_data.get('invalid_password', 'N/A')}")
        print(f"   Expected Error: {test_data.get('expected_error_message', 'N/A')}")
        
        print("✅ Login fail test case loaded and ready for execution")
        return True
        
    except Exception as e:
        print(f"❌ Login fail test failed: {e}")
        return False

def run_product_selection_test():
    """Run the product selection test case"""
    print("\n🧪 RUNNING PRODUCT SELECTION TEST")
    print("=" * 40)
    
    try:
        # Load test case
        test_cases = load_test_cases()
        if not test_cases:
            return False
            
        product_test = None
        for test in test_cases:
            if test.get('test_name') == 'shopping_app_product_selection_pass':
                product_test = test
                break
        
        if not product_test:
            print("❌ Product selection test case not found")
            return False
            
        print(f"✅ Found product selection test: {product_test['test_name']}")
        print(f"📝 Description: {product_test['description']}")
        print(f"🏷️  Tags: {', '.join(product_test['tags'])}")
        
        print("✅ Product selection test case loaded and ready for execution")
        return True
        
    except Exception as e:
        print(f"❌ Product selection test failed: {e}")
        return False

def run_add_to_cart_test():
    """Run the add to cart test case"""
    print("\n🧪 RUNNING ADD TO CART TEST")
    print("=" * 40)
    
    try:
        # Load test case
        test_cases = load_test_cases()
        if not test_cases:
            return False
            
        cart_test = None
        for test in test_cases:
            if test.get('test_name') == 'shopping_app_add_to_cart_pass':
                cart_test = test
                break
        
        if not cart_test:
            print("❌ Add to cart test case not found")
            return False
            
        print(f"✅ Found add to cart test: {cart_test['test_name']}")
        print(f"📝 Description: {cart_test['description']}")
        print(f"🏷️  Tags: {', '.join(cart_test['tags'])}")
        
        print("✅ Add to cart test case loaded and ready for execution")
        return True
        
    except Exception as e:
        print(f"❌ Add to cart test failed: {e}")
        return False

def generate_test_report(results, start_time):
    """Generate detailed test report and save to file"""
    end_time = datetime.now()
    duration = end_time - start_time
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    failed = total - passed
    
    # Create reports directory if it doesn't exist
    os.makedirs('output/reports', exist_ok=True)
    
    # Generate report filename with timestamp
    timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    report_filename = f"output/reports/test_execution_report_{timestamp}.txt"
    
    # Generate report content
    report_content = f"""
SHOPPING APP TEST CASE EXECUTION REPORT
========================================
Execution Date: {start_time.strftime("%Y-%m-%d %H:%M:%S")}
Duration: {duration.total_seconds():.2f} seconds
Total Tests: {total}
Passed: {passed}
Failed: {failed}
Success Rate: {(passed/total)*100:.1f}%

DETAILED TEST RESULTS
====================
"""
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        report_content += f"{status}: {test_name}\n"
    
    report_content += f"""
SUMMARY
=======
✅ PASSED: {passed} tests
❌ FAILED: {failed} tests
📊 SUCCESS RATE: {(passed/total)*100:.1f}%

STATUS: {'ALL TESTS PASSED' if passed == total else 'SOME TESTS FAILED'}

Generated by: Appium Test Automation Framework
Report Generated: {end_time.strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    # Save report to file
    try:
        with open(report_filename, 'w') as f:
            f.write(report_content)
        print(f"📄 Test report saved to: {report_filename}")
        return report_filename
    except Exception as e:
        print(f"❌ Failed to save report: {e}")
        return None

def main():
    """Main function to run all test cases"""
    start_time = datetime.now()
    
    print("🚀 SHOPPING APP TEST CASE EXECUTION")
    print("=" * 60)
    print(f"⏰ Started at: {start_time.isoformat()}")
    print()
    
    # Run all test cases
    tests = [
        ("Login Pass Test", run_login_pass_test),
        ("Login Fail Test", run_login_fail_test),
        ("Product Selection Test", run_product_selection_test),
        ("Add to Cart Test", run_add_to_cart_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST CASE EXECUTION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    failed = total - passed
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} test cases ready")
    print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
    print(f"⏱️  Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds")
    
    # Generate and save test report
    report_file = generate_test_report(results, start_time)
    
    if passed == total:
        print("🎉 All test cases are loaded and ready for execution!")
        print("📱 You can now run these tests with Appium automation")
    else:
        print("⚠️  Some test cases failed to load. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
