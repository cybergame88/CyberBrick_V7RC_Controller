# CyberBrick V7RC Controller

Firmware MicroPython cho ESP32-C3 Super Mini để điều khiển robot qua V7RC Mobile App.

## 📱 Tính Năng

- **4 kênh Servo** - Điều khiển servo góc 0-180° hoặc servo quay liên tục
- **2 động cơ DC** - Điều khiển tốc độ và hướng với H-Bridge driver
- **LED NeoPixel** - Hiệu ứng LED RGB (breathing, blink, solid)
- **Buzzer/Music** - Phát nhạc RTTTL và âm thanh
- **Wi-Fi AP** - Kết nối trực tiếp qua Wi-Fi Access Point
- **UDP Server** - Nhận lệnh điều khiển từ V7RC App

## 🚀 Bắt Đầu Nhanh

### 1. Nạp Firmware MicroPython

```powershell
# Xóa flash
python -m esptool --chip esp32c3 --port COM28 erase_flash

# Nạp firmware MicroPython v1.27.0
python -m esptool --chip esp32c3 --port COM28 --baud 460800 write_flash -z 0x0 "path\to\ESP32_GENERIC_C3-20251209-v1.27.0.bin"
```

### 2. Upload Code

```powershell
# Sử dụng script upload
.\upload.ps1
```

### 3. Kết Nối với V7RC App

