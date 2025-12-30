# Hardware Connection Guide - ESP32-C3 Super Mini
## CyberBrick V7RC Controller

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [GPIO Pin Diagram](#gpio-pin-diagram)
3. [Servo Connections](#servo-connections)
4. [DC Motor Connections](#dc-motor-connections)
5. [NeoPixel LED Connections](#neopixel-led-connections)
6. [Buzzer Connections](#buzzer-connections)
7. [Power Supply](#power-supply)
8. [Complete Connection Example](#complete-connection-example)
9. [Troubleshooting](#troubleshooting)

---

## Overview

CyberBrick V7RC Controller is MicroPython firmware for ESP32-C3 Super Mini that enables control of:
- **4 Servo Channels** (GPIO 0-3)
- **2 DC Motors** with H-Bridge driver (GPIO 4-7)
- **NeoPixel LEDs** (GPIO 20 or 21)
- **Buzzer** (GPIO 20 or 21)

Control via:
- **Wi-Fi AP**: 192.168.4.1
- **UDP Port**: 6188
- **V7RC Mobile App** (iOS/Android)

---

## GPIO Pin Diagram

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

### Pin Assignment Table

| GPIO | Function | Description | Signal Type |
|------|----------|-------------|-------------|
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

## Servo Connections

### Specifications

- **Channels**: 4
- **Signal**: PWM 50Hz
- **Angle Range**: 0° - 180°
- **Voltage**: 4.8V - 6V (separate power supply)
- **Duty Cycle**: 25-125 (corresponds to 0°-180°)

### Wiring Diagram

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

### Connection Details

Each servo has 3 wires:
- **Brown/Black**: GND → Connect to common GND (ESP32-C3 + Servo PSU)
- **Red**: VCC (5V) → Connect to separate 5V-6V power supply (NOT to ESP32 3.3V!)
- **Yellow/Orange/White**: Signal → Connect to corresponding GPIO

| Servo | GPIO | Signal Wire | VCC Wire | GND Wire |
|-------|------|-------------|----------|----------|
| Servo 1 | GPIO 3 | Yellow → GPIO 3 | Red → 5V PSU | Brown → GND |
| Servo 2 | GPIO 2 | Yellow → GPIO 2 | Red → 5V PSU | Brown → GND |
| Servo 3 | GPIO 1 | Yellow → GPIO 1 | Red → 5V PSU | Brown → GND |
| Servo 4 | GPIO 0 | Yellow → GPIO 0 | Red → 5V PSU | Brown → GND |

> **⚠️ CRITICAL WARNING:**
> - **DO NOT** power servos from ESP32-C3 3.3V pin (will damage board!)
> - **MUST** use separate 5V-6V power supply for servos
> - **MUST** connect common GND between ESP32-C3 and servo power supply

### Code Example

```python
from bbl import ServosController

# Initialize controller
servos = ServosController()

# Control servo 1 to 90 degrees
servos.set_angle(1, 90)

# Control servo 2 to 180 degrees with smooth motion
servos.set_angle_stepping(2, 180, step_speed=50)

# Control servo 3 with continuous rotation (360° servo)
servos.set_speed(3, 50)  # 50% speed forward

# Stop servo 4
servos.stop(4)
```

---

## DC Motor Connections

### Specifications

- **Motors**: 2
- **Control**: H-Bridge Driver (L298N, TB6612, DRV8833...)
- **Speed Range**: -2048 to +2048
- **Logic**: Software PWM (20 steps)

### Wiring with L298N

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

### L298N Connection Table

| ESP32-C3 | L298N | Function |
|----------|-------|----------|
| GPIO 4 | IN1 | Motor 1 Forward |
| GPIO 5 | IN2 | Motor 1 Reverse |
| GPIO 6 | IN3 | Motor 2 Forward |
| GPIO 7 | IN4 | Motor 2 Reverse |
| GND | GND | Common ground |
| - | +12V | Motor power (6-12V) |
| - | +5V | Can power ESP32 (if jumper enabled) |

### Wiring with TB6612FNG (Compact)

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

> **💡 Recommendations:**
> - **L298N**: Suitable for larger motors (6-12V, 2A), has built-in 5V regulator
> - **TB6612FNG**: Compact, higher efficiency, suitable for smaller motors (4.5-13.5V, 1.2A)
> - **DRV8833**: Similar to TB6612, more affordable

### Code Example

```python
from bbl import MotorsController

# Initialize controller
motors = MotorsController()

# Motor 1 forward at 50% speed
motors.set_speed(1, 1024)  # 1024 = 50% of 2048

# Motor 2 reverse at 25% speed
motors.set_speed(2, -512)  # -512 = 25% reverse

# Stop motor 1
motors.stop(1)

# Set max forward speed for motor 1 to 80%
motors.set_forward_rate(1, 80)

# Set max reverse speed for motor 2 to 60%
motors.set_reverse_rate(2, 60)

# Set offset to balance motors
motors.set_offset(1, 10)  # Motor 1 is 10% stronger
```

---

## NeoPixel LED Connections

### Specifications

- **Type**: WS2812B / SK6812
- **LEDs per Channel**: 4 LEDs
- **GPIO**: 20 or 21
- **Voltage**: 5V
- **Current**: ~60mA/LED (max)

### Wiring Diagram

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

> **⚠️ Notes:**
> - For few LEDs (≤4), can power from ESP32-C3 5V pin
> - For many LEDs (>4), need separate 5V power supply
> - 3.3V signal from ESP32-C3 usually works fine with WS2812B

### Code Example

```python
from bbl import LEDController

# Initialize LED controller for channel 1 (GPIO 21)
led = LEDController('LED1')

# Blinking red effect
# mode=1: blink, duration=500ms, repeat=255 (infinite), led_index=0b1111 (4 LEDs), rgb=0xFF0000 (red)
led.set_led_effect(1, 500, 255, 0b1111, 0xFF0000)

# Breathing green effect
# mode=0: breathing, duration=1000ms, repeat=255, led_index=0b0011 (LED 1&2), rgb=0x00FF00
led.set_led_effect(0, 1000, 255, 0b0011, 0x00FF00)

# Solid blue
# mode=2: solid, duration=0, repeat=1, led_index=0b1111, rgb=0x0000FF
led.set_led_effect(2, 0, 1, 0b1111, 0x0000FF)
```

**LED Index Bitmask:**
- `0b0001` = LED 1
- `0b0010` = LED 2
- `0b0100` = LED 3
- `0b1000` = LED 4
- `0b1111` = All 4 LEDs

---

## Buzzer Connections

### Specifications

- **Type**: Passive Buzzer (PWM)
- **GPIO**: 20 or 21
- **Frequency**: 20Hz - 20kHz
- **Voltage**: 3.3V - 5V

### Wiring Diagram

```
┌──────────────┐
│   ESP32-C3   │         ┌─────────────┐
├──────────────┤         │   Buzzer    │
│ GPIO 21 ─────┼────────▶│ (+)         │
│              │         │             │
│ GND     ─────┼────────▶│ (-)         │
└──────────────┘         └─────────────┘
```

> **💡 Note:**
> - Use **Passive Buzzer** (frequency controlled by PWM)
> - **DO NOT** use Active Buzzer (only on/off)

### Code Example

```python
from bbl import MusicController

# Initialize music controller for buzzer channel 1 (GPIO 21)
music = MusicController('BUZZER1', volume=50)

# Play RTTTL music
rtttl_song = "Mario:d=4,o=5,b=100:16e6,16e6,32p,8e6,16c6,8e6,8g6,8p,8g,8p"
music.play(rtttl_song)

# Stop playback
music.stop()

# Adjust volume
music.set_volume(70)  # 0-100

# Simple tone
from bbl.buzzer import BuzzerController
buzzer = BuzzerController('BUZZER1')
buzzer.set_freq(1000)  # 1000 Hz
buzzer.set_volume(50)  # 50% volume
# Stop
buzzer.stop()
```

---

## Power Supply

### Power Requirements

| Device | Voltage | Current | Power Source |
|--------|---------|---------|--------------|
| **ESP32-C3** | 5V | ~200mA | USB or 5V regulator |
| **Servo (each)** | 4.8-6V | 100mA-1A | Separate 5V/2A-5A |
| **DC Motors** | 6-12V | 500mA-3A | Separate via driver |
| **NeoPixel (4 LEDs)** | 5V | ~240mA | ESP32 5V or separate |
| **Buzzer** | 3.3-5V | ~30mA | ESP32 3.3V |

### Recommended Power Diagram

```
┌─────────────────┐
│   Battery/PSU   │
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

> **⚠️ CRITICAL:**
> - **ALWAYS** connect common GND between all power supplies and ESP32-C3
> - **DO NOT** power servos from ESP32 3.3V pin
> - Use 100-1000µF capacitor near servos to reduce noise
> - If using battery, need protection circuit (BMS)

---

## Complete Connection Example

### 2-Wheel Robot with Servo Arm

```
Components:
- ESP32-C3 Super Mini
- L298N Motor Driver
- 2x DC Motor 6V
- 2x SG90 Servo
- 4x NeoPixel LED
- 1x Passive Buzzer
- 7.4V 2000mAh Battery
- 5V/3A Buck Converter

Connections:
┌──────────────────────────────────────────┐
│              ESP32-C3                    │
├──────────────────────────────────────────┤
│ GPIO 0  → Servo 4 (Gripper)              │
│ GPIO 1  → Servo 3 (Arm)                  │
│ GPIO 2  → (Unused)                       │
│ GPIO 3  → (Unused)                       │
│ GPIO 4  → L298N IN1 (Left Motor Fwd)     │
│ GPIO 5  → L298N IN2 (Left Motor Rev)     │
│ GPIO 6  → L298N IN3 (Right Motor Fwd)    │
│ GPIO 7  → L298N IN4 (Right Motor Rev)    │
│ GPIO 20 → Buzzer (+)                     │
│ GPIO 21 → NeoPixel DIN                   │
│ 5V      ← Buck Converter 5V              │
│ GND     → Common GND                     │
└──────────────────────────────────────────┘

Power:
7.4V Battery → Buck 5V/3A → ESP32-C3 + Servos + LEDs
7.4V Battery → L298N +12V → Motors
```

### Example Code

```python
import uasyncio
from bbl import ServosController, MotorsController, LEDController, MusicController

# Initialize controllers
servos = ServosController()
motors = MotorsController()
led = LEDController('LED1')
music = MusicController('BUZZER1', volume=30)

# Initial setup
servos.set_angle(1, 90)  # Arm at center
servos.set_angle(4, 45)  # Gripper open

# Green blinking LEDs
led.set_led_effect(1, 500, 255, 0b1111, 0x00FF00)

# Move forward
motors.set_speed(1, 1500)  # Left motor
motors.set_speed(2, 1500)  # Right motor

# Wait 2 seconds
await uasyncio.sleep(2)

# Stop
motors.stop(1)
motors.stop(2)

# Lower arm
servos.set_angle_stepping(1, 45, step_speed=30)

# Play sound
music.play("Beep:d=4,o=5,b=100:8c6,8p,8c6")
```

---

## Troubleshooting

### Servo Not Working

**Symptoms**: Servo doesn't rotate or jitters

**Causes & Solutions**:
1. ❌ **Insufficient power**
   - ✅ Check servo 5V/2A power supply
   - ✅ Add 1000µF capacitor near servo
   
2. ❌ **GND not common**
   - ✅ Connect GND of ESP32-C3, servo PSU, and servo

3. ❌ **Wrong angle**
   - ✅ Check angle 0-180°
   - ✅ Try `servos.set_angle(1, 90)` to test

### Motor Not Spinning

**Symptoms**: Motor doesn't spin or spins weakly

**Causes & Solutions**:
1. ❌ **Wrong driver wiring**
   - ✅ Check GPIO 4-7 connected to IN1-IN4
   - ✅ Check motor driver power

2. ❌ **Speed too low**
   - ✅ Try `motors.set_speed(1, 2048)` (max)
   - ✅ Check `motors.set_forward_rate(1, 100)`

3. ❌ **Driver fault**
   - ✅ Check LED on L298N
   - ✅ Measure voltage on OUT1-OUT4

### NeoPixel Not Lighting

**Symptoms**: LEDs don't light or wrong colors

**Causes & Solutions**:
1. ❌ **Insufficient 5V power**
   - ✅ Provide separate 5V power for LEDs
   - ✅ Check current (60mA/LED)

2. ❌ **Weak signal**
   - ✅ Add 330Ω resistor in series with DIN
   - ✅ Keep signal wire short (<30cm)

3. ❌ **Wrong code**
   - ✅ Check `led_index` bitmask
   - ✅ Try `led.set_led_effect(2, 0, 1, 0b1111, 0xFF0000)` (solid red)

### ESP32-C3 Keeps Resetting

**Symptoms**: Board resets when servo/motor operates

**Causes & Solutions**:
1. ❌ **Unstable power**
   - ✅ Use separate power for servo/motor
   - ✅ Add 100µF capacitor near ESP32 5V pin

2. ❌ **Excessive current**
   - ✅ DO NOT power servos from ESP32
   - ✅ Check USB power ≥1A

### Wi-Fi Cannot Connect

**Symptoms**: Cannot see "cyber_V7RC" AP

**Causes & Solutions**:
1. ❌ **Code not running**
   - ✅ Check serial monitor: `[v7rc] AP started at: 192.168.4.1`
   - ✅ Reset board and wait 5-10 seconds

2. ❌ **Wrong SSID/password**
   - ✅ Check `app/main.py`:
     ```python
     essid='cyber_V7RC',
     password='12341234'
     ```

3. ❌ **Wi-Fi channel conflict**
   - ✅ Turn off other Wi-Fi devices
   - ✅ Try reconnecting

---

## Reference Documentation

### Code Files
- [servos.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/bbl/servos.py) - Servo controller
- [motors.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/bbl/motors.py) - Motor controller
- [leds.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/bbl/leds.py) - LED controller
- [buzzer.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/bbl/buzzer.py) - Buzzer/Music controller
- [main.py](file:///c:/Espressif/frameworks/esp-idf-v5.5.1/examples/cyberbrick-v7rc/app/main.py) - Application entry point

### V7RC App
- **iOS**: [App Store](https://apps.apple.com/tw/app/v7rc/id1390983964)
- **Android**: [Google Play](https://play.google.com/store/apps/details?id=com.v7idea.v7rcliteandroidsdkversion)

### Recommended Components
- **ESP32-C3 Super Mini**: ~$2-3 USD
- **L298N Motor Driver**: ~$1-2 USD
- **TB6612FNG Motor Driver**: ~$1-2 USD
- **SG90 Servo**: ~$1 USD each
- **WS2812B LED Strip**: ~$0.20 USD/LED
- **5V/3A Buck Converter**: ~$1 USD
- **7.4V 2000mAh Battery**: ~$5-10 USD

---

**Version**: 1.0  
**Last Updated**: 2025-12-30  
**Author**: CyberBrick V7RC Documentation Team
