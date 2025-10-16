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
    
    # Create preview window
    root = tk.Tk()
    root.title("PCB Label Preview - 40mm x 20mm")
    root.geometry("600x400")
    root.configure(bg='white')
    
    # Main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = ttk.Label(main_frame, text="PCB Label Preview", font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Label info
    info_frame = ttk.Frame(main_frame)
    info_frame.pack(fill="x", pady=(0, 20))
    
    ttk.Label(info_frame, text="Label Size: 40mm x 20mm", font=("Arial", 12)).pack(anchor="w")
    ttk.Label(info_frame, text="Printer: XPrinter XP-470B", font=("Arial", 12)).pack(anchor="w")
    ttk.Label(info_frame, text="Resolution: 203 DPI (315 x 157 dots)", font=("Arial", 12)).pack(anchor="w")
    
    # Label preview frame (scaled up for visibility)
    preview_frame = tk.Frame(main_frame, bg='black', relief='solid', bd=2)
    preview_frame.pack(pady=20)
    
    # Scale factor for display (3x bigger than actual)
    scale = 3
    label_width = 315 * scale // 5  # Divided by 5 for reasonable screen size
    label_height = 157 * scale // 5
    
    # Create canvas for label preview
    canvas = tk.Canvas(preview_frame, width=label_width, height=label_height, bg='white')
    canvas.pack(padx=5, pady=5)
    
    # Draw label content (scaled and CENTERED, moved further down, same font sizes)
    # Serial number centered horizontally, moved further down
    canvas.create_text(label_width//2, 40*scale//5, text=serial_number, anchor='n', 
                      font=("Courier", 15, "bold"), fill='black')
    
    # STC centered horizontally, moved further down, same font size  
    canvas.create_text(label_width//2, 80*scale//5, text=f"STC: {stc}", anchor='n', 
                      font=("Courier", 15, "bold"), fill='black')
    
    # Draw border to show label edges
    canvas.create_rectangle(2, 2, label_width-2, label_height-2, outline='red', width=1, dash=(2,2))
    
    # Label information
    info_text = f"""
Device Data:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Serial Number: {serial_number}
STC: {stc}

ZPL Commands Generated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
^XA
^MMT
^PW315
^LL157
^LS0
^CF0,22
^FB315,1,0,C^FO0,35^FD{serial_number}^FS
^CF0,22
^FB315,1,0,C^FO0,75^FDSTC: {stc}^FS
^XZ

Label Specifications:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Dimensions: 40mm (width) x 20mm (height)
• Dots: 315 x 157 (at 203 DPI)
• Serial Number: 22pt font CENTERED at Y=35
• STC: 22pt font CENTERED at Y=75 (SAME SIZE!)
• Text: Both texts same size, moved down for perfect spacing
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