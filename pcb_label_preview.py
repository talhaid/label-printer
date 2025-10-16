#!/usr/bin/env python3
"""
PCB Label Preview Tool
Shows how the 40mm x 20mm PCB label will look
"""

import tkinter as tk
from tkinter import ttk
from serial_auto_printer import DeviceDataParser

def create_pcb_preview():
    """Create a visual preview of the PCB label"""
    
    # Sample device data
    test_data = "##986063608048|867315088718139|286016570186236|8990011418220012368F|24:5D:F9:7D:78:50##"
    
    # Parse the data
    parser = DeviceDataParser()
    device_data = parser.parse_data(test_data)
    device_data['STC'] = '60001'  # Add test STC
    
    serial_number = device_data.get('SERIAL_NUMBER', 'UNKNOWN')
    stc = device_data.get('STC', 'UNKNOWN')
    imei = device_data.get('IMEI', 'UNKNOWN')
    imsi = device_data.get('IMSI', 'UNKNOWN')
    ccid = device_data.get('CCID', 'UNKNOWN')
    mac_address = device_data.get('MAC_ADDRESS', 'UNKNOWN')
    
    # Create preview window
    root = tk.Tk()
    root.title("PCB Label Preview - Complete Label with QR Code")
    root.geometry("800x600")
    root.configure(bg='white')
    
    # Main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = ttk.Label(main_frame, text="Complete PCB Label Preview", font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Label info
    info_frame = ttk.Frame(main_frame)
    info_frame.pack(fill="x", pady=(0, 20))
    
    ttk.Label(info_frame, text="Label Size: 399 x 240 dots", font=("Arial", 12)).pack(anchor="w")
    ttk.Label(info_frame, text="Printer: XPrinter XP-470B", font=("Arial", 12)).pack(anchor="w")
    ttk.Label(info_frame, text="Features: QR Code + Complete Device Data", font=("Arial", 12)).pack(anchor="w")
    
    # Label preview frame (scaled for visibility)
    preview_frame = tk.Frame(main_frame, bg='black', relief='solid', bd=2)
    preview_frame.pack(pady=20)
    
    # Scale factor for display
    scale = 2
    label_width = 399 * scale // 3  # Reasonable screen size
    label_height = 240 * scale // 3
    
    # Create canvas for label preview
    canvas = tk.Canvas(preview_frame, width=label_width, height=label_height, bg='white')
    canvas.pack(padx=5, pady=5)
    
    # Draw QR code area (left side)
    qr_size = 60
    canvas.create_rectangle(20*scale//3, 50*scale//3, (20+qr_size)*scale//3, (50+qr_size)*scale//3, 
                           outline='blue', width=2, fill='lightblue')
    canvas.create_text((20+qr_size//2)*scale//3, (50+qr_size//2)*scale//3, text="QR\nCODE", 
                      font=("Arial", 8, "bold"), fill='blue')
    
    # Draw labels (right side)
    labels = ["STC:", "S/N:", "IMEI:", "IMSI:", "CCID:", "MAC:"]
    values = [stc, serial_number, imei, imsi, ccid, mac_address]
    y_positions = [32.5, 70, 107.5, 145, 182.5, 220]
    
    for i, (label, value, y_pos) in enumerate(zip(labels, values, y_positions)):
        # Label text
        canvas.create_text(185*scale//3, y_pos*scale//3, text=label, anchor='w', 
                          font=("Arial", 8, "bold"), fill='black')
        # Value text
        canvas.create_text(225*scale//3, y_pos*scale//3, text=value, anchor='w', 
                          font=("Arial", 9, "bold"), fill='darkblue')
    
    # Draw border
    canvas.create_rectangle(2, 2, label_width-2, label_height-2, outline='red', width=1, dash=(2,2))
    
    # Label information
    info_text = f"""
Device Data:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Serial Number: {serial_number}
STC: {stc}
IMEI: {imei}
IMSI: {imsi}
CCID: {ccid}
MAC Address: {mac_address}

ZPL Commands Generated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
^XA
^PW399
^LL240
^CI28
^MD15
~SD15

^FO20,50^BQN,2,4
^FDLA,STC:{stc};SN:ATS{serial_number};IMEI:{imei};IMSI:{imsi};CCID:{ccid};MAC:{mac_address}^FS

^CF0,18,18
^FO185,32.5^FDSTC:^FS
^FO185,70^FDS/N:^FS
^FO185,107.5^FDIMEI:^FS
^FO185,145^FDIMSI:^FS
^FO185,182.5^FDCCID:^FS
^FO185,220^FDMAC:^FS

^CF0,22,16
^FO225,32.5^FD{stc}^FS
^FO225,70^FD{serial_number}^FS
^FO225,107.5^FD{imei}^FS
^FO225,145^FD{imsi}^FS
^FO225,182.5^FD{ccid}^FS
^FO225,220^FD{mac_address}^FS

^XZ

Label Layout:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Left Side: QR Code with all device data
• Right Side: Formatted text labels and values
• Dimensions: 399 x 240 dots
• QR Code contains: STC, Serial, IMEI, IMSI, CCID, MAC
• Text fields: Labels at X=185, Values at X=225
• Perfect alignment and professional appearance
"""
    
    # Text area for details
    text_frame = ttk.Frame(main_frame)
    text_frame.pack(fill="both", expand=True, pady=(10, 0))
    
    text_area = tk.Text(text_frame, wrap="word", font=("Courier", 9))
    text_area.pack(fill="both", expand=True)
    text_area.insert("1.0", info_text)
    text_area.config(state="disabled")
    
    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(10, 0))
    
    def close_preview():
        root.destroy()
    
    ttk.Button(button_frame, text="Close Preview", command=close_preview).pack(side="right", padx=(10, 0))
    ttk.Label(button_frame, text="Red dashed line shows label borders", 
             foreground="red", font=("Arial", 9)).pack(side="left")
    
    # Show window
    root.mainloop()

if __name__ == "__main__":
    create_pcb_preview()