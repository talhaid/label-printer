#!/usr/bin/env python3
"""
🎯 XPrinter PCB Test Studio
Advanced GUI for testing different TSPL templates, positions, and sizes
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
sys.path.append('.')

from zebra_zpl import ZebraZPL

class XPrinterPCBStudio:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("XPrinter PCB Test Studio - TSPL Designer")
        self.root.geometry("1200x800")
        
        # Variables
        self.printer_var = tk.StringVar()
        self.size_width = tk.StringVar(value="40")
        self.size_height = tk.StringVar(value="20")
        self.gap_size = tk.StringVar(value="0")
        
        # Serial number settings
        self.serial_font = tk.StringVar(value="2")
        self.serial_x = tk.StringVar(value="30")
        self.serial_y = tk.StringVar(value="20")
        self.serial_scale_x = tk.StringVar(value="1")
        self.serial_scale_y = tk.StringVar(value="1")
        
        # STC settings
        self.stc_font = tk.StringVar(value="1")
        self.stc_x = tk.StringVar(value="30")
        self.stc_y = tk.StringVar(value="60")
        self.stc_scale_x = tk.StringVar(value="1")
        self.stc_scale_y = tk.StringVar(value="1")
        
        # Test data
        self.test_serial = tk.StringVar(value="66182844496")
        self.test_stc = tk.StringVar(value="60000")
        
        self.setup_ui()
        self.update_printer_list()
        self.update_preview()
        
    def setup_ui(self):
        """Setup the GUI interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 XPrinter PCB Test Studio", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        control_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Right panel - Preview and Output
        preview_frame = ttk.LabelFrame(main_frame, text="Preview & Output", padding="10")
        preview_frame.grid(row=1, column=1, sticky="nsew")
        
        # Bottom panel - Actions
        action_frame = ttk.Frame(main_frame, padding="5")
        action_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.setup_controls(control_frame)
        self.setup_preview(preview_frame)
        self.setup_actions(action_frame)
        
    def setup_controls(self, parent):
        """Setup control panels"""
        row = 0
        
        # Printer selection
        ttk.Label(parent, text="🖨️ XPrinter:").grid(row=row, column=0, sticky="w", pady=2)
        self.printer_combo = ttk.Combobox(parent, textvariable=self.printer_var, width=30)
        self.printer_combo.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(parent, text="Refresh", command=self.update_printer_list).grid(row=row, column=2, padx=5, pady=2)
        row += 1
        
        # Separator
        ttk.Separator(parent, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=10)
        row += 1
        
        # Label size settings
        size_frame = ttk.LabelFrame(parent, text="📏 Label Size", padding="5")
        size_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=5)
        size_frame.columnconfigure(1, weight=1)
        
        ttk.Label(size_frame, text="Width (mm):").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(size_frame, textvariable=self.size_width, width=10).grid(row=0, column=1, padx=5)
        ttk.Label(size_frame, text="Height (mm):").grid(row=0, column=2, sticky="w", padx=5)
        ttk.Entry(size_frame, textvariable=self.size_height, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(size_frame, text="Gap (mm):").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(size_frame, textvariable=self.gap_size, width=10).grid(row=1, column=1, padx=5)
        
        row += 1
        
        # Serial number settings
        serial_frame = ttk.LabelFrame(parent, text="🔢 Serial Number", padding="5")
        serial_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=5)
        serial_frame.columnconfigure(1, weight=1)
        
        ttk.Label(serial_frame, text="Font:").grid(row=0, column=0, sticky="w", padx=2)
        font_combo = ttk.Combobox(serial_frame, textvariable=self.serial_font, 
                                 values=["1", "2", "3", "4", "5"], width=5)
        font_combo.grid(row=0, column=1, padx=2)
        
        ttk.Label(serial_frame, text="X:").grid(row=0, column=2, sticky="w", padx=2)
        ttk.Entry(serial_frame, textvariable=self.serial_x, width=8).grid(row=0, column=3, padx=2)
        
        ttk.Label(serial_frame, text="Y:").grid(row=0, column=4, sticky="w", padx=2)
        ttk.Entry(serial_frame, textvariable=self.serial_y, width=8).grid(row=0, column=5, padx=2)
        
        ttk.Label(serial_frame, text="Scale X:").grid(row=1, column=0, sticky="w", padx=2)
        scale_x_combo = ttk.Combobox(serial_frame, textvariable=self.serial_scale_x, 
                                    values=["1", "2", "3"], width=5)
        scale_x_combo.grid(row=1, column=1, padx=2)
        
        ttk.Label(serial_frame, text="Scale Y:").grid(row=1, column=2, sticky="w", padx=2)
        scale_y_combo = ttk.Combobox(serial_frame, textvariable=self.serial_scale_y, 
                                    values=["1", "2", "3"], width=5)
        scale_y_combo.grid(row=1, column=3, padx=2)
        
        row += 1
        
        # STC settings
        stc_frame = ttk.LabelFrame(parent, text="🏷️ STC Label", padding="5")
        stc_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=5)
        stc_frame.columnconfigure(1, weight=1)
        
        ttk.Label(stc_frame, text="Font:").grid(row=0, column=0, sticky="w", padx=2)
        stc_font_combo = ttk.Combobox(stc_frame, textvariable=self.stc_font, 
                                     values=["1", "2", "3", "4", "5"], width=5)
        stc_font_combo.grid(row=0, column=1, padx=2)
        
        ttk.Label(stc_frame, text="X:").grid(row=0, column=2, sticky="w", padx=2)
        ttk.Entry(stc_frame, textvariable=self.stc_x, width=8).grid(row=0, column=3, padx=2)
        
        ttk.Label(stc_frame, text="Y:").grid(row=0, column=4, sticky="w", padx=2)
        ttk.Entry(stc_frame, textvariable=self.stc_y, width=8).grid(row=0, column=5, padx=2)
        
        ttk.Label(stc_frame, text="Scale X:").grid(row=1, column=0, sticky="w", padx=2)
        stc_scale_x_combo = ttk.Combobox(stc_frame, textvariable=self.stc_scale_x, 
                                        values=["1", "2", "3"], width=5)
        stc_scale_x_combo.grid(row=1, column=1, padx=2)
        
        ttk.Label(stc_frame, text="Scale Y:").grid(row=1, column=2, sticky="w", padx=2)
        stc_scale_y_combo = ttk.Combobox(stc_frame, textvariable=self.stc_scale_y, 
                                        values=["1", "2", "3"], width=5)
        stc_scale_y_combo.grid(row=1, column=3, padx=2)
        
        row += 1
        
        # Test data
        data_frame = ttk.LabelFrame(parent, text="📝 Test Data", padding="5")
        data_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=5)
        data_frame.columnconfigure(1, weight=1)
        
        ttk.Label(data_frame, text="Serial:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(data_frame, textvariable=self.test_serial).grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(data_frame, text="STC:").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(data_frame, textvariable=self.test_stc).grid(row=1, column=1, sticky="ew", padx=5)
        
        row += 1
        
        # Bind update events
        for var in [self.size_width, self.size_height, self.gap_size,
                   self.serial_font, self.serial_x, self.serial_y, self.serial_scale_x, self.serial_scale_y,
                   self.stc_font, self.stc_x, self.stc_y, self.stc_scale_x, self.stc_scale_y,
                   self.test_serial, self.test_stc]:
            var.trace_add("write", lambda *args: self.update_preview())
            
    def setup_preview(self, parent):
        """Setup preview panel"""
        # TSPL preview
        ttk.Label(parent, text="📋 Generated TSPL:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.preview_text = scrolledtext.ScrolledText(parent, height=20, width=60, font=("Consolas", 10))
        self.preview_text.pack(fill="both", expand=True)
        
        # Visual representation
        visual_frame = ttk.LabelFrame(parent, text="📐 Visual Preview", padding="5")
        visual_frame.pack(fill="x", pady=(10, 0))
        
        # Add dynamic size info
        self.size_info_label = ttk.Label(visual_frame, text="", font=("Arial", 9), foreground="gray")
        self.size_info_label.pack(anchor="w", pady=(0, 5))
        
        self.canvas = tk.Canvas(visual_frame, width=400, height=200, bg="white", relief="sunken", bd=2)
        self.canvas.pack()
        
    def setup_actions(self, parent):
        """Setup action buttons"""
        # Quick templates
        template_frame = ttk.LabelFrame(parent, text="⚡ Quick Templates", padding="5")
        template_frame.pack(side="left", fill="y", padx=(0, 10))
        
        templates = [
            ("Small & Compact", {"serial_font": "1", "serial_x": "20", "serial_y": "15", 
                               "stc_font": "1", "stc_x": "20", "stc_y": "45"}),
            ("Medium Size", {"serial_font": "2", "serial_x": "25", "serial_y": "20", 
                           "stc_font": "2", "stc_x": "25", "stc_y": "50"}),
            ("Large Bold", {"serial_font": "3", "serial_x": "15", "serial_y": "25", 
                          "stc_font": "2", "stc_x": "15", "stc_y": "55"}),
            ("Current System", {"serial_font": "4", "serial_x": "50", "serial_y": "30", 
                              "stc_font": "3", "stc_x": "50", "stc_y": "80"})
        ]
        
        for name, settings in templates:
            btn = ttk.Button(template_frame, text=name, 
                           command=lambda s=settings: self.apply_template(s))
            btn.pack(fill="x", pady=2)
        
        # Actions
        action_buttons = ttk.Frame(parent)
        action_buttons.pack(side="right", fill="y")
        
        ttk.Button(action_buttons, text="🔍 Preview Only", 
                  command=self.preview_print, style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(action_buttons, text="🖨️ Print Single", 
                  command=self.test_print, style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(action_buttons, text="📦 Print Multiple", 
                  command=self.print_multiple, style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(action_buttons, text="� Import CSV", 
                  command=self.import_csv, style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(action_buttons, text="�💾 Save Template", 
                  command=self.save_template).pack(side="left", padx=5)
        
    def update_printer_list(self):
        """Update printer dropdown"""
        try:
            temp_printer = ZebraZPL()
            printers = temp_printer.list_printers()
            self.printer_combo['values'] = printers
            
            # Auto-select XPrinter
            for printer in printers:
                if 'xprinter' in printer.lower():
                    self.printer_var.set(printer)
                    break
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list printers: {e}")
    
    def generate_tspl(self):
        """Generate TSPL commands based on current settings"""
        try:
            tspl = f"""SIZE {self.size_width.get()} mm, {self.size_height.get()} mm
GAP {self.gap_size.get()} mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT {self.serial_x.get()}, {self.serial_y.get()}, "{self.serial_font.get()}", 0, {self.serial_scale_x.get()}, {self.serial_scale_y.get()}, "{self.test_serial.get()}"
TEXT {self.stc_x.get()}, {self.stc_y.get()}, "{self.stc_font.get()}", 0, {self.stc_scale_x.get()}, {self.stc_scale_y.get()}, "STC:{self.test_stc.get()}"
PRINT 1, 1
"""
            return tspl
        except Exception as e:
            return f"Error generating TSPL: {e}"
    
    def update_preview(self):
        """Update TSPL preview and visual"""
        tspl = self.generate_tspl()
        
        # Update text preview
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, tspl)
        
        # Update size info
        try:
            width = self.size_width.get()
            height = self.size_height.get()
            gap = self.gap_size.get()
            self.size_info_label.config(text=f"Label: {width}mm × {height}mm, Gap: {gap}mm")
        except:
            self.size_info_label.config(text="Label size info")
        
        # Update visual preview
        self.update_visual()
        
    def update_visual(self):
        """Update visual representation"""
        self.canvas.delete("all")
        
        # Draw single label outline (40mm x 20mm scaled to 400px x 200px)
        self.canvas.create_rectangle(10, 10, 390, 190, outline="black", width=2, fill="lightyellow")
        
        try:
            # Scale coordinates (10:1 ratio - 1mm = 10px)
            serial_x = int(self.serial_x.get()) * 10
            serial_y = int(self.serial_y.get()) * 10 + 10  # Add 10 for border offset
            stc_x = int(self.stc_x.get()) * 10  
            stc_y = int(self.stc_y.get()) * 10 + 10  # Add 10 for border offset
            
            # Font size mapping (approximate visual sizes)
            font_sizes = {"1": 8, "2": 10, "3": 12, "4": 14, "5": 16}
            serial_size = font_sizes.get(self.serial_font.get(), 10)
            stc_size = font_sizes.get(self.stc_font.get(), 8)
            
            # Apply scaling factors to font size
            serial_scale_x = int(self.serial_scale_x.get())
            serial_scale_y = int(self.serial_scale_y.get())
            stc_scale_x = int(self.stc_scale_x.get())
            stc_scale_y = int(self.stc_scale_y.get())
            
            # Adjust font sizes based on scaling
            serial_display_size = serial_size * max(serial_scale_x, serial_scale_y)
            stc_display_size = stc_size * max(stc_scale_x, stc_scale_y)
            
            # Make sure text stays within bounds
            if serial_x > 390:
                serial_x = 390
            if serial_y > 190:
                serial_y = 190
            if stc_x > 390:
                stc_x = 390
            if stc_y > 190:
                stc_y = 190
                
            # Draw actual text content
            serial_text = self.test_serial.get()
            stc_text = f"STC:{self.test_stc.get()}"
            
            # Draw serial number
            self.canvas.create_text(serial_x, serial_y, text=serial_text, 
                                  anchor="nw", font=("Arial", serial_display_size, "bold"), 
                                  fill="blue", tags="serial")
            
            # Draw STC text
            self.canvas.create_text(stc_x, stc_y, text=stc_text, 
                                  anchor="nw", font=("Arial", stc_display_size), 
                                  fill="red", tags="stc")
            
            # Draw position indicators (small dots)
            self.canvas.create_oval(serial_x-3, serial_y-3, serial_x+3, serial_y+3, 
                                  fill="blue", outline="darkblue", tags="serial_dot")
            self.canvas.create_oval(stc_x-3, stc_y-3, stc_x+3, stc_y+3, 
                                  fill="red", outline="darkred", tags="stc_dot")
            
            # Add coordinate labels
            self.canvas.create_text(serial_x-5, serial_y-15, text=f"({self.serial_x.get()},{self.serial_y.get()})", 
                                  anchor="ne", font=("Arial", 7), fill="blue")
            self.canvas.create_text(stc_x-5, stc_y-15, text=f"({self.stc_x.get()},{self.stc_y.get()})", 
                                  anchor="ne", font=("Arial", 7), fill="red")
            
        except ValueError:
            # Show error message if invalid coordinates
            self.canvas.create_text(200, 100, text="Invalid coordinates", 
                                  anchor="center", font=("Arial", 12), fill="red")
    
    def apply_template(self, settings):
        """Apply a template configuration"""
        for key, value in settings.items():
            if hasattr(self, key):
                getattr(self, key).set(value)
        self.update_preview()
    
    def preview_print(self):
        """Preview print in debug mode"""
        if not self.printer_var.get():
            messagebox.showwarning("Warning", "Please select a printer first!")
            return
            
        try:
            printer = ZebraZPL(self.printer_var.get(), debug_mode=True)
            tspl = self.generate_tspl()
            success = printer.send_tspl(tspl)
            
            if success:
                messagebox.showinfo("Preview", "TSPL preview successful!\nCheck console for debug output.")
            else:
                messagebox.showerror("Error", "Preview failed!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Preview error: {e}")
    
    def test_print(self):
        """Actual test print"""
        if not self.printer_var.get():
            messagebox.showwarning("Warning", "Please select a printer first!")
            return
            
        # Confirm with user
        result = messagebox.askyesno("Confirm Print", 
                                   f"Send test print to {self.printer_var.get()}?\n\n"
                                   f"Serial: {self.test_serial.get()}\n"
                                   f"STC: {self.test_stc.get()}\n\n"
                                   f"Make sure printer has labels loaded!")
        
        if not result:
            return
            
        try:
            printer = ZebraZPL(self.printer_var.get(), debug_mode=False)
            tspl = self.generate_tspl()
            success = printer.send_tspl(tspl)
            
            if success:
                messagebox.showinfo("Success", "Test print sent successfully!\nCheck your XPrinter output.")
            else:
                messagebox.showerror("Error", "Print failed!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Print error: {e}")
    
    def print_multiple(self):
        """Print multiple labels with different data"""
        if not self.printer_var.get():
            messagebox.showwarning("Warning", "Please select a printer first!")
            return
            
        # Create multiple print dialog
        multi_window = tk.Toplevel(self.root)
        multi_window.title("📦 Multiple Label Printing")
        multi_window.geometry("600x500")
        multi_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(multi_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Instructions
        ttk.Label(main_frame, text="📦 Multiple Label Printing", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="Enter serial numbers and STC values (one per line):",
                 font=("Arial", 10)).pack(anchor="w")
        
        ttk.Label(main_frame, text="Format: SerialNumber,STC (e.g., 66182844496,60000)",
                 font=("Arial", 9), foreground="gray").pack(anchor="w", pady=(0, 10))
        
        # Text area for multiple entries
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        text_area = scrolledtext.ScrolledText(text_frame, height=15, font=("Consolas", 10))
        text_area.pack(fill="both", expand=True)
        
        # Pre-fill with example data or CSV data
        if hasattr(self, '_csv_data') and self._csv_data:
            text_area.insert(1.0, self._csv_data)
            # Clear the CSV data after use
            del self._csv_data
        else:
            example_data = """66182844496,60001
66182844497,60002
66182844498,60003
66182844499,60004
66182844500,60005"""
            text_area.insert(1.0, example_data)
        
        # Options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill="x", pady=(0, 10))
        
        # Print delay option
        ttk.Label(options_frame, text="Delay between prints (seconds):").pack(side="left")
        delay_var = tk.StringVar(value="2")
        delay_entry = ttk.Entry(options_frame, textvariable=delay_var, width=5)
        delay_entry.pack(side="left", padx=(5, 20))
        
        # Dry run option
        dry_run_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Dry run first (preview only)", 
                       variable=dry_run_var).pack(side="left")
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill="x", pady=(0, 10))
        
        progress_label = ttk.Label(progress_frame, text="Ready to print...")
        progress_label.pack(anchor="w")
        
        progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        progress_bar.pack(fill="x", pady=(5, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        def start_printing():
            """Start the multiple printing process"""
            # Get data from text area
            data_text = text_area.get(1.0, tk.END).strip()
            lines = [line.strip() for line in data_text.split('\n') if line.strip()]
            
            if not lines:
                messagebox.showwarning("Warning", "Please enter some data to print!")
                return
            
            # Parse data
            print_jobs = []
            for i, line in enumerate(lines, 1):
                try:
                    if ',' in line:
                        serial, stc = line.split(',', 1)
                        print_jobs.append({'serial': serial.strip(), 'stc': stc.strip()})
                    else:
                        # Only serial number provided, use default STC
                        print_jobs.append({'serial': line.strip(), 'stc': self.test_stc.get()})
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid data on line {i}: {line}\nError: {e}")
                    return
            
            total_jobs = len(print_jobs)
            progress_bar['maximum'] = total_jobs
            
            is_dry_run = dry_run_var.get()
            delay_seconds = float(delay_var.get() or 2)
            
            # Confirm printing
            mode_text = "DRY RUN (Preview)" if is_dry_run else "ACTUAL PRINTING"
            result = messagebox.askyesno("Confirm Multiple Print", 
                                       f"Start {mode_text}?\n\n"
                                       f"Total labels: {total_jobs}\n"
                                       f"Printer: {self.printer_var.get()}\n"
                                       f"Delay: {delay_seconds}s between prints")
            
            if not result:
                return
            
            # Start printing process
            try:
                printer = ZebraZPL(self.printer_var.get(), debug_mode=is_dry_run)
                
                success_count = 0
                failed_count = 0
                
                for i, job in enumerate(print_jobs, 1):
                    progress_label.config(text=f"Processing {i}/{total_jobs}: {job['serial']}")
                    progress_bar['value'] = i
                    multi_window.update()
                    
                    # Generate TSPL for this job
                    tspl = self.generate_tspl_for_data(job['serial'], job['stc'])
                    
                    # Print
                    try:
                        success = printer.send_tspl(tspl)
                        if success:
                            success_count += 1
                            progress_label.config(text=f"✅ Printed {i}/{total_jobs}: {job['serial']}")
                        else:
                            failed_count += 1
                            progress_label.config(text=f"❌ Failed {i}/{total_jobs}: {job['serial']}")
                    except Exception as e:
                        failed_count += 1
                        progress_label.config(text=f"❌ Error {i}/{total_jobs}: {job['serial']} - {e}")
                    
                    multi_window.update()
                    
                    # Delay between prints (except for last one)
                    if i < total_jobs:
                        import time
                        time.sleep(delay_seconds)
                
                # Final summary
                mode_suffix = " (Preview)" if is_dry_run else ""
                progress_label.config(text=f"✅ Complete{mode_suffix}: {success_count} success, {failed_count} failed")
                
                messagebox.showinfo("Printing Complete", 
                                   f"Multiple print job completed{mode_suffix}!\n\n"
                                   f"Successfully processed: {success_count}\n"
                                   f"Failed: {failed_count}\n"
                                   f"Total: {total_jobs}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Printing process failed: {e}")
        
        ttk.Button(button_frame, text="🚀 Start Printing", 
                  command=start_printing, style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=multi_window.destroy).pack(side="left", padx=5)
    
    def generate_tspl_for_data(self, serial_number, stc):
        """Generate TSPL for specific data"""
        try:
            tspl = f"""SIZE {self.size_width.get()} mm, {self.size_height.get()} mm
GAP {self.gap_size.get()} mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT {self.serial_x.get()}, {self.serial_y.get()}, "{self.serial_font.get()}", 0, {self.serial_scale_x.get()}, {self.serial_scale_y.get()}, "{serial_number}"
TEXT {self.stc_x.get()}, {self.stc_y.get()}, "{self.stc_font.get()}", 0, {self.stc_scale_x.get()}, {self.stc_scale_y.get()}, "STC:{stc}"
PRINT 1, 1
"""
            return tspl
        except Exception as e:
            return f"Error generating TSPL: {e}"
    
    def save_template(self):
        """Save current settings as template"""
        settings = {
            'size_width': self.size_width.get(),
            'size_height': self.size_height.get(),
            'gap_size': self.gap_size.get(),
            'serial_font': self.serial_font.get(),
            'serial_x': self.serial_x.get(),
            'serial_y': self.serial_y.get(),
            'serial_scale_x': self.serial_scale_x.get(),
            'serial_scale_y': self.serial_scale_y.get(),
            'stc_font': self.stc_font.get(),
            'stc_x': self.stc_x.get(),
            'stc_y': self.stc_y.get(),
            'stc_scale_x': self.stc_scale_x.get(),
            'stc_scale_y': self.stc_scale_y.get()
        }
        
        # Show TSPL for copying
        tspl = self.generate_tspl()
        
        info_window = tk.Toplevel(self.root)
        info_window.title("Template Settings")
        info_window.geometry("600x400")
        
        ttk.Label(info_window, text="📋 Current TSPL Template:", font=("Arial", 12, "bold")).pack(pady=5)
        
        text_widget = scrolledtext.ScrolledText(info_window, height=15, font=("Consolas", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=5)
        text_widget.insert(1.0, tspl)
        
        ttk.Label(info_window, text="Copy this TSPL to update your main program!").pack(pady=5)
    
    def import_csv(self):
        """Import data from CSV file for batch printing"""
        from tkinter import filedialog
        
        # Select CSV file
        csv_file = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not csv_file:
            return
        
        try:
            import csv
            
            # Read CSV file
            data_rows = []
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)  # Skip header row if exists
                
                for row_num, row in enumerate(reader, 2):
                    if len(row) >= 2:
                        serial = row[0].strip()
                        stc = row[1].strip()
                        if serial and stc:
                            data_rows.append(f"{serial},{stc}")
                    elif len(row) == 1:
                        serial = row[0].strip()
                        if serial:
                            data_rows.append(f"{serial},{self.test_stc.get()}")
            
            if not data_rows:
                messagebox.showwarning("Warning", "No valid data found in CSV file!\n\nExpected format:\nSerial,STC\n66182844496,60001\n...")
                return
            
            # Show import preview
            preview_text = '\n'.join(data_rows[:10])
            if len(data_rows) > 10:
                preview_text += f"\n... and {len(data_rows) - 10} more rows"
            
            result = messagebox.askyesno("Import CSV", 
                                       f"Import {len(data_rows)} records from CSV?\n\n"
                                       f"Preview:\n{preview_text}")
            
            if result:
                # Open multiple print dialog with imported data
                self.print_multiple_with_data('\n'.join(data_rows))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {e}")
    
    def print_multiple_with_data(self, data_text):
        """Open multiple print dialog with pre-filled data"""
        # This is similar to print_multiple but with CSV data pre-filled
        # For brevity, using the existing print_multiple and pre-filling the text area
        # In a real implementation, you'd create the dialog and populate it
        messagebox.showinfo("CSV Import", f"CSV data imported successfully!\nUse 'Print Multiple' to process the data.")
        
        # Store the data for the multiple print dialog
        self._csv_data = data_text
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = XPrinterPCBStudio()
    app.run()