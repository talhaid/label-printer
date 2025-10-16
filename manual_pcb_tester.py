#!/usr/bin/env python3
"""
🎯 MANUAL PCB TESTER - Direct TSPL Editor
Edit TSPL commands directly and test them immediately
"""

import sys
sys.path.append('.')

from zebra_zpl import ZebraZPL

def manual_pcb_test():
    """Manual TSPL editor and tester"""
    print("🎯 MANUAL PCB TESTER")
    print("="*50)
    
    # Find XPrinter
    try:
        temp_printer = ZebraZPL()
        printers = temp_printer.list_printers()
        
        xprinter = None
        for printer in printers:
            if 'xprinter' in printer.lower():
                xprinter = printer
                break
                
        if xprinter:
            print(f"✅ XPrinter found: {xprinter}")
        else:
            print("❌ No XPrinter found!")
            print("Available printers:")
            for p in printers:
                print(f"  - {p}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Current template
    current_template = """SIZE 40 mm, 20 mm
GAP 0 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 100, 40, "3", 0, 1, 1, "66182844496"
TEXT 120, 80, "2", 0, 1, 1, "STC:60000"
PRINT 1, 1
"""
    
    print(f"\n📋 CURRENT TEMPLATE:")
    print("-" * 30)
    for i, line in enumerate(current_template.strip().split('\n'), 1):
        print(f"{i:2d}: {line}")
    
    while True:
        print(f"\n🎛️ MANUAL ADJUSTMENT OPTIONS:")
        print("1. Test current template")
        print("2. Move serial LEFT (X-20)")
        print("3. Move serial RIGHT (X+20)")  
        print("4. Move serial UP (Y-20)")
        print("5. Move serial DOWN (Y+20)")
        print("6. Move STC LEFT (X-20)")
        print("7. Move STC RIGHT (X+20)")
        print("8. Move STC UP (Y-20)")
        print("9. Move STC DOWN (Y+20)")
        print("10. Use Font 2 (bigger)")
        print("11. Reset to centered")
        print("12. Custom edit")
        print("0. Exit")
        
        choice = input("\nChoose option (0-12): ")
        
        if choice == "0":
            break
        elif choice == "1":
            test_template(xprinter, current_template)
        elif choice == "2":
            current_template = adjust_serial_x(current_template, -20)
        elif choice == "3":
            current_template = adjust_serial_x(current_template, +20)
        elif choice == "4":
            current_template = adjust_serial_y(current_template, -20)
        elif choice == "5":
            current_template = adjust_serial_y(current_template, +20)
        elif choice == "6":
            current_template = adjust_stc_x(current_template, -20)
        elif choice == "7":
            current_template = adjust_stc_x(current_template, +20)
        elif choice == "8":
            current_template = adjust_stc_y(current_template, -20)
        elif choice == "9":
            current_template = adjust_stc_y(current_template, +20)
        elif choice == "10":
            current_template = change_fonts(current_template, "2")
        elif choice == "11":
            current_template = reset_centered()
        elif choice == "12":
            current_template = custom_edit(current_template)
        
        # Show updated template
        if choice != "1":
            print(f"\n📋 UPDATED TEMPLATE:")
            lines = current_template.strip().split('\n')
            for i, line in enumerate(lines, 1):
                if 'TEXT' in line:
                    print(f"{i:2d}: {line} ← CHANGED")
                else:
                    print(f"{i:2d}: {line}")

def test_template(xprinter, template):
    """Test the template"""
    print(f"\n🖨️ Testing template...")
    
    try:
        printer = ZebraZPL(xprinter, debug_mode=False)
        success = printer.send_tspl(template)
        
        if success:
            print("✅ Print sent successfully!")
            input("👀 Check the physical label. Press Enter when ready...")
            
            quality = input("How does it look? (good/bad/adjust): ").lower()
            if quality == 'good':
                print("🎉 PERFECT! Save this template!")
                save_template(template)
        else:
            print("❌ Print failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def adjust_serial_x(template, delta):
    """Adjust serial X position"""
    lines = template.split('\n')
    for i, line in enumerate(lines):
        if 'TEXT' in line and '66182844496' in line:
            parts = line.split(', ')
            if len(parts) >= 2:
                current_x = int(parts[0].split(' ')[1])
                new_x = current_x + delta
                parts[0] = f"TEXT {new_x}"
                lines[i] = ', '.join(parts)
                print(f"📍 Serial X: {current_x} → {new_x}")
                break
    return '\n'.join(lines)

def adjust_serial_y(template, delta):
    """Adjust serial Y position"""
    lines = template.split('\n')
    for i, line in enumerate(lines):
        if 'TEXT' in line and '66182844496' in line:
            parts = line.split(', ')
            if len(parts) >= 2:
                current_y = int(parts[1])
                new_y = current_y + delta
                parts[1] = str(new_y)
                lines[i] = ', '.join(parts)
                print(f"📍 Serial Y: {current_y} → {new_y}")
                break
    return '\n'.join(lines)

def adjust_stc_x(template, delta):
    """Adjust STC X position"""
    lines = template.split('\n')
    for i, line in enumerate(lines):
        if 'TEXT' in line and 'STC:' in line:
            parts = line.split(', ')
            if len(parts) >= 2:
                current_x = int(parts[0].split(' ')[1])
                new_x = current_x + delta
                parts[0] = f"TEXT {new_x}"
                lines[i] = ', '.join(parts)
                print(f"📍 STC X: {current_x} → {new_x}")
                break
    return '\n'.join(lines)

def adjust_stc_y(template, delta):
    """Adjust STC Y position"""
    lines = template.split('\n')
    for i, line in enumerate(lines):
        if 'TEXT' in line and 'STC:' in line:
            parts = line.split(', ')
            if len(parts) >= 2:
                current_y = int(parts[1])
                new_y = current_y + delta
                parts[1] = str(new_y)
                lines[i] = ', '.join(parts)
                print(f"📍 STC Y: {current_y} → {new_y}")
                break
    return '\n'.join(lines)

def change_fonts(template, new_font):
    """Change font size"""
    lines = template.split('\n')
    for i, line in enumerate(lines):
        if 'TEXT' in line:
            parts = line.split(', ')
            if len(parts) >= 3:
                parts[2] = f'"{new_font}"'
                lines[i] = ', '.join(parts)
    print(f"🔤 Changed fonts to size {new_font}")
    return '\n'.join(lines)

def reset_centered():
    """Reset to centered template"""
    print("🎯 Reset to centered layout")
    return """SIZE 40 mm, 20 mm
GAP 0 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 80, 35, "3", 0, 1, 1, "66182844496"
TEXT 90, 75, "2", 0, 1, 1, "STC:60000"
PRINT 1, 1
"""

def custom_edit(template):
    """Custom template editor"""
    print(f"\n✏️ CUSTOM EDITOR")
    print("Current template:")
    print(template)
    print("\nPaste your modified TSPL (end with empty line):")
    
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    
    if lines:
        return '\n'.join(lines)
    else:
        return template

def save_template(template):
    """Save working template"""
    with open('working_pcb_template.tspl', 'w') as f:
        f.write(template)
    print("💾 Template saved to 'working_pcb_template.tspl'")
    print("📧 Copy this to update your main program!")

if __name__ == "__main__":
    manual_pcb_test()