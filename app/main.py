import uasyncio
import bbl.v7rc as v7rc
from bbl import ServosController, MotorsController, LEDController, MusicController
from bbl.v7rc_parser import V7RCParser

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
    while True:
        servos.timing_proc()  # Update servo stepping
        motors.motors_period_cb()  # Update motor PWM
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
            for i, led_data in enumerate(leds):
                led1.set_led_rgbm(
                    i,
                    led_data['r'],
                    led_data['g'],
                    led_data['b'],
                    led_data['mode'],
                    led_data['blink_ms']
                )
        
        elif cmd_type == 'LE2':
            # LE2: Second LED group
            leds = data['leds']
            print(f"[LE2] LEDs: {leds}")
            for i, led_data in enumerate(leds):
                led2.set_led_rgbm(
                    i,
                    led_data['r'],
                    led_data['g'],
                    led_data['b'],
                    led_data['mode'],
                    led_data['blink_ms']
                )
        
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
