# V7RC Protocol Documentation / Tài liệu Giao thức V7RC

## English Version

### Overview

The V7RC protocol is a UDP-based communication protocol designed for controlling robots and RC devices. All commands are exactly **20 bytes** long and end with a `#` terminator character.

### Protocol Format

```
[CMD][DATA................]#
 3    16 characters        1
```

- **CMD**: 3-character command identifier (e.g., `SRV`, `LED`)
- **DATA**: 16 characters of command-specific data
- **#**: Terminator character (required)

### Supported Commands

#### 1. SRV - Basic PWM Control

**Format**: `SRV[PWM1][PWM2][PWM3][PWM4]#`

Controls 4 servo motors (C1-C4) with precise PWM values.

**Parameters**:
- Each PWM value: 4 digits (0000-2000 microseconds)
- Typical range: 500-2500μs
- Center position: 1500μs (90 degrees)

**Examples**:
```
SRV1500150015001500#  → All servos at center (90°)
SRV0500100015002000#  → S1=0°, S2=45°, S3=90°, S4=180°
```

**Use Case**: Precise servo control for robotic arms, pan-tilt mechanisms

---

#### 2. SR2 - Second PWM Group

**Format**: `SR2[PWM5][PWM6][PWM7][PWM8]#`

Controls servos C5-C8 (if available). Same format as SRV.

**Note**: CyberBrick V7RC only supports 4 servos (C1-C4), so this command logs a warning.

**Example**:
```
SR21200130014001500#  → C5-C8 control (not supported on V7RC)
```

---

#### 3. SS8 - Simplified 8-Channel PWM

**Format**: `SS8[H1][H2][H3][H4][H5][H6][H7][H8]#`

Simplified control for 8 channels using hexadecimal values.

**Parameters**:
- Each channel: 2 hex digits (00-FF)
- PWM value = Hex value × 10
- Example: `96` (hex) = 150 (dec) × 10 = 1500μs

**Examples**:
```
SS896969696969696#    → All channels at 1500μs (0x96 = 150)
SS800326496AAFF0000#  → Mixed values:
                         CH1=0, CH2=500, CH3=1000, CH4=1500
                         CH5=1700, CH6=2550, CH7=0, CH8=0
```

**Use Case**: Quick control with reduced precision, supports more channels

---

#### 4. SRT - Tank Mode PWM

**Format**: `SRT[THRT][STER][PWM3][PWM4]#`

Tank/differential drive control using throttle and steering.

**Parameters**:
- **THRT** (Throttle): 4 digits, 0000-2000 (1000 = neutral)
- **STER** (Steering): 4 digits, 0000-2000 (1000 = neutral)
- PWM3, PWM4: Optional servo control

**Tank Mixing Algorithm**:
```
Left Motor  = Throttle + Steering
Right Motor = Throttle - Steering
```

**Examples**:
```
SRT1500100000000000#  → Forward (throttle=1500, steering=neutral)
SRT1000150000000000#  → Turn right (neutral throttle, right steering)
SRT1800080000000000#  → Forward + left turn
```

**Use Case**: Tracked vehicles, differential drive robots

---

#### 5. LED - LED Control (WS2812)

**Format**: `LED[RGBM][RGBM][RGBM][RGBM]#`

Controls 4 WS2812 RGB LEDs with color and blink mode.

**RGBM Format** (4 characters per LED):
- **R**: Red (0-F hex, 0=off, F=max brightness)
- **G**: Green (0-F hex)
- **B**: Blue (0-F hex)
- **M**: Mode
  - `0`: Off
  - `1-9`: Blink (M × 100ms on per second)
  - `A-F`: Solid (always on)

**Color Conversion**:
- Hex 0-F → RGB 0-255 (multiply by 17)
- Example: `F` = 15 × 17 = 255

**Examples**:
```
LEDF00AF00AF00AF00A#  → All LEDs solid red
LED0F0A0F0A0F0A0F0A#  → All LEDs solid green
LED00FAF00A00FA00FA#  → All LEDs solid blue
LED0F050F050F050F05#  → All LEDs blink green (500ms on/500ms off)
LEDFFFA0000FFFA0000#  → LED1,3=white solid, LED2,4=off
```

**Use Case**: Status indicators, decorative lighting, visual feedback

---

#### 6. LE2 - Second LED Group

**Format**: `LE2[RGBM][RGBM][RGBM][RGBM]#`

Controls a second group of 4 LEDs. Same format as LED command.

**Example**:
```
LE200F0F00FF00FF00F#  → Second LED group control
```

---

### Command Summary Table

