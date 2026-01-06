# CyberBrick V7RC Controller

MicroPython firmware for ESP32-C3 Super Mini to control robots via V7RC Mobile App.

## 📱 Features

- **4 Servo Channels** - Control 0-180° angle servos or continuous rotation servos
- **2 DC Motors** - Speed and direction control with H-Bridge driver
- **NeoPixel LEDs** - RGB LED effects (breathing, blink, solid)
- **Buzzer/Music** - Play RTTTL music and sounds
- **Wi-Fi AP** - Direct connection via Wi-Fi Access Point
- **UDP Server** - Receive control commands from V7RC App

## 🚀 Quick Start

### 1. Flash MicroPython Firmware

```powershell
# Erase flash
python -m esptool --chip esp32c3 --port COM28 erase_flash

# Flash MicroPython v1.27.0 firmware
python -m esptool --chip esp32c3 --port COM28 --baud 460800 write_flash -z 0x0 "path\to\ESP32_GENERIC_C3-20251209-v1.27.0.bin"
```

### 2. Upload Code

```powershell
# Use upload script
.\upload.ps1
```

### 3. Connect with V7RC App

1. Download V7RC App: [iOS](https://apps.apple.com/tw/app/v7rc/id1390983964) | [Android](https://play.google.com/store/apps/details?id=com.v7idea.v7rcliteandroidsdkversion)
2. Connect to Wi-Fi: **cyber_V7RC** (password: **12341234**)
3. Open V7RC App and start controlling!

## 📚 Documentation

- **[HARDWARE_GUIDE_EN.md](HARDWARE_GUIDE_EN.md)** - Detailed hardware connection guide
  - GPIO pin diagram
  - Servo, Motor, LED, Buzzer connections
  - Power supply requirements
  - Complete connection examples
  - Troubleshooting

- **[HARDWARE_GUIDE_VI.md](HARDWARE_GUIDE_VI.md)** - Vietnamese hardware guide
- **[README_VI.md](README_VI.md)** - Vietnamese documentation
- **[README.md](README.md)** - Original project documentation

## 📁 Project Structure

```
cyberbrick-v7rc/
├── app/                    # Main application
│   ├── main.py            # Entry point
│   ├── control.mpy        # Control logic
│   └── parser.mpy         # Command parser
├── bbl/                    # CyberBrick library
│   ├── __init__.py        # Package init
│   ├── servos.py          # Servo controller
│   ├── motors.py          # DC motor controller
│   ├── leds.py            # NeoPixel LED controller
│   ├── buzzer.py          # Buzzer/music controller
│   ├── executor.py        # Command executor
│   ├── dgram.py           # UDP server
│   ├── neopixel.py        # NeoPixel driver
│   └── v7rc.py            # V7RC protocol
├── boot.py                # Boot script
├── bbl_product.py         # Product info module
├── upload.ps1             # 🔧 Upload script (optimized)
├── HARDWARE_GUIDE_EN.md   # 📖 English hardware guide
├── HARDWARE_GUIDE_VI.md   # 📖 Vietnamese hardware guide
├── README_EN.md           # 📖 This document
└── README_VI.md           # 📖 Vietnamese documentation
```

## 🔌 GPIO Pin Summary

| GPIO | Function | Device |
|------|----------|--------|
| 0-3 | Servo 4-1 | SG90, MG90S, etc. |
| 4-7 | Motor 1-2 | L298N, TB6612, DRV8833 |
| 20-21 | LED/Buzzer | WS2812B, Passive Buzzer |

## 💡 Code Examples

### Servo Control

```python
from bbl import ServosController

servos = ServosController()
servos.set_angle(1, 90)  # Servo 1 to 90°
servos.set_angle_stepping(2, 180, 50)  # Servo 2 smooth motion
```

### Motor Control

```python
from bbl import MotorsController

motors = MotorsController()
motors.set_speed(1, 1500)  # Motor 1 forward
motors.set_speed(2, -1000)  # Motor 2 reverse
```

### LED Control

```python
from bbl import LEDController

led = LEDController('LED1')
led.set_led_effect(1, 500, 255, 0b1111, 0xFF0000)  # Blinking red
```

### Play Music

```python
from bbl import MusicController

music = MusicController('BUZZER1', volume=50)
music.play("Mario:d=4,o=5,b=100:16e6,16e6,32p,8e6")
```

## 🛠️ Helper Scripts

### Upload Code

```powershell
# Use mpremote (fast)
.\upload.ps1
```

### Monitor Serial

```powershell
# Use mpremote
mpremote connect COM28

# Or miniterm
python -m serial.tools.miniterm COM28 115200
```

## ⚙️ Configuration

### Change Wi-Fi SSID/Password

Edit `app/main.py`:

```python
start = v7rc.init_ap(
    essid='YourWiFiName',      # Change Wi-Fi name
    password='YourPassword',   # Change password (min 8 chars)
    udp_ip='192.168.4.1',
    udp_port=6188,
    use_default_led=True
)
```

### Change Product Information

Edit `boot.py`:

```python
_PRODUCT_NAME = "RC"
_PRODUCT_VERSION = "01.00.00.13"
```

## 🔧 Troubleshooting

### Cannot Upload Code

```powershell
# Kill all Python processes holding the port
Get-Process -Name python* | Stop-Process -Force

# Wait 2 seconds and retry
Start-Sleep -Seconds 2
.\upload.ps1
```

### ESP32 Keeps Resetting

- Check stable power supply
- DO NOT power servos from ESP32
- Add 100µF capacitor near 5V pin

### Servo/Motor Not Working

- See details in [HARDWARE_GUIDE_EN.md](HARDWARE_GUIDE_EN.md)

## 📦 Requirements

### Hardware

- ESP32-C3 Super Mini
- SG90 Servos (optional, max 4)
- DC Motors + L298N/TB6612 Driver (optional, max 2)
- WS2812B NeoPixel LEDs (optional)
- Passive Buzzer (optional)
- 5V/2A-3A Power Supply

### Software

- Python 3.7+
- esptool: `pip install esptool`
- mpremote: `pip install mpremote`
- MicroPython v1.27.0 for ESP32-C3

## 📄 License

CyberBrick Codebase License - See [LICENSE.txt](LICENSE.txt)

## 🙏 Credits

- **V7RC App** by Ameba (嵐奕科技有限公司)
- **CyberBrick Platform** by CyberBrick Team
- **MicroPython** by Damien George and contributors

## 🔗 Links

- [V7RC iOS App](https://apps.apple.com/tw/app/v7rc/id1390983964)
- [V7RC Android App](https://play.google.com/store/apps/details?id=com.v7idea.v7rcliteandroidsdkversion)
- [CyberBrick API Documentation](https://makerworld.com/en/cyberbrick/api-doc)
- [MicroPython Documentation](https://docs.micropython.org/)

---

**Version**: 1.1  
**Last Updated**: 2025-12-30  
**Author**: CyberBrick V7RC Community
