#!/usr/bin/env python3
"""
Position test for XPrinter to see if positioning actually works
"""

import win32print

def test_positions():
    """Test different positions to see if they actually change."""
    
    # Test with extreme positions
    commands = b''
    commands += b'SIZE 40 mm, 20 mm\n'
    commands += b'CLS\n'
    commands += b'TEXT 5,40,"3",0,1,1,"LEFT 5"\n'      # Far left
    commands += b'TEXT 50,60,"3",0,1,1,"MID 50"\n'     # Middle
    commands += b'TEXT 100,80,"3",0,1,1,"RIGHT 100"\n' # Far right
    commands += b'PRINT 1\n'
    
    try:
        handle = win32print.OpenPrinter("Xprinter XP-470B")
        job = win32print.StartDocPrinter(handle, 1, ("Position Test", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, commands)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
        win32print.ClosePrinter(handle)
        
        print("Position test sent successfully!")
        print("Check XPrinter for:")
        print("- 'LEFT 5' should be on the left")
        print("- 'MID 50' should be in middle") 
        print("- 'RIGHT 100' should be on the right")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_positions()