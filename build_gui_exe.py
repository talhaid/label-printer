#!/usr/bin/env python3
"""
Standalone EXE Builder for Printer GUI
Creates a single executable file for Windows distribution
"""

import subprocess
import sys
import os
import shutil

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def clean_build_folders():
    """Clean previous build folders"""
    folders_to_clean = ['build', '__pycache__']  # Don't clean dist if exe is running
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"🧹 Cleaning {folder} folder...")
            try:
                shutil.rmtree(folder)
            except PermissionError:
                print(f"⚠️  Could not clean {folder} (files in use)")
    
    # Try to clean dist folder, but don't fail if exe is running
    if os.path.exists('dist'):
        try:
            print("🧹 Cleaning dist folder...")
            shutil.rmtree('dist')
        except PermissionError:
            print("⚠️  Could not clean dist folder (executable may be running)")
            print("    The new executable will overwrite the old one.")

def create_spec_file():
    """Create a custom spec file for better control"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['printer_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('device_label_template.zpl', '.'),
        ('*.csv', '.'),
        ('serial_auto_printer.py', '.'),
        ('zebra_zpl.py', '.'),
    ],
    hiddenimports=[
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.lib.units',
        'reportlab.lib.colors',
        'qrcode',
        'qrcode.image',
        'qrcode.image.pil',
        'pandas',
        'PIL',
        'PIL.Image',
        'numpy',
        'openpyxl',
        'xlsxwriter',
        'threading',
        'queue',
        'datetime',
        'subprocess',
        'csv',
        're',
        'win32print',
        'win32api',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ZebraPrinterGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE'
)
'''
    
    with open('printer_gui.spec', 'w') as f:
        f.write(spec_content)
    print("📝 Created custom spec file")

def create_exe():
    """Create standalone EXE using spec file"""
    print("🚀 Creating standalone EXE for Printer GUI...")
    
    try:
        # First try with the spec file
        print("🔧 Building EXE using spec file (this may take a few minutes)...")
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "printer_gui.spec"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ EXE created successfully using spec file!")
            print(f"📂 Output location: {os.path.abspath('dist/ZebraPrinterGUI.exe')}")
            return True
        else:
            print("❌ Spec file build failed, trying direct command...")
            print("Error output:", result.stderr)
            
            # Fallback to direct command
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--name=ZebraPrinterGUI",
                "--icon=NONE",
                "--add-data=device_label_template.zpl;.",
                "--add-data=*.csv;.",
                "--hidden-import=serial",
                "--hidden-import=serial.tools",
                "--hidden-import=serial.tools.list_ports",
                "--hidden-import=tkinter",
                "--hidden-import=tkinter.ttk",
                "--hidden-import=tkinter.scrolledtext",
                "--hidden-import=tkinter.messagebox",
                "--hidden-import=tkinter.filedialog",
                "--hidden-import=reportlab",
                "--hidden-import=reportlab.pdfgen",
                "--hidden-import=reportlab.lib.units",
                "--hidden-import=reportlab.lib.colors",
                "--hidden-import=qrcode",
                "--hidden-import=qrcode.image.pil",
                "--hidden-import=pandas",
                "--hidden-import=PIL",
                "--hidden-import=numpy",
                "--collect-all=reportlab",
                "--collect-all=qrcode",
                "--collect-all=serial",
                "printer_gui.py"
            ]
            
            print("🔧 Building EXE with direct command...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ EXE created successfully!")
                print(f"📂 Output location: {os.path.abspath('dist/ZebraPrinterGUI.exe')}")
                return True
            else:
                print("❌ Build failed!")
                print("Error output:", result.stderr)
                print("Standard output:", result.stdout)
                return False
                
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def copy_dependencies():
    """Copy necessary files to dist folder"""
    if os.path.exists('dist'):
        files_to_copy = [
            'device_label_template.zpl',
            'device_log.csv',
            'cleaned_devices.csv'
        ]
        
        for file in files_to_copy:
            if os.path.exists(file):
                try:
                    shutil.copy2(file, f'dist/{file}')
                    print(f"📋 Copied {file} to dist folder")
                except Exception as e:
                    print(f"⚠️  Could not copy {file}: {e}")

def test_dependencies():
    """Test if all required modules are available"""
    print("🔍 Testing dependencies...")
    
    required_modules = [
        'tkinter',
        'serial',
        'reportlab',
        'qrcode',
        'pandas',
        'PIL'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  Missing modules: {', '.join(missing_modules)}")
        print("Please install them using: pip install " + " ".join(missing_modules))
        return False
    
    print("✅ All dependencies available!")
    return True

def main():
    """Main build process"""
    print("🏗️  Zebra Printer GUI - Standalone EXE Builder")
    print("=" * 50)
    
    # Test dependencies first
    if not test_dependencies():
        print("\n❌ Please install missing dependencies before building.")
        return
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Clean previous builds
    clean_build_folders()
    
    # Create spec file
    create_spec_file()
    
    # Create EXE
    if create_exe():
        # Copy dependencies
        copy_dependencies()
        
        print("\n🎉 Build completed successfully!")
        print(f"📂 Your executable is ready: {os.path.abspath('dist/ZebraPrinterGUI.exe')}")
        print("\n📋 To distribute:")
        print("1. Copy the entire 'dist' folder to the target computer")
        print("2. Run ZebraPrinterGUI.exe")
        print("3. Make sure the target computer has the Zebra printer drivers installed")
        
        # Show file size
        exe_path = 'dist/ZebraPrinterGUI.exe'
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n📊 EXE size: {size_mb:.1f} MB")
    else:
        print("\n❌ Build failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
