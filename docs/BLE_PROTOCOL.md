# BLE Protocol Documentation
# CyberBrick V7RC Controller

## Overview

CyberBrick V7RC supports BLE (Bluetooth Low Energy) connectivity using the **Nordic UART Service (NUS)** standard. This allows wireless control via BLE-capable devices without requiring WiFi.

## BLE Service Details

### Service UUID
```
6E400001-B5A3-F393-E0A9-E50E24DCCA9E
```

### Characteristics

#### RX Characteristic (Write)
- **UUID**: `6E400002-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: WRITE, WRITE_NO_RESPONSE
- **Purpose**: Receive V7RC commands from BLE client
- **Data Format**: 20 bytes, same as UDP V7RC protocol

#### TX Characteristic (Notify)
- **UUID**: `6E400003-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: READ, NOTIFY
- **Purpose**: Send status updates to BLE client (optional)
- **Data Format**: JSON or plain text

## Connection Procedure

### 1. Scan for BLE Devices
Use a BLE scanner app to find device named **"CyberBrick_V7RC"**

### 2. Connect to Device
No pairing required (open connection)

### 3. Discover Services
Find service UUID: `6E400001-B5A3-F393-E0A9-E50E24DCCA9E`

### 4. Send V7RC Commands
Write 20-byte V7RC commands to RX characteristic:
```
6E400002-B5A3-F393-E0A9-E50E24DCCA9E
```

## V7RC Command Format

All commands are **exactly 20 bytes** with `#` terminator:

### Examples

#### Servo Control (SRV)
```
SRV1500150015001500#
```

#### Motor Control (SRT)
```
SRT1800120000000000#
```

#### LED Control
```
LED0F050F050F050F05#
```

#### Simplified 8-Channel (SS8)
```
SS896969696969696969#
```

## Compatible BLE Apps

### Android
- **Serial Bluetooth Terminal** (free)
- **nRF Connect** (Nordic Semiconductor)
- **BLE Terminal** (various)

### iOS
- **LightBlue** (free)
- **nRF Connect** (Nordic Semiconductor)
- **BLE Terminal** (various)

### Desktop
- **nRF Connect Desktop** (Windows/Mac/Linux)
- **Web Bluetooth** (Chrome/Edge browser)

## Example: Python BLE Client

```python
import asyncio
from bleak import BleakClient, BleakScanner

# UUIDs
SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

async def send_v7rc_command(address, command):
    """Send V7RC command via BLE"""
    async with BleakClient(address) as client:
        # Ensure command is 20 bytes
        if len(command) != 20:
            raise ValueError("Command must be exactly 20 bytes")
        
        # Write to RX characteristic
        await client.write_gatt_char(RX_UUID, command.encode())
        print(f"Sent: {command}")

async def main():
    # Scan for CyberBrick
    print("Scanning for CyberBrick...")
    devices = await BleakScanner.discover()
    
    cyberbrick = None
    for device in devices:
        if "CyberBrick" in device.name:
            cyberbrick = device
            break
    
    if not cyberbrick:
        print("CyberBrick not found!")
        return
    
    print(f"Found: {cyberbrick.name} ({cyberbrick.address})")
    
    # Send commands
    await send_v7rc_command(cyberbrick.address, "SRV1500150015001500#")
    await asyncio.sleep(1)
    await send_v7rc_command(cyberbrick.address, "LED0F050F050F050F05#")

# Run
asyncio.run(main())
```

## Example: Web Bluetooth (JavaScript)

```javascript
// Web Bluetooth API (Chrome/Edge only)
const SERVICE_UUID = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
const RX_UUID = '6e400002-b5a3-f393-e0a9-e50e24dcca9e';

async function connectCyberBrick() {
    try {
        // Request device
        const device = await navigator.bluetooth.requestDevice({
            filters: [{ name: 'CyberBrick_V7RC' }],
            optionalServices: [SERVICE_UUID]
        });
        
        // Connect to GATT server
        const server = await device.gatt.connect();
        const service = await server.getPrimaryService(SERVICE_UUID);
        const rxChar = await service.getCharacteristic(RX_UUID);
        
        // Send V7RC command
        const command = "SRV1500150015001500#";
        const encoder = new TextEncoder();
        await rxChar.writeValue(encoder.encode(command));
        
        console.log("Command sent:", command);
    } catch (error) {
        console.error("Error:", error);
    }
}

// Call function
connectCyberBrick();
```

## Configuration

### Enable/Disable BLE

Edit `bbl/config.py`:

```python
# Disable BLE
BLE_ENABLED = False

# Enable BLE
BLE_ENABLED = True
```

### Change Device Name

```python
BLE_DEVICE_NAME = "MyRobot_V7RC"
```

### Connection Modes

```python
# WiFi only (original mode)
CONNECTION_MODE = 'WIFI'

# BLE only (lower power)
CONNECTION_MODE = 'BLE'

# Both WiFi and BLE (default)
CONNECTION_MODE = 'BOTH'
```

## Troubleshooting

### Device Not Discoverable

1. Check `BLE_ENABLED = True` in `config.py`
2. Verify `CONNECTION_MODE` includes `'BLE'`
3. Restart ESP32-C3
4. Check serial log for `[ble] Advertising as 'CyberBrick_V7RC'`

### Connection Drops

1. Move closer to ESP32-C3 (BLE range ~10-30m)
2. Reduce WiFi interference
3. Check battery level (low power can cause disconnects)

### Commands Not Working

1. Verify command is exactly 20 bytes
2. Check command ends with `#`
3. Use serial monitor to see if command is received
4. Test same command via WiFi to verify it works

### BLE and WiFi Interference

If experiencing issues with concurrent WiFi + BLE:

```python
# Use BLE only
CONNECTION_MODE = 'BLE'
```

Or:

```python
# Use WiFi only
CONNECTION_MODE = 'WIFI'
```

## Performance Comparison

| Feature | WiFi UDP | BLE |
|---------|----------|-----|
| **Range** | ~50m | ~10-30m |
| **Latency** | ~10ms | ~20-50ms |
| **Power** | Higher | Lower |
| **Setup** | Connect to AP | Pair device |
| **Multi-client** | Yes | Single connection |
| **Throughput** | Higher | Lower |

## Security

Current implementation uses **open BLE connection** (no pairing required) for ease of use.

For production/public demos, consider enabling BLE security:
- Pairing with PIN
- Bonding (remember paired devices)
- Encrypted connection

(Security features to be added in future update)

## Notes

- BLE uses **Nordic UART Service (NUS)** standard
- Compatible with most BLE UART terminal apps
- Same V7RC protocol as WiFi (no app changes needed)
- BLE runs in background via IRQ (no async task needed)
- Auto-reconnect on disconnect (if enabled)
