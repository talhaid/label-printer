#!/usr/bin/env python3
"""
Alternative XPrinter Test Methods
Tries different ways to communicate with XPrinter that might work better.
"""

import win32print
import time

def test_with_different_doc_info():
    """Test with different document info parameters."""
    print("=== Testing Different Document Parameters ===\n")
    
    try:
        printer_name = "Xprinter XP-470B"
        
        # Method 1: Different datatype
        print("1. Testing with TEXT datatype...")
        data = "TEXT DATATYPE TEST\nLine 2\nLine 3\n\n\n"
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("Text Test", None, "TEXT"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, data.encode('utf-8'))
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        print("   ✅ TEXT datatype sent")
        time.sleep(2)
        
        # Method 2: No datatype specified
        print("2. Testing with no datatype...")
        data = b"NO DATATYPE TEST\nLine 2\nLine 3\n\n\n"
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("No Datatype", None, None))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        print("   ✅ No datatype sent")
        time.sleep(2)
        
        # Method 3: XPS datatype
        print("3. Testing with XPS datatype...")
        data = b"XPS DATATYPE TEST\nLine 2\nLine 3\n\n\n"
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("XPS Test", None, "XPS"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        print("   ✅ XPS datatype sent")
        
    except Exception as e:
        print(f"❌ Alternative test failed: {e}")

def test_printer_properties():
    """Check printer properties that might affect printing."""
    print("\n=== Printer Properties Check ===\n")
    
    try:
        printer_name = "Xprinter XP-470B"
        handle = win32print.OpenPrinter(printer_name)
        
        # Get printer info level 2
        printer_info = win32print.GetPrinter(handle, 2)
        
        print(f"Printer Name: {printer_info['pPrinterName']}")
        print(f"Share Name: {printer_info['pShareName']}")
        print(f"Port Name: {printer_info['pPortName']}")
        print(f"Driver Name: {printer_info['pDriverName']}")
        print(f"Comment: {printer_info['pComment']}")
        print(f"Location: {printer_info['pLocation']}")
        print(f"Default DataType: {printer_info['pDatatype']}")
        print(f"Parameters: {printer_info['pParameters']}")
        print(f"Status: {printer_info['Status']}")
        print(f"Jobs: {printer_info['cJobs']}")
        
        # Check printer attributes
        attributes = printer_info['Attributes']
        print(f"\nAttributes: {attributes}")
        if attributes & win32print.PRINTER_ATTRIBUTE_DIRECT:
            print("   - Direct printing enabled")
        if attributes & win32print.PRINTER_ATTRIBUTE_QUEUED:
            print("   - Queued printing enabled")
        if attributes & win32print.PRINTER_ATTRIBUTE_WORK_OFFLINE:
            print("   - ⚠️ Working offline!")
        if attributes & win32print.PRINTER_ATTRIBUTE_ENABLE_DEVQ:
            print("   - Device queue enabled")
        
        win32print.ClosePrinter(handle)
        
    except Exception as e:
        print(f"❌ Could not check printer properties: {e}")

def test_manual_commands():
    """Test with manually crafted commands that definitely should work."""
    print("\n=== Manual Command Test ===\n")
    
    try:
        printer_name = "Xprinter XP-470B"
        
        # Very basic test - just text and line feeds
        print("Testing ultra-simple command...")
        
        # Just text with lots of line feeds to ensure it prints
        simple_text = b"MANUAL TEST\n" * 10  # Repeat 10 times
        simple_text += b"\x0C"  # Form feed
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("Manual", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, simple_text)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ Manual command sent")
        print("   📄 Should see 'MANUAL TEST' repeated 10 times")
        
    except Exception as e:
        print(f"❌ Manual test failed: {e}")

def main():
    """Run all alternative tests."""
    print("🧪 XPrinter Alternative Test Methods\n")
    
    test_printer_properties()
    test_with_different_doc_info()
    test_manual_commands()
    
    print(f"\n{'='*50}")
    print("📋 RESULTS CHECK")
    print(f"{'='*50}")
    print("Please check your XPrinter for any printed output.")
    print("We tested:")
    print("- TEXT datatype")
    print("- No datatype")
    print("- XPS datatype") 
    print("- Manual repeated text")
    print("\nIf STILL nothing prints, please:")
    print("1. Check paper is loaded correctly")
    print("2. Ensure XPrinter is powered on")
    print("3. Try the working app again to confirm XPrinter works")
    print("4. Tell me what app works so I can match its method")

if __name__ == "__main__":
    main()