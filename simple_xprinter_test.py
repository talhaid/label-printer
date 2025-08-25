#!/usr/bin/env python3
"""
Simple XPrinter Raw Test
Tests XPrinter with minimal commands to match what other apps do.
"""

import win32print
import time

def test_simple_raw_print():
    """Test XPrinter with very simple raw commands."""
    print("=== Simple XPrinter Raw Test ===\n")
    
    try:
        printer_name = "Xprinter XP-470B"
        
        # Test 1: Minimal text
        print("1. Testing minimal text...")
        simple_data = b"Hello XPrinter\n\n\n"
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("Simple Test", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, simple_data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ Minimal text sent")
        time.sleep(2)
        
        # Test 2: Basic ESC/POS
        print("2. Testing basic ESC/POS...")
        basic_data = b"\x1b@"  # Initialize
        basic_data += b"Basic ESC/POS Test\n"
        basic_data += b"Line 2\n"
        basic_data += b"Line 3\n"
        basic_data += b"\x0A\x0A\x0A"  # Line feeds
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("Basic ESC/POS", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, basic_data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ Basic ESC/POS sent")
        time.sleep(2)
        
        # Test 3: Different approach - no ESC/POS
        print("3. Testing plain text (no ESC/POS)...")
        plain_data = "Plain Text Test\nNo ESC/POS commands\nJust text\n\n\n\n".encode('utf-8')
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("Plain Text", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, plain_data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ Plain text sent")
        time.sleep(2)
        
        # Test 4: Test with cut command
        print("4. Testing with cut command...")
        cut_data = b"Test with cut\n"
        cut_data += b"Second line\n"
        cut_data += b"\x0A\x0A"  # Extra line feeds
        cut_data += b"\x1dV\x00"  # Cut command
        
        handle = win32print.OpenPrinter(printer_name)
        job = win32print.StartDocPrinter(handle, 1, ("Cut Test", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, cut_data)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("   ✅ Cut test sent")
        
        print("\n📋 Test completed!")
        print("Check XPrinter for any printed output from these 4 tests.")
        print("If nothing prints, the issue might be:")
        print("- Paper not loaded")
        print("- Printer not powered on")
        print("- Different data format needed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_windows_print_api():
    """Test using Windows print API differently."""
    print("\n=== Windows Print API Test ===\n")
    
    try:
        import subprocess
        
        # Create a simple text file
        with open("test_print.txt", "w") as f:
            f.write("Windows API Test\n")
            f.write("Print via notepad\n")
            f.write("Line 3\n")
        
        # Try printing via Windows command
        print("Trying to print via Windows command...")
        result = subprocess.run([
            "notepad", "/p", "test_print.txt"
        ], capture_output=True, text=True, timeout=10)
        
        print(f"Command result: {result.returncode}")
        
    except Exception as e:
        print(f"Windows API test failed: {e}")

def main():
    """Run all simple tests."""
    test_simple_raw_print()
    
    print("\n" + "="*50)
    print("💡 IMPORTANT: Check XPrinter now!")
    print("="*50)
    print("Did any of the 4 tests produce physical output?")
    print("- Test 1: Minimal text")
    print("- Test 2: Basic ESC/POS") 
    print("- Test 3: Plain text")
    print("- Test 4: With cut command")
    print("\nIf NONE printed, the issue is likely hardware/paper related.")
    print("If SOME printed, we can identify which format works.")

if __name__ == "__main__":
    main()