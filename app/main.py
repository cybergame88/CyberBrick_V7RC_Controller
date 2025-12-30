import uasyncio
import bbl.v7rc as v7rc
from bbl import ServosController, MotorsController, LEDController, MusicController

# Initialize all controllers
servos = ServosController()
motors = MotorsController()
led1 = LEDController('LED1')
music = MusicController('BUZZER1', volume=50)

# Periodic task to update servo stepping and motor PWM
async def periodic_update():
    """Update servos and motors at regular intervals"""
    while True:
        servos.timing_proc()  # Update servo stepping
        motors.motors_period_cb()  # Update motor PWM
        await uasyncio.sleep_ms(10)  # 100Hz update rate

# V7RC command parser and handler
def handle_v7rc_command(msg, addr):
    """
    Process incoming V7RC UDP commands
    
    V7RC Protocol Format: SS89AABBCCDDEEFFGG#
    - SS: Header (0x53 0x53)
    - 89: Command type
    - AA-GG: 7 data bytes (14 hex chars)
    - #: Terminator (0x23)
    
    Data byte mapping:
    - Byte 0-1 (AA-BB): Motor control
    - Byte 2 (CC): Unknown/reserved
    - Byte 3-6 (DD-EE-FF-GG): Servo 1-4 values
    """
    print(f"[v7rc] UDP received: {msg} from {addr}")
    
    if not msg or len(msg) < 20:
        return
    
    try:
        # Validate format
        if not msg.startswith(b'SS89') or not msg.endswith(b'#'):
            return
        
        # Extract hex data (remove 'SS89' and '#')
        data = msg[4:-1].decode('ascii')
        
        # Parse all data bytes
        bytes_data = []
        for i in range(7):
            hex_val = data[i*2:i*2+2]
            bytes_data.append(int(hex_val, 16))
        
        # --- MOTOR CONTROL ---
        # Bytes 0-1: Motor control (left/right or forward/reverse)
        motor1_val = bytes_data[0]  # Left motor / Motor A
        motor2_val = bytes_data[1]  # Right motor / Motor B
        
        # Map 0x00-0xFF to motor speed -2048 to +2048
        # 0x69 (105) is neutral/stop
        def map_motor_value(val):
            if val == 0x69:  # Neutral
                return 0
            elif val > 0x69:  # Forward
                return int(((val - 0x69) / (0xFF - 0x69)) * 2048)
            else:  # Reverse
                return -int(((0x69 - val) / 0x69) * 2048)
        
        speed1 = map_motor_value(motor1_val)
        speed2 = map_motor_value(motor2_val)
        
        if speed1 != 0 or speed2 != 0:
            print(f"[motor] M1: 0x{motor1_val:02X}→{speed1}, M2: 0x{motor2_val:02X}→{speed2}")
            motors.set_speed(1, speed1)
            motors.set_speed(2, speed2)
        else:
            motors.stop(1)
            motors.stop(2)
        
        # --- SERVO CONTROL ---
        # Bytes 3-6: Servo 1-4 values
        for i in range(4):
            servo_val = bytes_data[3 + i]
            
            # Only update if not neutral position
            if servo_val != 0x69:
                # Map 0x00-0xFF to 0-180 degrees
                angle = int((servo_val / 255.0) * 180)
                servo_idx = i + 1
                
                print(f"[servo] S{servo_idx}: 0x{servo_val:02X}→{angle}°")
                servos.set_angle(servo_idx, angle)
        
        # --- LED CONTROL (Optional) ---
        # You can add LED effects based on motor/servo activity
        # Example: Show green when motors active
        if speed1 != 0 or speed2 != 0:
            led1.set_led_effect(2, 0, 1, 0b1111, 0x00FF00)  # Solid green
        else:
            led1.set_led_effect(2, 0, 1, 0b1111, 0x0000FF)  # Solid blue
        
    except Exception as e:
        print(f"[parser] Error: {e}")

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

