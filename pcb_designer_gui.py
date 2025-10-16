#!/usr/bin/env python3
"""
PCB Label Designer GUI for XPrinter XP-470B
Real-time TSPL editing and preview
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from zebra_zpl import ZebraZPL
import threading

class PCBLabelDesigner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PCB Label Designer - XPrinter XP-470B (TSPL)")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Sample data
        self.serial_number = "986063608048"
        self.stc = "60001"
        
        # TSPL parameters
        self.label_width = tk.StringVar(value="40")
        self.label_height = tk.StringVar(value="20")
        self.serial_x = tk.StringVar(value="70")
        self.serial_y = tk.StringVar(value="40")
        self.stc_x = tk.StringVar(value="80")
        self.stc_y = tk.StringVar(value="90")
        self.font_size = tk.StringVar(value="5")
        self.font_scale_x = tk.StringVar(value="2")
        self.font_scale_y = tk.StringVar(value="2")
        self.gap_size = tk.StringVar(value="0")
        
        self.setup_ui()
        self.update_preview()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = ttk.Label(title_frame, text="PCB Label Designer for XPrinter XP-470B", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="TSPL Command Generator and Preview", 
                                  font=("Arial", 10))
        subtitle_label.pack()
        
        # Create main horizontal layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left panel - Controls
        left_panel = ttk.LabelFrame(main_frame, text="Label Parameters", padding=10)
        left_panel.pack(side="left", fill="y", padx=(0, 5))
        
        # Right panel - Preview and TSPL
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.setup_controls(left_panel)
        self.setup_preview(right_panel)
        
    def setup_controls(self, parent):
        """Setup control panel"""
        
        # Sample data section
        data_frame = ttk.LabelFrame(parent, text="Sample Data", padding=5)
        data_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(data_frame, text="Serial Number:").pack(anchor="w")
        self.serial_entry = ttk.Entry(data_frame, width=20)
        self.serial_entry.insert(0, self.serial_number)
        self.serial_entry.pack(fill="x", pady=(0, 5))
        self.serial_entry.bind('<KeyRelease>', self.on_data_change)
        
        ttk.Label(data_frame, text="STC:").pack(anchor="w")
        self.stc_entry = ttk.Entry(data_frame, width=20)
        self.stc_entry.insert(0, self.stc)
        self.stc_entry.pack(fill="x")
        self.stc_entry.bind('<KeyRelease>', self.on_data_change)
        
        # Label dimensions
        dim_frame = ttk.LabelFrame(parent, text="Label Dimensions", padding=5)
        dim_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(dim_frame, text="Width (mm):").pack(anchor="w")
        width_spin = ttk.Spinbox(dim_frame, from_=10, to=100, textvariable=self.label_width, width=10)
        width_spin.pack(fill="x", pady=(0, 5))
        width_spin.bind('<KeyRelease>', self.update_preview)
        
        ttk.Label(dim_frame, text="Height (mm):").pack(anchor="w")
        height_spin = ttk.Spinbox(dim_frame, from_=10, to=100, textvariable=self.label_height, width=10)
        height_spin.pack(fill="x", pady=(0, 5))
        height_spin.bind('<KeyRelease>', self.update_preview)
        
        ttk.Label(dim_frame, text="Gap (mm):").pack(anchor="w")
        gap_spin = ttk.Spinbox(dim_frame, from_=0, to=10, textvariable=self.gap_size, width=10)
        gap_spin.pack(fill="x")
        gap_spin.bind('<KeyRelease>', self.update_preview)
        
        # Font settings
        font_frame = ttk.LabelFrame(parent, text="Font Settings", padding=5)
        font_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(font_frame, text="Font Size:").pack(anchor="w")
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_size, width=17)
        font_combo['values'] = ('1', '2', '3', '4', '5')
        font_combo.pack(fill="x", pady=(0, 5))
        font_combo.bind('<<ComboboxSelected>>', self.update_preview)
        
        # Font scaling
        ttk.Label(font_frame, text="Font Scale X:").pack(anchor="w")
        scale_x_spin = ttk.Spinbox(font_frame, from_=1, to=5, textvariable=self.font_scale_x, width=17)
        scale_x_spin.pack(fill="x", pady=(0, 5))
        scale_x_spin.bind('<KeyRelease>', self.update_preview)
        
        ttk.Label(font_frame, text="Font Scale Y:").pack(anchor="w")
        scale_y_spin = ttk.Spinbox(font_frame, from_=1, to=5, textvariable=self.font_scale_y, width=17)
        scale_y_spin.pack(fill="x", pady=(0, 5))
        scale_y_spin.bind('<KeyRelease>', self.update_preview)
        
        # Font reference
        ref_frame = ttk.Frame(font_frame)
        ref_frame.pack(fill="x", pady=(5, 0))
        ref_text = tk.Text(ref_frame, height=8, width=25, font=("Courier", 8))
        ref_text.pack()
        ref_text.insert("1.0", """Font Reference:
