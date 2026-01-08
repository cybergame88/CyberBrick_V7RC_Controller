# -*- coding: utf-8 -*-
"""
BLE GATT Service for V7RC Protocol
CyberBrick V7RC Controller

Provides BLE connectivity for V7RC commands using standard BLE UART service UUIDs.
Compatible with generic BLE UART terminal apps.
"""

import bluetooth
from micropython import const
import struct

# BLE Events
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_GATTS_INDICATE_DONE = const(7)

# BLE UUIDs (using standard Nordic UART Service)
_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_RX_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")  # Write (RX from client)
_TX_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")  # Notify (TX to client)

# BLE Flags
_FLAG_READ = const(0x0002)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)


class BLEService:
    """
    BLE GATT Service for V7RC Protocol
    
    Implements Nordic UART Service (NUS) for V7RC command reception.
    Compatible with BLE UART terminal apps.
    
    Example:
        >>> def command_handler(data, addr):
        ...     print(f"Received: {data}")
        >>> 
        >>> ble = BLEService(name="CyberBrick", callback=command_handler)
        >>> # BLE service runs in background via IRQ
    """
    
    def __init__(self, name="Cyber_V7RC", callback=None):
        """
        Initialize BLE GATT service
        
        Args:
            name (str): BLE device name for advertising
            callback (function): Callback(data, addr) when V7RC command received
                - data: bytes, V7RC command (20 bytes)
                - addr: tuple, BLE client address (for logging)
        """
        self.name = name
        self.callback = callback
        self._conn_handle = None
        self._rx_handle = None
        self._tx_handle = None
        
        # Initialize BLE
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq_handler)
        
        # Register GATT services
        self._register_services()
        
        # Start advertising
        self._advertise()
        
        print(f"[ble] Initialized: {name}")
    
    def _register_services(self):
        """
        Register V7RC GATT service and characteristics
        
        Service: Nordic UART Service (NUS)
        - RX Characteristic: Client writes V7RC commands here
        - TX Characteristic: Server sends status/responses here (optional)
        """
        # Define characteristics
        # RX: WRITE + WRITE_NO_RESPONSE (client → server)
        # TX: NOTIFY (server → client)
        
        NUS = (
            _SERVICE_UUID,
            (
                (_RX_UUID, _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE),
                (_TX_UUID, _FLAG_NOTIFY | _FLAG_READ),
            ),
        )
        
        # Register services
        services = (NUS,)
        ((self._rx_handle, self._tx_handle),) = self.ble.gatts_register_services(services)
        
        print("[ble] GATT services registered")
    
    def _advertise(self, interval_us=500000):
        """
        Start BLE advertising
        
        Args:
            interval_us (int): Advertising interval in microseconds (default: 500ms)
        """
        # Advertising payload
        # Format: Flags + Complete Local Name
        name_bytes = self.name.encode('utf-8')
        
        # Flags: General Discoverable + BR/EDR Not Supported
        adv_data = bytearray(b'\x02\x01\x06')  # Flags
        
        # Complete Local Name
        adv_data.extend(struct.pack('BB', len(name_bytes) + 1, 0x09))
        adv_data.extend(name_bytes)
        
        # Start advertising
        self.ble.gap_advertise(interval_us, adv_data=adv_data)
        print(f"[ble] Advertising as '{self.name}'")
    
    def _irq_handler(self, event, data):
        """
        Handle BLE IRQ events
        
        Events:
        - CENTRAL_CONNECT: Client connected
        - CENTRAL_DISCONNECT: Client disconnected
        - GATTS_WRITE: Client wrote data to RX characteristic
        """
        if event == _IRQ_CENTRAL_CONNECT:
            # Client connected
            conn_handle, addr_type, addr = data
            self._conn_handle = conn_handle
            addr_str = ':'.join(['%02X' % b for b in bytes(addr)])
            print(f"[ble] Connected: {addr_str}")
        
        elif event == _IRQ_CENTRAL_DISCONNECT:
            # Client disconnected
            conn_handle, addr_type, addr = data
            self._conn_handle = None
            addr_str = ':'.join(['%02X' % b for b in bytes(addr)])
            print(f"[ble] Disconnected: {addr_str}")
            
            # Restart advertising
            self._advertise()
        
        elif event == _IRQ_GATTS_WRITE:
            # Client wrote data
            conn_handle, attr_handle = data
            
            if attr_handle == self._rx_handle:
                # Read data from RX characteristic
                data = self.ble.gatts_read(self._rx_handle)
                
                # Get client address for logging
                # Note: We don't have direct access to addr in WRITE event,
                # so we'll use a placeholder
                addr = ("BLE", 0)  # Placeholder address
                
                # Call callback with V7RC command
                if self.callback and len(data) == 20:
                    try:
                        self.callback(data, addr)
                    except Exception as e:
                        print(f"[ble] Callback error: {e}")
                elif len(data) != 20:
                    print(f"[ble] Invalid data length: {len(data)}, expected 20")
    
    def send(self, data):
        """
        Send data to connected BLE client via TX characteristic
        
        Args:
            data (bytes): Data to send (max 20 bytes for BLE)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if self._conn_handle is None:
            return False
        
        try:
            self.ble.gatts_notify(self._conn_handle, self._tx_handle, data)
            return True
        except Exception as e:
            print(f"[ble] Send error: {e}")
            return False
    
    def is_connected(self):
        """
        Check if a BLE client is connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._conn_handle is not None
    
    def disconnect(self):
        """
        Disconnect current BLE client
        """
        if self._conn_handle is not None:
            self.ble.gap_disconnect(self._conn_handle)
    
    def stop(self):
        """
        Stop BLE service and advertising
        """
        if self._conn_handle is not None:
            self.disconnect()
        
        self.ble.gap_advertise(None)  # Stop advertising
        self.ble.active(False)
        print("[ble] Stopped")


# Test code
if __name__ == '__main__':
    def test_callback(data, addr):
        print(f"Received from {addr}: {data}")
    
    ble = BLEService(name="Test_V7RC", callback=test_callback)
    print("BLE service running. Connect via BLE UART app and send 20-byte commands.")
    
    # Keep running
    import utime
    while True:
        utime.sleep(1)
