#!/usr/bin/env python3
"""
Quick demo of the Box Labels functionality with Select All button
"""

import subprocess
import time
import os

def demo_box_labels():
    """Show how to use the new Box Labels features"""
    
    print("📦 Box Labels Demo - Select All Feature")
    print("=" * 60)
    
    # Check if sample data exists
    if not os.path.exists("sample_devices.csv"):
        print("⚠️ Sample data not found. Generating now...")
        subprocess.run(["python", "sample_data_generator.py"], input="1\n", text=True)
        print("✅ Sample data created!")
    
    print("\n🎯 New Box Labels Features:")
    print("=" * 40)
    print("✅ Select All Button - Select all devices on current page")
    print("✅ Clear All Button - Clear all selected devices") 
    print("✅ Smart Selection - Won't exceed 20 device limit")
    print("✅ Page Navigation - Browse through devices 20 at a time")
    
    print("\n📋 How to Use:")
    print("=" * 40)
    print("1. Open printer_gui.py")
    print("2. Go to 'Box Labels' tab")
    print("3. Load 'sample_devices.csv' file")
    print("4. Use navigation buttons to browse pages")
    print("5. Click 'Select All' to select all devices on current page")
    print("6. Click 'Clear All' to deselect all devices")
    print("7. Enter box number (e.g., BOX001)")
    print("8. Click 'Create PDF Label' to generate the label")
    
    print("\n💡 Tips:")
    print("=" * 40)
    print("• Maximum 20 devices per box")
    print("• Select All will only select up to the 20 device limit")
    print("• You can mix Select All with manual clicking")
    print("• Clear All removes all selections across all pages")
    
    print("\n🚀 Ready to test!")
    print("The GUI is already running - switch to the Box Labels tab!")

if __name__ == "__main__":
    demo_box_labels()