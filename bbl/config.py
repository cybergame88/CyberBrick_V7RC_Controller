# -*-coding:utf-8-*-
"""
Motor Driver Configuration
CyberBrick V7RC Controller

Supported motor drivers:
- L298N: Dual H-Bridge, digital control
- TB6612FNG: Dual H-Bridge, digital control (similar to L298N)
- L9110S: Dual H-Bridge, PWM control

Auto-detection feature:
- Set MOTOR_DRIVER_TYPE = 'AUTO' to automatically detect driver type
- Detection result is saved to file for faster subsequent boots
- Manual override is always available
"""

# Motor driver type selection
# Options: 'AUTO', 'L298N', 'TB6612', 'L9110S'
# 'AUTO' will detect driver type on first boot
MOTOR_DRIVER_TYPE = 'AUTO'

# Auto-detection settings
AUTO_DETECT_ENABLED = True
DETECTED_DRIVER_FILE = 'detected_driver.txt'  # Stores detected type

# Driver-specific configuration
MOTOR_DRIVER_CONFIG = {
    'L298N': {
        'use_hardware_pwm': False,
        'pwm_freq': 1000,
        'logic_type': 'digital',
        'stop_state': 'high',  # Both pins HIGH to stop
        'pwm_period': 100,  # Increased from 20 to 100 for smoother control
        'description': 'L298N Dual H-Bridge (software PWM control)'
    },
    'TB6612': {
        'use_hardware_pwm': False,
        'pwm_freq': 1000,
        'logic_type': 'digital',
        'stop_state': 'high',  # Both pins HIGH to stop
        'pwm_period': 100,  # Increased from 20 to 100 for smoother control
        'description': 'TB6612FNG Dual H-Bridge (software PWM control)'
    },
    'L9110S': {
        'use_hardware_pwm': False,  # Use software PWM (ESP32-C3 only has 6 PWM channels, servos use 4)
        'pwm_freq': 1000,
        'logic_type': 'pwm',
        'stop_state': 'low',  # Both pins LOW to stop
        'pwm_period': 100,  # Higher resolution software PWM (100 steps vs 20)
        'description': 'L9110S Dual H-Bridge (software PWM control)'
    }
}

# Software PWM settings
SOFTWARE_PWM_PERIOD = 20  # Default for L298N/TB6612
L9110S_PWM_PERIOD = 100   # Higher resolution for L9110S

# ============================================================================
# BLE (Bluetooth Low Energy) Configuration
# ============================================================================

# BLE Enable/Disable
# IMPORTANT: Set to False if your MicroPython firmware doesn't support BLE
# Error "nimble host init failed" means BLE is not available in firmware
BLE_ENABLED = False  # Set to True only if firmware has BLE support

# BLE Device Name (shown in BLE scanner apps)
BLE_DEVICE_NAME = "CyberBrick_V7RC"

# BLE Auto-reconnect
# If True, automatically restart advertising when client disconnects
BLE_AUTO_RECONNECT = True

# Connection Mode
# Options: 'WIFI', 'BLE', 'BOTH'
# - 'WIFI': WiFi AP only (original mode)
# - 'BLE': BLE only (lower power, no WiFi)
# - 'BOTH': WiFi + BLE concurrent (maximum compatibility)
CONNECTION_MODE = 'BOTH'

# BLE Service UUIDs (Nordic UART Service - NUS)
# These are standard UUIDs compatible with most BLE UART apps
BLE_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
BLE_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write (RX from client)
BLE_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notify (TX to client)
