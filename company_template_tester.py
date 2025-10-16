#!/usr/bin/env python3
"""
🏢 Company Template Tester
Quick script to test different PCB label layouts at company
"""

import sys
sys.path.append('.')

from zebra_zpl import ZebraZPL
from tspl_templates import get_all_templates

def company_template_test():
    """Test different templates at company"""
    print("🏢 COMPANY TEMPLATE TESTER")
    print("="*50)
    
    # Find XPrinter
    print("🔍 Finding XPrinter...")
    try:
        temp_printer = ZebraZPL()
        printers = temp_printer.list_printers()
        
        xprinter = None
        for printer in printers:
            if 'xprinter' in printer.lower():
                xprinter = printer
                break
                
        if not xprinter:
            print("❌ No XPrinter found!")
            return
            
        print(f"✅ Found XPrinter: {xprinter}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test data
    test_data = {
        'serial_number': '66182844496',
        'stc': '60000'
    }
    
    print(f"\n📋 Test Data:")
    print(f"   Serial: {test_data['serial_number']}")
    print(f"   STC: {test_data['stc']}")
    
    # Get all templates
    templates = get_all_templates()
    
    print(f"\n🎯 Available Templates:")
    for i, name in enumerate(templates.keys(), 1):
        print(f"   {i}. {name}")
    
    # Test each template
    for i, (name, template) in enumerate(templates.items(), 1):
        print(f"\n" + "="*50)
        print(f"📋 TEMPLATE {i}: {name}")
        print("="*50)
        
        # Fill template with data
        filled_template = template.format(**test_data)
        
        print("TSPL Commands:")
        for line_num, line in enumerate(filled_template.strip().split('\n'), 1):
            print(f"  {line_num:2d}: {line}")
        
        # Ask to print
        response = input(f"\n🖨️ Print '{name}' template? (y/n/quit): ").lower()
        
        if response == 'quit' or response == 'q':
            print("👋 Testing stopped by user")
            break
        elif response == 'y':
            try:
                printer = ZebraZPL(xprinter, debug_mode=False)
                success = printer.send_tspl(filled_template)
                
                if success:
                    print("✅ Print sent successfully!")
                    input("👀 Check the label. Press Enter when ready...")
                    
                    quality = input("How does it look? (good/bad/ok): ").lower()
                    
                    if quality == 'good':
                        print(f"🎉 WINNER! '{name}' template works well!")
                        print(f"\n💡 SOLUTION for main program:")
                        print("   Update _create_pcb_label_data() method with:")
                        print(f"   {repr(filled_template)}")
                        
                        save_winner = input("\nSave this as the winner template? (y/n): ")
                        if save_winner.lower() == 'y':
                            with open('winning_template.tspl', 'w') as f:
                                f.write(filled_template)
                            print("💾 Saved to 'winning_template.tspl'")
                            break
                    elif quality == 'ok':
                        print(f"👍 '{name}' is acceptable")
                    else:
                        print(f"👎 '{name}' has issues")
                else:
                    print("❌ Print failed!")
                    
            except Exception as e:
                print(f"❌ Print error: {e}")
        else:
            print("⏭️ Skipped")
    
    print(f"\n✅ Template testing complete!")
    print(f"📧 Report the winner template so we can update the main program!")

def quick_custom_test():
    """Quick custom template test"""
    print("\n🎨 CUSTOM TEMPLATE BUILDER")
    print("-" * 30)
    
    # Get settings from user
    print("Enter custom settings (or press Enter for defaults):")
    
    serial_font = input("Serial font (1-5) [default: 2]: ") or "2"
    serial_x = input("Serial X position [default: 25]: ") or "25"
    serial_y = input("Serial Y position [default: 20]: ") or "20"
    
    stc_font = input("STC font (1-5) [default: 1]: ") or "1"
    stc_x = input("STC X position [default: 25]: ") or "25"
    stc_y = input("STC Y position [default: 50]: ") or "50"
    
    # Build custom template
    custom_template = f"""SIZE 40 mm, 20 mm
GAP 0 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT {serial_x}, {serial_y}, "{serial_font}", 0, 1, 1, "66182844496"
TEXT {stc_x}, {stc_y}, "{stc_font}", 0, 1, 1, "STC:60000"
PRINT 1, 1
"""
    
    print(f"\n📋 Your Custom Template:")
    for line_num, line in enumerate(custom_template.strip().split('\n'), 1):
        print(f"  {line_num:2d}: {line}")
    
    test_it = input("\nTest this custom template? (y/n): ")
    if test_it.lower() == 'y':
        # Test the custom template (similar to above)
        print("🖨️ Testing custom template...")
        # Implementation similar to template testing above

if __name__ == "__main__":
    print("🎯 PCB Label Template Tester")
    print("Choose your test mode:")
    print("1. Test all predefined templates")
    print("2. Custom template builder")
    
    choice = input("\nEnter choice (1 or 2): ")
    
    if choice == "1":
        company_template_test()
    elif choice == "2":
        quick_custom_test()
    else:
        print("Invalid choice!")