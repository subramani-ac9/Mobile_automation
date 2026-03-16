#!/usr/bin/env python3
"""
Comprehensive Test Execution Script for AOL Teacher App Automation
Executes all test scenarios with proper reporting and logging
"""

import subprocess
import sys
import time
import os
from datetime import datetime


class TestExecutor:
    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = {}
        self.base_command = "python -m pytest"
        self.common_args = "-v -s --tb=short"
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_test_command(self, test_name, command):
        """Execute a test command and capture results"""
        self.log(f"Starting {test_name}...")
        full_command = f"{self.base_command} {command} {self.common_args}"
        
        start_time = time.time()
        try:
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                status = "PASSED"
                self.log(f"PASS: {test_name} completed successfully in {duration:.1f}s")
            else:
                status = "FAILED"
                self.log(f"FAIL: {test_name} failed in {duration:.1f}s")
                if result.stderr:
                    self.log(f"Error: {result.stderr}")
                    
            self.test_results[test_name] = {
                'status': status,
                'duration': duration,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            self.log(f"ERROR: {test_name} crashed: {str(e)}")
            self.test_results[test_name] = {
                'status': 'CRASHED',
                'duration': 0,
                'error': str(e)
            }
            
    def run_smoke_tests(self):
        """Run all smoke tests for quick validation"""
        self.log("RUNNING SMOKE TESTS")
        self.run_test_command("Smoke Tests", "-m smoke tests/")
        
    def run_data_driven_tests(self):
        """Run all data-driven tests with status tracking"""
        self.log("RUNNING DATA-DRIVEN TESTS")
        self.run_test_command("Data-Driven Tests", "-m data_driven_with_status tests/")
        
    def run_login_tests(self):
        """Run login functionality tests"""
        self.log("RUNNING LOGIN TESTS")
        self.run_test_command("Login Tests", "-m login tests/test_login_page.py")
        
    def run_registration_tests(self):
        """Run registration functionality tests"""
        self.log("RUNNING REGISTRATION TESTS")
        self.run_test_command("Registration Tests", "-m register tests/test_register_page.py")
        
    def run_forgot_password_tests(self):
        """Run forgot password functionality tests"""
        self.log("RUNNING FORGOT PASSWORD TESTS")
        self.run_test_command("Forgot Password Tests", "-m forgot_password tests/test_forgot_password_page.py")
        
    def run_course_creation_tests(self):
        """Run course creation tests"""
        self.log("RUNNING COURSE CREATION TESTS")
        self.run_test_command("Course Creation Tests", "-m course_creation tests/test_course_creation_page.py")
        
    def run_meetup_creation_tests(self):
        """Run meetup creation tests"""
        self.log("RUNNING MEETUP CREATION TESTS")
        self.run_test_command("Meetup Creation Tests", "-m meetup_create tests/test_meetup_create.py")
        
    def run_attendance_tests(self):
        """Run attendance marking tests"""
        self.log("RUNNING ATTENDANCE TESTS")
        self.run_test_command("Attendance Tests", "-m attendance tests/test_attendance.py")
        
    def run_event_edit_tests(self):
        """Run event edit functionality tests"""
        self.log("RUNNING EVENT EDIT TESTS")
        self.run_test_command("Event Edit Tests", "-m edit tests/test_event_edit.py")
        
    def run_event_validation_tests(self):
        """Run event details validation tests"""
        self.log("RUNNING EVENT VALIDATION TESTS")
        self.run_test_command("Event Validation Tests", "-m validation tests/test_event_details_validation.py")
        
    def run_regression_tests(self):
        """Run full regression test suite"""
        self.log("RUNNING REGRESSION TESTS")
        self.run_test_command("Regression Tests", "-m regression tests/")
        
    def run_specific_test_case(self, test_case_id):
        """Run a specific test case by ID"""
        self.log(f"RUNNING SPECIFIC TEST CASE: {test_case_id}")
        self.run_test_command(f"Test Case {test_case_id}", f"-m testcase_id tests/ -k {test_case_id}")
        
    def generate_summary_report(self):
        """Generate a summary report of all test executions"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*80)
        print("AOL TEACHER APP AUTOMATION TEST EXECUTION SUMMARY")
        print("="*80)
        print(f"Execution Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Duration: {total_duration:.1f} seconds")
        print(f"Platform: iOS (com.aoljourney.teacher.app.dev)")
        print(f"Total Test Suites: {len(self.test_results)}")
        print("-"*80)
        
        passed_count = sum(1 for result in self.test_results.values() if result['status'] == 'PASSED')
        failed_count = sum(1 for result in self.test_results.values() if result['status'] == 'FAILED')
        crashed_count = sum(1 for result in self.test_results.values() if result['status'] == 'CRASHED')
        
        print(f"PASSED: {passed_count}")
        print(f"FAILED: {failed_count}")
        print(f"CRASHED: {crashed_count}")
        print(f"SUCCESS RATE: {(passed_count/len(self.test_results)*100):.1f}%")
        print("-"*80)
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status_icon = "PASS" if result['status'] == 'PASSED' else "FAIL" if result['status'] == 'FAILED' else "ERROR"
            duration = result.get('duration', 0)
            print(f"{status_icon} {test_name:<30} {result['status']:<8} ({duration:.1f}s)")
            
        print("-"*80)
        
        # Failed test details
        failed_tests = {name: result for name, result in self.test_results.items() if result['status'] != 'PASSED'}
        if failed_tests:
            print("FAILED TEST DETAILS:")
        for test_name, result in failed_tests.items():
            print(f"\n{test_name}:")
            if 'stderr' in result and result['stderr']:
                print(f"   Error: {result['stderr'][:200]}...")
            if 'error' in result:
                print(f"   Exception: {result['error']}")
                    
        print("\n" + "="*80)
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"reports/test_execution_summary_{timestamp}.txt"
        
        try:
            os.makedirs("reports", exist_ok=True)
            with open(report_file, 'w') as f:
                f.write(f"AOL Teacher App Test Execution Summary\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Duration: {total_duration:.1f} seconds\n")
                f.write(f"Passed: {passed_count}, Failed: {failed_count}, Crashed: {crashed_count}\n")
                f.write(f"Success Rate: {(passed_count/len(self.test_results)*100):.1f}%\n\n")
                
                for test_name, result in self.test_results.items():
                    f.write(f"{test_name}: {result['status']} ({result.get('duration', 0):.1f}s)\n")
                    
            print(f"Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"WARNING: Could not save report: {e}")


def main():
    """Main execution function"""
    executor = TestExecutor()
    
    if len(sys.argv) > 1:
        # Run specific test type
        test_type = sys.argv[1].lower()
        
        test_functions = {
            'smoke': executor.run_smoke_tests,
            'login': executor.run_login_tests,
            'register': executor.run_registration_tests,
            'forgot_password': executor.run_forgot_password_tests,
            'course': executor.run_course_creation_tests,
            'meetup': executor.run_meetup_creation_tests,
            'attendance': executor.run_attendance_tests,
            'edit': executor.run_event_edit_tests,
            'validation': executor.run_event_validation_tests,
            'data_driven': executor.run_data_driven_tests,
            'regression': executor.run_regression_tests,
        }
        
        if test_type in test_functions:
            test_functions[test_type]()
        elif test_type.startswith('tc_') or test_type.startswith('testcase'):
            # Run specific test case
            executor.run_specific_test_case(test_type)
        else:
            print(f"ERROR: Unknown test type: {test_type}")
            print("Available options: smoke, login, register, forgot_password, course, meetup, attendance, edit, validation, data_driven, regression")
            sys.exit(1)
    else:
        # Run comprehensive test suite
        print("Starting Comprehensive AOL Teacher App Test Execution")
        print("This will run all major test scenarios...")
        
        # Execute test suites in logical order
        executor.run_smoke_tests()           # Quick validation first
        executor.run_login_tests()           # Core authentication
        executor.run_registration_tests()    # User onboarding
        executor.run_forgot_password_tests() # Password recovery
        executor.run_course_creation_tests() # Core functionality
        executor.run_meetup_creation_tests() # Core functionality
        executor.run_attendance_tests()      # Event management
        executor.run_event_edit_tests()      # Event modification
        executor.run_event_validation_tests() # Event validation
        executor.run_data_driven_tests()     # Comprehensive data validation
        
        # Optional: Run regression if all core tests pass
        if all(result['status'] == 'PASSED' for result in executor.test_results.values()):
            executor.run_regression_tests()
    
    # Generate final report
    executor.generate_summary_report()
    
    # Exit with appropriate code
    failed_tests = sum(1 for result in executor.test_results.values() if result['status'] != 'PASSED')
    sys.exit(0 if failed_tests == 0 else 1)


if __name__ == "__main__":
    main()
