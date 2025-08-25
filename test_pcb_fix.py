#!/usr/bin/env python3
"""
PCB Status Detection Test
Verifies that the GUI correctly shows PCB printing status.
"""

import time
import serial

def send_test_device():
    """Send a test device through COM7 to verify PCB status detection."""
    print("=== PCB Status Detection Test ===\n")
    
    try:
        print("Connecting to COM7...")
        with serial.Serial('COM7', 115200, timeout=2) as ser:
            print("✅ Connected to COM7")
            
            # Clear any existing data
            ser.reset_input_buffer()
            
            # Test data with unique serial number
            test_data = "##PCB999888777666|999888777666555|999888777666555|9999888877766655|EE:FF:00:11:22:33##"
            
            print(f"\nSending test data: {test_data}")
            
            # Send the data
            ser.write(test_data.encode('utf-8'))
            ser.write(b'\n')
            
            print("✅ Test data sent successfully!")
            
            print("\n📋 Instructions:")
            print("1. Check the GUI - Device Labels tab should show the new device as 'Printed'")
            print("2. Check the GUI - PCB Labels tab should show:")
            print("   - If XPrinter printed successfully: Status = 'Printed'")
            print("   - If XPrinter failed: Status = 'Failed'")
            print("3. The PCB status should accurately reflect actual XPrinter behavior")
            print("\n🔍 What to verify:")
            print("- Device: PCB999888777666")
            print("- PCB status should match actual XPrinter output")
            print("- Previously the bug showed 'Printed' even when XPrinter failed")
            
    except serial.SerialException as e:
        print(f"❌ Failed to connect to COM7: {e}")
        print("\nPossible solutions:")
        print("- Make sure GUI is running and connected")
        print("- Check if COM7 is available")
        print("- Restart the device")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    send_test_device()