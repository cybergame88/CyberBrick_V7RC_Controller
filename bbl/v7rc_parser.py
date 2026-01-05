# -*- coding: utf-8 -*-
"""
V7RC Protocol Parser
Parses V7RC protocol commands according to V7RC_IO_Command_Protocol.pdf

Supported Commands (all 20 bytes with '#' terminator):
- SRV: Basic PWM control (4 channels, 4 digits each: 0000-2000)
- SR2: Second PWM group (C5-C8)
- SS8: Simplified 8-channel PWM (8 channels, 2 hex digits each: 00-FF)
- SRT: Tank mode PWM (same format as SRV, but CH1/CH2 used for tank control)
- LED: 4 LED control with RGBM format (4 LEDs × 4 chars)
- LE2: Second LED group (same format as LED)
"""


class V7RCParser:
    """Parser for V7RC protocol commands"""

    def __init__(self, log_func=print):
        """
        Initialize V7RC parser
        
        Args:
            log_func: Function to use for logging (default: print)
        """
        self.log = log_func

    def parse(self, msg):
        """
        Parse V7RC command and return structured data
        
        Args:
            msg (bytes): Raw UDP message
            
        Returns:
            dict: {
                'type': 'SRV'|'SR2'|'SS8'|'SRT'|'LED'|'LE2'|None,
                'data': {...}  # Command-specific data
            }
            Returns None if parsing fails
        """
        if not msg or len(msg) != 20:
            self.log(f"[v7rc_parser] Invalid length: {len(msg) if msg else 0}, expected 20")
            return None

        # Check terminator
        if not msg.endswith(b'#'):
            self.log(f"[v7rc_parser] Missing '#' terminator")
            return None

        try:
            # Extract command type (first 3 bytes)
            cmd_type = msg[:3].decode('ascii')
            # Extract data (bytes 3-19, excluding '#')
            data_str = msg[3:19].decode('ascii')

            # Route to appropriate parser
            if cmd_type == 'SRV':
                return {'type': 'SRV', 'data': self._parse_srv(data_str)}
            elif cmd_type == 'SR2':
                return {'type': 'SR2', 'data': self._parse_sr2(data_str)}
            elif cmd_type == 'SS8':
                return {'type': 'SS8', 'data': self._parse_ss8(data_str)}
            elif cmd_type == 'SRT':
                return {'type': 'SRT', 'data': self._parse_srt(data_str)}
            elif cmd_type == 'LED':
                return {'type': 'LED', 'data': self._parse_led(data_str)}
            elif cmd_type == 'LE2':
                return {'type': 'LE2', 'data': self._parse_le2(data_str)}
            else:
                self.log(f"[v7rc_parser] Unknown command type: {cmd_type}")
                return None

        except Exception as e:
            self.log(f"[v7rc_parser] Parse error: {e}")
            return None

    def _parse_srv(self, data):
        """
        Parse SRV command: 4 PWM values (0000-2000)
        Format: SRV1500150015001500#
        
        Args:
            data (str): 16-character data string
            
        Returns:
            dict: {'pwm': [ch1, ch2, ch3, ch4]} where values are 0-2000
        """
        if len(data) != 16:
            raise ValueError(f"SRV data length {len(data)}, expected 16")

        pwm_values = []
        for i in range(4):
            pwm_str = data[i*4:(i+1)*4]
            pwm_val = int(pwm_str)
            if not 0 <= pwm_val <= 2000:
                self.log(f"[v7rc_parser] SRV CH{i+1} out of range: {pwm_val}")
            pwm_values.append(pwm_val)

        return {'pwm': pwm_values}

    def _parse_sr2(self, data):
        """
        Parse SR2 command: 4 PWM values for C5-C8 (same format as SRV)
        Format: SR21500100018002000#
        
        Args:
            data (str): 16-character data string
            
        Returns:
            dict: {'pwm': [ch5, ch6, ch7, ch8]} where values are 0-2000
        """
        # Same format as SRV, but for channels 5-8
        result = self._parse_srv(data)
        return result

    def _parse_ss8(self, data):
        """
        Parse SS8 command: 8 hex values (00-FF) × 10 = PWM value
        Format: SS896969696969696#
        
        Args:
            data (str): 16-character data string (8 channels × 2 hex digits)
            
        Returns:
            dict: {'pwm': [ch1, ch2, ..., ch8]} where values are 0-2550
        """
        if len(data) != 16:
            raise ValueError(f"SS8 data length {len(data)}, expected 16")

        pwm_values = []
        for i in range(8):
            hex_str = data[i*2:(i+1)*2]
            hex_val = int(hex_str, 16)  # Convert hex to decimal
            pwm_val = hex_val * 10  # Multiply by 10 per protocol
            pwm_values.append(pwm_val)

        return {'pwm': pwm_values}

    def _parse_srt(self, data):
        """
        Parse SRT command: Tank mode PWM (same format as SRV)
        Format: SRT1500150015001500#
        CH1 = throttle, CH2 = steering (converted to tank control)
        
        Args:
            data (str): 16-character data string
            
        Returns:
            dict: {
                'throttle': int,  # CH1 value (0-2000)
                'steering': int,  # CH2 value (0-2000)
                'pwm': [ch1, ch2, ch3, ch4]  # Raw PWM values
            }
        """
        result = self._parse_srv(data)
        # Extract throttle and steering from first two channels
        result['throttle'] = result['pwm'][0]
        result['steering'] = result['pwm'][1]
        return result

    def _parse_led(self, data):
        """
        Parse LED command: 4 LEDs with RGBM format
        Format: LEDF00AF00AF00AF00A#
        Each LED: 4 chars (R, G, B, M)
        - R/G/B: 0-F hex (brightness)
        - M: 0-9 = blink (M×100ms on per second), A-F = solid
        
        Args:
            data (str): 16-character data string (4 LEDs × 4 chars)
            
        Returns:
            dict: {'leds': [
                {'r': 0-255, 'g': 0-255, 'b': 0-255, 'mode': 'solid'|'blink', 'blink_ms': int},
                ...
            ]}
        """
        if len(data) != 16:
            raise ValueError(f"LED data length {len(data)}, expected 16")

        leds = []
        for i in range(4):
            rgbm = data[i*4:(i+1)*4]
            r_hex = int(rgbm[0], 16)
            g_hex = int(rgbm[1], 16)
            b_hex = int(rgbm[2], 16)
            m_hex = int(rgbm[3], 16)

            # Convert 0-F to 0-255 (multiply by 17)
            r = r_hex * 17
            g = g_hex * 17
            b = b_hex * 17

            # Parse mode: 0-9 = blink, A-F (10-15) = solid
            if m_hex == 0:
                mode = 'off'
                blink_ms = 0
            elif m_hex < 10:
                mode = 'blink'
                blink_ms = m_hex * 100  # M×100ms on per second
            else:
                mode = 'solid'
                blink_ms = 0

            leds.append({
                'r': r,
                'g': g,
                'b': b,
                'mode': mode,
                'blink_ms': blink_ms
            })

        return {'leds': leds}

    def _parse_le2(self, data):
        """
        Parse LE2 command: Second LED group (same format as LED)
        Format: LE20111100000111110000022222#
        
        Args:
            data (str): 16-character data string
            
        Returns:
            dict: Same as _parse_led
        """
        return self._parse_led(data)


# Test code
if __name__ == '__main__':
    parser = V7RCParser()

    # Test SRV
    test_srv = b'SRV1500150015001500#'
    result = parser.parse(test_srv)
    print(f"SRV: {result}")

    # Test SS8
    test_ss8 = b'SS89696969696969696#'
    result = parser.parse(test_ss8)
    print(f"SS8: {result}")

    # Test SRT
    test_srt = b'SRT1800150000000000#'
    result = parser.parse(test_srt)
    print(f"SRT: {result}")

    # Test LED
    test_led = b'LEDF00AF00AF00AF00A#'
    result = parser.parse(test_led)
    print(f"LED: {result}")
