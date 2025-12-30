# Hướng Dẫn Kết Nối Phần Cứng ESP32-C3 Super Mini
## CyberBrick V7RC Controller

---

## 📋 Mục Lục

1. [Tổng Quan](#tổng-quan)
2. [Sơ Đồ Chân GPIO](#sơ-đồ-chân-gpio)
3. [Kết Nối Servo](#kết-nối-servo)
4. [Kết Nối Động Cơ DC](#kết-nối-động-cơ-dc)
5. [Kết Nối LED NeoPixel](#kết-nối-led-neopixel)
6. [Kết Nối Buzzer](#kết-nối-buzzer)
7. [Nguồn Điện](#nguồn-điện)
8. [Ví Dụ Kết Nối Hoàn Chỉnh](#ví-dụ-kết-nối-hoàn-chỉnh)
9. [Khắc Phục Sự Cố](#khắc-phục-sự-cố)

---

## Tổng Quan

CyberBrick V7RC Controller là firmware MicroPython cho ESP32-C3 Super Mini, cho phép điều khiển:
- **4 kênh Servo** (GPIO 0-3)
- **2 động cơ DC** với driver H-Bridge (GPIO 4-7)
- **LED NeoPixel** (GPIO 20 hoặc 21)
- **Buzzer** (GPIO 20 hoặc 21)

Điều khiển qua:
- **Wi-Fi AP**: 192.168.4.1
- **UDP Port**: 6188
- **V7RC Mobile App** (iOS/Android)

---

## Sơ Đồ Chân GPIO

### ESP32-C3 Super Mini Pinout

```
┌─────────────────────────────────┐
│     ESP32-C3 Super Mini         │
├─────────────────────────────────┤
│ GPIO 0  ──────────── SERVO 4    │
│ GPIO 1  ──────────── SERVO 3    │
│ GPIO 2  ──────────── SERVO 2    │
│ GPIO 3  ──────────── SERVO 1    │
│ GPIO 4  ──────────── MOTOR1_CH1 │
│ GPIO 5  ──────────── MOTOR1_CH2 │
│ GPIO 6  ──────────── MOTOR2_CH1 │
│ GPIO 7  ──────────── MOTOR2_CH2 │
│ GPIO 8  ──────────── (Reserved) │
│ GPIO 9  ──────────── (Reserved) │
│ GPIO 10 ──────────── (Reserved) │
│ GPIO 20 ──────────── LED/BUZZER │
│ GPIO 21 ──────────── LED/BUZZER │
│ 3V3     ──────────── Power Out  │
│ 5V      ──────────── Power In   │
│ GND     ──────────── Ground     │
└─────────────────────────────────┘
```

### Bảng Phân Bổ Chân

| GPIO | Chức Năng | Mô Tả | Tín Hiệu |
|------|-----------|-------|----------|
| **0** | SERVO_CHANNEL4 | Servo #4 | PWM 50Hz |
| **1** | SERVO_CHANNEL3 | Servo #3 | PWM 50Hz |
| **2** | SERVO_CHANNEL2 | Servo #2 | PWM 50Hz |
| **3** | SERVO_CHANNEL1 | Servo #1 | PWM 50Hz |
| **4** | MOTOR1_CHANNEL1 | Motor 1 Forward | Digital PWM |
| **5** | MOTOR1_CHANNEL2 | Motor 1 Reverse | Digital PWM |
| **6** | MOTOR2_CHANNEL1 | Motor 2 Forward | Digital PWM |
| **7** | MOTOR2_CHANNEL2 | Motor 2 Reverse | Digital PWM |
| **20** | LED_CHANNEL2 / BUZZER_CHANNEL2 | NeoPixel/Buzzer | WS2812B/PWM |
| **21** | LED_CHANNEL1 / BUZZER_CHANNEL1 | NeoPixel/Buzzer | WS2812B/PWM |

---

## Kết Nối Servo

### Thông Số Kỹ Thuật

- **Số lượng**: 4 kênh
- **Tín hiệu**: PWM 50Hz
- **Góc quay**: 0° - 180°
- **Điện áp**: 4.8V - 6V (nguồn riêng)
- **Duty Cycle**: 25-125 (tương ứng 0°-180°)

### Sơ Đồ Kết Nối

```
┌──────────────┐
│   ESP32-C3   │
├──────────────┤         ┌─────────────┐
│ GPIO 3  ─────┼────────▶│ Servo 1     │
│ GPIO 2  ─────┼────────▶│ Servo 2     │
│ GPIO 1  ─────┼────────▶│ Servo 3     │
│ GPIO 0  ─────┼────────▶│ Servo 4     │
│              │         │             │
│ GND     ─────┼────┬───▶│ GND (Brown) │
└──────────────┘    │    └─────────────┘
                    │
              ┌─────┴──────┐
              │ Servo PSU  │
              │ 5V/6V      │
              │ 2A-5A      │
              └────────────┘
```

### Chi Tiết Kết Nối Servo

Mỗi servo có 3 dây:
- **Nâu/Đen**: GND → Nối chung với GND của ESP32-C3 và nguồn servo
- **Đỏ**: VCC (5V) → Nối với nguồn riêng 5V-6V (KHÔNG nối vào 3.3V của ESP32)
- **Vàng/Cam/Trắng**: Signal → Nối với GPIO tương ứng

| Servo | GPIO | Dây Signal | Dây VCC | Dây GND |
|-------|------|------------|---------|---------|
| Servo 1 | GPIO 3 | Vàng → GPIO 3 | Đỏ → 5V PSU | Nâu → GND |
| Servo 2 | GPIO 2 | Vàng → GPIO 2 | Đỏ → 5V PSU | Nâu → GND |
| Servo 3 | GPIO 1 | Vàng → GPIO 1 | Đỏ → 5V PSU | Nâu → GND |
| Servo 4 | GPIO 0 | Vàng → GPIO 0 | Đỏ → 5V PSU | Nâu → GND |

> **⚠️ LƯU Ý QUAN TRỌNG:**
> - **KHÔNG** cấp nguồn servo từ chân 3.3V của ESP32-C3 (sẽ cháy board!)
> - **BẮT BUỘC** dùng nguồn riêng 5V-6V cho servo
> - **BẮT BUỘC** nối chung GND giữa ESP32-C3 và nguồn servo

### Ví Dụ Code Điều Khiển Servo

```python
from bbl import ServosController

# Khởi tạo controller
servos = ServosController()

# Điều khiển servo 1 đến góc 90 độ
servos.set_angle(1, 90)

# Điều khiển servo 2 đến góc 180 độ với chuyển động mượt
servos.set_angle_stepping(2, 180, step_speed=50)

# Điều khiển servo 3 với tốc độ quay liên tục (servo 360°)
servos.set_speed(3, 50)  # 50% tốc độ thuận

# Dừng servo 4
servos.stop(4)
```

---

## Kết Nối Động Cơ DC

### Thông Số Kỹ Thuật

- **Số lượng**: 2 động cơ
- **Điều khiển**: H-Bridge Driver (L298N, TB6612, DRV8833...)
- **Tốc độ**: -2048 đến +2048
- **Logic**: Software PWM (20 steps)

### Sơ Đồ Kết Nối với L298N

```
┌──────────────┐                  ┌─────────────────┐
│   ESP32-C3   │                  │     L298N       │
├──────────────┤                  ├─────────────────┤
│ GPIO 4  ─────┼─────────────────▶│ IN1 (Motor A)   │
│ GPIO 5  ─────┼─────────────────▶│ IN2 (Motor A)   │
│ GPIO 6  ─────┼─────────────────▶│ IN3 (Motor B)   │
│ GPIO 7  ─────┼─────────────────▶│ IN4 (Motor B)   │
│              │                  │                 │
│ GND     ─────┼─────────────────▶│ GND             │
└──────────────┘                  │                 │
                                  │ OUT1 ───────────┼──▶ Motor 1 (+)
                                  │ OUT2 ───────────┼──▶ Motor 1 (-)
                                  │ OUT3 ───────────┼──▶ Motor 2 (+)
                                  │ OUT4 ───────────┼──▶ Motor 2 (-)
                                  │                 │
                ┌────────────────▶│ +12V            │
                │                 │ GND             │
                │                 └─────────────────┘
          ┌─────┴──────┐
          │ Motor PSU  │
          │ 6V-12V     │
          │ 2A-10A     │
          └────────────┘
```

### Bảng Kết Nối L298N

| ESP32-C3 | L298N | Chức Năng |
|----------|-------|-----------|
| GPIO 4 | IN1 | Motor 1 Forward |
| GPIO 5 | IN2 | Motor 1 Reverse |
| GPIO 6 | IN3 | Motor 2 Forward |
| GPIO 7 | IN4 | Motor 2 Reverse |
| GND | GND | Ground chung |
| - | +12V | Nguồn động cơ (6-12V) |
| - | +5V | Có thể cấp cho ESP32 (nếu có jumper) |

### Sơ Đồ Kết Nối với TB6612FNG (Nhỏ Gọn Hơn)

```
┌──────────────┐                  ┌─────────────────┐
│   ESP32-C3   │                  │    TB6612FNG    │
├──────────────┤                  ├─────────────────┤
│ GPIO 4  ─────┼─────────────────▶│ AIN1            │
│ GPIO 5  ─────┼─────────────────▶│ AIN2            │
│ GPIO 6  ─────┼─────────────────▶│ BIN1            │
│ GPIO 7  ─────┼─────────────────▶│ BIN2            │
│              │                  │                 │
│ 3.3V    ─────┼─────────────────▶│ VCC (Logic)     │
│ GND     ─────┼─────────────────▶│ GND             │
└──────────────┘                  │                 │
                                  │ AO1 ────────────┼──▶ Motor 1 (+)
                                  │ AO2 ────────────┼──▶ Motor 1 (-)
                                  │ BO1 ────────────┼──▶ Motor 2 (+)
                                  │ BO2 ────────────┼──▶ Motor 2 (-)
                                  │                 │
                ┌────────────────▶│ VM (Motor)      │
                │                 │ GND             │
                │                 └─────────────────┘
          ┌─────┴──────┐
          │ Motor PSU  │
          │ 4.5V-13.5V │
          │ 1A-3A      │
          └────────────┘
```

> **💡 Khuyến Nghị:**
> - **L298N**: Phù hợp với động cơ lớn (6-12V, 2A), có sẵn regulator 5V
> - **TB6612FNG**: Nhỏ gọn, hiệu suất cao hơn, phù hợp động cơ nhỏ (4.5-13.5V, 1.2A)
> - **DRV8833**: Tương tự TB6612, giá rẻ hơn

### Ví Dụ Code Điều Khiển Động Cơ

```python
from bbl import MotorsController

# Khởi tạo controller
motors = MotorsController()

# Motor 1 chạy tiến với tốc độ 50%
motors.set_speed(1, 1024)  # 1024 = 50% của 2048

# Motor 2 chạy lùi với tốc độ 25%
motors.set_speed(2, -512)  # -512 = 25% lùi

# Dừng motor 1
motors.stop(1)

# Cài đặt tốc độ tối đa tiến cho motor 1 là 80%
motors.set_forward_rate(1, 80)

# Cài đặt tốc độ tối đa lùi cho motor 2 là 60%
motors.set_reverse_rate(2, 60)

# Cài đặt offset để cân bằng 2 motor
motors.set_offset(1, 10)  # Motor 1 mạnh hơn 10%
```

---

## Kết Nối LED NeoPixel

### Thông Số Kỹ Thuật

- **Loại**: WS2812B / SK6812
- **Số lượng LED**: 4 LED mỗi kênh
- **GPIO**: 20 hoặc 21
- **Điện áp**: 5V
- **Dòng điện**: ~60mA/LED (max)

### Sơ Đồ Kết Nối

```
┌──────────────┐
│   ESP32-C3   │         ┌─────────────────┐
├──────────────┤         │  NeoPixel Strip │
│ GPIO 21 ─────┼────────▶│ DIN             │
│              │         │                 │
│ 3.3V    ─────┼────┬───▶│ VCC (5V)        │
│ GND     ─────┼────┼───▶│ GND             │
└──────────────┘    │    └─────────────────┘
                    │
              ┌─────┴──────┐
              │ 5V PSU     │
              │ 1A-2A      │
              └────────────┘
```

> **⚠️ LƯU Ý:**
> - Nếu dùng ít LED (≤4), có thể cấp từ 5V của ESP32-C3
> - Nếu dùng nhiều LED (>4), cần nguồn 5V riêng
> - Tín hiệu 3.3V từ ESP32-C3 thường hoạt động tốt với WS2812B

### Ví Dụ Code Điều Khiển LED

```python
from bbl import LEDController

# Khởi tạo LED controller cho kênh 1 (GPIO 21)
led = LEDController('LED1')

# Hiệu ứng nhấp nháy màu đỏ
# mod=1: blink, duration=500ms, repeat=255 (vô hạn), led_index=0b1111 (4 LED), rgb=0xFF0000 (đỏ)
led.set_led_effect(1, 500, 255, 0b1111, 0xFF0000)

# Hiệu ứng thở màu xanh lá
# mod=0: breathing, duration=1000ms, repeat=255, led_index=0b0011 (LED 1&2), rgb=0x00FF00
led.set_led_effect(0, 1000, 255, 0b0011, 0x00FF00)

# Sáng cố định màu xanh dương
# mod=2: solid, duration=0, repeat=1, led_index=0b1111, rgb=0x0000FF
led.set_led_effect(2, 0, 1, 0b1111, 0x0000FF)
```

**LED Index Bitmask:**
- `0b0001` = LED 1
- `0b0010` = LED 2
- `0b0100` = LED 3
- `0b1000` = LED 4
- `0b1111` = Tất cả 4 LED

---

## Kết Nối Buzzer

### Thông Số Kỹ Thuật

- **Loại**: Passive Buzzer (PWM)
- **GPIO**: 20 hoặc 21
- **Tần số**: 20Hz - 20kHz
- **Điện áp**: 3.3V - 5V

### Sơ Đồ Kết Nối

```
┌──────────────┐
│   ESP32-C3   │         ┌─────────────┐
├──────────────┤         │   Buzzer    │
│ GPIO 21 ─────┼────────▶│ (+)         │
│              │         │             │
│ GND     ─────┼────────▶│ (-)         │
└──────────────┘         └─────────────┘
```

> **💡 Lưu Ý:**
> - Dùng **Passive Buzzer** (điều khiển tần số bằng PWM)
> - **KHÔNG** dùng Active Buzzer (chỉ bật/tắt)

### Ví Dụ Code Điều Khiển Buzzer

```python
from bbl import MusicController

# Khởi tạo music controller cho buzzer kênh 1 (GPIO 21)
music = MusicController('BUZZER1', volume=50)

# Phát nhạc RTTTL (Ring Tone Text Transfer Language)
rtttl_song = "Mario:d=4,o=5,b=100:16e6,16e6,32p,8e6,16c6,8e6,8g6,8p,8g,8p"
music.play(rtttl_song)

# Dừng phát nhạc
music.stop()

# Điều chỉnh âm lượng
music.set_volume(70)  # 0-100

# Phát âm thanh đơn giản
from bbl.buzzer import BuzzerController
buzzer = BuzzerController('BUZZER1')
buzzer.set_freq(1000)  # 1000 Hz
buzzer.set_volume(50)  # 50% volume
# Dừng
buzzer.stop()
```

---

## Nguồn Điện

### Yêu Cầu Nguồn

| Thiết Bị | Điện Áp | Dòng Điện | Nguồn |
|----------|---------|-----------|-------|
| **ESP32-C3** | 5V | ~200mA | USB hoặc 5V regulator |
| **Servo (mỗi cái)** | 4.8-6V | 100mA-1A | Nguồn riêng 5V/2A-5A |
| **Động cơ DC** | 6-12V | 500mA-3A | Nguồn riêng qua driver |
| **NeoPixel (4 LED)** | 5V | ~240mA | 5V ESP32 hoặc riêng |
| **Buzzer** | 3.3-5V | ~30mA | 3.3V ESP32 |

### Sơ Đồ Nguồn Khuyến Nghị

```
┌─────────────────┐
│   Pin/Battery   │
│   7.4V-12V      │
│   2000mAh+      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌──────────┐
│ 5V DC │ │ Motor    │
│ Buck  │ │ Driver   │
│ 3A    │ │ (L298N)  │
└───┬───┘ └────┬─────┘
    │          │
    │          └──────▶ Motors (6-12V)
    │
    ├──────▶ ESP32-C3 (5V)
    ├──────▶ Servos (5V)
    └──────▶ NeoPixel (5V)
```

> **⚠️ QUAN TRỌNG:**
> - **LUÔN** nối chung GND giữa tất cả các nguồn và ESP32-C3
> - **KHÔNG** cấp nguồn servo từ chân 3.3V của ESP32
> - Dùng tụ điện 100-1000µF gần servo để giảm nhiễu
> - Nếu dùng pin, cần mạch bảo vệ (BMS)

---

## Ví Dụ Kết Nối Hoàn Chỉnh

### Xe Robot 2 Bánh với Servo Arm

```
Linh Kiện:
- ESP32-C3 Super Mini
- L298N Motor Driver
- 2x DC Motor 6V
- 2x Servo SG90
- 4x NeoPixel LED
- 1x Passive Buzzer
- Pin 7.4V 2000mAh
- Buck Converter 5V/3A

Kết Nối:
┌──────────────────────────────────────────┐
│              ESP32-C3                    │
├──────────────────────────────────────────┤
│ GPIO 0  → Servo 4 (Gripper)              │
│ GPIO 1  → Servo 3 (Arm)                  │
│ GPIO 2  → (Không dùng)                   │
│ GPIO 3  → (Không dùng)                   │
│ GPIO 4  → L298N IN1 (Motor Trái Tiến)    │
│ GPIO 5  → L298N IN2 (Motor Trái Lùi)     │
│ GPIO 6  → L298N IN3 (Motor Phải Tiến)    │
│ GPIO 7  → L298N IN4 (Motor Phải Lùi)     │
│ GPIO 20 → Buzzer (+)                     │
│ GPIO 21 → NeoPixel DIN                   │
│ 5V      ← Buck Converter 5V              │
│ GND     → GND chung                      │
└──────────────────────────────────────────┘

Nguồn:
Pin 7.4V → Buck 5V/3A → ESP32-C3 + Servos + LEDs
Pin 7.4V → L298N +12V → Motors
```

### Code Ví Dụ

```python
import uasyncio
from bbl import ServosController, MotorsController, LEDController, MusicController

# Khởi tạo controllers
servos = ServosController()
motors = MotorsController()
led = LEDController('LED1')
music = MusicController('BUZZER1', volume=30)

# Cấu hình ban đầu
servos.set_angle(1, 90)  # Arm ở giữa
servos.set_angle(4, 45)  # Gripper mở

# LED xanh lá nhấp nháy
led.set_led_effect(1, 500, 255, 0b1111, 0x00FF00)

# Xe tiến
motors.set_speed(1, 1500)  # Motor trái
motors.set_speed(2, 1500)  # Motor phải

# Chờ 2 giây
await uasyncio.sleep(2)

# Dừng xe
motors.stop(1)
motors.stop(2)

# Arm hạ xuống
servos.set_angle_stepping(1, 45, step_speed=30)

# Phát âm thanh
music.play("Beep:d=4,o=5,b=100:8c6,8p,8c6")
```

---

## Khắc Phục Sự Cố

### Servo Không Hoạt Động

**Triệu chứng**: Servo không quay hoặc rung lắc

**Nguyên nhân & Giải pháp**:
1. ❌ **Nguồn không đủ**
   - ✅ Kiểm tra nguồn servo 5V/2A
   - ✅ Thêm tụ 1000µF gần servo
   
2. ❌ **GND không chung**
   - ✅ Nối GND của ESP32-C3, servo PSU, và servo

3. ❌ **Góc quay sai**
   - ✅ Kiểm tra góc 0-180°
   - ✅ Thử `servos.set_angle(1, 90)` để test

### Động Cơ Không Quay

**Triệu chứng**: Motor không quay hoặc quay yếu

**Nguyên nhân & Giải pháp**:
1. ❌ **Kết nối driver sai**
   - ✅ Kiểm tra GPIO 4-7 nối đúng IN1-IN4
   - ✅ Kiểm tra nguồn motor driver

2. ❌ **Tốc độ quá thấp**
   - ✅ Thử `motors.set_speed(1, 2048)` (max)
   - ✅ Kiểm tra `motors.set_forward_rate(1, 100)`

3. ❌ **Driver bị lỗi**
   - ✅ Kiểm tra LED trên L298N
   - ✅ Đo điện áp OUT1-OUT4

### LED NeoPixel Không Sáng

**Triệu chứng**: LED không sáng hoặc sai màu

**Nguyên nhân & Giải pháp**:
1. ❌ **Nguồn 5V không đủ**
   - ✅ Cấp nguồn 5V riêng cho LED
   - ✅ Kiểm tra dòng điện (60mA/LED)

2. ❌ **Tín hiệu yếu**
   - ✅ Thêm điện trở 330Ω nối tiếp với DIN
   - ✅ Dây tín hiệu ngắn (<30cm)

3. ❌ **Code sai**
   - ✅ Kiểm tra `led_index` bitmask
   - ✅ Thử `led.set_led_effect(2, 0, 1, 0b1111, 0xFF0000)` (đỏ cố định)

### ESP32-C3 Reset Liên Tục

**Triệu chứng**: Board reset khi servo/motor hoạt động

**Nguyên nhân & Giải pháp**:
1. ❌ **Nguồn không ổn định**
   - ✅ Dùng nguồn riêng cho servo/motor
   - ✅ Thêm tụ 100µF gần chân 5V của ESP32

2. ❌ **Dòng điện quá lớn**
   - ✅ KHÔNG cấp nguồn servo từ ESP32
   - ✅ Kiểm tra nguồn USB ≥1A

### Wi-Fi Không Kết Nối Được

**Triệu chứng**: Không thấy AP "cyber_V7RC"

**Nguyên nhân & Giải pháp**:
1. ❌ **Code chưa chạy**
   - ✅ Kiểm tra serial monitor: `[v7rc] AP started at: 192.168.4.1`
   - ✅ Reset board và đợi 5-10 giây

2. ❌ **Tên/mật khẩu sai**
   - ✅ Kiểm tra `app/main.py`:
     ```python
     essid='cyber_V7RC',
     password='12341234'
     ```

3. ❌ **Kênh Wi-Fi bị xung đột**
   - ✅ Tắt các thiết bị Wi-Fi khác
   - ✅ Thử kết nối lại

---

## Tài Liệu Tham Khảo

### Code Files
- [servos.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/bbl/servos.py) - Servo controller
- [motors.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/bbl/motors.py) - Motor controller
- [leds.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/bbl/leds.py) - LED controller
- [buzzer.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/bbl/buzzer.py) - Buzzer/Music controller
- [main.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/app/main.py) - Application entry point

### V7RC App
- **iOS**: [App Store](https://apps.apple.com/tw/app/v7rc/id1390983964)
- **Android**: [Google Play](https://play.google.com/store/apps/details?id=com.v7idea.v7rcliteandroidsdkversion)

### Linh Kiện Khuyến Nghị
- **ESP32-C3 Super Mini**: ~50k VND
- **L298N Motor Driver**: ~30k VND
- **TB6612FNG Motor Driver**: ~25k VND
- **Servo SG90**: ~15k VND/cái
- **WS2812B LED Strip**: ~5k VND/LED
- **Buck Converter 5V/3A**: ~20k VND
- **Pin 7.4V 2000mAh**: ~100k VND

---

**Phiên bản**: 1.0  
**Ngày cập nhật**: 2025-12-26  
**Tác giả**: CyberBrick V7RC Documentation Team
