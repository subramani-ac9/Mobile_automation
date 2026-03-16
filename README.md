# AOL Teacher App - Comprehensive Mobile Automation Framework

A comprehensive mobile automation testing framework for the **AOL Teacher App** (com.aoljourney.teacher.app.dev) built with **Appium**, **pytest**, and **Python** using the Page Object Model (POM) design pattern.

## Framework Overview

This automation framework provides complete test coverage for the AOL Teacher App, supporting all major user workflows from authentication to event management and attendance tracking.

### Supported Test Scenarios
1. **User Authentication**
   - Login (valid/invalid credentials, field validation)
   - Registration (5-field signup with validation)
   - Forgot Password (email-based verification code reset)

2. **Event Management**
   - Course Creation (with teacher/product validation)
   - Meetup Creation (with timezone/date handling)
   - Event Details Validation (card display verification)
   - Course/Meetup Editing (search and modify existing events)

3. **Attendance Management**
   - QR Code Attendance (camera-based scanning)
   - Manual Attendance (toggle-based marking)
   - Bulk Attendance (multiple participants)
   - Notes & Summary (attendance tracking with notes)

### Test Execution Types
- **Smoke Tests**: Quick validation of critical functionality
- **Data-Driven Tests**: CSV-based comprehensive test scenarios
- **Regression Tests**: Full feature validation
- **Individual Tests**: Specific test case execution

## Project Structure

```
Mobile_automation/
├── constants/
│   ├── locator/               # Element locators for all pages
│   │   ├── login_locator.py
│   │   ├── register_locator.py
│   │   ├── forgot_password_locator.py
│   │   ├── course_create_locator.py
│   │   ├── meetup_create_locator.py
│   │   ├── course_edit_locator.py
│   │   ├── attendance_locator.py
│   │   └── ...
│   └── message/               # Expected messages and validations
├── pages/                     # Page Object Model implementation
│   ├── base_page.py          # Common page functionality
│   ├── login_page.py
│   ├── register_page.py
│   ├── forgot_password_page.py
│   ├── course_creation_page.py
│   ├── meetup_create_page.py
│   ├── course_edit_page.py
│   ├── attendance_page.py
│   ├── course_details_page.py
│   ├── meetup_details_page.py
│   └── ...
├── tests/                     # Test cases organized by functionality
│   ├── test_login_page.py
│   ├── test_register_page.py
│   ├── test_forgot_password_page.py
│   ├── test_course_creation_page.py
│   ├── test_meetup_create.py
│   ├── test_event_edit.py
│   ├── test_attendance.py
│   ├── test_event_details_validation.py
│   └── ...
├── data/                      # Test data CSV files
│   ├── valid_credentials.csv
│   ├── register_test_data.csv
│   ├── forgot_password_test_data.csv
│   ├── course_create_run1.csv
│   ├── meetup_create_run1.csv
│   ├── event_edit_data.csv
│   ├── attendance_test_data.csv
│   ├── products.csv          
│   └── All Teachers.csv      
├── utils/                    
│   ├── driver_manager.py     
│   ├── logger_config.py      
│   ├── navigator.py          
│   └── helpers.py            
├── reports/                  
├── logs/                     
├── config/                   
│   └── config.py             
├── run_all_tests.py          
└── pytest.ini           
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Appium Server 2.0+
- iOS Simulator or Physical iOS Device
- Xcode (for iOS testing)

### Installation
1. **Clone the repository**:
```bash
git clone <repository-url>
cd Mobile_automation
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Setup virtual environment (recommended)**:
```bash
python -m venv mvenv
source mvenv/bin/activate  # On macOS/Linux
# mvenv\Scripts\activate     # On Windows
pip install -r requirements.txt
```

4. **Install Appium**:
```bash
# Install Appium CLI
npm install -g appium

# Install required drivers
appium driver install uiautomator2  # For Android
appium driver install xcuitest      # For iOS
```

5. **Configure test settings**:
   - Update `config/config.py` with your test credentials
   - Ensure iOS device/simulator is connected
   - Start Appium server: `appium`

6. **Validate setup**:
```bash
python validate_setup.py
```

## Running Tests

