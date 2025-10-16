#!/usr/bin/env python3
"""
🔍 STEP-BY-STEP PCB PRINTING DIAGNOSTIC
Test each step of the PCB printing process to find the exact problem
"""

import sys
sys.path.append('.')

from serial_auto_printer import DeviceAutoPrinter
from zebra_zpl import ZebraZPL

def test_pcb_printing_steps():
    """Test each step of PCB printing process"""
    print("🔍 PCB PRINTING DIAGNOSTIC - STEP BY STEP")
    print("="*60)
    
    # Test data
    device_data = {
        'SERIAL_NUMBER': '66182844496',
        'STC': '60000',
        'IMEI': '866988074133496',
        'IMSI': '286019876543210',
        'CCID': '8991101200003204510',
        'MAC_ADDRESS': 'AA:BB:CC:DD:EE:FF'
    }
    
    print("📋 Test Data:")
    for key, value in device_data.items():
        print(f"  {key}: {value}")
    
    # STEP 1: Check available printers
    print(f"\n🖨️ STEP 1: Check Available Printers")
    print("-" * 40)
    temp_printer = ZebraZPL()
    printers = temp_printer.list_printers()
    print(f"Available printers: {len(printers)}")
    
    xprinter_found = None
    for printer in printers:
        print(f"  - {printer}")
        if 'xprinter' in printer.lower():
            xprinter_found = printer
            print(f"    ✅ XPrinter detected!")
    
    if not xprinter_found:
        print("❌ No XPrinter found! This is the problem.")
        return
    
    # STEP 2: Initialize PCB printer object  
    print(f"\n🔧 STEP 2: Initialize PCB Printer")
    print("-" * 40)
    try:
        pcb_printer = ZebraZPL(xprinter_found, debug_mode=True)  # Debug first
        print(f"✅ PCB printer initialized: {xprinter_found}")
    except Exception as e:
        print(f"❌ Failed to initialize PCB printer: {e}")
        return
    
    # STEP 3: Create DeviceAutoPrinter instance
    print(f"\n⚙️ STEP 3: Create Auto-Printer Instance") 
    print("-" * 40)
    try:
        template = "^XA^FO20,50^FD{SERIAL_NUMBER}^FS^XZ"
        auto_printer = DeviceAutoPrinter(
            template, 
            pcb_printer_name=xprinter_found,
            debug_mode=True
        )
        auto_printer.enable_pcb_printing(True)
        print(f"✅ Auto-printer created")
        print(f"  PCB printing enabled: {auto_printer.pcb_printing_enabled}")
        print(f"  PCB printer: {auto_printer.pcb_printer.printer_name if auto_printer.pcb_printer else 'None'}")
    except Exception as e:
        print(f"❌ Failed to create auto-printer: {e}")
        return
        
    # STEP 4: Test TSPL generation  
    print(f"\n📝 STEP 4: Test TSPL Generation")
    print("-" * 40)
    try:
        tspl_data = auto_printer._create_pcb_label_data(device_data)
        print(f"✅ TSPL generated ({len(tspl_data)} characters)")
        print(f"TSPL Commands:")
        for i, line in enumerate(tspl_data.strip().split('\n'), 1):
            if line.strip():
                print(f"  {i:2d}: {line}")
                
        # Check for problems in TSPL
        print(f"\n🔍 TSPL Analysis:")
        print(f"  Contains 'SIZE': {'SIZE' in tspl_data}")
        print(f"  Contains 'TEXT': {'TEXT' in tspl_data}")
        print(f"  Contains serial number: {device_data['SERIAL_NUMBER'] in tspl_data}")
        print(f"  Contains STC: {device_data['STC'] in tspl_data}")
        
    except Exception as e:
        print(f"❌ Failed to generate TSPL: {e}")
        return
    
    # STEP 5: Test TSPL transmission (DEBUG MODE)
    print(f"\n📤 STEP 5: Test TSPL Transmission (Debug)")
    print("-" * 40)
    try:
        success = pcb_printer.send_tspl(tspl_data)
        print(f"✅ Debug TSPL transmission: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"❌ Failed TSPL transmission: {e}")
        return
        
    # STEP 6: Test with REAL printing (if user wants)
    print(f"\n🎯 STEP 6: Real Printing Test")
    print("-" * 40)
    response = input("Do you want to test REAL printing to XPrinter? (y/n): ")
    
    if response.lower() == 'y':
        try:
            real_printer = ZebraZPL(xprinter_found, debug_mode=False)
            success = real_printer.send_tspl(tspl_data)
            print(f"🖨️ Real TSPL printing: {'SUCCESS' if success else 'FAILED'}")
            
            if success:
                print(f"👀 Check the physical label from XPrinter!")
                print(f"   Should show: {device_data['SERIAL_NUMBER']}")
                print(f"   Should show: STC:{device_data['STC']}")
                
                label_ok = input("Does the physical label look correct? (y/n): ")
                if label_ok.lower() == 'y':
                    print(f"🎉 PCB PRINTING IS WORKING CORRECTLY!")
                else:
                    print(f"❌ Physical label has problems - need to investigate XPrinter settings")
            
        except Exception as e:
            print(f"❌ Real printing failed: {e}")
    
    print(f"\n✅ DIAGNOSTIC COMPLETE")

if __name__ == "__main__":
    test_pcb_printing_steps()