1 → Small (8×12 dots)
2 → Medium small (12×20)
3 → Medium (16×24)
4 → Large (24×32 dots)
5 → Extra large (32×48) ★

Scale: 2,2 = 2x bigger
Scale: 3,3 = 3x bigger""")
        ref_text.config(state="disabled")
        
        # Position settings
        pos_frame = ttk.LabelFrame(parent, text="Text Positioning", padding=5)
        pos_frame.pack(fill="x", pady=(0, 10))
        
        # Serial position
        ttk.Label(pos_frame, text="Serial Number Position:").pack(anchor="w")
        pos_serial_frame = ttk.Frame(pos_frame)
        pos_serial_frame.pack(fill="x")
        ttk.Label(pos_serial_frame, text="X:").pack(side="left")
        ttk.Spinbox(pos_serial_frame, from_=0, to=200, textvariable=self.serial_x, width=8).pack(side="left", padx=(2, 5))
        ttk.Label(pos_serial_frame, text="Y:").pack(side="left")
        ttk.Spinbox(pos_serial_frame, from_=0, to=200, textvariable=self.serial_y, width=8).pack(side="left", padx=2)
        
        # STC position
        ttk.Label(pos_frame, text="STC Position:").pack(anchor="w", pady=(5, 0))
        pos_stc_frame = ttk.Frame(pos_frame)
        pos_stc_frame.pack(fill="x")
        ttk.Label(pos_stc_frame, text="X:").pack(side="left")
        ttk.Spinbox(pos_stc_frame, from_=0, to=200, textvariable=self.stc_x, width=8).pack(side="left", padx=(2, 5))
        ttk.Label(pos_stc_frame, text="Y:").pack(side="left")
        ttk.Spinbox(pos_stc_frame, from_=0, to=200, textvariable=self.stc_y, width=8).pack(side="left", padx=2)
        
        # Bind position changes
        for var in [self.serial_x, self.serial_y, self.stc_x, self.stc_y]:
            var.trace('w', self.update_preview)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Test Print", command=self.test_print).pack(fill="x", pady=(0, 5))
        ttk.Button(button_frame, text="Reset to Default", command=self.reset_defaults).pack(fill="x", pady=(0, 5))
        ttk.Button(button_frame, text="Copy TSPL", command=self.copy_tspl).pack(fill="x")
        
    def setup_preview(self, parent):
        """Setup preview panel"""
        
        # Preview section
        preview_frame = ttk.LabelFrame(parent, text="Label Preview", padding=10)
        preview_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        # Visual preview
        self.canvas = tk.Canvas(preview_frame, width=400, height=200, bg="white", relief="sunken", bd=2)
        self.canvas.pack(pady=(0, 10))
        
        # TSPL code section
        tspl_frame = ttk.LabelFrame(parent, text="Generated TSPL Commands", padding=10)
        tspl_frame.pack(fill="both", expand=True)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(tspl_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.tspl_text = tk.Text(text_frame, height=15, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.tspl_text.yview)
        self.tspl_text.configure(yscrollcommand=scrollbar.set)
        
        self.tspl_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def generate_tspl(self):
        """Generate TSPL commands with current settings"""
        serial = self.serial_entry.get()
        stc = self.stc_entry.get()
        
        tspl = f"""SIZE {self.label_width.get()} mm, {self.label_height.get()} mm
