# Smart Alert System 🚨

A comprehensive motion detection system for Raspberry Pi that captures images and sends email alerts when motion is detected.

## 📋 Features

- **Motion Detection**: Uses PIR sensor to detect movement
- **Image Capture**: Takes high-quality photos with Raspberry Pi camera
- **LED Alert**: Visual indicator when motion is detected
- **Email Notifications**: Sends captured images via email
- **Error Handling**: Robust error recovery and GPIO management
- **Auto-Recovery**: Handles GPIO busy errors automatically

## 🗂️ Project Structure

```
smart_alert_system/
├── smart_alert.py              # Main application
├── start.sh                    # Quick start script
├── install_startup.sh          # Install auto-start service
├── uninstall_startup.sh        # Remove auto-start service
├── smart-alert.service         # Systemd service file
├── config/
│   └── .env                   # Email configuration (private)
├── captured_images/           # Stored motion detection images
├── tests/
│   ├── test_pir_sensor.py    # PIR sensor testing
│   ├── test_led.py           # LED testing
│   ├── test_email.py         # Email configuration testing
│   └── release_gpio.py       # GPIO cleanup utility
├── docs/
│   ├── README.md             # Main documentation
│   ├── AUTOSTART.md          # Auto-start setup guide
│   └── EMAIL_SETUP.md        # Email configuration guide
└── README.md                  # Quick reference
```

## 🔧 Hardware Requirements

### Components:
1. **Raspberry Pi** (any model with GPIO)
2. **PIR Motion Sensor** (HC-SR501 or similar)
3. **LED** with 220Ω resistor
4. **Raspberry Pi Camera Module** (v1, v2, or HQ)
5. **Jumper wires**
6. **Breadboard** (optional)

### Connections:

#### PIR Sensor:
- VCC → Pin 2 or 4 (5V)
- OUT → Pin 11 (GPIO 17)
- GND → Pin 6 (GND)

#### LED:
- Long leg (+) → 220Ω Resistor → Pin 12 (GPIO 18)
- Short leg (-) → Pin 6 (GND)

#### Camera:
- Connect to Camera Serial Interface (CSI) port

## 📦 Software Requirements

```bash
# System packages
sudo apt-get update
sudo apt-get install python3-pip python3-rpi.gpio

# Python packages
pip3 install picamera2 python-dotenv

# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

## ⚙️ Installation & Setup

### 1. Navigate to Project Directory
```bash
cd ~/smart_alert_system
```

### 2. Configure Email Settings
Edit the configuration file:
```bash
nano config/.env
```

Add your email credentials:
```env
SENDER_EMAIL=youremail@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=recipient@gmail.com
EMAIL_SUBJECT=🚨 Motion Detected Alert
```

**Important**: Use Google App Password, not your regular Gmail password!
- Generate at: https://myaccount.google.com/apppasswords
- Enable 2-Step Verification first

### 3. Test Components

Test PIR Sensor:
```bash
python3 tests/test_pir_sensor.py
```

Test LED:
```bash
python3 tests/test_led.py
```

Test Email:
```bash
python3 tests/test_email.py
```

## 🚀 Usage

### Option 1: Auto-Start on Boot (Recommended)

Install as a system service to run automatically at startup:

```bash
cd ~/smart_alert_system
./install_startup.sh
```

**Benefits:**
- ✅ Starts automatically when Raspberry Pi boots
- ✅ Auto-restarts if it crashes
- ✅ Runs in background as a service
- ✅ Easy log management with systemd

**Manage the service:**
```bash
sudo systemctl status smart-alert   # Check status
sudo systemctl stop smart-alert     # Stop service
sudo systemctl start smart-alert    # Start service
sudo systemctl restart smart-alert  # Restart service
sudo journalctl -u smart-alert -f   # View live logs
```

**Remove from auto-start:**
```bash
./uninstall_startup.sh
```

See [AUTOSTART.md](AUTOSTART.md) for detailed instructions.

---

### Option 2: Manual Start

Start the system manually:
```bash
cd ~/smart_alert_system
python3 smart_alert.py
```

Or use the helper script:
```bash
./start.sh
```

### Run in Background (Manual):
```bash
nohup python3 smart_alert.py > smart_alert.log 2>&1 &
```

### Stop Background Process:
```bash
pkill -f smart_alert.py
```

### View Logs:
```bash
tail -f smart_alert.log
```

## 📧 Email Setup Guide

### Generate Google App Password:

1. Go to Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if needed)
3. Scroll to **App passwords**: https://myaccount.google.com/apppasswords
4. Select: **Mail** and **Other (Custom name)**
5. Enter: "Smart Alert System"
6. Click **Generate**
7. Copy the 16-character password
8. Update `config/.env` file

### Email Features:
- Subject line with motion alert
- Timestamp of detection
- Attached JPEG image
- System location identifier

## 🔍 Troubleshooting

### GPIO Busy Error:
The system automatically handles GPIO busy errors. If issues persist:
```bash
# Kill any existing instances
pkill -f smart_alert.py

