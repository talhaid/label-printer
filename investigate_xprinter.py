#!/usr/bin/env python3
"""
Deep investigation of XPrinter PCB printing issues
"""

import win32print
from zebra_zpl import ZebraZPL

def investigate_xprinter_issue():
    """Deep dive into XPrinter issues"""
    print("🔍 DEEP INVESTIGATION: XPrinter PCB Issues")
    print("=" * 60)
    
    # Test 1: Check available printers and their details
    print("\n📋 STEP 1: Available Printers Analysis")
    print("-" * 40)
    
    printers = []
    for printer_info in win32print.EnumPrinters(2):
        printers.append(printer_info[2])
        
    for i, printer in enumerate(printers, 1):
        print(f"  {i}. {printer}")
        
        # Get detailed printer info
        try:
            hprinter = win32print.OpenPrinter(printer)
            info = win32print.GetPrinter(hprinter, 2)
            print(f"     Driver: {info['pDriverName']}")
            print(f"     Port: {info['pPortName']}")
            print(f"     Status: {info['Status']}")
            win32print.ClosePrinter(hprinter)
        except Exception as e:
            print(f"     Error getting info: {e}")
    
    # Test 2: Check XPrinter capabilities
    print("\n🖨️  STEP 2: XPrinter Specific Analysis")
    print("-" * 40)
    
    xprinter_name = "Xprinter XP-470B"
    if xprinter_name in printers:
        print(f"✅ Found XPrinter: {xprinter_name}")
        
        # Test 3: Compare ZPL sizes
        print(f"\n📏 STEP 3: ZPL Template Comparison")
        print("-" * 40)
        
        # Current template (40mm x 20mm)
        current_zpl = """^XA
^MMT
^PW315
^LL157
^LS0
^CF0,20
^FO5,10^FD986063608048^FS
^CF0,15
^FO5,40^FDSTC: 60001^FS
^XZ"""
        
        # Test different sizes for comparison
        test_templates = {
            "Current (40x20mm)": current_zpl,
            "Medium (50x25mm)": """^XA
^MMT
^PW394
^LL197
^LS0
^CF0,25
^FO10,20^FD986063608048^FS
^CF0,20
^FO10,60^FDSTC: 60001^FS
^XZ""",
            "Large (60x30mm)": """^XA
^MMT
^PW472
^LL236
^LS0
^CF0,30
^FO15,30^FD986063608048^FS
^CF0,25
^FO15,80^FDSTC: 60001^FS
^XZ""",
            "XPrinter Standard": """^XA
^MMT
^PW400
^LL300
^LS0
^CF0,40
^FO20,50^FD986063608048^FS
^CF0,30
^FO20,120^FDSTC: 60001^FS
^XZ"""
        }
        
        for name, zpl in test_templates.items():
            print(f"\n🏷️  {name}:")
            lines = zpl.strip().split('\n')
            for line in lines:
                if line.startswith('^PW') or line.startswith('^LL') or line.startswith('^CF') or line.startswith('^FO'):
                    print(f"    {line}")
        
        # Test 4: XPrinter compatibility test
        print(f"\n🧪 STEP 4: XPrinter Compatibility Test")
        print("-" * 40)
        
        printer = ZebraZPL(xprinter_name, debug_mode=True)
        
        print("Testing current template...")
        result = printer.send_zpl(current_zpl)
        print(f"Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
    else:
        print(f"❌ XPrinter not found: {xprinter_name}")
        print("Available printers:")
        for p in printers:
            if 'xprint' in p.lower() or 'xp-' in p.lower():
                print(f"  - {p}")

if __name__ == "__main__":
    investigate_xprinter_issue()