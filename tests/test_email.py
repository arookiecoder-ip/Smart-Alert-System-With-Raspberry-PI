#!/usr/bin/env python3
"""
Email Configuration Test
Tests if email is properly configured and can send test messages
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Get the project directory
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(PROJECT_DIR, "config", ".env")

def load_email_config():
    """Load email configuration from .env file"""
    email_config = {}
    
    if not os.path.exists(ENV_FILE):
        print(f"❌ .env file not found at: {ENV_FILE}")
        return None
    
    with open(ENV_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                email_config[key.strip()] = value.strip()
    
    # Validate
    required = ['SENDER_EMAIL', 'EMAIL_PASSWORD', 'RECIPIENT_EMAIL']
    missing = [f for f in required if not email_config.get(f) or email_config.get(f).startswith('your_')]
    
    if missing:
        print(f"❌ Missing configuration: {', '.join(missing)}")
        print(f"\nPlease edit {ENV_FILE} with your email details")
        return None
    
    return email_config

def send_test_email(config):
    """Send a test email"""
    try:
        print("\n📧 Sending test email...")
        
        msg = MIMEMultipart()
        msg['From'] = config['SENDER_EMAIL']
        msg['To'] = config['RECIPIENT_EMAIL']
        msg['Subject'] = '✅ Smart Alert System - Email Test'
        
        body = f"""
This is a test email from your Smart Alert System.

Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
From: {config['SENDER_EMAIL']}
To: {config['RECIPIENT_EMAIL']}

If you received this email, your configuration is working correctly! ✅

Your motion detection system is ready to send alerts.

---
Smart Alert System
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Send via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(config['SENDER_EMAIL'], config['EMAIL_PASSWORD'])
            server.send_message(msg)
        
        print(f"✅ Test email sent successfully!")
        print(f"   From: {config['SENDER_EMAIL']}")
        print(f"   To: {config['RECIPIENT_EMAIL']}")
        print(f"\n📬 Check your inbox (and spam folder)")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed!")
        print("\nPossible issues:")
        print("  • Using regular Gmail password instead of App Password")
        print("  • App password is incorrect")
        print("  • 2-Step Verification not enabled")
        print("\n💡 Solution:")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Generate a new App Password")
        print("  3. Update EMAIL_PASSWORD in .env file")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 50)
    print("📧 Email Configuration Test")
    print("=" * 50)
    print(f"📂 Config file: {ENV_FILE}\n")
    
    config = load_email_config()
    if not config:
        return 1
    
    print("✅ Configuration loaded:")
    print(f"   Sender: {config['SENDER_EMAIL']}")
    print(f"   Recipient: {config['RECIPIENT_EMAIL']}")
    print(f"   Password: {'*' * len(config['EMAIL_PASSWORD'])} (hidden)")
    
    if send_test_email(config):
        print("\n🎉 Email system is working correctly!")
        return 0
    else:
        print("\n❌ Email test failed. Please check configuration.")
        return 1

if __name__ == "__main__":
    exit(main())