# Check GPIO status
gpioinfo gpiochip0 | grep -E "line  (17|18):"
```

### Camera Not Working:
```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable → Reboot

# Test camera
libcamera-still -o test.jpg
```

### Email Not Sending:
- Verify app password (not regular password)
- Check 2-Step Verification is enabled
- Ensure correct email addresses
- Check spam folder
- Test with: `python3 tests/test_email.py`

### No Motion Detection:
- Check PIR sensor connections
- Verify GPIO 17 is used
- Test sensor with: `python3 tests/test_pir_sensor.py`
- Adjust PIR sensitivity (potentiometer on sensor)

### LED Not Working:
- Verify LED polarity (long leg = positive)
- Check resistor is connected
- Test with: `python3 tests/test_led.py`

## 📝 Configuration Options

Edit `smart_alert.py` to customize:

```python
PIR_PIN = 17          # PIR sensor GPIO pin
LED_PIN = 18          # LED GPIO pin
LED_ON_TIME = 10      # LED duration (seconds)
COOLDOWN_TIME = 2     # Cooldown between detections
```

Image settings (in `setup_camera()`):
```python
main={"size": (1920, 1080)}  # Image resolution
```

## 🔒 Security Notes

- Keep `config/.env` file private (contains passwords)
- Never commit `.env` to version control
- Use dedicated Gmail account for IoT projects
- Revoke app passwords when no longer needed
- Regularly review sent emails

## 📊 System Information

### When Motion is Detected:
1. PIR sensor triggers
2. LED turns ON
3. Camera captures image
4. Image saved to `captured_images/`
5. Email sent with attachment
6. LED stays on for 10 seconds
7. LED turns OFF
8. System ready for next detection

### File Naming:
Images are saved as: `motion_YYYYMMDD_HHMMSS.jpg`

Example: `motion_20251102_143022.jpg`

## 🛠️ Advanced Usage

### Run on Boot (systemd):
Create service file:
```bash
sudo nano /etc/systemd/system/smart-alert.service
```

Add:
```ini
[Unit]
Description=Smart Alert Motion Detection System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/jkarm/smart_alert_system
ExecStart=/usr/bin/python3 /home/jkarm/smart_alert_system/smart_alert.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smart-alert.service
sudo systemctl start smart-alert.service
sudo systemctl status smart-alert.service
```

### View Service Logs:
```bash
sudo journalctl -u smart-alert.service -f
```

## 📈 Future Enhancements

Potential improvements:
- Cloud storage integration (Google Drive, Dropbox)
- Web interface for viewing images
- Mobile app notifications (Pushbullet, Telegram)
- Multiple PIR sensor support
- Video recording capability
- Motion analytics and statistics
- Integration with home automation systems

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is open source and available for personal and educational use.

## 👤 Author

Smart Alert System
Version 1.0
Created: November 2025

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Test individual components using test scripts
3. Review system logs
4. Check GPIO and camera status

---

**Happy Monitoring! 🎥👁️**