| Command | Channels | Data Format | Use Case |
|---------|----------|-------------|----------|
| **SRV** | 4 servos | 4-digit PWM (0000-2000) | Precise servo control |
| **SR2** | 4 servos | 4-digit PWM (0000-2000) | Extended servo control |
| **SS8** | 8 channels | 2-digit hex (00-FF) | Simplified multi-channel |
| **SRT** | 2 motors + 2 servos | Throttle + Steering | Tank/differential drive |
| **LED** | 4 LEDs | RGBM format | RGB LED control |
| **LE2** | 4 LEDs | RGBM format | Second LED group |

---

### UDP Communication

**Network Settings**:
- **Protocol**: UDP
- **IP Address**: `192.168.4.1` (ESP32 AP mode)
- **Port**: `6188`
- **WiFi SSID**: `cyber_V7RC`
- **Password**: `12341234`

**Sending Commands** (PowerShell example):
```powershell
$udp = New-Object System.Net.Sockets.UdpClient
$bytes = [System.Text.Encoding]::ASCII.GetBytes("SRV1500150015001500#")
$udp.Send($bytes, $bytes.Length, "192.168.4.1", 6188)
$udp.Close()
```

---

### Error Handling

The parser validates:
- ✅ Command length (must be exactly 20 bytes)
- ✅ Terminator character (must end with `#`)
- ✅ Command type (must be SRV, SR2, SS8, SRT, LED, or LE2)
- ✅ Data format (numeric/hex values in correct positions)

**Invalid commands are ignored** and logged to serial output.

---

## Phiên bản Tiếng Việt

### Tổng quan

Giao thức V7RC là giao thức truyền thông UDP được thiết kế để điều khiển robot và thiết bị RC. Tất cả lệnh đều có độ dài chính xác **20 bytes** và kết thúc bằng ký tự `#`.

### Định dạng Giao thức

```
[CMD][DATA................]#
 3    16 ký tự              1
```

- **CMD**: Mã lệnh 3 ký tự (ví dụ: `SRV`, `LED`)
- **DATA**: 16 ký tự dữ liệu theo lệnh
- **#**: Ký tự kết thúc (bắt buộc)

### Các Lệnh Hỗ trợ

#### 1. SRV - Điều khiển PWM Cơ bản

**Định dạng**: `SRV[PWM1][PWM2][PWM3][PWM4]#`

Điều khiển 4 động cơ servo (C1-C4) với giá trị PWM chính xác.

**Tham số**:
- Mỗi giá trị PWM: 4 chữ số (0000-2000 micro giây)
- Phạm vi thông thường: 500-2500μs
- Vị trí giữa: 1500μs (90 độ)

**Ví dụ**:
```
SRV1500150015001500#  → Tất cả servo ở giữa (90°)
SRV0500100015002000#  → S1=0°, S2=45°, S3=90°, S4=180°
```

**Ứng dụng**: Điều khiển servo chính xác cho cánh tay robot, cơ cấu xoay nghiêng

---

#### 2. SR2 - Nhóm PWM Thứ hai

**Định dạng**: `SR2[PWM5][PWM6][PWM7][PWM8]#`

Điều khiển servo C5-C8 (nếu có). Định dạng giống SRV.

**Lưu ý**: CyberBrick V7RC chỉ hỗ trợ 4 servo (C1-C4), nên lệnh này sẽ ghi cảnh báo.

**Ví dụ**:
```
SR21200130014001500#  → Điều khiển C5-C8 (không hỗ trợ trên V7RC)
```

---

#### 3. SS8 - PWM Đơn giản 8 Kênh

**Định dạng**: `SS8[H1][H2][H3][H4][H5][H6][H7][H8]#`

Điều khiển đơn giản cho 8 kênh sử dụng giá trị thập lục phân.

**Tham số**:
- Mỗi kênh: 2 chữ số hex (00-FF)
- Giá trị PWM = Giá trị Hex × 10
- Ví dụ: `96` (hex) = 150 (thập phân) × 10 = 1500μs

**Ví dụ**:
```
SS896969696969696#    → Tất cả kênh ở 1500μs (0x96 = 150)
SS800326496AAFF0000#  → Giá trị hỗn hợp:
                         CH1=0, CH2=500, CH3=1000, CH4=1500
                         CH5=1700, CH6=2550, CH7=0, CH8=0
```

**Ứng dụng**: Điều khiển nhanh với độ chính xác giảm, hỗ trợ nhiều kênh hơn

---

#### 4. SRT - Chế độ Tank PWM

**Định dạng**: `SRT[THRT][STER][PWM3][PWM4]#`

Điều khiển xe tank/vi sai sử dụng ga và lái.

**Tham số**:
- **THRT** (Ga): 4 chữ số, 0000-2000 (1000 = trung tính)
- **STER** (Lái): 4 chữ số, 0000-2000 (1000 = trung tính)
- PWM3, PWM4: Điều khiển servo tùy chọn

