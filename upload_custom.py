#!/usr/bin/env python3
"""
Custom upload script for ESP32-C3 MicroPython
Handles timing issues better than mpremote
"""
import serial
import time
import os
import sys

PORT = 'COM28'
BAUD = 115200

def send_ctrl_c(ser):
    """Send Ctrl+C to interrupt running code"""
    ser.write(b'\x03')
    time.sleep(0.5)
    ser.read_all()

def enter_raw_repl(ser, retries=5):
    """Enter raw REPL mode with retries"""
    for attempt in range(retries):
        print(f"Attempting to enter raw REPL (attempt {attempt + 1}/{retries})...")
        
        # Send Ctrl+C to interrupt
        send_ctrl_c(ser)
        
        # Send Ctrl+A to enter raw REPL
        ser.write(b'\x01')
        time.sleep(1)
        
        # Read response
        response = ser.read_all()
        if b'raw REPL; CTRL-B to exit' in response:
            print("✓ Entered raw REPL successfully!")
            return True
        
        print(f"  Failed, retrying...")
        time.sleep(1)
    
    return False

def upload_file(ser, local_path, remote_path):
    """Upload a single file"""
    print(f"Uploading {local_path} -> {remote_path}")
    
    with open(local_path, 'rb') as f:
        content = f.read()
    
    # Create command to write file
    cmd = f"f=open('{remote_path}','wb');f.write({content!r});f.close()\r\n"
    
    # Send command
    ser.write(cmd.encode())
    time.sleep(0.5)
    
    # Execute
    ser.write(b'\x04')
    time.sleep(1)
    
    response = ser.read_all()
    if b'OK' in response or b'>>>' in response:
        print(f"  ✓ Uploaded {os.path.basename(local_path)}")
        return True
    else:
        print(f"  ✗ Failed to upload {os.path.basename(local_path)}")
        return False

def main():
    print("=" * 50)
    print("Custom MicroPython Upload Script")
    print("=" * 50)
    
    # Open serial connection
    print(f"\nConnecting to {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        time.sleep(2)
        print("✓ Connected!")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return 1
    
    # Enter raw REPL
    if not enter_raw_repl(ser):
        print("✗ Could not enter raw REPL")
        ser.close()
        return 1
    
    # Upload files
    files_to_upload = [
        ('boot.py', 'boot.py'),
        ('bbl_product.py', 'bbl_product.py'),
    ]
    
    for local, remote in files_to_upload:
        if not upload_file(ser, local, remote):
            print(f"✗ Upload failed at {local}")
            ser.close()
            return 1
    
    print("\n" + "=" * 50)
    print("✓ Upload completed successfully!")
    print("=" * 50)
    
    # Reset device
    print("\nResetting device...")
    ser.write(b'\x02')  # Exit raw REPL
    time.sleep(0.5)
    ser.write(b'import machine\r\n')
    ser.write(b'machine.reset()\r\n')
    
    ser.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
