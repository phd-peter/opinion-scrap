#!/bin/bash

echo "Setting up Chosun Editorial Scraper..."
echo ""

echo "Step 1: Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 2: Installing Chrome/Chromium..."
echo "Checking for Chrome/Chromium installation..."

if command -v google-chrome &> /dev/null; then
    echo "✓ Google Chrome is already installed"
elif command -v chromium-browser &> /dev/null; then
    echo "✓ Chromium is already installed"
elif command -v chromium &> /dev/null; then
    echo "✓ Chromium is already installed"
else
    echo "Chrome/Chromium not found. Installing..."
    
    if [[ -f /etc/debian_version ]]; then
        echo "Detected Debian/Ubuntu system"
        sudo apt-get update
        sudo apt-get install -y chromium-browser chromium-chromedriver
    elif [[ -f /etc/redhat-release ]]; then
        echo "Detected RedHat/CentOS system"
        sudo yum install -y chromium chromedriver
    else
        echo "⚠️  Unable to detect package manager. Please install Chrome/Chromium manually:"
        echo "   Ubuntu/Debian: sudo apt-get install chromium-browser"
        echo "   macOS: brew install chromium"
    fi
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "To run the scraper:"
echo "  python scraper.py"
