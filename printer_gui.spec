
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
