#!/bin/bash
# Install and enable the Smart Alert System to run at startup

echo "=================================================="
echo "Smart Alert System - Startup Installation"
echo "=================================================="

SERVICE_FILE="/home/jkarm/smart_alert_system/smart-alert.service"
SYSTEM_SERVICE="/etc/systemd/system/smart-alert.service"

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

echo ""
echo "📋 This script will:"
echo "   1. Copy service file to systemd"
echo "   2. Enable auto-start on boot"
echo "   3. Start the service immediately"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Copy service file
echo "📝 Copying service file..."
sudo cp "$SERVICE_FILE" "$SYSTEM_SERVICE"

if [ $? -ne 0 ]; then
    echo "❌ Failed to copy service file"
    exit 1
fi

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
echo "✅ Enabling service..."
sudo systemctl enable smart-alert.service

# Start service
echo "🚀 Starting service..."
sudo systemctl start smart-alert.service

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status smart-alert.service --no-pager -l

echo ""
echo "=================================================="
echo "✅ Installation Complete!"
echo "=================================================="
echo ""
echo "The Smart Alert System will now:"
echo "  ✓ Start automatically on boot"
echo "  ✓ Restart automatically if it crashes"
echo "  ✓ Run in the background as a service"
echo ""
echo "Useful commands:"
echo "  • Check status:  sudo systemctl status smart-alert"
echo "  • View logs:     sudo journalctl -u smart-alert -f"
echo "  • Stop service:  sudo systemctl stop smart-alert"
echo "  • Start service: sudo systemctl start smart-alert"
echo "  • Restart:       sudo systemctl restart smart-alert"
echo "  • Disable:       sudo systemctl disable smart-alert"
echo ""
