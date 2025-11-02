import RPi.GPIO as GPIO
import time
import sys

PIR_PIN = 17  
MAX_RETRIES = 10

try:
    GPIO.cleanup()
except:
    pass

for attempt in range(MAX_RETRIES):
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
        break
    except Exception as e:
        print(f"GPIO busy, retrying ({attempt+1}/{MAX_RETRIES})... Error: {e}")
        GPIO.cleanup()
        time.sleep(1)
else:
    print("GPIO still busy after retries. Exiting.")
    sys.exit(1)

print("Starting PIR sensor test. Press CTRL+C to exit.")

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("Motion detected! ✅")
        else:
            print("No motion detected")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nExiting test...")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up. Test finished.")
