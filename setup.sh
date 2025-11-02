#!/bin/bash
# Quick installation and setup script

clear
echo "=================================================="
echo "   Smart Alert System - Quick Setup"
echo "=================================================="
echo ""
echo "This script will help you set up the Smart Alert System."
echo ""
echo "Steps:"
echo "  1. Configure email (if not done)"
echo "  2. Test hardware components"
echo "  3. Install auto-start service"
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 1: Email Configuration
echo "Step 1: Email Configuration"
echo "----------------------------"
if [ -f "config/.env" ]; then
    if grep -q "your_email@gmail.com" config/.env || grep -q "your_16_char_app_password" config/.env; then
        echo "⚠️  Email not configured yet."
        echo ""
        echo "Please edit: config/.env"
        echo "Add your Gmail and App Password"
        echo ""
        echo "See docs for help: less AUTOSTART.md"
        echo ""
        read -p "Press Enter when done..."
    else
        echo "✅ Email configuration found"
        
        # Test email
        echo ""
        read -p "Test email configuration? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 tests/test_email.py
        fi
    fi
else
    echo "❌ Email config not found!"
    echo "Please create: config/.env"
    exit 1
fi

echo ""
echo ""

# Step 2: Hardware Test
echo "Step 2: Hardware Tests"
echo "----------------------"
read -p "Test PIR sensor? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Testing PIR sensor for 10 seconds..."
    timeout 10 python3 tests/test_pir_sensor.py || true
fi

echo ""
read -p "Test LED? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Testing LED (will blink 3 times)..."
    timeout 10 python3 tests/test_led.py || true
fi

echo ""
echo ""

# Step 3: Installation
echo "Step 3: Installation"
echo "--------------------"
read -p "Install auto-start on boot? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./install_startup.sh
else
    echo ""
    echo "Skipping auto-start installation."
    echo "You can run manually with: ./start.sh"
    echo "Or install later with: ./install_startup.sh"
fi

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  • View logs: sudo journalctl -u smart-alert -f"
echo "  • Check status: sudo systemctl status smart-alert"
echo "  • View images: ls -lh captured_images/"
echo ""
echo "Documentation:"
echo "  • README.md - Main documentation"
echo "  • AUTOSTART.md - Service management"
echo ""
