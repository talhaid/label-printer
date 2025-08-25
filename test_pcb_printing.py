#!/usr/bin/env python3
"""
Comprehensive PCB Printing Test
Tests XPrinter PCB functionality and status detection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xprinter_pcb import XPrinterPCB
import time

def test_xprinter_pcb():
    """Test XPrinter PCB printing functionality."""
    print("=== XPrinter PCB Printing Test ===\n")
    
    try:
        # Initialize XPrinter
        print("1. Initializing XPrinter...")
        pcb_printer = XPrinterPCB()
        print(f"✅ XPrinter initialized: {pcb_printer.printer_name}")
        
        # Test 1: Simple text printing
        print("\n2. Testing simple PCB label printing...")
        test_serial = "TEST123456789"
        result = pcb_printer.print_pcb_label(test_serial)
        
        if result:
            print(f"✅ PCB label printed successfully for: {test_serial}")
        else:
            print(f"❌ PCB label printing failed for: {test_serial}")
        
        # Test 2: Multiple labels
        print("\n3. Testing multiple PCB labels...")
        test_serials = ["MULTI001", "MULTI002", "MULTI003"]
        
        for i, serial in enumerate(test_serials, 1):
            print(f"   Testing {i}/3: {serial}")
            result = pcb_printer.print_pcb_label(serial)
            if result:
                print(f"   ✅ Success: {serial}")
            else:
                print(f"   ❌ Failed: {serial}")
            time.sleep(1)  # Small delay between prints
        
        # Test 3: Get printer stats
        print("\n4. Checking printer statistics...")
        try:
            stats = pcb_printer.get_stats()
            print(f"   📊 Total prints attempted: {stats.get('total_prints', 'Unknown')}")
            print(f"   📊 Successful prints: {stats.get('successful_prints', 'Unknown')}")
            print(f"   📊 Failed prints: {stats.get('failed_prints', 'Unknown')}")
            success_rate = stats.get('successful_prints', 0) / max(stats.get('total_prints', 1), 1) * 100
            print(f"   📊 Success rate: {success_rate:.1f}%")
        except Exception as e:
            print(f"   ⚠️ Could not get stats: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ XPrinter test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_printer_detection():
    """Test if XPrinter is detected by the system."""
    print("\n=== XPrinter Detection Test ===\n")
    
    try:
        import win32print
        
        # Get all printers
        printers = [win32print.EnumPrinters(2)[i][2] for i in range(len(win32print.EnumPrinters(2)))]
        print("Available printers:")
        
        xprinter_found = False
        for printer in printers:
            if 'xprinter' in printer.lower() or 'xp-470b' in printer.lower():
                print(f"   ✅ {printer} (XPrinter detected)")
                xprinter_found = True
            else:
                print(f"   📄 {printer}")
        
        if not xprinter_found:
            print("   ⚠️ No XPrinter detected in system")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Printer detection failed: {e}")
        return False

def main():
    """Run all PCB printing tests."""
    print("🧪 Starting PCB Printing Tests...\n")
    
    # Test 1: Printer Detection
    detection_ok = test_printer_detection()
    
    # Test 2: XPrinter Functionality
    if detection_ok:
        printing_ok = test_xprinter_pcb()
    else:
        print("⚠️ Skipping printing test due to detection failure")
        printing_ok = False
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    print(f"Printer Detection: {'✅ PASS' if detection_ok else '❌ FAIL'}")
    print(f"PCB Printing:      {'✅ PASS' if printing_ok else '❌ FAIL'}")
    
    if detection_ok and printing_ok:
        print("\n🎉 All tests passed! PCB printing is working correctly.")
    elif detection_ok and not printing_ok:
        print("\n⚠️ Printer detected but printing failed. Check printer status/connection.")
    else:
        print("\n❌ PCB printing system has issues. Check printer installation.")

if __name__ == "__main__":
    main()