# 🚀 Auto-Start Configuration

## Quick Setup (Recommended)

Run the automated installation script:

```bash
cd ~/smart_alert_system
./install_startup.sh
```

This will:
- ✅ Install the systemd service
- ✅ Enable auto-start on boot
- ✅ Start the service immediately
- ✅ Configure automatic restart on failure

## Manual Setup

If you prefer to set it up manually:

### 1. Copy Service File
```bash
sudo cp ~/smart_alert_system/smart-alert.service /etc/systemd/system/
```

### 2. Reload Systemd
```bash
sudo systemctl daemon-reload
```

### 3. Enable Auto-Start
```bash
sudo systemctl enable smart-alert.service
```

### 4. Start the Service
```bash
sudo systemctl start smart-alert.service
```

## Service Management Commands

### Check Status
```bash
sudo systemctl status smart-alert
```

### View Live Logs
```bash
sudo journalctl -u smart-alert -f
```

### View Recent Logs
```bash
sudo journalctl -u smart-alert -n 50
```

### Stop Service
```bash
sudo systemctl stop smart-alert
```

### Start Service
```bash
sudo systemctl start smart-alert
```

### Restart Service
```bash
sudo systemctl restart smart-alert
```

### Disable Auto-Start
```bash
sudo systemctl disable smart-alert
```

## Uninstall from Startup

To remove from auto-start:

```bash
cd ~/smart_alert_system
./uninstall_startup.sh
```

Or manually:
```bash
sudo systemctl stop smart-alert
sudo systemctl disable smart-alert
sudo rm /etc/systemd/system/smart-alert.service
sudo systemctl daemon-reload
```

## Troubleshooting

### Service Won't Start
1. Check logs:
   ```bash
   sudo journalctl -u smart-alert -n 50
   ```

2. Verify file permissions:
   ```bash
   ls -la ~/smart_alert_system/smart_alert.py
   ```

3. Test manually:
   ```bash
   cd ~/smart_alert_system
   ./start.sh
   ```

### Service Starts But Stops Immediately
- Check GPIO permissions
- Verify camera is connected
- Check .env file configuration
- Review logs for errors

### Email Not Working
- Ensure .env file is properly configured
- Test with: `python3 tests/test_email.py`
- Check internet connection

### Multiple Instances Running
Stop the service before manual testing:
```bash
sudo systemctl stop smart-alert
```

## What Happens at Boot?

1. **Raspberry Pi powers on**
2. System boots up
3. Network starts (if configured)
4. Systemd launches smart-alert service
5. Service initializes GPIO and camera
6. **Motion detection begins automatically**
7. If service crashes, it auto-restarts after 10 seconds

## Service Configuration

The service file is configured with:
- **Auto-restart**: On failure (10 second delay)
- **User**: jkarm (your user)
- **Working Directory**: /home/jkarm/smart_alert_system
- **Python**: /usr/bin/python3
- **Logging**: systemd journal

## Viewing Captured Images

Images are saved to:
```
~/smart_alert_system/captured_images/
```

Access them:
```bash
ls -lh ~/smart_alert_system/captured_images/
```

View latest image:
```bash
ls -lt ~/smart_alert_system/captured_images/ | head -n 2
```

## Performance Tips

- Service uses minimal resources when idle
- Camera stays initialized (faster capture)
- GPIO monitoring is efficient (0.1s polling)
- Auto-cleanup on crash or shutdown
- 10-second LED duration prevents constant triggering

---

**Ready to install?** Run: `./install_startup.sh`

**Need help?** Check logs: `sudo journalctl -u smart-alert -f`
