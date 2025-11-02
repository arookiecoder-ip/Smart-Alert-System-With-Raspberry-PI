import RPi.GPIO as GPIO
import time
import sys

# Pin Configuration
LED_PIN = 18  # GPIO 18 (Physical pin 12)

# Setup
try:
    GPIO.cleanup()
except:
    pass

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    print("LED control initialized on GPIO 18")
except Exception as e:
    print(f"Error setting up GPIO: {e}")
    sys.exit(1)

# ========================
# Main Loop - Blink LED every 2 seconds
# ========================
print("LED will blink every 2 seconds. Press CTRL+C to exit.")

try:
    while True:
        # Turn LED ON
        GPIO.output(LED_PIN, GPIO.HIGH)
        print("💡 LED ON")
        time.sleep(2)
        
        # Turn LED OFF
        GPIO.output(LED_PIN, GPIO.LOW)
        print("🌑 LED OFF")
        time.sleep(2)

except KeyboardInterrupt:
    print("\n\nExiting...")

finally:
    GPIO.output(LED_PIN, GPIO.LOW)  # Ensure LED is off
    GPIO.cleanup()
    print("GPIO cleaned up. LED control finished.")