1. Tải V7RC App: [iOS](https://apps.apple.com/tw/app/v7rc/id1390983964) | [Android](https://play.google.com/store/apps/details?id=com.v7idea.v7rcliteandroidsdkversion)
2. Kết nối Wi-Fi: **cyber_V7RC** (mật khẩu: **12341234**)
3. Mở V7RC App và bắt đầu điều khiển!

## 📚 Tài Liệu

- **[HARDWARE_GUIDE.md](HARDWARE_GUIDE.md)** - Hướng dẫn kết nối phần cứng chi tiết
  - Sơ đồ chân GPIO
  - Kết nối Servo, Motor, LED, Buzzer
  - Yêu cầu nguồn điện
  - Ví dụ kết nối hoàn chỉnh
  - Khắc phục sự cố

- **[README.md](README.md)** - Tài liệu gốc của dự án

## 📁 Cấu Trúc Thư Mục

```
cyberbrick-v7rc/
├── app/                    # Ứng dụng chính
│   ├── main.py            # Entry point
│   ├── control.mpy        # Logic điều khiển
│   └── parser.mpy         # Parser lệnh
├── bbl/                    # Thư viện CyberBrick
│   ├── __init__.py        # Package init
│   ├── servos.py          # Điều khiển servo
│   ├── motors.py          # Điều khiển motor DC
│   ├── leds.py            # Điều khiển LED NeoPixel
│   ├── buzzer.py          # Điều khiển buzzer/music
│   ├── executor.py        # Command executor
│   ├── dgram.py           # UDP server
│   ├── neopixel.py        # NeoPixel driver
│   └── v7rc.py            # V7RC protocol
├── boot.py                # Boot script
├── bbl_product.py         # Product info module
├── upload_mpremote.ps1    # Upload script (mpremote)
├── upload.ps1             # Upload script (ampy)
├── kill_and_upload.ps1    # Helper script
├── HARDWARE_GUIDE.md      # 📖 Hướng dẫn kết nối phần cứng
└── README_VI.md           # 📖 Tài liệu này
```

## 🔌 Sơ Đồ Chân GPIO Tóm Tắt

| GPIO | Chức Năng | Thiết Bị |
|------|-----------|----------|
| 0-3 | Servo 4-1 | SG90, MG90S, etc. |
| 4-7 | Motor 1-2 | L298N, TB6612, DRV8833 |
| 20-21 | LED/Buzzer | WS2812B, Passive Buzzer |

## 💡 Ví Dụ Code

### Điều Khiển Servo

```python
from bbl import ServosController

servos = ServosController()
servos.set_angle(1, 90)  # Servo 1 đến 90°
servos.set_angle_stepping(2, 180, 50)  # Servo 2 chuyển động mượt
```

### Điều Khiển Motor

```python
from bbl import MotorsController

motors = MotorsController()
motors.set_speed(1, 1500)  # Motor 1 tiến
motors.set_speed(2, -1000)  # Motor 2 lùi
```

### Điều Khiển LED

```python
from bbl import LEDController

led = LEDController('LED1')
led.set_led_effect(1, 500, 255, 0b1111, 0xFF0000)  # Nhấp nháy đỏ
```

### Phát Nhạc

```python
from bbl import MusicController

music = MusicController('BUZZER1', volume=50)
music.play("Mario:d=4,o=5,b=100:16e6,16e6,32p,8e6")
```

## 🛠️ Scripts Hỗ Trợ

### Upload Code

```powershell
# Sử dụng mpremote (nhanh)
.\upload.ps1
```

### Monitor Serial

```powershell
# Sử dụng mpremote
mpremote connect COM28

# Hoặc miniterm
python -m serial.tools.miniterm COM28 115200
```

## ⚙️ Cấu Hình

### Thay Đổi Wi-Fi SSID/Password

Chỉnh sửa `app/main.py`:

```python
start = v7rc.init_ap(
    essid='TenWiFiCuaBan',      # Đổi tên Wi-Fi
    password='MatKhauCuaBan',   # Đổi mật khẩu (tối thiểu 8 ký tự)
    udp_ip='192.168.4.1',
    udp_port=6188,
    use_default_led=True
)
```

### Thay Đổi Thông Tin Sản Phẩm

Chỉnh sửa `boot.py`:

```python
_PRODUCT_NAME = "RC"
_PRODUCT_VERSION = "01.00.00.13"
```

## 🔧 Khắc Phục Sự Cố

### Không Upload Được Code

```powershell
# Kill tất cả process Python đang giữ port
Get-Process -Name python* | Stop-Process -Force

# Đợi 2 giây và thử lại
Start-Sleep -Seconds 2
.\upload_mpremote.ps1
```

### ESP32 Reset Liên Tục

- Kiểm tra nguồn điện ổn định
- KHÔNG cấp nguồn servo từ ESP32
- Thêm tụ 100µF gần chân 5V

### Servo/Motor Không Hoạt Động

- Xem chi tiết trong [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md)

## 📦 Yêu Cầu

### Phần Cứng

- ESP32-C3 Super Mini
- Servo SG90 (tùy chọn, tối đa 4 cái)
- Motor DC + Driver L298N/TB6612 (tùy chọn, tối đa 2 motor)
- LED NeoPixel WS2812B (tùy chọn)
- Passive Buzzer (tùy chọn)
- Nguồn 5V/2A-3A

### Phần Mềm

- Python 3.7+
- esptool: `pip install esptool`
- mpremote: `pip install mpremote`
- MicroPython v1.27.0 cho ESP32-C3

## 📄 License

CyberBrick Codebase License - Xem [LICENSE.txt](LICENSE.txt)

## 🙏 Credits

- **V7RC App** by Ameba (嵐奕科技有限公司)
- **CyberBrick Platform** by CyberBrick Team
- **MicroPython** by Damien George and contributors

## 🔗 Liên Kết

- [V7RC iOS App](https://apps.apple.com/tw/app/v7rc/id1390983964)
- [V7RC Android App](https://play.google.com/store/apps/details?id=com.v7idea.v7rcliteandroidsdkversion)
- [CyberBrick API Documentation](https://makerworld.com/en/cyberbrick/api-doc)
- [MicroPython Documentation](https://docs.micropython.org/)

---

**Phiên bản**: 1.0  
**Ngày cập nhật**: 2025-12-26  
**Tác giả**: CyberBrick V7RC Community
