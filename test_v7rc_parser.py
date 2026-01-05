# -*- coding: utf-8 -*-
"""
V7RC Protocol Test Script
Tests the V7RC parser with various command formats
"""

import sys
sys.path.insert(0, 'bbl')

from v7rc_parser import V7RCParser

def test_parser():
    """Test V7RC parser with all command types"""
    parser = V7RCParser()
    
    print("=" * 60)
    print("V7RC Protocol Parser Test")
    print("=" * 60)
    
    # Test 1: SRV command
    print("\n[Test 1] SRV - Basic PWM Control")
    test_srv = b'SRV1500150015001500#'
    result = parser.parse(test_srv)
    print(f"Input:  {test_srv}")
    print(f"Result: {result}")
    assert result['type'] == 'SRV'
    assert result['data']['pwm'] == [1500, 1500, 1500, 1500]
    print("✓ PASS")
    
    # Test 2: SRV with different values
    print("\n[Test 2] SRV - Different PWM Values")
    test_srv2 = b'SRV0500100015002000#'
    result = parser.parse(test_srv2)
    print(f"Input:  {test_srv2}")
    print(f"Result: {result}")
    assert result['data']['pwm'] == [500, 1000, 1500, 2000]
    print("✓ PASS")
    
    # Test 3: SR2 command
    print("\n[Test 3] SR2 - Second PWM Group")
    test_sr2 = b'SR21200130014001500#'
    result = parser.parse(test_sr2)
    print(f"Input:  {test_sr2}")
    print(f"Result: {result}")
    assert result['type'] == 'SR2'
    assert result['data']['pwm'] == [1200, 1300, 1400, 1500]
    print("✓ PASS")
    
    # Test 4: SS8 command
    print("\n[Test 4] SS8 - Simplified 8-Channel PWM")
    test_ss8 = b'SS89696969696969696#'
    result = parser.parse(test_ss8)
    print(f"Input:  {test_ss8}")
    print(f"Result: {result}")
    assert result['type'] == 'SS8'
    # 0x96 = 150 decimal, × 10 = 1500
    assert result['data']['pwm'] == [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
    print("✓ PASS")
    
    # Test 5: SS8 with different values
    print("\n[Test 5] SS8 - Different Hex Values")
    test_ss8_2 = b'SS800326496AAFF0000#'
    result = parser.parse(test_ss8_2)
    print(f"Input:  {test_ss8_2}")
    print(f"Result: {result}")
    # 0x00=0, 0x32=50×10=500, 0x64=100×10=1000, 0x96=150×10=1500
    # 0xAA=170×10=1700, 0xFF=255×10=2550, 0x00=0, 0x00=0
    expected = [0, 500, 1000, 1500, 1700, 2550, 0, 0]
    assert result['data']['pwm'] == expected
    print("✓ PASS")
    
    # Test 6: SRT command (Tank mode)
    print("\n[Test 6] SRT - Tank Mode PWM")
    test_srt = b'SRT1800120000000000#'
    result = parser.parse(test_srt)
    print(f"Input:  {test_srt}")
    print(f"Result: {result}")
    assert result['type'] == 'SRT'
    assert result['data']['throttle'] == 1800
    assert result['data']['steering'] == 1200
    print("✓ PASS")
    
    # Test 7: LED command
    print("\n[Test 7] LED - 4 LED Control")
    test_led = b'LEDF00AF00AF00AF00A#'
    result = parser.parse(test_led)
    print(f"Input:  {test_led}")
    print(f"Result: {result}")
    assert result['type'] == 'LED'
    leds = result['data']['leds']
    # F00A = Red solid (R=F=255, G=0, B=0, M=A=solid)
    assert leds[0]['r'] == 255
    assert leds[0]['g'] == 0
    assert leds[0]['b'] == 0
    assert leds[0]['mode'] == 'solid'
    print("✓ PASS")
    
    # Test 8: LED with blink mode
    print("\n[Test 8] LED - Blink Mode")
    test_led2 = b'LED0F050F050F050F05#'
    result = parser.parse(test_led2)
    print(f"Input:  {test_led2}")
    print(f"Result: {result}")
    leds = result['data']['leds']
    # 0F05 = Green blink (R=0, G=F=255, B=0, M=5=500ms)
    assert leds[0]['r'] == 0
    assert leds[0]['g'] == 255
    assert leds[0]['b'] == 0
    assert leds[0]['mode'] == 'blink'
    assert leds[0]['blink_ms'] == 500
    print("✓ PASS")
    
    # Test 9: LE2 command
    print("\n[Test 9] LE2 - Second LED Group")
    test_le2 = b'LE200F0F00FF00FF00F#'
    result = parser.parse(test_le2)
    print(f"Input:  {test_le2}")
    print(f"Result: {result}")
    assert result['type'] == 'LE2'
    print("✓ PASS")
    
    # Test 10: Invalid length
    print("\n[Test 10] Invalid Length")
    test_invalid = b'SRV1500#'
    result = parser.parse(test_invalid)
    print(f"Input:  {test_invalid}")
    print(f"Result: {result}")
    assert result is None
    print("✓ PASS")
    
    # Test 11: Invalid terminator
    print("\n[Test 11] Invalid Terminator")
    test_invalid2 = b'SRV1500150015001500!'
    result = parser.parse(test_invalid2)
    print(f"Input:  {test_invalid2}")
    print(f"Result: {result}")
    assert result is None
    print("✓ PASS")
    
    # Test 12: Unknown command
    print("\n[Test 12] Unknown Command Type")
    test_unknown = b'XXX1234567890123456#'
    result = parser.parse(test_unknown)
    print(f"Input:  {test_unknown}")
    print(f"Result: {result}")
    assert result is None
    print("✓ PASS")
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)

if __name__ == '__main__':
    test_parser()
