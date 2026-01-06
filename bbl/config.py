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
        'description': 'L298N Dual H-Bridge (digital control)'
    },
    'TB6612': {
        'use_hardware_pwm': False,
        'pwm_freq': 1000,
        'logic_type': 'digital',
        'stop_state': 'high',  # Both pins HIGH to stop
        'description': 'TB6612FNG Dual H-Bridge (digital control)'
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
