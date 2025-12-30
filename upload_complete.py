#!/usr/bin/env python3
"""
Complete upload script for CyberBrick V7RC
Uploads all files and directories to ESP32-C3
"""
import serial
import time
import os
import sys
import glob

PORT = 'COM28'
BAUD = 115200

def send_ctrl_c(ser):
    """Send Ctrl+C to interrupt running code"""
    ser.write(b'\x03')
    time.sleep(0.5)
    ser.read_all()

def enter_raw_repl(ser, retries=10):
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
        
        print(f"  Retrying...")
        time.sleep(1)
    
    return False

def exec_raw(ser, cmd):
    """Execute command in raw REPL"""
    # Send command
    ser.write(cmd.encode() + b'\r\n')
    time.sleep(0.1)
    
    # Execute with Ctrl+D
    ser.write(b'\x04')
    time.sleep(0.5)
    
    # Read response
    response = ser.read_all()
    return response

def upload_file(ser, local_path, remote_path):
    """Upload a single file"""
    print(f"  Uploading {local_path} -> {remote_path}")
    
    with open(local_path, 'rb') as f:
        content = f.read()
    
    # Escape content for Python string
    content_repr = repr(content)
    
    # Create command to write file
    cmd = f"f=open('{remote_path}','wb');f.write({content_repr});f.close()"
    
    response = exec_raw(ser, cmd)
    
    if b'OK' in response or len(response) < 100:
        print(f"    ✓ {os.path.basename(local_path)}")
        return True
    else:
        print(f"    ✗ Failed: {os.path.basename(local_path)}")
        return False

def create_dir(ser, dir_path):
    """Create directory on device"""
    cmd = f"import os;os.mkdir('{dir_path}')"
    exec_raw(ser, cmd)

def main():
    print("=" * 60)
    print("CyberBrick V7RC Complete Upload Script")
    print("=" * 60)
    
    # Open serial connection
    print(f"\nConnecting to {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUD, timeout=3)
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
    
    print("\n" + "=" * 60)
    print("Uploading files...")
    print("=" * 60)
    
    # Upload root files
    print("\n[1/4] Root files:")
    for f in ['boot.py', 'bbl_product.py']:
        if not upload_file(ser, f, f):
            print(f"✗ Upload failed at {f}")
            ser.close()
            return 1
    
    # Create and upload bbl directory
    print("\n[2/4] bbl/ directory:")
    create_dir(ser, 'bbl')
    bbl_files = glob.glob('bbl/*.py')
    for f in bbl_files:
        remote = f.replace('\\', '/')
        if not upload_file(ser, f, remote):
            print(f"✗ Upload failed at {f}")
            ser.close()
            return 1
    
    # Create and upload app directory
    print("\n[3/4] app/ directory:")
    create_dir(ser, 'app')
    app_files = glob.glob('app/*.py') + glob.glob('app/*.mpy')
    for f in app_files:
        remote = f.replace('\\', '/')
        if not upload_file(ser, f, remote):
            print(f"✗ Upload failed at {f}")
            ser.close()
            return 1
    
    print("\n" + "=" * 60)
    print("✓ All files uploaded successfully!")
    print("=" * 60)
    
    # Reset device
    print("\n[4/4] Resetting device...")
    ser.write(b'\x02')  # Exit raw REPL
    time.sleep(0.5)
    ser.write(b'import machine\r\n')
    ser.write(b'machine.reset()\r\n')
    time.sleep(1)
    
    ser.close()
    
    print("\n" + "=" * 60)
    print("✓ Upload completed! Device is resetting...")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
