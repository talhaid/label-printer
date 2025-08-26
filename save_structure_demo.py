#!/usr/bin/env python3
"""
CSV Management & Save Folder Demo
Shows the new organized file structure and CSV management features
"""

import os

def demo_save_structure():
    """Demo the new save folder structure and CSV management"""
    
    print("💾 SAVE FOLDER STRUCTURE & CSV MANAGEMENT")
    print("=" * 60)
    
    print("📁 NEW ORGANIZED STRUCTURE:")
    print("=" * 40)
    print("📂 save/")
    print("  ├── 📂 csv/")
    print("  │   ├── 📄 device_log.csv          (Main device database)")
    print("  │   ├── 📄 cleaned_devices.csv     (Cleaned data)")
    print("  │   ├── 📄 sample_devices.csv      (Test data)")
    print("  │   └── 📄 *_backup_*.csv          (Auto backups)")
    print("  └── 📂 zpl_output/")
    print("      └── 📄 SERIAL_TIMESTAMP.zpl    (Label files)")
    
    print("\n✨ NEW CSV MANAGER TAB FEATURES:")
    print("=" * 40)
    print("🔍 VIEWING & ANALYSIS:")
    print("  • Live CSV statistics (total, valid, errors)")
    print("  • Filterable view (Latest 50/100, All, Errors Only, Valid Only)")
    print("  • Search functionality across all fields")
    print("  • Color-coded rows (errors in red)")
    print("  • Real-time file info (size, last modified)")
    
    print("\n🛠️ MANAGEMENT TOOLS:")
    print("  • 📂 Open CSV Folder - Direct folder access")
    print("  • 📄 Open CSV File - Open in Excel/default app")
    print("  • 🔄 Refresh View - Update display")
    print("  • 🧹 Clean CSV - Remove errors & duplicates")
    print("  • 📤 Export Filtered - Save filtered data")
    
    print("\n📊 SMART CLEANING FEATURES:")
    print("  • Automatic backup before cleaning")
    print("  • Remove PARSE_ERROR entries")
    print("  • Eliminate duplicate serial numbers")
    print("  • Keep latest entry for duplicates")
    print("  • Show cleaning statistics")
    
    print("\n🎯 HOW TO USE:")
    print("=" * 40)
    print("1. Launch printer_gui.py")
    print("2. Go to 'CSV Manager' tab")
    print("3. View live statistics and data")
    print("4. Use filters and search to find specific records")
    print("5. Click 'Clean CSV' to optimize database")
    print("6. Export filtered data as needed")
    print("7. Use folder buttons for quick access")
    
    print("\n💡 BENEFITS:")
    print("=" * 40)
    print("✅ Organized file structure for easy backups")
    print("✅ Centralized CSV management")
    print("✅ Automatic data cleaning and optimization")
    print("✅ Advanced filtering and search")
    print("✅ Export capabilities for reporting")
    print("✅ Visual feedback with color coding")
    print("✅ File statistics and monitoring")
    
    # Check if save folder exists
    save_exists = os.path.exists("save")
    csv_exists = os.path.exists("save/csv") if save_exists else False
    zpl_exists = os.path.exists("save/zpl_output") if save_exists else False
    
    print(f"\n📋 CURRENT STATUS:")
    print("=" * 40)
    print(f"📂 Save folder: {'✅ Ready' if save_exists else '❌ Missing'}")
    print(f"📂 CSV folder: {'✅ Ready' if csv_exists else '❌ Missing'}")
    print(f"📂 ZPL folder: {'✅ Ready' if zpl_exists else '❌ Missing'}")
    
    if csv_exists and os.path.exists("save/csv/device_log.csv"):
        file_size = os.path.getsize("save/csv/device_log.csv") / 1024
        print(f"📄 CSV file: ✅ Ready ({file_size:.1f} KB)")
    else:
        print(f"📄 CSV file: ✅ Created fresh")
    
    print(f"\n🎉 All systems ready! Check the CSV Manager tab!")

if __name__ == "__main__":
    demo_save_structure()