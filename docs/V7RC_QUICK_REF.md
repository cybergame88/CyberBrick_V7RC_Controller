# V7RC Protocol Quick Reference

## Command Format (20 bytes)
```
[CMD][DATA................]#
```

## Commands

### SRV - Servo Control
```
SRV[PWM1][PWM2][PWM3][PWM4]#
Example: SRV1500150015001500#
```

### SR2 - Second Servo Group
```
SR2[PWM5][PWM6][PWM7][PWM8]#
Example: SR21200130014001500#
```

### SS8 - Simplified 8-Channel
```
SS8[HEX1][HEX2][HEX3][HEX4][HEX5][HEX6][HEX7][HEX8]#
Example: SS896969696969696#
Note: Hex value × 10 = PWM (0x96 = 150 × 10 = 1500)
```

### SRT - Tank Mode
```
SRT[THRT][STER][PWM3][PWM4]#
Example: SRT1500100000000000#
```

### LED - LED Control
```
LED[RGBM][RGBM][RGBM][RGBM]#
Example: LEDF00AF00AF00AF00A#

RGBM Format:
- R/G/B: 0-F (hex brightness)
- M: 0=off, 1-9=blink, A-F=solid
```

### LE2 - Second LED Group
```
LE2[RGBM][RGBM][RGBM][RGBM]#
Example: LE200F0F00FF00FF00F#
```

## Network Settings
- IP: 192.168.4.1
- Port: 6188
- SSID: cyber_V7RC
- Password: 12341234

## PowerShell Test
```powershell
$udp = New-Object System.Net.Sockets.UdpClient
$bytes = [System.Text.Encoding]::ASCII.GetBytes("SRV1500150015001500#")
$udp.Send($bytes, $bytes.Length, "192.168.4.1", 6188)
$udp.Close()
```