### Quick Start - All Tests
```bash
# Run comprehensive test suite
python run_all_tests.py

# Or using pytest directly
pytest tests/ -v -s
```

### Specific Test Categories
```bash
# Smoke tests (critical functionality)
python run_all_tests.py smoke
pytest -m smoke tests/ -v -s

# Data-driven tests (CSV-based)
python run_all_tests.py data_driven
pytest -m data_driven_with_status tests/ -v -s

# Individual functionality tests
python run_all_tests.py login
python run_all_tests.py register
python run_all_tests.py forgot_password
python run_all_tests.py course
python run_all_tests.py meetup
python run_all_tests.py edit
python run_all_tests.py validation
python run_all_tests.py attendance

# Regression tests (full suite)
python run_all_tests.py regression
pytest -m regression tests/ -v -s
```

### Advanced Test Execution
```bash
# Run specific test file
pytest tests/test_login_page.py -v -s

# Run tests by marker
pytest -m "login and smoke" tests/ -v -s
pytest -m "data_driven_with_status" tests/ -v -s

# Run specific test case
pytest tests/test_login_page.py::TestLoginPage::test_successful_login -v -s

# Run with specific test case ID
pytest -m testcase_id tests/ -k "TC_001" -v -s

# Generate HTML report
pytest tests/ --html=reports/test_report.html --self-contained-html
```

### Allure Report (with screenshot on failure)
1. **Run tests with Allure results** (writes to `allure-results/`):
   ```bash
   pytest tests/ -v -s --alluredir=allure-results
   ```