GAP {self.gap_size.get()} mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT {self.serial_x.get()}, {self.serial_y.get()}, "{self.font_size.get()}", 0, {self.font_scale_x.get()}, {self.font_scale_y.get()}, "{serial}"
TEXT {self.stc_x.get()}, {self.stc_y.get()}, "{self.font_size.get()}", 0, {self.font_scale_x.get()}, {self.font_scale_y.get()}, "STC: {stc}"
PRINT 1, 1
"""
        return tspl
        
    def update_preview(self, *args):
        """Update the visual preview and TSPL code"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw label border (scaled)
        scale = 8  # Scale factor for display
        width = int(self.label_width.get()) * scale
        height = int(self.label_height.get()) * scale
        
        x_offset = (400 - width) // 2
        y_offset = (200 - height) // 2
        
        # Draw label background
        self.canvas.create_rectangle(x_offset, y_offset, x_offset + width, y_offset + height, 
                                   fill="lightyellow", outline="black", width=2)
        
        # Draw text positions (scaled)
        serial_x_scaled = x_offset + int(self.serial_x.get()) * scale // 8
        serial_y_scaled = y_offset + int(self.serial_y.get()) * scale // 8
        stc_x_scaled = x_offset + int(self.stc_x.get()) * scale // 8
        stc_y_scaled = y_offset + int(self.stc_y.get()) * scale // 8
        
        # Font size mapping for display
        font_sizes = {"1": 8, "2": 10, "3": 12, "4": 14, "5": 16}
        display_font_size = font_sizes.get(self.font_size.get(), 12)
        
        # Draw text
        serial = self.serial_entry.get()
        stc = self.stc_entry.get()
        
        self.canvas.create_text(serial_x_scaled, serial_y_scaled, text=serial, 
                              anchor="nw", font=("Arial", display_font_size, "bold"))
        self.canvas.create_text(stc_x_scaled, stc_y_scaled, text=f"STC: {stc}", 
                              anchor="nw", font=("Arial", display_font_size))
        
        # Add dimension labels
        self.canvas.create_text(x_offset + width//2, y_offset - 15, 
                              text=f"{self.label_width.get()}mm", font=("Arial", 8))
        self.canvas.create_text(x_offset - 25, y_offset + height//2, 
                              text=f"{self.label_height.get()}mm", font=("Arial", 8), angle=90)
        
        # Update TSPL code
        tspl = self.generate_tspl()
        self.tspl_text.delete("1.0", "end")
        self.tspl_text.insert("1.0", tspl)
        
    def on_data_change(self, event=None):
        """Handle data field changes"""
        self.update_preview()
        
    def test_print(self):
        """Test print the current label"""
        try:
            printer = ZebraZPL("Xprinter XP-470B", debug_mode=False)
            tspl = self.generate_tspl()
            
            result = messagebox.askyesno("Test Print", 
                                       "Send this label to XPrinter XP-470B?\n\nMake sure the printer is connected and has labels loaded.")
            
            if result:
                def print_thread():
                    try:
                        success = printer.send_tspl(tspl)
                        if success:
                            messagebox.showinfo("Success", "Label sent to printer successfully!")
                        else:
                            messagebox.showerror("Error", "Failed to send label to printer.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Print error: {e}")
                
                threading.Thread(target=print_thread, daemon=True).start()
                
        except Exception as e:
            messagebox.showerror("Error", f"Printer error: {e}")
            
    def reset_defaults(self):
        """Reset to default values"""
        self.label_width.set("40")
        self.label_height.set("20")
        self.serial_x.set("70")
        self.serial_y.set("40")
        self.stc_x.set("80")
        self.stc_y.set("90")
        self.font_size.set("5")
        self.font_scale_x.set("2")
        self.font_scale_y.set("2")
        self.gap_size.set("0")
        self.serial_entry.delete(0, "end")
        self.serial_entry.insert(0, "986063608048")
        self.stc_entry.delete(0, "end")
        self.stc_entry.insert(0, "60001")
        self.update_preview()
        
    def copy_tspl(self):
        """Copy TSPL to clipboard"""
        tspl = self.generate_tspl()
        self.root.clipboard_clear()
        self.root.clipboard_append(tspl)
        messagebox.showinfo("Copied", "TSPL commands copied to clipboard!")
        
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PCBLabelDesigner()
    app.run()