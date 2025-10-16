#!/usr/bin/env python3
"""
🧹 COMPLETE CLEANUP: Remove all old ZPL PCB test files
This will eliminate any sources of old ZPL templates for PCB printing
"""

import os
import shutil

def clean_old_pcb_files():
    """Remove all files that might contain old ZPL PCB templates"""
    print("🧹 COMPLETE CLEANUP: Removing Old PCB Test Files")
    print("="*60)
    
    # Files that contain old ZPL PCB templates (should be removed)
    old_files_to_remove = [
        'test_pcb_printing.py',     # Contains old ZPL template
        'test_real_xprinter.py',    # Contains old ZPL templates
        'test_escpos_xprinter.py',  # Contains old ZPL templates  
        'test_xprinter_dpi.py',     # Contains old ZPL templates
        'investigate_xprinter.py',  # Contains old ZPL templates
        'test_new_pcb_template.py', # Contains old ZPL templates
        'pcb_label_preview.py',     # Contains old ZPL templates
        'test_actual_pcb.py',       # Contains old templates
        'debug_test.py'             # Contains old ZPL templates
    ]
    
    # Check and remove files
    for file_name in old_files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"✅ Removed: {file_name}")
            except Exception as e:
                print(f"❌ Error removing {file_name}: {e}")
        else:
            print(f"⚪ Not found: {file_name}")
    
    print(f"\n🎯 KEEPING ONLY:")
    print(f"  ✅ serial_auto_printer.py (TSPL method)")
    print(f"  ✅ printer_gui.py (main GUI)")  
    print(f"  ✅ zebra_zpl.py (send_tspl method)")
    print(f"  ✅ pcb_designer_gui.py (TSPL designer)")
    print(f"  ✅ tspl_demo.py (TSPL demo)")
    print(f"  ✅ test_tspl_xprinter.py (TSPL test)")
    
    print(f"\n🔥 ALL OLD ZPL PCB TEMPLATES REMOVED!")
    print(f"🎯 Only TSPL-based PCB printing remains!")

if __name__ == "__main__":
    clean_old_pcb_files()