#!/usr/bin/env python3
"""
PCB Label Position Tester
=========================

Tool for testing different X/Y positions for PCB labels on XPrinter XP-470B
to help you adjust the positioning visually.
"""

import sys
import os
from xprinter_pcb import XPrinterPCB
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PCBPositionTester:
    """Test different positions for PCB labels."""
    
    def __init__(self):
        """Initialize the tester."""
        self.printer = XPrinterPCB()
        
    def test_position(self, stc_x=65, stc_y=20, serial_x=65, serial_y=50, date_x=65, date_y=80):
        """
        Test PCB label with custom positions.
        
        Args:
            stc_x, stc_y: Position for STC line
            serial_x, serial_y: Position for Serial Number line  
            date_x, date_y: Position for Date line
        """
        if not self.printer.is_available():
            print("❌ XPrinter XP-470B not found!")
            return False
            
        try:
            # Create custom TSPL commands with your specified positions
            commands = b''
            commands += b'SIZE 40 mm, 20 mm\n'  # Set label size to 4cm x 2cm
            commands += b'GAP 2 mm, 0 mm\n'     # Gap between labels
            commands += b'DIRECTION 1,0\n'       # Print direction
            commands += b'REFERENCE 0,0\n'       # Reference point
            commands += b'OFFSET 0 mm\n'         # Offset
            commands += b'SET TEAR ON\n'         # Tear mode
            commands += b'CLS\n'                 # Clear buffer
            
            # Custom positioned text
            commands += f'TEXT {stc_x},{stc_y},"3",0,1,1,"STC:60999"\n'.encode('utf-8')
            commands += f'TEXT {serial_x},{serial_y},"3",0,1,1,"TEST12345"\n'.encode('utf-8')
            commands += f'TEXT {date_x},{date_y},"3",0,1,1,"26/08/25"\n'.encode('utf-8')
            
            commands += b'PRINT 1,1\n'           # Print 1 copy
            
            # Send to printer
            success = self.printer._send_to_printer(commands)
            
            if success:
                print(f"✅ Test label printed with positions:")
                print(f"   STC: X={stc_x}, Y={stc_y}")
                print(f"   Serial: X={serial_x}, Y={serial_y}")
                print(f"   Date: X={date_x}, Y={date_y}")
            else:
                print("❌ Failed to print test label")
                
            return success
            
        except Exception as e:
            logger.error(f"Error printing test label: {e}")
            return False
    
    def test_grid_positions(self):
        """Test multiple positions in a grid pattern."""
        print("🔧 Testing grid positions...")
        
        positions = [
            # Format: (stc_x, stc_y, serial_x, serial_y, date_x, date_y, description)
            (50, 15, 50, 45, 50, 75, "Left aligned"),
            (65, 20, 65, 50, 65, 80, "Center aligned (current)"),
            (80, 25, 80, 55, 80, 85, "Right aligned"),
            (65, 10, 65, 40, 65, 70, "Compact vertical"),
            (65, 30, 65, 60, 65, 90, "Spread vertical"),
        ]
        
        for i, (sx, sy, srx, sry, dx, dy, desc) in enumerate(positions, 1):
            print(f"\n📍 Test {i}: {desc}")
            print(f"   Press Enter to print test {i}, or 'q' to quit...")
            
            user_input = input().strip().lower()
            if user_input == 'q':
                break
                
            self.test_position(sx, sy, srx, sry, dx, dy)
    
    def interactive_mode(self):
        """Interactive mode for custom positioning."""
        print("\n🎯 Interactive Position Testing")
        print("Enter coordinates for STC, Serial Number, and Date")
        print("Label size: 40mm x 20mm (coordinates in dots, ~3 dots per mm)")
        print("Safe range: X: 10-150, Y: 10-180")
        
        while True:
            try:
                print("\n" + "="*50)
                stc_x = int(input("STC X position (default 65): ") or 65)
                stc_y = int(input("STC Y position (default 20): ") or 20)
                
                serial_x = int(input("Serial X position (default 65): ") or 65)
                serial_y = int(input("Serial Y position (default 50): ") or 50)
                
                date_x = int(input("Date X position (default 65): ") or 65)
                date_y = int(input("Date Y position (default 80): ") or 80)
                
                print(f"\n🖨️  Printing test with:")
                print(f"   STC: ({stc_x}, {stc_y})")
                print(f"   Serial: ({serial_x}, {serial_y})")
                print(f"   Date: ({date_x}, {date_y})")
                
                self.test_position(stc_x, stc_y, serial_x, serial_y, date_x, date_y)
                
                print("\nContinue testing? (y/n): ", end="")
                if input().strip().lower() != 'y':
                    break
                    
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Exiting...")
                break

def main():
    """Main function."""
    print("🏷️  PCB Label Position Tester")
    print("==============================")
    
    tester = PCBPositionTester()
    
    if not tester.printer.is_available():
        print("❌ XPrinter XP-470B not found. Please check:")
        print("   1. Printer is connected via USB")
        print("   2. Printer is powered on")
        print("   3. Printer drivers are installed")
        return
    
    print("✅ XPrinter XP-470B found!")
    print("\nChoose testing mode:")
    print("1. Quick test with current position")
    print("2. Test grid positions")
    print("3. Interactive custom positioning")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🔍 Testing current position...")
        tester.test_position()
        
    elif choice == "2":
        tester.test_grid_positions()
        
    elif choice == "3":
        tester.interactive_mode()
        
    else:
        print("Invalid choice. Exiting...")

if __name__ == "__main__":
    main()