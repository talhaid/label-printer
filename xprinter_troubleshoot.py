#!/usr/bin/env python3
"""
XPrinter Physical Printing Troubleshooter
Helps diagnose why XPrinter software succeeds but no physical printing occurs.
"""

def xprinter_troubleshooting_guide():
    """Provide step-by-step troubleshooting guide."""
    print("🔧 XPrinter Physical Printing Troubleshooter")
    print("=" * 50)
    print()
    
    print("The software shows printing is successful, but if no physical")
    print("labels are coming out of the XPrinter, follow these steps:\n")
    
    print("1. 📄 PAPER CHECK")
    print("   ✓ Is thermal paper loaded in XPrinter?")
    print("   ✓ Is paper inserted correctly (not upside down)?")
    print("   ✓ Is there enough paper in the roll?")
    print("   ✓ Try manually feeding paper to test mechanism\n")
    
    print("2. 🔌 POWER & CONNECTION CHECK")
    print("   ✓ Is XPrinter powered on? (LED indicators)")
    print("   ✓ Is USB cable firmly connected to both ends?")
    print("   ✓ Try a different USB cable")
    print("   ✓ Try a different USB port on computer")
    print("   ✓ Check if XPrinter shows up in Device Manager\n")
    
    print("3. 🖨️ PRINTER DRIVER CHECK")
    print("   ✓ Go to Windows Settings > Printers & Scanners")
    print("   ✓ Find 'Xprinter XP-470B' and click on it")
    print("   ✓ Click 'Print test page' to see if Windows can print")
    print("   ✓ If test page fails, reinstall XPrinter drivers\n")
    
    print("4. 🔧 MANUAL PRINTER TEST")
    print("   ✓ Look for a 'FEED' button on XPrinter")
    print("   ✓ Press FEED button - does paper advance?")
    print("   ✓ If no paper movement, check paper loading")
    print("   ✓ If paper moves but no printing, check thermal head\n")
    
    print("5. 💡 THERMAL HEAD CHECK")
    print("   ✓ Thermal paper is heat-sensitive")
    print("   ✓ Check if thermal head is clean")
    print("   ✓ Try printing on different thermal paper")
    print("   ✓ Some thermal paper works better than others\n")
    
    print("6. 🚨 COMMON FIXES")
    print("   ✓ Restart XPrinter (power off/on)")
    print("   ✓ Disconnect/reconnect USB cable")
    print("   ✓ Restart computer if driver issues")
    print("   ✓ Check XPrinter manual for paper loading instructions\n")
    
    print("7. 🧪 FINAL TEST")
    print("   After checking above, run this command:")
    print("   python -c \"from xprinter_pcb import XPrinterPCB; XPrinterPCB().test_print()\"")
    print("   This should print a test PCB label with 'TEST12345'\n")
    
    print("📞 If still not working:")
    print("   - XPrinter might have hardware failure")
    print("   - Contact XPrinter support")
    print("   - Try with different thermal paper")
    print("   - Check if XPrinter works with other software")

def check_windows_printer():
    """Check Windows printer settings."""
    print("\n🖨️ Windows Printer Quick Check")
    print("-" * 30)
    
    try:
        import win32print
        
        # Get XPrinter info
        handle = win32print.OpenPrinter("Xprinter XP-470B")
        printer_info = win32print.GetPrinter(handle, 2)
        
        print(f"Printer Name: {printer_info['pPrinterName']}")
        print(f"Port Name: {printer_info['pPortName']}")
        print(f"Driver Name: {printer_info['pDriverName']}")
        print(f"Status: {printer_info['Status']} (0 = Ready)")
        
        # Check attributes
        attributes = printer_info['Attributes']
        print(f"Attributes: {attributes}")
        
        if attributes & win32print.PRINTER_ATTRIBUTE_WORK_OFFLINE:
            print("⚠️ WARNING: Printer is set to WORK OFFLINE!")
            print("   Go to Printers & Scanners and uncheck 'Use Printer Offline'")
        
        win32print.ClosePrinter(handle)
        
    except Exception as e:
        print(f"Could not check Windows printer: {e}")

def main():
    """Run troubleshooting guide."""
    xprinter_troubleshooting_guide()
    check_windows_printer()

if __name__ == "__main__":
    main()