2. **Generate and open the Allure report** (requires [Allure CLI](https://docs.qameta.io/allure/#_installing_a_commandline)):
   ```bash
   allure generate allure-results -o allure-report --clean
   allure serve allure-results
   ```
   Or one-shot: `allure serve allure-results` (generates and opens in browser).
3. **Screenshot on failure**: When a test fails, a screenshot is automatically attached to that test in the Allure report. Ensure the Allure results directory is generated in the same run (e.g. `--alluredir=allure-results`).
4. **Steps for debugging**: Page actions (e.g. "Enter email", "Tap Sign In", "Validate dashboard") and test-level steps (e.g. "Navigate to Login screen", "Perform login") are recorded as Allure steps. In the report, open a test to see the step tree; the failed step shows where the error was raised.

## Test Data Management

### CSV-Based Test Data
The framework uses CSV files for data-driven testing:

- **products.csv**: Available courses/meetups (9 products)
- **All Teachers.csv**: Teacher eligibility (556 teachers)
- **valid_credentials.csv**: Valid login credentials
- **register_test_data.csv**: Registration test scenarios
- **forgot_password_test_data.csv**: Password reset scenarios
- **course_create_run1.csv**: Course creation test data
- **meetup_create_run1.csv**: Meetup creation test data
- **event_edit_data.csv**: Event editing test scenarios
- **attendance_test_data.csv**: Attendance marking scenarios

### Output Files
Test results are automatically saved to CSV output files:
- `*_output.csv`: Detailed test execution results
- `reports/`: HTML and text reports

## Configuration

### Test Configuration (config/config.py)
```python
class TestConfig:
    PLATFORM = "ios"
    TEST_EMAIL = "nivedhas@abovecloud9.ai"
    TEST_PASSWORD = "Admin@ac9"
    DEVICE_NAME = "iPhone 15"
    PLATFORM_VERSION = "17.0"
    BUNDLE_ID = "com.aoljourney.teacher.app.dev"
```

### Pytest Configuration (pytest.ini)
```ini
[pytest]
markers =
    smoke: Critical functionality tests
    regression: Full regression test suite
    login: Login functionality tests
    register: Registration functionality tests
    forgot_password: Password reset tests
    course_creation: Course creation tests
    meetup_create: Meetup creation tests
    edit: Edit functionality tests
    validation: Data validation tests
    attendance: Attendance marking tests
    data_driven_with_status: Data-driven tests with status tracking
```

## Test Scenarios Details

### 1. Authentication Tests
- **Login**: Valid/invalid credentials, field validation, rapid login attempts
- **Registration**: 5-field signup (First Name, Last Name, Email, Password, Confirm Password)
- **Forgot Password**: Email → Send Reset Code → Verification Code → New Password → Re-enter Password

### 2. Event Management Tests
- **Course Creation**: Multi-date courses with teacher assignment and location
- **Meetup Creation**: Single-date meetups with timezone handling
- **Event Editing**: Modify existing events (excluding mode and product)
- **Event Validation**: Verify created events display correctly

### 3. Attendance Management Tests
- **QR Code Attendance**: Camera-based participant check-in
- **Manual Attendance**: Toggle-based attendance marking
- **Bulk Operations**: Mark attendance for multiple participants
- **Notes & Summary**: Add notes and view attendance statistics

## Test Execution Examples

### Example 1: Login Testing
```bash
# Run all login tests
pytest -m login tests/test_login_page.py -v -s

# Expected output:
# test_successful_login - PASSED
# test_invalid_credentials - PASSED  
# test_login_page_elements_visibility - PASSED
```

### Example 2: Data-Driven Course Creation
```bash
# Run course creation with CSV data
pytest -m data_driven_with_status tests/test_course_creation_page.py -v -s

# Processes course_create_run1.csv and generates:
# - course_create_run1_output.csv (detailed results)
# - Success/failure status for each test case
```

### Example 3: Event Editing
```bash
# Run event edit tests
pytest -m edit tests/test_event_edit.py -v -s

# Tests editing of existing courses and meetups
# Validates business rules (mode/product cannot be edited)
# Verifies save/cancel functionality
```

## Logging and Reporting

### Comprehensive Logging
- **Centralized logging** via `utils/logger_config.py`
- **Test lifecycle tracking** (start/end times)
- **Step-by-step logging** for debugging
- **Assertion logging** for validation tracking
- **Log files** saved to `logs/` directory

### Test Reports
- **HTML Reports**: Visual test execution results
- **CSV Output**: Detailed data-driven test results
- **Summary Reports**: Overall execution statistics
- **Screenshots**: Captured on test failures

### Log Analysis
```bash
# View latest logs
ls -la logs/

# Check for errors
grep "ERROR" logs/*.log

# Monitor real-time execution
tail -f logs/latest_test.log
```

## Troubleshooting

### Common Issues
1. **Driver Connection**: Ensure Appium server is running
2. **Device Setup**: Verify iOS device/simulator connectivity
3. **App Installation**: Confirm app is installed and accessible
4. **Permissions**: Grant necessary camera/location permissions

### Debug Mode
```bash
# Run with verbose logging
pytest tests/ -v -s --log-cli-level=DEBUG

# Run single test for debugging
pytest tests/test_login_page.py::TestLoginPage::test_successful_login -v -s
```

### Performance Optimization
- Use explicit waits instead of hardcoded sleeps
- Implement smart element detection
- Reuse app sessions when possible
- Monitor test execution times in logs

## Framework Features

- **Cross-Platform Ready**: iOS and Android support
- **Data-Driven**: CSV-based test data management
- **Comprehensive Logging**: Detailed execution tracking
- **Page Object Model**: Maintainable test structure
- **Dynamic Waits**: Robust element interaction (10s default timeout)
- **Flexible Navigation**: Smart page navigation logic
- **Report Generation**: Multiple output formats
- **Test Categories**: Organized by functionality and priority
- **Status Tracking**: Success/failure monitoring
- **Integration Ready**: CI/CD pipeline compatible
- **Business Rules**: Mode/Product edit restrictions enforced
- **Search Functionality**: Find and edit existing events
- **Error Handling**: Robust exception management

## Support

For issues, questions, or contributions:
1. Check the logs in `logs/` directory
2. Review test execution reports in `reports/`
3. Validate setup using `python validate_setup.py`
4. Ensure all dependencies are installed correctly

## Business Rules

### Authentication
- Email format validation
- Password strength requirements
- Registration redirect to Login or Continue page
- Forgot password uses email verification codes

### Event Management
- **Cannot Edit**: Event mode and product (business restriction)
- **Can Edit**: Description, attendees, dates, times, teachers, organizer, contact, location/URL
- Teacher eligibility validated against products
- Timezone handling for meetup scheduling

### Attendance Management
- QR code and manual attendance marking
- Bulk operations for multiple participants
- Notes support for attendance tracking
- Summary statistics (present/absent/total)

