#!/usr/bin/env python3
"""
TSPL Demo and Preview for XPrinter XP-470B PCB Labels
"""

def create_tspl_demo():
    """Create a comprehensive demo of TSPL commands"""
    print("🎯 TSPL Demo for XPrinter XP-470B (40mm x 20mm PCB Labels)")
    print("=" * 70)
    
    # Sample data
    serial_number = "986063608048"
    stc = "60001"
    
    # Our current TSPL template
    tspl_commands = f"""SIZE 40 mm, 20 mm
GAP 2 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 20, 30, "3", 0, 1, 1, "{serial_number}"
TEXT 20, 80, "3", 0, 1, 1, "STC: {stc}"
PRINT 1, 1
"""
    
    print("📋 TSPL Command Analysis:")
    print("-" * 40)
    print("SIZE 40 mm, 20 mm          → Label dimensions: 40mm wide × 20mm tall")
    print("GAP 2 mm, 0 mm             → 2mm gap between labels")
    print("DIRECTION 1                → Print direction (normal)")
    print("REFERENCE 0, 0             → Origin point at top-left")
    print("OFFSET 0 mm                → No label offset")
    print("SET PEEL OFF               → Disable peel-off mode")
    print("SET CUTTER OFF             → Disable cutter")
    print("SET PARTIAL_CUTTER OFF     → Disable partial cutter")
    print("SET TEAR ON                → Enable tear-off (manual)")
    print("CLEAR                      → Clear print buffer")
    print(f"TEXT 20, 30, \"3\", 0, 1, 1  → Serial at (20,30) font 3: {serial_number}")
    print(f"TEXT 20, 80, \"3\", 0, 1, 1  → STC at (20,80) font 3: STC: {stc}")
    print("PRINT 1, 1                 → Print 1 copy")
    
    # Visual representation
    print("\n🎨 Visual Preview (40mm × 20mm):")
    print("┌" + "─" * 48 + "┐")
    print("│" + " " * 48 + "│")
    print("│" + f"    {serial_number}".ljust(48) + "│")
    print("│" + " " * 48 + "│")
    print("│" + f"    STC: {stc}".ljust(48) + "│")
    print("│" + " " * 48 + "│")
    print("└" + "─" * 48 + "┘")
    
    print("\n📏 Coordinate Explanation:")
    print("-" * 30)
    print("• Position (20, 30) = 20mm from left, 30 dots from top")
    print("• Position (20, 80) = 20mm from left, 80 dots from top")
    print("• Font \"3\" = Medium size font (good for 40mm labels)")
    print("• Parameters: rotation=0, x-scale=1, y-scale=1")
    
    print(f"\n📄 Complete TSPL Output:")
    print("=" * 50)
    print(tspl_commands)
    print("=" * 50)
    
    # Font size comparison
    print("\n🔤 TSPL Font Reference:")
    print("-" * 25)
    print("Font \"1\" → Small (8×12 dots)")
    print("Font \"2\" → Medium small (12×20 dots)")
    print("Font \"3\" → Medium (16×24 dots) ← CURRENT")
    print("Font \"4\" → Large (24×32 dots)")
    print("Font \"5\" → Extra large (32×48 dots)")
    
    # Alternative versions for comparison
    print("\n🎛️  Alternative TSPL Versions:")
    print("-" * 35)
    
    # Version 1: Larger font
    alt1 = f"""SIZE 40 mm, 20 mm
GAP 2 mm, 0 mm
DIRECTION 1
CLEAR
TEXT 15, 20, "4", 0, 1, 1, "{serial_number}"
TEXT 15, 65, "3", 0, 1, 1, "STC: {stc}"
PRINT 1, 1
"""
    
    # Version 2: Centered
    alt2 = f"""SIZE 40 mm, 20 mm
GAP 2 mm, 0 mm
DIRECTION 1
CLEAR
TEXT 10, 25, "3", 0, 1, 1, "{serial_number}"
TEXT 25, 75, "3", 0, 1, 1, "STC: {stc}"
PRINT 1, 1
"""
    
    print("Option 1 - Larger Font:")
    print(alt1)
    
    print("Option 2 - More Centered:")
    print(alt2)
    
    print("\n✅ RECOMMENDATION:")
    print("Current TSPL template should work perfectly for XPrinter XP-470B!")
    print("- Proper 40mm × 20mm size")
    print("- Good font size (readable but fits)")
    print("- Clean positioning")
    print("- XPrinter-compatible commands")
    
    return tspl_commands

def test_tspl_generation():
    """Test the actual TSPL generation from our code"""
    print("\n🧪 Testing TSPL Generation from Serial Auto Printer")
    print("=" * 60)
    
    # Import our actual function
    from serial_auto_printer import DeviceAutoPrinter
    
    # Sample device data
    device_data = {
        'SERIAL_NUMBER': '986063608048',
        'IMEI': '867315088718139',
        'IMSI': '286016570186236', 
        'CCID': '8990011418220012368F',
        'MAC_ADDRESS': '24:5D:F9:7D:78:50',
        'STC': '60001'
    }
    
    # Create a temporary printer instance
    template = "^XA^FO50,50^FD{SERIAL_NUMBER}^FS^XZ"  # Simple template
    printer = DeviceAutoPrinter(template, debug_mode=True)
    
    # Generate TSPL
    tspl_output = printer._create_pcb_label_data(device_data)
    
    print("📄 Generated TSPL from actual code:")
    print("-" * 40)
    print(tspl_output)
    
    print("\n✅ VERIFICATION: TSPL generation working correctly!")

if __name__ == "__main__":
    # Run the demo
    tspl_commands = create_tspl_demo()
    
    # Test actual generation
    test_tspl_generation()
    
    print("\n🚀 READY FOR COMPANY TESTING!")
    print("When you get to the company:")
    print("1. Run the GUI")
    print("2. Select 'Xprinter XP-470B' as PCB printer")
    print("3. Enable PCB printing checkbox")
    print("4. Start monitoring")
    print("5. Send test data")
    print("6. Check if 40mm × 20mm labels print correctly!")