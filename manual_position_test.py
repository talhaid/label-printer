#!/usr/bin/env python3
"""
Manual Position Testing for PCB Labels
Allows manual adjustment of X/Y coordinates for TSPL positioning
"""

import sys
from xprinter_pcb import XPrinterPCB

class ManualPositionTester:
    def __init__(self):
        self.printer = XPrinterPCB()
        # Starting position (current working position)
        self.x_pos1 = 100  # X position for line 1 (serial number)
        self.x_pos2 = 100  # X position for line 2 (date)
        self.y_pos1 = 40   # S/N line Y
        self.y_pos2 = 90   # Date line Y
        self.test_serial = "ATS542912923728"
        self.test_date = "25/08/2025"
        
    def print_current_status(self):
        print(f"\n=== Current Position Settings ===")
        print(f"Line 1 (S/N) X: {self.x_pos1}")
        print(f"Line 2 (Date) X: {self.x_pos2}")
        print(f"S/N Line Y: {self.y_pos1}")
        print(f"Date Line Y: {self.y_pos2}")
        print(f"Test Serial: {self.test_serial}")
        print(f"Test Date: {self.test_date}")
        print("="*35)
        
    def print_commands(self):
        print("\n=== Manual Position Commands ===")
        print("Line 1 (Serial Number):")
        print("  x1left, x1right - Move line 1 X left/right (-10/+10)")
        print("  x1l1, x1l5 - Move line 1 left 1 or 5 units")
        print("  x1r1, x1r5 - Move line 1 right 1 or 5 units")
        print("  x1=NUMBER - Set line 1 X to specific value")
        print("\nLine 2 (Date):")
        print("  x2left, x2right - Move line 2 X left/right (-10/+10)")
        print("  x2l1, x2l5 - Move line 2 left 1 or 5 units")
        print("  x2r1, x2r5 - Move line 2 right 1 or 5 units")
        print("  x2=NUMBER - Set line 2 X to specific value")
        print("\nBoth lines together:")
        print("  left, right - Move both X positions left/right (-10/+10)")
        print("  up, down - Move both Y positions up/down (-10/+10)")
        print("  x=NUMBER - Set both X positions to same value")
        print("\nY positioning:")
        print("  y1=NUMBER - Set S/N line Y to specific value")
        print("  y2=NUMBER - Set Date line Y to specific value")
        print("\nActions:")
        print("  print - Print test label with current settings")
        print("  status - Show current position settings")
        print("  reset - Reset to starting position")
        print("  quit - Exit the program")
        print("="*40)
        
    def test_print(self):
        """Create and send test TSPL commands with current coordinates"""
        print(f"\nSending TSPL commands:")
        print(f"Line 1 (S/N) at position ({self.x_pos1}, {self.y_pos1})")
        print(f"Line 2 (Date) at position ({self.x_pos2}, {self.y_pos2})")
        
        try:
            # Use a custom method that accepts different X positions for each line
            from xprinter_pcb import XPrinterPCB
            printer = XPrinterPCB()
            
            # Create TSPL commands with different X positions
            commands = b''
            commands += b'SIZE 40 mm, 20 mm\n'
            commands += b'GAP 2 mm, 0 mm\n'
            commands += b'DIRECTION 1,0\n'
            commands += b'REFERENCE 0,0\n'
            commands += b'OFFSET 0 mm\n'
            commands += b'SET TEAR ON\n'
            commands += b'CLS\n'
            
            # Line 1: Serial number with its own X position
            commands += f'TEXT {self.x_pos1},{self.y_pos1},"3",0,1,1,"{self.test_serial}"\n'.encode('utf-8')
            
            # Line 2: Date with its own X position
            commands += f'TEXT {self.x_pos2},{self.y_pos2},"3",0,1,1,"{self.test_date}"\n'.encode('utf-8')
            
            commands += b'PRINT 1,1\n'
            
            # Send to printer
            result = printer._send_to_printer(commands)
            
            if result:
                print("✅ Test label sent successfully!")
            else:
                print("❌ Failed to send test label")
            return result
        except Exception as e:
            print(f"❌ Error printing test label: {e}")
            return False
            
    def adjust_position(self, command):
        """Process position adjustment commands"""
        command = command.strip().lower()
        
        # Line 1 (Serial Number) adjustments
        if command == "x1left":
            self.x_pos1 -= 10
            print(f"Line 1 moved left: X1 = {self.x_pos1}")
        elif command == "x1right":
            self.x_pos1 += 10
            print(f"Line 1 moved right: X1 = {self.x_pos1}")
        elif command == "x1l1":
            self.x_pos1 -= 1
            print(f"Line 1 fine left: X1 = {self.x_pos1}")
        elif command == "x1l5":
            self.x_pos1 -= 5
            print(f"Line 1 left 5: X1 = {self.x_pos1}")
        elif command == "x1r1":
            self.x_pos1 += 1
            print(f"Line 1 fine right: X1 = {self.x_pos1}")
        elif command == "x1r5":
            self.x_pos1 += 5
            print(f"Line 1 right 5: X1 = {self.x_pos1}")
        elif command.startswith("x1="):
            try:
                self.x_pos1 = int(command[3:])
                print(f"Set Line 1 X position: {self.x_pos1}")
            except ValueError:
                print("❌ Invalid X1 value. Use: x1=NUMBER")
                
        # Line 2 (Date) adjustments
        elif command == "x2left":
            self.x_pos2 -= 10
            print(f"Line 2 moved left: X2 = {self.x_pos2}")
        elif command == "x2right":
            self.x_pos2 += 10
            print(f"Line 2 moved right: X2 = {self.x_pos2}")
        elif command == "x2l1":
            self.x_pos2 -= 1
            print(f"Line 2 fine left: X2 = {self.x_pos2}")
        elif command == "x2l5":
            self.x_pos2 -= 5
            print(f"Line 2 left 5: X2 = {self.x_pos2}")
        elif command == "x2r1":
            self.x_pos2 += 1
            print(f"Line 2 fine right: X2 = {self.x_pos2}")
        elif command == "x2r5":
            self.x_pos2 += 5
            print(f"Line 2 right 5: X2 = {self.x_pos2}")
        elif command.startswith("x2="):
            try:
                self.x_pos2 = int(command[3:])
                print(f"Set Line 2 X position: {self.x_pos2}")
            except ValueError:
                print("❌ Invalid X2 value. Use: x2=NUMBER")
                
        # Both lines together
        elif command == "left":
            self.x_pos1 -= 10
            self.x_pos2 -= 10
            print(f"Both moved left: X1 = {self.x_pos1}, X2 = {self.x_pos2}")
        elif command == "right":
            self.x_pos1 += 10
            self.x_pos2 += 10
            print(f"Both moved right: X1 = {self.x_pos1}, X2 = {self.x_pos2}")
        elif command == "up":
            self.y_pos1 -= 10
            self.y_pos2 -= 10
            print(f"Moved up: Y1 = {self.y_pos1}, Y2 = {self.y_pos2}")
        elif command == "down":
            self.y_pos1 += 10
            self.y_pos2 += 10
            print(f"Moved down: Y1 = {self.y_pos1}, Y2 = {self.y_pos2}")
        elif command.startswith("x="):
            try:
                value = int(command[2:])
                self.x_pos1 = value
                self.x_pos2 = value
                print(f"Set both X positions: X1 = X2 = {value}")
            except ValueError:
                print("❌ Invalid X value. Use: x=NUMBER")
                
        # Y positioning
        elif command.startswith("y1="):
            try:
                self.y_pos1 = int(command[3:])
                print(f"Set S/N Y position: {self.y_pos1}")
            except ValueError:
                print("❌ Invalid Y1 value. Use: y1=NUMBER")
        elif command.startswith("y2="):
            try:
                self.y_pos2 = int(command[3:])
                print(f"Set Date Y position: {self.y_pos2}")
            except ValueError:
                print("❌ Invalid Y2 value. Use: y2=NUMBER")
                
        elif command == "reset":
            self.x_pos1 = 100
            self.x_pos2 = 100
            self.y_pos1 = 40
            self.y_pos2 = 90
            print("Reset to starting position: X1=X2=100, Y1=40, Y2=90")
        else:
            print(f"❌ Unknown command: {command}")
            
    def run_interactive(self):
        """Main interactive loop"""
        print("🏷️  PCB Label Position Tester")
        print("Interactive coordinate adjustment for XPrinter PCB labels")
        self.print_commands()
        self.print_current_status()
        
        while True:
            try:
                user_input = input("\nEnter command (or 'help' for commands): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                elif user_input.lower() in ['help', 'commands']:
                    self.print_commands()
                elif user_input.lower() == 'status':
                    self.print_current_status()
                elif user_input.lower() == 'print':
                    self.test_print()
                else:
                    self.adjust_position(user_input)
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--quick-test":
        # Quick test mode for immediate printing
        tester = ManualPositionTester()
        print("Quick test mode - printing current position...")
        tester.print_current_status()
        tester.test_print()
    else:
        # Interactive mode
        tester = ManualPositionTester()
        tester.run_interactive()

if __name__ == "__main__":
    main()