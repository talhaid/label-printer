#!/usr/bin/env python3
"""
XPrinter TSPL Test
Tests XPrinter using TSPL (TSC Printer Language) commands instead of ESC/POS.
"""

import win32print
import time

def test_tspl_commands():
    """Test XPrinter with TSPL commands."""
    print("=== XPrinter TSPL Command Test ===\n")
    
    try:
        printer_name = "Xprinter XP-470B"
        
        # Test 1: Basic TSPL
        print("1. Testing basic TSPL...")
        tspl_data = b''
        tspl_data += b'SIZE 40 mm, 20 mm\n'  # Set label size 4cm x 2cm
        tspl_data += b'GAP 2 mm, 0 mm\n'     # Gap between labels
        tspl_data += b'DIRECTION 1,0\n'       # Print direction
        tspl_data += b'REFERENCE 0,0\n'       # Reference point
        tspl_data += b'OFFSET 0 mm\n'         # Offset
        tspl_data += b'SET PEEL OFF\n'        # Peel off mode
        tspl_data += b'SET CUTTER OFF\n'      # Cutter off
        tspl_data += b'SET PARTIAL_CUTTER OFF\n'  # Partial cutter off
        tspl_data += b'SET TEAR ON\n'         # Tear on
        tspl_data += b'CLS\n'                 # Clear buffer
        tspl_data += b'TEXT 50,50,"3",0,1,1,"TSPL TEST"\n'  # Print text
        tspl_data += b'TEXT 50,100,"2",0,1,1,"Serial: TEST123"\n'  # Print serial
        tspl_data += b'PRINT 1,1\n'           # Print 1 copy
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("TSPL Test", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, tspl_data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ TSPL commands sent")
        time.sleep(2)
        
        # Test 2: Simpler TSPL
        print("2. Testing simple TSPL...")
        simple_tspl = b''
        simple_tspl += b'SIZE 40 mm, 20 mm\n'
        simple_tspl += b'CLS\n'
        simple_tspl += b'TEXT 10,10,"4",0,1,1,"SIMPLE TSPL"\n'
        simple_tspl += b'TEXT 10,50,"3",0,1,1,"Line 2"\n'
        simple_tspl += b'PRINT 1\n'
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("Simple TSPL", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, simple_tspl)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ Simple TSPL sent")
        time.sleep(2)
        
        # Test 3: Minimal TSPL
        print("3. Testing minimal TSPL...")
        minimal_tspl = b'CLS\nTEXT 10,10,"4",0,1,1,"MINIMAL"\nPRINT 1\n'
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("Minimal TSPL", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, minimal_tspl)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ Minimal TSPL sent")
        
    except Exception as e:
        print(f"❌ TSPL test failed: {e}")

def test_zpl_commands():
    """Test XPrinter with ZPL commands (Zebra Printer Language)."""
    print("\n=== XPrinter ZPL Command Test ===\n")
    
    try:
        printer_name = "Xprinter XP-470B"
        
        print("Testing ZPL commands...")
        zpl_data = b''
        zpl_data += b'^XA\n'  # Start format
        zpl_data += b'^LH30,30\n'  # Label home position
        zpl_data += b'^FO50,50^ADN,36,20^FDZPL TEST^FS\n'  # Text field
        zpl_data += b'^FO50,100^ADN,24,10^FDSerial: TEST123^FS\n'  # Serial field
        zpl_data += b'^XZ\n'  # End format
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("ZPL Test", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, zpl_data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ ZPL commands sent")
        
    except Exception as e:
        print(f"❌ ZPL test failed: {e}")

def test_cpcl_commands():
    """Test XPrinter with CPCL commands (Comtec Printer Control Language)."""
    print("\n=== XPrinter CPCL Command Test ===\n")
    
    try:
        printer_name = "Xprinter XP-470B"
        
        print("Testing CPCL commands...")
        cpcl_data = b''
        cpcl_data += b'! 0 200 200 160 1\n'  # Init: density, width, height, qty
        cpcl_data += b'TEXT 4 0 30 40 CPCL TEST\n'  # Text command
        cpcl_data += b'TEXT 2 0 30 80 Serial: TEST123\n'  # Text command
        cpcl_data += b'FORM\n'  # Form feed
        cpcl_data += b'PRINT\n'  # Print command
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("CPCL Test", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, cpcl_data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ CPCL commands sent")
        
    except Exception as e:
        print(f"❌ CPCL test failed: {e}")

def main():
    """Test all printer command languages."""
    print("🧪 Testing Different Printer Command Languages\n")
    print("XPrinter XP-470B might use TSPL, ZPL, CPCL, or ESC/POS")
    print("Let's test all of them to see which one works!\n")
    
    test_tspl_commands()
    test_zpl_commands() 
    test_cpcl_commands()
    
    print(f"\n{'='*60}")
    print("📋 CHECK YOUR XPRINTER NOW!")
    print(f"{'='*60}")
    print("Look for printed output from:")
    print("1. TSPL Test (most likely to work)")
    print("2. Simple TSPL")
    print("3. Minimal TSPL")
    print("4. ZPL Test")
    print("5. CPCL Test")
    print("\nWhichever format printed successfully is what we need to use!")
    print("Tell me which test(s) produced actual printed labels.")

if __name__ == "__main__":
    main()