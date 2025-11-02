#!/usr/bin/env python3
"""
Smart Motion Detection System
- Detects motion using PIR sensor
- Captures image with camera
- Turns on LED for 10 seconds when motion detected
- Sends captured image via email
- Comprehensive error handling
"""

import RPi.GPIO as GPIO
import time
from datetime import datetime
import os
import sys
import signal
import traceback
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

# ========================
# Configuration
# ========================
# Get the project directory (where this script is located)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

PIR_PIN = 17        # PIR sensor connected to GPIO 17 (Physical pin 11)
LED_PIN = 18        # LED connected to GPIO 18 (Physical pin 12)
LED_ON_TIME = 10    # LED stays on for 10 seconds
COOLDOWN_TIME = 2   # Cooldown after detection to avoid multiple triggers
SAVE_DIR = os.path.join(PROJECT_DIR, "captured_images")
ENV_FILE = os.path.join(PROJECT_DIR, "config", ".env")

# ========================
# Global Variables
# ========================
picam2 = None
gpio_initialized = False
camera_initialized = False
email_configured = False
email_config = {}

# ========================
# Load Email Configuration
# ========================
def load_email_config():
    """Load email configuration from .env file"""
    global email_configured, email_config
    
    try:
        if not os.path.exists(ENV_FILE):
            print(f"⚠️ Email config file not found: {ENV_FILE}")
            print("   Email notifications will be disabled")
            return False
        
        # Read .env file
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    email_config[key.strip()] = value.strip()
        
        # Validate required fields
        required_fields = ['SENDER_EMAIL', 'EMAIL_PASSWORD', 'RECIPIENT_EMAIL']
        missing_fields = [field for field in required_fields if not email_config.get(field) or email_config.get(field).startswith('your_')]
        
        if missing_fields:
            print(f"⚠️ Missing email configuration: {', '.join(missing_fields)}")
            print(f"   Please edit {ENV_FILE} with your email details")
            print("   Email notifications will be disabled")
            return False
        
        email_configured = True
        print("✅ Email configuration loaded")
        print(f"   From: {email_config['SENDER_EMAIL']}")
        print(f"   To: {email_config['RECIPIENT_EMAIL']}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading email config: {e}")
        traceback.print_exc()
        return False

