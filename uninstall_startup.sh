#!/bin/bash
# Uninstall the Smart Alert System from startup

echo "=================================================="
echo "Smart Alert System - Startup Removal"
echo "=================================================="

SYSTEM_SERVICE="/etc/systemd/system/smart-alert.service"

echo ""
echo "This will remove Smart Alert from auto-start."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Removal cancelled."
    exit 0
fi

# Stop service
echo "🛑 Stopping service..."
sudo systemctl stop smart-alert.service

# Disable service
echo "❌ Disabling service..."
sudo systemctl disable smart-alert.service

# Remove service file
if [ -f "$SYSTEM_SERVICE" ]; then
    echo "🗑️  Removing service file..."
    sudo rm "$SYSTEM_SERVICE"
fi

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "✅ Smart Alert System removed from startup"
echo "   You can still run it manually with:"
echo "   ./start.sh"
echo ""
