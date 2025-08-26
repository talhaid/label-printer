#!/usr/bin/env python3
"""
Standalone EXE Builder for Printer System
Creates a single executable file for Windows distribution
"""

import subprocess
import sys
import os

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def create_exe():
    """Create standalone EXE"""
    print("🚀 Creating standalone EXE...")
    
    # Main command to create the EXE
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single EXE file
        "--windowed",                   # No console window for GUI
        "--name=PrinterSystem",         # EXE name
        "--icon=NONE",                  # No icon for now
        "--add-data=save;save",         # Include save folder
        "--add-data=device_label_template.zpl;.",  # Include ZPL template
        "--hidden-import=serial",       # Ensure serial module is included
        "--hidden-import=tkinter",      # Ensure tkinter is included
        "--hidden-import=reportlab",    # Ensure reportlab is included
        "--hidden-import=qrcode",       # Ensure qrcode is included
        "--hidden-import=pandas",       # Ensure pandas is included
        "--hidden-import=PIL",          # Ensure PIL is included
        "--collect-all=reportlab",      # Include all reportlab files
        "--collect-all=qrcode",         # Include all qrcode files
        "printer_gui.py"                # Main file
    ]
    
    try:
        print("🔧 Building EXE (this may take a few minutes)...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ EXE created successfully!")
            print("📁 Location: dist/PrinterSystem.exe")
            print("📦 Size: ~50-100MB (includes all dependencies)")
            print("")
            print("🎯 Distribution Instructions:")
            print("1. Copy 'dist/PrinterSystem.exe' to target PC")
            print("2. No Python installation needed on target PC")
            print("3. Run PrinterSystem.exe directly")
            print("4. All features will work (GUI, printing, CSV, box labels)")
        else:
            print("❌ Error creating EXE:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def create_console_exe():
    """Create console version for debugging"""
    print("🔧 Creating console version for debugging...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",                    # Keep console for debugging
        "--name=PrinterSystem-Console",
        "--add-data=save;save",
        "--add-data=device_label_template.zpl;.",
        "--hidden-import=serial",
        "--hidden-import=tkinter",
        "--hidden-import=reportlab",
        "--hidden-import=qrcode",
        "--hidden-import=pandas",
        "--hidden-import=PIL",
        "--collect-all=reportlab",
        "--collect-all=qrcode",
        "printer_gui.py"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Console EXE created: dist/PrinterSystem-Console.exe")
        else:
            print("❌ Console EXE failed")
    except Exception as e:
        print(f"❌ Console EXE error: {e}")

def main():
    print("🏗️  Printer System EXE Builder")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("printer_gui.py"):
        print("❌ Error: printer_gui.py not found!")
        print("Please run this script from the printer project directory")
        return
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create both versions
    create_exe()
    create_console_exe()
    
    print("")
    print("🎉 Build complete!")
    print("📁 Check the 'dist' folder for:")
    print("   - PrinterSystem.exe (main GUI version)")
    print("   - PrinterSystem-Console.exe (debug version)")

if __name__ == "__main__":
    main()