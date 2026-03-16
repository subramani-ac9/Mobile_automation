#!/usr/bin/env python3
"""
Mobile Automation Framework Setup Validation Script

This script validates that all required dependencies and configurations
are properly set up for the mobile automation framework.
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'  # End color

def print_status(message, status="info"):
    """Print colored status message"""
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "header": Colors.MAGENTA
    }
    color = colors.get(status, Colors.WHITE)
    print(f"{color}[{status.upper()}]{Colors.ENDC} {message}")

def check_python_version():
    """Check Python version compatibility"""
    print_status("Checking Python version...", "info")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} ✓", "success")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Requires 3.8+", "error")
        return False

def check_package_installation():
    """Check if required packages are installed"""
    print_status("Checking Python package dependencies...", "info")
    
    required_packages = [
        "appium",
        "selenium", 
        "pytest",
        "pandas",
        "dotenv",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace("-", "_"))
            print_status(f"  {package} ✓", "success")
        except ImportError:
            print_status(f"  {package} ✗", "error")
            missing_packages.append(package)
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "error")
        print_status("Run: pip install -r requirements.txt", "info")
        return False
    
    return True

def check_external_tools():
    """Check external tools availability"""
    print_status("Checking external tools...", "info")
    
    tools = {
        "appium": "Appium server",
        "adb": "Android Debug Bridge (Android SDK)",
        "node": "Node.js (required for Appium)",
        "npm": "Node Package Manager"
    }
    
    results = {}
    
    for tool, description in tools.items():
        try:
            result = subprocess.run([tool, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print_status(f"  {description}: {version} ✓", "success")
                results[tool] = True
            else:
                print_status(f"  {description}: Not working properly", "warning")
                results[tool] = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print_status(f"  {description}: Not found", "warning")
            results[tool] = False
    
    return results

def check_appium_server():
    """Check if Appium server is accessible"""
    print_status("Checking Appium server connectivity...", "info")
    
    try:
        import requests
        response = requests.get("http://localhost:4723/status", timeout=5)
        if response.status_code == 200:
            print_status("  Appium server running on localhost:4723 ✓", "success")
            return True
        else:
            print_status("  Appium server not responding correctly", "warning")
            return False
    except Exception as e:
        print_status("  Appium server not running (start with 'appium')", "warning")
        return False

def check_configuration_files():
    """Check for required configuration files"""
    print_status("Checking configuration files...", "info")
    
    files = {
        "pytest.ini": "Pytest configuration",
        "requirements.txt": "Python dependencies",
        "config/config.py": "Application configuration",
        ".env": "Environment variables (optional)"
    }
    
    all_good = True
    
    for file_path, description in files.items():
        if Path(file_path).exists():
            print_status(f"  {description}: Found ✓", "success")
        else:
            status = "warning" if file_path == ".env" else "error"
            print_status(f"  {description}: Missing", status)
            if file_path != ".env":
                all_good = False
    
    return all_good

def check_test_structure():
    """Check test directory structure"""
    print_status("Checking project structure...", "info")
    
    directories = [
        "tests",
        "pages", 
        "utils",
        "config",
        "data",
        "reports"
    ]
    
    all_good = True
    
    for directory in directories:
        if Path(directory).exists():
            test_files = list(Path(directory).glob("*.py"))
            if directory == "tests":
                count = len([f for f in test_files if f.name.startswith("test_")])
                print_status(f"  {directory}/: Found with {count} test files ✓", "success")
            else:
                count = len(test_files)
                print_status(f"  {directory}/: Found with {count} Python files ✓", "success")
        else:
            print_status(f"  {directory}/: Missing", "error")
            all_good = False
    
    return all_good

def run_sample_test():
    """Run a simple test to validate the framework"""
    print_status("Running framework validation test...", "info")
    
    try:
        # Try to import main framework components
        from config.config import TestConfig
        from utils.driver_manager import DriverManager
        
        print_status("  Framework imports successful ✓", "success")
        
        # Check configuration loading
        config_items = [
            TestConfig.MOBILE_PLATFORM,
            TestConfig.APPIUM_HOST,
            TestConfig.APPIUM_PORT
        ]
        
        print_status("  Configuration loading successful ✓", "success")
        print_status(f"    Platform: {TestConfig.MOBILE_PLATFORM}", "info")
        print_status(f"    Appium: {TestConfig.APPIUM_HOST}:{TestConfig.APPIUM_PORT}", "info")
        
        return True
        
    except Exception as e:
        print_status(f"  Framework validation failed: {str(e)}", "error")
        return False

def main():
    """Main validation function"""
    print_status("Mobile Automation Framework Setup Validation", "header")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Package Dependencies", check_package_installation),
        ("External Tools", lambda: all(check_external_tools().values())),
        ("Configuration Files", check_configuration_files),
        ("Project Structure", check_test_structure),
        ("Framework Components", run_sample_test),
        ("Appium Server", check_appium_server)
    ]
    
    results = {}
    
    for check_name, check_function in checks:
        print()
        try:
            results[check_name] = check_function()
        except Exception as e:
            print_status(f"Error during {check_name} check: {str(e)}", "error")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print_status("Validation Summary", "header")
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "success" if result else "error"
        symbol = "✓" if result else "✗"
        print_status(f"  {check_name}: {symbol}", status)
    
    print()
    if passed == total:
        print_status(f"🎉 All checks passed! ({passed}/{total})", "success")
        print_status("Your mobile automation framework is ready to use!", "success")
        print_status("Next steps:", "info")
        print("  1. Start Appium server: appium")
        print("  2. Connect your device/start emulator")
        print("  3. Run tests: pytest tests/ -v")
    else:
        print_status(f"WARNING: {passed}/{total} checks passed", "warning")
        print_status("Please fix the issues above before running tests.", "warning")
        
        if not results.get("Appium Server", True):
            print_status("TIP: Start Appium server with 'appium' command", "info")
        
        if not results.get("Package Dependencies", True):
            print_status("TIP: Install dependencies with 'pip install -r requirements.txt'", "info")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
