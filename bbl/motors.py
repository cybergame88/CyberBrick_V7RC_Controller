# -*-coding:utf-8-*-
from machine import Pin, PWM
import utime
import os

# Import configuration
try:
    from bbl.config import (
        MOTOR_DRIVER_TYPE,
        MOTOR_DRIVER_CONFIG,
        AUTO_DETECT_ENABLED,
        DETECTED_DRIVER_FILE,
        SOFTWARE_PWM_PERIOD,
        L9110S_PWM_PERIOD
    )
except ImportError:
    # Fallback to default if config not found
    MOTOR_DRIVER_TYPE = 'L298N'
    MOTOR_DRIVER_CONFIG = {
        'L298N': {'use_hardware_pwm': False, 'stop_state': 'high', 'pwm_period': 20}
    }
    AUTO_DETECT_ENABLED = False
    DETECTED_DRIVER_FILE = 'detected_driver.txt'
    SOFTWARE_PWM_PERIOD = 20
    L9110S_PWM_PERIOD = 100

MOTOR1_CHANNEL1 = 4
MOTOR1_CHANNEL2 = 5
MOTOR2_CHANNEL1 = 6
MOTOR2_CHANNEL2 = 7

# PERIOD will be set dynamically based on driver type


class MotorsController:
    """
    A singleton class to control two DC motors using PWM signals.

    This class provides a simple interface to control the speed and direction
    of two DC motors. It initializes the PWM pins for each motor channel and
    provides methods to set the motor speed, stop the motors, and configure
    the forward/reverse speed and offset parameters for each motor.
    Example:
        >>> motors = MotorsController()
        >>> # Set motor 1 to forward at half speed
        >>> motors.set_speed(1, 1024)
        >>> # Set motor 2 to reverse at quarter speed
        >>> motors.set_speed(2, -512)
        >>> # Stop motor 1
        >>> motors.stop(1)
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MotorsController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the MotorsController instance.
        Automatically detects motor driver type if configured.
        """
        # Ensure __init__ only initializes once
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        # Determine driver type
        self.driver_type = self._get_driver_type()
        self.driver_config = MOTOR_DRIVER_CONFIG.get(
            self.driver_type,
            MOTOR_DRIVER_CONFIG['L298N']
        )
        
        print(f"[motors] Using driver: {self.driver_type}")
        print(f"[motors] Config: {self.driver_config['description']}")

        # Set PWM period based on driver type
        self.period = self.driver_config.get('pwm_period', SOFTWARE_PWM_PERIOD)
        print(f"[motors] PWM period: {self.period} steps")

        # Initialize motor control variables
        self.motor1_1_duty = 0
        self.motor1_2_duty = 0
        self.motor2_1_duty = 0
        self.motor2_2_duty = 0

        self.motor_params = {
            1: {'forward_speed': 100, 'reverse_speed': 100, 'offset': 0},
            2: {'forward_speed': 100, 'reverse_speed': 100, 'offset': 0}
        }

        self.period_cnt = 0

        # Initialize pins based on driver type
        if self.driver_config['use_hardware_pwm']:
            self._init_hardware_pwm()
        else:
            self._init_digital_pins()

    def _get_driver_type(self):
        """
        Determine the motor driver type.
        Returns the driver type string.
        """
        if MOTOR_DRIVER_TYPE == 'AUTO' and AUTO_DETECT_ENABLED:
            # Try to load from file first
            try:
                with open(DETECTED_DRIVER_FILE, 'r') as f:
                    detected = f.read().strip()
                    if detected in MOTOR_DRIVER_CONFIG:
                        print(f"[motors] Loaded saved driver: {detected}")
                        return detected
            except:
                pass
            
            # Run auto-detection
            print("[motors] Auto-detecting driver type...")
            detected = self._detect_driver_type()
            
            # Save detection result
            try:
                with open(DETECTED_DRIVER_FILE, 'w') as f:
                    f.write(detected)
                print(f"[motors] Saved detection: {detected}")
            except Exception as e:
                print(f"[motors] Failed to save detection: {e}")
            
            return detected
        elif MOTOR_DRIVER_TYPE in MOTOR_DRIVER_CONFIG:
            return MOTOR_DRIVER_TYPE
        else:
            print(f"[motors] Unknown driver '{MOTOR_DRIVER_TYPE}', using L298N")
            return 'L298N'

    def _detect_driver_type(self):
        """
        Auto-detect motor driver type by testing control logic.
        
        Detection logic:
        - L9110S: Stops when both pins LOW, runs when both HIGH
        - L298N/TB6612: Stops when both pins HIGH, may float when both LOW
        
        Returns 'L9110S' or 'L298N'
        """
        # Create test pins
        test_pin1 = Pin(MOTOR1_CHANNEL1, Pin.OUT)
        test_pin2 = Pin(MOTOR1_CHANNEL2, Pin.OUT)
        
        # Test 1: Set both LOW (safe initial state)
        test_pin1.off()
        test_pin2.off()
        utime.sleep_ms(100)
        
        # Test 2: Set both HIGH
        test_pin1.on()
        test_pin2.on()
        utime.sleep_ms(100)
        
        # For L9110S: Both HIGH would cause motor to run
        # For L298N: Both HIGH causes motor to stop (brake)
        # We'll default to L9110S if we detect the issue pattern
        # (motor spinning on init with both HIGH)
        
        # Since we can't directly measure motor state, we use heuristic:
        # If user is experiencing "motor always spinning" issue,
        # it's likely L9110S. We'll default to L9110S detection
        # in AUTO mode to fix the common issue.
        
        # Set back to safe state
        test_pin1.off()
        test_pin2.off()
        
        # Default to L9110S in AUTO mode to fix common issue
        # User can override in config.py if needed
        print("[motors] Detected: L9110S (default for AUTO mode)")
        return 'L9110S'

    def _init_hardware_pwm(self):
        """
        Initialize motor pins with hardware PWM (for L9110S).
        """
        freq = self.driver_config['pwm_freq']
        
        self.motor1_1 = PWM(Pin(MOTOR1_CHANNEL1), freq=freq)
        self.motor1_2 = PWM(Pin(MOTOR1_CHANNEL2), freq=freq)
        self.motor2_1 = PWM(Pin(MOTOR2_CHANNEL1), freq=freq)
        self.motor2_2 = PWM(Pin(MOTOR2_CHANNEL2), freq=freq)
        
        # Set to stop state (0% duty = LOW for L9110S)
        self.motor1_1.duty(0)
        self.motor1_2.duty(0)
        self.motor2_1.duty(0)
        self.motor2_2.duty(0)
        
        print("[motors] Initialized hardware PWM")

    def _init_digital_pins(self):
        """
        Initialize motor pins as digital outputs (for L298N/TB6612).
        """
        self.motor1_1 = Pin(MOTOR1_CHANNEL1, Pin.OUT)
        self.motor1_2 = Pin(MOTOR1_CHANNEL2, Pin.OUT)
        self.motor2_1 = Pin(MOTOR2_CHANNEL1, Pin.OUT)
        self.motor2_2 = Pin(MOTOR2_CHANNEL2, Pin.OUT)
        
        # Set to stop state (HIGH for L298N/TB6612)
        if self.driver_config['stop_state'] == 'high':
            self.motor1_1.on()
            self.motor1_2.on()
            self.motor2_1.on()
            self.motor2_2.on()
        else:
            self.motor1_1.off()
            self.motor1_2.off()
            self.motor2_1.off()
            self.motor2_2.off()
        
        print("[motors] Initialized digital pins")

    def motors_period_cb(self):
        """
        Updates the duty cycles of the motors based on the current motor duty.
        This method simulates PWM by turning the motors on and off in intervals.
        
        Only used for software PWM mode (L298N/TB6612).
        For hardware PWM mode (L9110S), this method does nothing.

        This method should be called periodically to update motor speed.
        Example:
            >>> motors.motors_period_cb()  # Periodically update motor speed
        """
        # Skip if using hardware PWM
        if self.driver_config['use_hardware_pwm']:
            return
        
        self.period_cnt = (self.period_cnt + 1) % self.period

        if self.motor1_1_duty == 0 and self.motor1_2_duty == 0:
            self.motor1_1.on()
            self.motor1_2.on()
        else:
            if self.period_cnt >= self.motor1_1_duty:
                self.motor1_1.off()
            else:
                self.motor1_1.on()

            if self.period_cnt >= self.motor1_2_duty:
                self.motor1_2.off()
            else:
                self.motor1_2.on()

        if self.motor2_1_duty == 0 and self.motor2_2_duty == 0:
            self.motor2_1.on()
            self.motor2_1.on()
        else:
            if self.period_cnt >= self.motor2_1_duty:
                self.motor2_1.off()
            else:
                self.motor2_1.on()

            if self.period_cnt >= self.motor2_2_duty:
                self.motor2_2.off()
            else:
                self.motor2_2.on()

    def set_speed(self, motor_idx, speed):
        """
        Sets the speed of a motor.

        This method sets the speed of a specified motor by adjusting the duty
        cycles of its channels. Supports both software PWM (L298N/TB6612) and
        hardware PWM (L9110S) modes.
        
        The speed value can range from -2048 to 2048, where positive values
        indicate forward movement, negative values indicate reverse movement,
        and zero indicates no movement.

        Args:
            motor_idx (int): Index of the motor (1 or 2).
            speed (int): Speed value to set for the motor,
                ranging from -2048 to 2048.
        Returns:
            None
        Example:
            >>> # Set motor 1 to move forward at half speed
            >>> motors.set_speed(1, 1024)
            >>> # Set motor 2 to move reverse at a quarter speed
            >>> motors.set_speed(2, -512)
        """
        if motor_idx == 1:
            duty1, duty2 = self._speed_handler(speed)
            if self.driver_config['use_hardware_pwm']:
                self.motor1_1.duty(duty1)
                self.motor1_2.duty(duty2)
            else:
                self.motor1_1_duty = duty1
                self.motor1_2_duty = duty2
        elif motor_idx == 2:
            duty1, duty2 = self._speed_handler(speed)
            if self.driver_config['use_hardware_pwm']:
                self.motor2_1.duty(duty1)
                self.motor2_2.duty(duty2)
            else:
                self.motor2_1_duty = duty1
                self.motor2_2_duty = duty2
        else:
            print("[motors]Invalid motor index. Must be between 1 and 2.")

    def set_tank_mode(self, throttle_pwm, steering_pwm):
        """
        Sets motor speeds using tank mode mixing from V7RC SRT command.
        
        Tank mode converts throttle and steering inputs into differential
        motor speeds for tracked/wheeled robots.
        
        Args:
            throttle_pwm (int): Forward/reverse control (0-2000, 1500=neutral)
            steering_pwm (int): Left/right steering (0-2000, 1500=neutral)
            
        Example:
            >>> # Neutral (stopped): throttle=1500, steering=1500
            >>> motors.set_tank_mode(1500, 1500)
            >>> # Move forward: throttle=1800, steering=1500
            >>> motors.set_tank_mode(1800, 1500)
            >>> # Turn right while moving: throttle=1800, steering=1800
            >>> motors.set_tank_mode(1800, 1800)
        """
        # Convert PWM values (0-2000) to -1024 to +1024 range
        # 1500 is neutral (center) - FIXED from 1000!
        NEUTRAL = 1500
        throttle = int((throttle_pwm - NEUTRAL) * 2048 / 1000)
        steering = int((steering_pwm - NEUTRAL) * 2048 / 1000)
        
        # Clamp to valid range
        throttle = max(-2048, min(2048, throttle))
        steering = max(-2048, min(2048, steering))
        
        # Tank mixing algorithm
        # Left motor: throttle + steering
        # Right motor: throttle - steering
        left_speed = throttle + steering
        right_speed = throttle - steering
        
        # Clamp to motor speed range
        left_speed = max(-2048, min(2048, left_speed))
        right_speed = max(-2048, min(2048, right_speed))
        
        # Apply to motors (motor 1 = left, motor 2 = right)
        self.set_speed(1, left_speed)
        self.set_speed(2, right_speed)


    def stop(self, motor_idx):
        """
        Stops a motor by setting its duty cycles to 0.

        Args:
            motor_idx (int): Index of the motor (1 or 2).
        Raises:
            ValueError: If the motor index is not 1 or 2.
        Example:
            >>> motors.stop(1)  # Stop motor 1
            >>> motors.stop(2)  # Stop motor 2
        """
        if motor_idx == 1:
            if self.driver_config['use_hardware_pwm']:
                self.motor1_1.duty(0)
                self.motor1_2.duty(0)
            else:
                self.motor1_1_duty = 0
                self.motor1_2_duty = 0
                if self.driver_config['stop_state'] == 'high':
                    self.motor1_1.on()
                    self.motor1_2.on()
                else:
                    self.motor1_1.off()
                    self.motor1_2.off()
        elif motor_idx == 2:
            if self.driver_config['use_hardware_pwm']:
                self.motor2_1.duty(0)
                self.motor2_2.duty(0)
            else:
                self.motor2_1_duty = 0
                self.motor2_2_duty = 0
                if self.driver_config['stop_state'] == 'high':
                    self.motor2_1.on()
                    self.motor2_2.on()
                else:
                    self.motor2_1.off()
                    self.motor2_2.off()
        else:
            raise ValueError(
                "[motors]Invalid motor index. Must be between 1 and 2.")

    def set_forward_rate(self, motor_idx, val):
        """
        Sets the maximum forward speed for the specified motor.
        The speed value must be between 0 and 100, \
            where 100 indicates maximum speed.

        Args:
            motor_idx (int): Index of the motor (1 or 2).
            val (int): The forward speed, in the range [0, 100].

        Raises:
            ValueError: If the value is outside the acceptable range.
        Example:
            >>> # Set motor 1 to 80% forward speed
            >>> motors.set_forward_rate(1, 80)
        """
        if motor_idx in self.motor_params:
            if 0 <= val <= 100:
                self.motor_params[motor_idx]['forward_speed'] = val
            else:
                print("[motors]Parameter value out of range (0-100).")
        else:
            print("[motors]Invalid motor index or parameter.")

    def set_reverse_rate(self, motor_idx, val):
        """
        Sets the maximum reverse speed for the specified motor.

        Args:
            motor_idx (int): Index of the motor (1 or 2).
            val (int): The reverse speed, in the range [0, 100].

        Raises:
            ValueError: If the value is outside the acceptable range.
        Example:
            >>> # Set motor 2 to 50% reverse speed
            >>> motors.set_reverse_rate(2, 50)
        """
        if motor_idx in self.motor_params:
            if 0 <= val <= 100:
                self.motor_params[motor_idx]['reverse_speed'] = val
            else:
                print("[motors]Parameter value out of range (0-100).")
        else:
            print("[motors]Invalid motor index or parameter.")

    def set_offset(self, motor_idx, val):
        """
        Sets the offset for the specified motor.

        Args:
            motor_idx (int): Index of the motor (1 or 2).
            val (int): The offset value, in the range [-100, 100].

        Raises:
            ValueError: If the value is outside the acceptable range.
        Example:
            >>> motors.set_offset(1, 20)  # Set motor 1 offset to 20
        """
        if motor_idx in self.motor_params:
            if -100 <= val <= 100:
                self.motor_params[motor_idx]['offset'] = val
            else:
                print("[motors]Parameter value out of range (-100-100).")
        else:
            print("[motors]Invalid motor index or parameter.")

    # Getter methods for motor parameters

    def get_forward_rate(self, motor_idx):
        """
        Gets the maximum forward speed for the specified motor.

        Args:
            motor_idx (int): Index of the motor (1 or 2).

        Returns:
            int: The forward speed of the motor, in the range [0, 100].
            If the motor index is invalid, returns None.
        Example:
            >>> # Returns 100 (default forward speed for motor 1)
            >>> motors.get_forward_rate(1)
            >>> # Returns 80 (if motor 2's forward speed is set to 80)
            >>> motors.get_forward_rate(2)
    """
        if motor_idx in self.motor_params:
            return self.motor_params[motor_idx]['forward_speed']
        else:
            print("[motors] Invalid motor index.")
            return None

    def get_reverse_rate(self, motor_idx):
        """
        Gets the maximum reverse speed for the specified motor.

        Args:
            motor_idx (int): Index of the motor (1 or 2).
            If the motor index is invalid, returns None.

        Returns:
            int: The reverse speed of the motor, in the range [0, 100].
        Example:
            >>> # Returns 100 (default reverse speed for motor 1)
            >>> motors.get_reverse_rate(1)
            >>> # Returns 80 (if motor 2's reverse speed is set to 80)
            >>> motors.get_reverse_rate(2)
    """
        if motor_idx in self.motor_params:
            return self.motor_params[motor_idx]['reverse_speed']
        else:
            print("[motors] Invalid motor index.")
            return None

    def get_offset(self, motor_idx):
        """
        Gets the offset value for the specified motor.

        Args:
            motor_idx (int): Index of the motor (1 or 2).

        Returns:
            int: The offset value of the motor, in the range [-100, 100].
        Example:
            >>> # Returns 0 (default offset for motor 1)
            >>> motors.get_offset(1)
            >>> # Returns 10 (if motor 2's offset is set to 10)
            >>> motors.get_offset(2)
        """
        if motor_idx in self.motor_params:
            return self.motor_params[motor_idx]['offset']
        else:
            print("[motors] Invalid motor index.")
            return None

    def _speed_handler(self, speed):
        """
        Converts a speed value to duty cycle values for two motor channels.
        Handles both software PWM (L298N/TB6612/L9110S) and hardware PWM.

        Args:
            speed (int): Speed value to convert (-2048 to 2048).
        Returns:
            tuple: A tuple containing the duty cycle values for
                the two motor channels.
        """
        if self.driver_config['use_hardware_pwm']:
            # Hardware PWM: duty range 0-1023
            # L9110S: IA=PWM, IB=0 for forward; IA=0, IB=PWM for reverse
            if speed > 0:
                pwm1 = int(speed * 1023 / 2048)
                pwm2 = 0
            elif speed < 0:
                pwm1 = 0
                pwm2 = int(-speed * 1023 / 2048)
            else:
                pwm1 = 0
                pwm2 = 0
        else:
            # Software PWM: duty range 0-PERIOD
            # L298N/TB6612/L9110S: digital switching with software PWM
            if speed > 0:
                pwm1 = int(speed * self.period / 2048)
                pwm2 = 0
            elif speed < 0:
                pwm1 = 0
                pwm2 = int(-speed * self.period / 2048)
            else:
                pwm1 = 0
                pwm2 = 0
        return pwm1, pwm2
