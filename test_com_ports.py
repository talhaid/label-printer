#!/usr/bin/env python3
"""
COM Port Diagnostic Tool
Tests which COM ports are actually available and accessible.
"""

import serial
import serial.tools.list_ports
import time

def test_com_ports():
    """Test all available COM ports to find which ones work."""
    print("=== COM Port Diagnostic Tool ===\n")
    
    # List all detected ports
    print("1. Detected COM ports:")
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"   {port.device}: {port.description}")
    
    if not ports:
        print("   No COM ports detected!")
        return
    
    print("\n2. Testing port accessibility:")
    
    working_ports = []
    
    for port in ports:
        port_name = port.device
        print(f"\n   Testing {port_name}...")
        
        try:
            # Try to open the port briefly
            with serial.Serial(port_name, 115200, timeout=0.5) as ser:
                print(f"   ✅ {port_name}: Successfully opened")
                working_ports.append(port_name)
                
                # Try to read any available data
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    print(f"      📡 Data available: {len(data)} bytes")
                else:
                    print(f"      📡 No data available")
                    
        except serial.SerialException as e:
            print(f"   ❌ {port_name}: Failed - {e}")
        except Exception as e:
            print(f"   ❌ {port_name}: Unexpected error - {e}")
    
    print(f"\n3. Summary:")
    if working_ports:
        print(f"   Working ports: {', '.join(working_ports)}")
        print(f"   Recommended port for GUI: {working_ports[0]}")
    else:
        print("   No working ports found!")
        print("   Possible solutions:")
        print("   - Run as Administrator")
        print("   - Close other applications using COM ports")
        print("   - Check device connections")
        print("   - Restart the device")

if __name__ == "__main__":
    test_com_ports()