# ========================
# Force Release GPIO if Busy
# ========================
def force_release_gpio():
    """Force release GPIO pins if they're busy"""
    try:
        import lgpio
        import subprocess
        
        print("🔧 Attempting to force release GPIO pins...")
        
        # First, try to kill any other instances of this script
        try:
            current_pid = os.getpid()
            result = subprocess.run(
                ['pgrep', '-f', 'smart_alert.py'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid.strip() and pid.strip() != str(current_pid):
                        print(f"   ⚠️ Found existing smart_alert.py process (PID {pid}), terminating...")
                        try:
                            subprocess.run(['kill', pid.strip()], timeout=2)
                            time.sleep(1)
                            print(f"   ✓ Terminated PID {pid}")
                        except:
                            print(f"   ⚠️ Could not terminate PID {pid}")
        except Exception as e:
            print(f"   ⚠️ Could not check for existing processes: {e}")
        
        # Try to get the chip handle and free pins
        try:
            h = lgpio.gpiochip_open(0)
            
            # Try to free the specific pins
            for pin in [PIR_PIN, LED_PIN]:
                try:
                    lgpio.gpio_free(h, pin)
                    print(f"   ✓ Released GPIO {pin}")
                except Exception as e:
                    if "not allocated" not in str(e).lower():
                        print(f"   ℹ️ GPIO {pin}: {e}")
            
            lgpio.gpiochip_close(h)
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"   ⚠️ Could not open gpiochip: {e}")
            
    except ImportError:
        print("   ⚠️ lgpio module not available for direct pin release")
    except Exception as e:
        print(f"   ⚠️ Error during force release: {e}")
    
    return False

# ========================
# GPIO Setup with Error Handling
# ========================
def setup_gpio():
    """Initialize GPIO pins with error handling and retry logic"""
    global gpio_initialized
    
    MAX_RETRIES = 5
    
    # Try to force release GPIO on first attempt
    force_release_gpio()
    
    for attempt in range(MAX_RETRIES):
        try:
            # Clean up any existing GPIO setup
            try:
                GPIO.cleanup()
            except:
                pass
            
            # Small delay between retries
            if attempt > 0:
                time.sleep(1)
            
            # Set up GPIO mode and pins
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # PIR with pull-down
            GPIO.setup(LED_PIN, GPIO.OUT)
            GPIO.output(LED_PIN, GPIO.LOW)  # Ensure LED is off initially
            
            gpio_initialized = True
            print("✅ GPIO initialized successfully")
            print(f"   PIR Sensor: GPIO {PIR_PIN}")
            print(f"   LED: GPIO {LED_PIN}")
            return True
            
        except Exception as e:
            print(f"⚠️ GPIO setup attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            
            # If it's a "GPIO busy" error, try to identify which pin is busy
            if "busy" in str(e).lower():
                print(f"   Checking GPIO status...")
                try:
                    import subprocess
                    result = subprocess.run(
                        ['gpioinfo', 'gpiochip0'], 
                        capture_output=True, 
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if f'line  {PIR_PIN}:' in line or f'line {PIR_PIN}:' in line:
                                print(f"   PIR Pin (GPIO {PIR_PIN}): {line.strip()}")
                            if f'line  {LED_PIN}:' in line or f'line {LED_PIN}:' in line:
                                print(f"   LED Pin (GPIO {LED_PIN}): {line.strip()}")
                except Exception as check_error:
                    print(f"   Could not check GPIO status: {check_error}")
            
            if attempt == MAX_RETRIES - 1:
                print(f"❌ Failed to initialize GPIO after {MAX_RETRIES} attempts")
                traceback.print_exc()
                return False
    
    return False

# ========================
# Camera Setup with Error Handling
# ========================
def setup_camera():
    """Initialize camera with error handling"""
    global picam2, camera_initialized
    
    try:
        from picamera2 import Picamera2
        
        picam2 = Picamera2()
        config = picam2.create_still_configuration(
            main={"size": (1920, 1080)},
            display="main"
        )
        picam2.configure(config)
        picam2.start()
        
        # Small delay to let camera stabilize
        time.sleep(2)
        
        camera_initialized = True
        print("✅ Camera initialized successfully")
        return True
        
    except ImportError:
        print("❌ Error: picamera2 module not found. Install with: pip install picamera2")
        return False
    except Exception as e:
        print(f"❌ Error setting up camera: {e}")
        traceback.print_exc()
        return False

# ========================
# Image Capture with Error Handling
# ========================
def capture_image():
    """Capture an image and save it with timestamp"""
    try:
        if not camera_initialized or picam2 is None:
            print("⚠️ Camera not initialized, skipping capture")
            return None
        
        # Create save directory if it doesn't exist
        os.makedirs(SAVE_DIR, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"motion_{timestamp}.jpg"
        filepath = os.path.join(SAVE_DIR, filename)
        
        # Capture image
        picam2.capture_file(filepath)
        print(f"📷 Image captured: {filename}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error capturing image: {e}")
        traceback.print_exc()
        return None

# ========================
# Email Sending with Error Handling
# ========================
def send_email_alert(image_path):
    """Send email with captured image"""
    try:
        if not email_configured:
            print("⚠️ Email not configured, skipping email send")
            return False
        
        if not image_path or not os.path.exists(image_path):
            print("⚠️ Image file not found, cannot send email")
            return False
        
        print("📧 Sending email alert...")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_config['SENDER_EMAIL']
        msg['To'] = email_config['RECIPIENT_EMAIL']
        msg['Subject'] = email_config.get('EMAIL_SUBJECT', '🚨 Motion Detected Alert')
        
        # Email body
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"""
Motion Detected!

Time: {timestamp}
Location: Smart Alert System
Image: {os.path.basename(image_path)}

This is an automated alert from your motion detection system.
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach image
        with open(image_path, 'rb') as f:
            img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(image_path))
            msg.attach(image)
        
        # Send email via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_config['SENDER_EMAIL'], email_config['EMAIL_PASSWORD'])
            server.send_message(msg)
        
        print(f"✅ Email sent to {email_config['RECIPIENT_EMAIL']}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Email authentication failed!")
        print("   Please check your email and app password in .env file")
        print("   Note: Use Google App Password, not your regular password")
        return False
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        traceback.print_exc()
        return False

# ========================
# LED Control
# ========================
def led_on():
    """Turn LED on with error handling"""
    try:
        if gpio_initialized:
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("💡 LED ON")
    except Exception as e:
        print(f"❌ Error turning LED on: {e}")

def led_off():
    """Turn LED off with error handling"""
    try:
        if gpio_initialized:
            GPIO.output(LED_PIN, GPIO.LOW)
            print("🌑 LED OFF")
    except Exception as e:
        print(f"❌ Error turning LED off: {e}")

# ========================
# Cleanup Function
# ========================
def cleanup():
    """Clean up all resources"""
    print("\n🛑 Shutting down...")
    
    # Turn off LED
    try:
        if gpio_initialized:
            GPIO.output(LED_PIN, GPIO.LOW)
    except:
        pass
    
    # Stop camera
    try:
        if camera_initialized and picam2 is not None:
            picam2.stop()
            print("✅ Camera stopped")
    except Exception as e:
        print(f"⚠️ Error stopping camera: {e}")
    
    # Clean up GPIO
    try:
        if gpio_initialized:
            GPIO.cleanup()
            print("✅ GPIO cleaned up")
    except Exception as e:
        print(f"⚠️ Error cleaning up GPIO: {e}")

# ========================
# Signal Handlers
# ========================
def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    print("\n⚠️ Received interrupt signal")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ========================
# Main Function
# ========================
def main():
    """Main program loop"""
    print("=" * 50)
    print("🚀 Smart Motion Detection System")
    print("=" * 50)
    print(f"📂 Project Directory: {PROJECT_DIR}")
    
    # Initialize GPIO
    if not setup_gpio():
        print("❌ Failed to initialize GPIO. Exiting.")
        return 1
    
    # Initialize Camera
    if not setup_camera():
        print("⚠️ Camera initialization failed. Running without camera.")
    
    # Load Email Configuration
    load_email_config()
    
    # Ensure save directory exists
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        print(f"📁 Images will be saved to: {SAVE_DIR}")
    except Exception as e:
        print(f"❌ Error creating save directory: {e}")
        cleanup()
        return 1
    
    print("\n✅ System ready! Monitoring for motion...")
    if email_configured:
        print("   📧 Email alerts: ENABLED")
    else:
        print("   📧 Email alerts: DISABLED")
    print("   Press CTRL+C to exit\n")
    
    # Main monitoring loop
    motion_detected_time = 0
    
    try:
        while True:
            try:
                # Check for motion
                if GPIO.input(PIR_PIN):
                    current_time = time.time()
                    
                    # Only trigger if cooldown period has passed
                    if current_time - motion_detected_time > COOLDOWN_TIME:
                        print("\n" + "="*50)
                        print(f"👁️  MOTION DETECTED! [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
                        print("="*50)
                        
                        # Turn LED on
                        led_on()
                        
                        # Capture image
                        filepath = capture_image()
                        if filepath:
                            print(f"✅ Saved to: {filepath}")
                            
                            # Send email with image
                            if email_configured:
                                send_email_alert(filepath)
                        
                        # Keep LED on for specified time
                        print(f"⏳ LED will stay on for {LED_ON_TIME} seconds...")
                        time.sleep(LED_ON_TIME)
                        
                        # Turn LED off
                        led_off()
                        
                        # Update last detection time
                        motion_detected_time = current_time
                        
                        print(f"✅ Ready for next detection\n")
                
                # Small delay to avoid excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                traceback.print_exc()
                time.sleep(1)  # Wait a bit before retrying
                
    except KeyboardInterrupt:
        pass  # Handled by signal handler
    
    return 0

# ========================
# Entry Point
# ========================
if __name__ == "__main__":
    try:
        exit_code = main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        exit_code = 1
    finally:
        cleanup()
        print("\n👋 System stopped")
        sys.exit(exit_code)
