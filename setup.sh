#!/bin/bash

# Mobile Automation Framework Setup Script
# This script helps you set up the mobile automation testing environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_status "Starting Mobile Automation Framework Setup..."

# Check Python version
print_status "Checking Python version..."
if command_exists python; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    print_success "Python version: $PYTHON_VERSION"
    
    # Check if Python version is 3.8+
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ required. Current version: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python not found. Please install Python 3.8+ first."
    exit 1
fi

# Check Node.js for Appium
print_status "Checking Node.js for Appium..."
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js version: $NODE_VERSION"
else
    print_warning "Node.js not found. You'll need Node.js to install Appium."
    print_status "Install Node.js from: https://nodejs.org/"
fi

# Check if virtual environment directory exists
if [ -d "mvenv" ]; then
    print_warning "Virtual environment 'mvenv' already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing virtual environment..."
        rm -rf mvenv
    else
        print_status "Using existing virtual environment..."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "mvenv" ]; then
    print_status "Creating Python virtual environment..."
    python -m venv mvenv
    print_success "Virtual environment created successfully!"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source mvenv/bin/activate
print_success "Virtual environment activated!"

# Upgrade pip
print_status "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed successfully!"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Install development dependencies (optional)
read -p "Do you want to install development dependencies? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "requirements-dev.txt" ]; then
        print_status "Installing development dependencies..."
        pip install -r requirements-dev.txt
        print_success "Development dependencies installed!"
    else
        print_warning "requirements-dev.txt not found, skipping development dependencies."
    fi
fi

# Check for Appium installation
print_status "Checking Appium installation..."
if command_exists appium; then
    APPIUM_VERSION=$(appium --version)
    print_success "Appium version: $APPIUM_VERSION"
else
    print_warning "Appium not found."
    if command_exists npm; then
        read -p "Do you want to install Appium globally? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Installing Appium..."
            npm install -g appium
            print_success "Appium installed successfully!"
            
            print_status "Installing Appium drivers..."
            appium driver install uiautomator2
            appium driver install xcuitest
            print_success "Appium drivers installed!"
        fi
    else
        print_error "npm not found. Please install Node.js and npm first."
    fi
fi

# Create .env file from template
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_success ".env file created! Please edit it with your configuration."
        print_warning "Remember to update .env file with your device/emulator settings!"
    else
        print_warning "env.example not found. You'll need to create .env file manually."
    fi
else
    print_warning ".env file already exists. Skipping creation."
fi

# Check for Android SDK (optional)
if command_exists adb; then
    print_success "Android SDK found (adb available)"
else
    print_warning "Android SDK not found. Install Android Studio for Android testing."
fi

# Check for iOS tools (on macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command_exists xcrun; then
        print_success "Xcode tools found"
    else
        print_warning "Xcode not found. Install Xcode for iOS testing."
    fi
    
    if command_exists idevice_id; then
        print_success "libimobiledevice found (iOS device support)"
    else
        print_warning "libimobiledevice not found. Install with: brew install libimobiledevice"
    fi
else
    print_warning "iOS testing only available on macOS"
fi

# Final instructions
print_success "🎉 Setup completed successfully!"
echo
print_status "Next steps:"
echo "1. Edit .env file with your device/app configuration"
echo "2. Start Appium server: appium"
echo "3. Run tests: pytest tests/ -v"
echo
print_status "Useful commands:"
echo "• Activate virtual environment: source mvenv/bin/activate"
echo "• Run specific tests: pytest -m login tests/ -v"
echo "• Generate HTML report: pytest tests/ --html=reports/report.html"
echo "• Check Appium doctor: appium doctor"
echo
print_success "Happy testing! "