**Thuật toán Trộn Tank**:
```
Động cơ Trái  = Ga + Lái
Động cơ Phải = Ga - Lái
```

**Ví dụ**:
```
SRT1500100000000000#  → Tiến (ga=1500, lái=trung tính)
SRT1000150000000000#  → Rẽ phải (ga trung tính, lái phải)
SRT1800080000000000#  → Tiến + rẽ trái
```

**Ứng dụng**: Xe bánh xích, robot dẫn động vi sai

---

#### 5. LED - Điều khiển LED (WS2812)

**Định dạng**: `LED[RGBM][RGBM][RGBM][RGBM]#`

Điều khiển 4 đèn LED RGB WS2812 với màu sắc và chế độ nhấp nháy.

**Định dạng RGBM** (4 ký tự mỗi LED):
- **R**: Đỏ (0-F hex, 0=tắt, F=sáng tối đa)
- **G**: Xanh lá (0-F hex)
- **B**: Xanh dương (0-F hex)
- **M**: Chế độ
  - `0`: Tắt
  - `1-9`: Nhấp nháy (M × 100ms sáng mỗi giây)
  - `A-F`: Sáng liên tục (luôn bật)

**Chuyển đổi Màu**:
- Hex 0-F → RGB 0-255 (nhân với 17)
- Ví dụ: `F` = 15 × 17 = 255

**Ví dụ**:
```
LEDF00AF00AF00AF00A#  → Tất cả LED đỏ sáng liên tục
LED0F0A0F0A0F0A0F0A#  → Tất cả LED xanh lá sáng liên tục
LED00FAF00A00FA00FA#  → Tất cả LED xanh dương sáng liên tục
LED0F050F050F050F05#  → Tất cả LED nhấp nháy xanh (500ms sáng/500ms tắt)
LEDFFFA0000FFFA0000#  → LED1,3=trắng sáng, LED2,4=tắt
```

**Ứng dụng**: Chỉ báo trạng thái, đèn trang trí, phản hồi trực quan

---

#### 6. LE2 - Nhóm LED Thứ hai

**Định dạng**: `LE2[RGBM][RGBM][RGBM][RGBM]#`

Điều khiển nhóm thứ hai gồm 4 LED. Định dạng giống lệnh LED.

**Ví dụ**:
```
LE200F0F00FF00FF00F#  → Điều khiển nhóm LED thứ hai
```

---

### Bảng Tóm tắt Lệnh

| Lệnh | Kênh | Định dạng Dữ liệu | Ứng dụng |
|------|------|-------------------|----------|
| **SRV** | 4 servo | PWM 4 chữ số (0000-2000) | Điều khiển servo chính xác |
| **SR2** | 4 servo | PWM 4 chữ số (0000-2000) | Điều khiển servo mở rộng |
| **SS8** | 8 kênh | Hex 2 chữ số (00-FF) | Đa kênh đơn giản |
| **SRT** | 2 động cơ + 2 servo | Ga + Lái | Dẫn động tank/vi sai |
| **LED** | 4 LED | Định dạng RGBM | Điều khiển LED RGB |
| **LE2** | 4 LED | Định dạng RGBM | Nhóm LED thứ hai |

---

### Truyền thông UDP

**Cài đặt Mạng**:
- **Giao thức**: UDP
- **Địa chỉ IP**: `192.168.4.1` (chế độ AP của ESP32)
- **Cổng**: `6188`
- **WiFi SSID**: `cyber_V7RC`
- **Mật khẩu**: `12341234`

**Gửi Lệnh** (ví dụ PowerShell):
```powershell
$udp = New-Object System.Net.Sockets.UdpClient
$bytes = [System.Text.Encoding]::ASCII.GetBytes("SRV1500150015001500#")
$udp.Send($bytes, $bytes.Length, "192.168.4.1", 6188)
$udp.Close()
```

---

### Xử lý Lỗi

Parser kiểm tra:
- ✅ Độ dài lệnh (phải chính xác 20 bytes)
- ✅ Ký tự kết thúc (phải kết thúc bằng `#`)
- ✅ Loại lệnh (phải là SRV, SR2, SS8, SRT, LED, hoặc LE2)
- ✅ Định dạng dữ liệu (giá trị số/hex ở đúng vị trí)

**Lệnh không hợp lệ sẽ bị bỏ qua** và ghi vào serial output.

---

### Quick Reference / Tham khảo Nhanh

```
# Servo center / Servo giữa
SRV1500150015001500#

# Tank forward / Tank tiến
SRT1500100000000000#

# Red LED solid / LED đỏ sáng
LEDF00AF00AF00AF00A#

# Green LED blink / LED xanh nhấp nháy
LED0F050F050F050F05#

# Simplified control / Điều khiển đơn giản
SS896969696969696#
```
