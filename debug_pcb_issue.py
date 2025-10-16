#!/usr/bin/env python3
"""
🔥 EMERGENCY DEBUG: Check what's ACTUALLY being sent to XPrinter
This will tell us if the problem is in TSPL generation or elsewhere
"""

import sys
sys.path.append('.')

from serial_auto_printer import DeviceAutoPrinter

def debug_pcb_templates():
    """Debug what's actually being generated for PCB printing"""
    print("🔥 EMERGENCY DEBUG: PCB Template Issue")
    print("="*60)
    
    # Create test data
    device_data = {
        'SERIAL_NUMBER': '66182844496',
        'STC': '60000',
        'IMEI': '866988074133496',
        'IMSI': '286019876543210',
        'CCID': '8991101200003204510',
        'MAC_ADDRESS': 'AA:BB:CC:DD:EE:FF'
    }
    
    # Initialize printer with template
    template = "^XA^FO20,50^FD{SERIAL_NUMBER}^FS^XZ"
    printer = DeviceAutoPrinter(template, debug_mode=True)
    
    # Get the CURRENT PCB label data from the main method
    print("\n📋 CURRENT PCB TEMPLATE OUTPUT:")
    print("-"*40)
    
    pcb_data = printer._create_pcb_label_data(device_data)
    
    print(pcb_data)
    
    # Check if it contains TSPL or ZPL commands
    print("\n🔍 ANALYSIS:")
    print(f"Contains 'SIZE': {'SIZE' in pcb_data}")
    print(f"Contains 'TEXT': {'TEXT' in pcb_data}")
    print(f"Contains '^XA': {'^XA' in pcb_data}")  # ZPL start
    print(f"Contains '^FO': {'^FO' in pcb_data}")  # ZPL field origin
    print(f"Contains '^CF': {'^CF' in pcb_data}")  # ZPL change font
    print(f"Contains 'TSPL': {'TSPL' in pcb_data}")
    print(f"Contains 'GAP': {'GAP' in pcb_data}")
    
    # Check line by line
    print(f"\n📝 LINE ANALYSIS:")
    lines = pcb_data.strip().split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line:
            print(f"  {i:2d}: {line}")

if __name__ == "__main__":
    debug_pcb_templates()