#!/bin/bash
# Smart Alert System - Quick Start Script

PROJECT_DIR="/home/jkarm/smart_alert_system"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "🚀 Smart Alert System - Quick Start"
echo "=========================================="
echo ""

# Function to show menu
show_menu() {
    echo "Select an option:"
    echo "1) Start Smart Alert System"
    echo "2) Start in background"
    echo "3) Stop background process"
    echo "4) Test PIR Sensor"
    echo "5) Test LED"
    echo "6) Test Email Configuration"
    echo "7) View captured images"
    echo "8) Edit email configuration"
    echo "9) View system status"
    echo "0) Exit"
    echo ""
}

# Function to start system
start_system() {
    echo -e "${GREEN}Starting Smart Alert System...${NC}"
    cd "$PROJECT_DIR"
    python3 smart_alert.py
}

# Function to start in background
start_background() {
    cd "$PROJECT_DIR"
    if pgrep -f "smart_alert.py" > /dev/null; then
        echo -e "${YELLOW}Smart Alert System is already running!${NC}"
        echo "PID: $(pgrep -f smart_alert.py)"
    else
        nohup python3 smart_alert.py > smart_alert.log 2>&1 &
        sleep 2
        if pgrep -f "smart_alert.py" > /dev/null; then
            echo -e "${GREEN}✅ Started in background!${NC}"
            echo "PID: $(pgrep -f smart_alert.py)"
            echo "View logs: tail -f $PROJECT_DIR/smart_alert.log"
        else
            echo -e "${RED}❌ Failed to start${NC}"
        fi
    fi
}

# Function to stop background process
stop_background() {
    if pgrep -f "smart_alert.py" > /dev/null; then
        echo -e "${YELLOW}Stopping Smart Alert System...${NC}"
        pkill -f smart_alert.py
        sleep 1
        if pgrep -f "smart_alert.py" > /dev/null; then
            echo -e "${RED}❌ Failed to stop. Trying force kill...${NC}"
            pkill -9 -f smart_alert.py
        else
            echo -e "${GREEN}✅ Stopped successfully${NC}"
        fi
    else
        echo -e "${YELLOW}Smart Alert System is not running${NC}"
    fi
}

# Function to test PIR
test_pir() {
    echo -e "${GREEN}Testing PIR Sensor...${NC}"
    cd "$PROJECT_DIR"
    python3 tests/test_pir_sensor.py
}

# Function to test LED
test_led() {
    echo -e "${GREEN}Testing LED...${NC}"
    cd "$PROJECT_DIR"
    python3 tests/test_led.py
}

# Function to test email
test_email() {
    echo -e "${GREEN}Testing Email Configuration...${NC}"
    cd "$PROJECT_DIR"
    python3 tests/test_email.py
}

# Function to view images
view_images() {
    echo -e "${GREEN}Captured Images:${NC}"
    if [ -d "$PROJECT_DIR/captured_images" ]; then
        ls -lh "$PROJECT_DIR/captured_images/"
        echo ""
        echo "Total images: $(ls -1 $PROJECT_DIR/captured_images/ 2>/dev/null | wc -l)"
    else
        echo "No images captured yet"
    fi
}

# Function to edit config
edit_config() {
    echo -e "${GREEN}Opening email configuration...${NC}"
    nano "$PROJECT_DIR/config/.env"
}

# Function to show status
show_status() {
    echo -e "${GREEN}System Status:${NC}"
    echo ""
    
    # Check if running
    if pgrep -f "smart_alert.py" > /dev/null; then
        echo -e "Status: ${GREEN}Running ✅${NC}"
        echo "PID: $(pgrep -f smart_alert.py)"
    else
        echo -e "Status: ${YELLOW}Not Running ❌${NC}"
    fi
    
    echo ""
    
    # Check GPIO
    echo "GPIO Status:"
    gpioinfo gpiochip0 2>/dev/null | grep -E "line  (17|18):" || echo "Cannot read GPIO status"
    
    echo ""
    
    # Check config
    if [ -f "$PROJECT_DIR/config/.env" ]; then
        echo -e "Email Config: ${GREEN}Found ✅${NC}"
    else
        echo -e "Email Config: ${RED}Missing ❌${NC}"
    fi
    
    echo ""
    
    # Check images
    if [ -d "$PROJECT_DIR/captured_images" ]; then
        IMAGE_COUNT=$(ls -1 "$PROJECT_DIR/captured_images/" 2>/dev/null | wc -l)
        echo "Captured Images: $IMAGE_COUNT"
    else
        echo "Captured Images: 0"
    fi
    
    echo ""
    
    # Disk space
    echo "Disk Space:"
    df -h "$PROJECT_DIR" | tail -1
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter choice [0-9]: " choice
    echo ""
    
    case $choice in
        1) start_system ;;
        2) start_background ;;
        3) stop_background ;;
        4) test_pir ;;
        5) test_led ;;
        6) test_email ;;
        7) view_images ;;
        8) edit_config ;;
        9) show_status ;;
        0) echo "Goodbye! 👋"; exit 0 ;;
        *) echo -e "${RED}Invalid option. Please try again.${NC}" ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    echo ""
done
