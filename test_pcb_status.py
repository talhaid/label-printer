#!/usr/bin/env python3
"""
XPrinter PCB Status Checker
Diagnoses XPrinter connection and printing issues.
"""

import win32print
import win32api
import time

def check_xprinter_status():
    """Check XPrinter status and connection."""
    print("=== XPrinter PCB Status Diagnosis ===\n")
    
    try:
        # 1. Find XPrinter
        print("1. Searching for XPrinter...")
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
        print(f"   Available printers: {len(printers)}")
        
        xprinter_name = None
        for printer in printers:
            print(f"   - {printer}")
            if 'xprinter' in printer.lower() or 'xp-470b' in printer.lower():
                xprinter_name = printer
                print(f"   ✅ Found XPrinter: {printer}")
        
        if not xprinter_name:
            print("   ❌ XPrinter not found!")
            return False
        
        # 2. Check printer status
        print(f"\n2. Checking printer status for: {xprinter_name}")
        try:
            handle = win32print.OpenPrinter(xprinter_name)
            printer_info = win32print.GetPrinter(handle, 2)
            status = printer_info['Status']
            
            print(f"   Printer Status Code: {status}")
            if status == 0:
                print("   ✅ Printer status: Ready")
            else:
                print(f"   ⚠️ Printer status: Error (Code: {status})")
                # Common status codes
                status_messages = {
                    1: "Paused",
                    2: "Error",
                    3: "Pending Deletion", 
                    4: "Paper Jam",
                    5: "Paper Out",
                    6: "Manual Feed",
                    7: "Paper Problem",
                    8: "Offline",
                    16: "Out of Memory",
                    32: "Door Open",
                    64: "Server Unknown",
                    128: "Power Save",
                    256: "Warming Up",
                    512: "Toner Low",
                    1024: "No Toner",
                    2048: "Page Punt",
                    4096: "User Intervention",
                    8192: "Out of Memory",
                    16384: "Door Open"
                }
                if status in status_messages:
                    print(f"   Status meaning: {status_messages[status]}")
            
            win32print.ClosePrinter(handle)
            
        except Exception as e:
            print(f"   ❌ Could not check printer status: {e}")
            return False
        
        # 3. Test basic printing
        print(f"\n3. Testing basic print job...")
        try:
            # Simple test print
            test_data = b"\x1b@"  # Initialize
            test_data += b"\x1ba\x01"  # Center align
            test_data += b"XPrinter Test\n"
            test_data += b"COM Port Check\n"
            test_data += b"\x1dV\x00"  # Cut
            
            handle = win32print.OpenPrinter(xprinter_name)
            job = win32print.StartDocPrinter(handle, 1, ("XPrinter Test", None, "RAW"))
            win32print.StartPagePrinter(handle)
            win32print.WritePrinter(handle, test_data)
            win32print.EndPagePrinter(handle)
            win32print.EndDocPrinter(handle)
            win32print.ClosePrinter(handle)
            
            print("   ✅ Test print job sent successfully")
            print("   📄 Check if a test label printed on XPrinter")
            
        except Exception as e:
            print(f"   ❌ Test print failed: {e}")
            return False
        
        # 4. Check printer queue
        print(f"\n4. Checking printer queue...")
        try:
            handle = win32print.OpenPrinter(xprinter_name)
            jobs = win32print.EnumJobs(handle, 0, -1, 1)
            if jobs:
                print(f"   📄 {len(jobs)} job(s) in queue:")
                for job in jobs:
                    print(f"   - Job {job['JobId']}: {job['pDocument']} (Status: {job['Status']})")
            else:
                print("   ✅ Printer queue is empty")
            win32print.ClosePrinter(handle)
        except Exception as e:
            print(f"   ⚠️ Could not check queue: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ XPrinter diagnosis failed: {e}")
        return False

def check_com_ports():
    """Check COM port usage."""
    print("\n=== COM Port Analysis ===\n")
    
    import serial.tools.list_ports
    
    print("Available COM ports:")
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"   {port.device}: {port.description}")
        if 'ch340' in port.description.lower() or 'usb' in port.description.lower():
            print(f"   ⚠️ This might be your device COM port: {port.device}")

def main():
    """Run all diagnostic tests."""
    xprinter_ok = check_xprinter_status()
    check_com_ports()
    
    print(f"\n{'='*50}")
    print("📋 DIAGNOSIS SUMMARY")
    print(f"{'='*50}")
    
    if xprinter_ok:
        print("✅ XPrinter appears to be working")
        print("💡 If PCB labels still don't print, check:")
        print("   - Paper loaded correctly")
        print("   - Printer power and USB connection")
        print("   - Windows printer queue for errors")
    else:
        print("❌ XPrinter has issues")
        print("💡 Try:")
        print("   - Restart XPrinter")
        print("   - Check USB connection")
        print("   - Reinstall XPrinter drivers")
        print("   - Check Windows Devices and Printers")

if __name__ == "__main__":
    main()