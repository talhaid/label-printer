"""
Simple EXE Builder for printer_gui.py
Creates an exact copy of your current GUI as a standalone EXE
"""

import subprocess
import sys
import os

def main():
    print("🔧 Creating EXE for printer_gui.py")
    print("=" * 40)
    
    # Simple PyInstaller command - no fancy stuff
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single EXE
        "--windowed",                   # No console
        "--name=PrinterGUI",            # EXE name  
        "printer_gui.py"                # Your current GUI file
    ]
    
    print("🚀 Building EXE...")
    print("Command:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUCCESS! EXE created")
            print(f"📁 Location: dist\\PrinterGUI.exe")
            
            # Check file size
            exe_path = "dist\\PrinterGUI.exe"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📊 Size: {size_mb:.1f} MB")
        else:
            print("❌ FAILED!")
            print("Error:", result.stderr)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
