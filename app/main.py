import uasyncio
import bbl.v7rc as v7rc
from bbl import ServosController, MotorsController, LEDController, MusicController
from bbl.v7rc_parser import V7RCParser

# Import motor driver configuration
try:
    from bbl.config import MOTOR_DRIVER_TYPE, MOTOR_DRIVER_CONFIG
except ImportError:
    MOTOR_DRIVER_TYPE = 'L298N'
    MOTOR_DRIVER_CONFIG = {'L298N': {'use_hardware_pwm': False}}

# Initialize all controllers
servos = ServosController()
motors = MotorsController()
led1 = LEDController('LED1')
led2 = LEDController('LED2')  # Second LED group for LE2 command
music = MusicController('BUZZER1', volume=50)

# Initialize V7RC parser
parser = V7RCParser(log_func=print)

# Periodic task to update servo stepping and motor PWM
async def periodic_update():
    """Update servos and motors at regular intervals"""
    # Determine if we need to call motor callback
    driver_config = MOTOR_DRIVER_CONFIG.get(
        motors.driver_type if hasattr(motors, 'driver_type') else MOTOR_DRIVER_TYPE,
        {'use_hardware_pwm': False}
    )
    use_motor_callback = not driver_config['use_hardware_pwm']
    
    while True:
        servos.timing_proc()  # Update servo stepping
        
        # Only call motor callback for software PWM (L298N/TB6612)
        if use_motor_callback:
            motors.motors_period_cb()  # Update motor software PWM
        
        led1.timing_proc()  # Update LED1 effects
        led2.timing_proc()  # Update LED2 effects
        await uasyncio.sleep_ms(10)  # 100Hz update rate

# V7RC command handler
def handle_v7rc_command(msg, addr):
    """
    Process incoming V7RC UDP commands
    
    Supported V7RC Commands (all 20 bytes with '#' terminator):
    - SRV: Basic PWM control (4 channels)
    - SR2: Second PWM group (C5-C8) - not supported (only 4 servos)
    - SS8: Simplified 8-channel PWM
    - SRT: Tank mode PWM
    - LED: 4 LED control with RGBM format
    - LE2: Second LED group
    """
    print(f"[v7rc] UDP received: {msg} from {addr}")
    
    # Parse V7RC command
    result = parser.parse(msg)
    if not result:
        return
    
    cmd_type = result['type']
    data = result['data']
    
    try:
        if cmd_type == 'SRV':
            # SRV: Basic PWM control for servos C1-C4
            pwm_values = data['pwm']
            print(f"[SRV] PWM: {pwm_values}")
            for i in range(min(4, len(pwm_values))):
                if pwm_values[i] > 0:  # Only update non-zero values
                    servos.set_pwm(i + 1, pwm_values[i])
        
        elif cmd_type == 'SR2':
            # SR2: Second PWM group (C5-C8) - not supported
            print("[SR2] Warning: Only 4 servos supported (C1-C4). SR2 command ignored.")
        
        elif cmd_type == 'SS8':
            # SS8: Simplified 8-channel PWM
            # First 4 channels → servos, channels 5-6 → motors (optional)
            pwm_values = data['pwm']
            print(f"[SS8] PWM: {pwm_values}")
            
            # Control servos (channels 1-4)
            for i in range(min(4, len(pwm_values))):
                if pwm_values[i] > 0:
                    servos.set_pwm(i + 1, pwm_values[i])
            
            # Optionally control motors with channels 5-6
            # Uncomment if you want SS8 to control motors:
            # if len(pwm_values) >= 6:
            #     # Map PWM 0-2550 to motor speed -2048 to +2048
            #     # 1275 is neutral
            #     motor1_speed = int((pwm_values[4] - 1275) * 2048 / 1275)
            #     motor2_speed = int((pwm_values[5] - 1275) * 2048 / 1275)
            #     motors.set_speed(1, motor1_speed)
            #     motors.set_speed(2, motor2_speed)
        
        elif cmd_type == 'SRT':
            # SRT: Tank mode PWM
            throttle = data['throttle']
            steering = data['steering']
            print(f"[SRT] Throttle: {throttle}, Steering: {steering}")
            motors.set_tank_mode(throttle, steering)
            
            # Also control servos C3-C4 if provided
            pwm_values = data['pwm']
            if len(pwm_values) >= 4:
                for i in range(2, 4):
                    if pwm_values[i] > 0:
                        servos.set_pwm(i + 1, pwm_values[i])
        
        elif cmd_type == 'LED':
            # LED: 4 LED control with RGBM format
            leds = data['leds']
            print(f"[LED] LEDs: {leds}")
            
            # Group LEDs by (color, mode, blink_ms) to apply effects efficiently
            # This prevents each LED from overwriting the previous one
            led_groups = {}
            for i, led_data in enumerate(leds):
                key = (led_data['r'], led_data['g'], led_data['b'], 
                       led_data['mode'], led_data['blink_ms'])
                if key not in led_groups:
                    led_groups[key] = []
                led_groups[key].append(i)
            
            # Apply effect for each group
            for (r, g, b, mode, blink_ms), led_indices in led_groups.items():
                # Create bitmask for all LEDs in this group
                led_mask = sum(1 << idx for idx in led_indices)
                rgb = (r << 16) | (g << 8) | b
                
                if mode == 'off':
                    led1.set_led_effect(0, 0, 1, led_mask, 0x000000)
                elif mode == 'solid':
                    led1.set_led_effect(0, 0, 0xFF, led_mask, rgb)
                elif mode == 'blink':
                    duration = blink_ms * 2 if blink_ms > 0 else 1000
                    led1.set_led_effect(1, duration, 0xFF, led_mask, rgb)
        
        elif cmd_type == 'LE2':
            # LE2: Second LED group
            leds = data['leds']
            print(f"[LE2] LEDs: {leds}")
            
            # Group LEDs by (color, mode, blink_ms) to apply effects efficiently
            led_groups = {}
            for i, led_data in enumerate(leds):
                key = (led_data['r'], led_data['g'], led_data['b'], 
                       led_data['mode'], led_data['blink_ms'])
                if key not in led_groups:
                    led_groups[key] = []
                led_groups[key].append(i)
            
            # Apply effect for each group
            for (r, g, b, mode, blink_ms), led_indices in led_groups.items():
                led_mask = sum(1 << idx for idx in led_indices)
                rgb = (r << 16) | (g << 8) | b
                
                if mode == 'off':
                    led2.set_led_effect(0, 0, 1, led_mask, 0x000000)
                elif mode == 'solid':
                    led2.set_led_effect(0, 0, 0xFF, led_mask, rgb)
                elif mode == 'blink':
                    duration = blink_ms * 2 if blink_ms > 0 else 1000
                    led2.set_led_effect(1, duration, 0xFF, led_mask, rgb)
        
    except Exception as e:
        print(f"[v7rc] Handler error: {e}")

# Initialize V7RC with custom callback
start = v7rc.init_ap(
    essid='cyber_V7RC',
    password='12341234',
    udp_ip='192.168.4.1',
    udp_port=6188,
    use_default_led=True,  # Enable built-in LED (GPIO 8)
    cb=handle_v7rc_command
)

# Main async function
async def main():
    """Run V7RC server and periodic updates"""
    await uasyncio.gather(
        start(),
        periodic_update()
    )

# Run the application
uasyncio.run(main())
