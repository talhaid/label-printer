#!/usr/bin/env python3
"""
Zebra GC420T Auto-Printer GUI
============================

A user-friendly GUI for the Zebra GC420T serial auto-printer system.

Features:
- Serial port selection and monitoring
- Real-time printer status
- Live data preview and parsing
- Manual test printing
- Statistics and logging
- Template management
- Easy configuration

Author: GUI for Zebra GC420T Auto-Printer
Date: August 2025
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
from datetime import datetime
import os
import sys

# Import our modules
from serial_auto_printer import DeviceAutoPrinter, SerialPortMonitor, DeviceDataParser, ZPLTemplate
from zebra_zpl import ZebraZPL


class AutoPrinterGUI:
    """Main GUI application for the auto-printer system."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Zebra GC420T Auto-Printer")
        self.root.geometry("900x700")
        
        # System components
        self.auto_printer = None
        self.printer = ZebraZPL()
        self.is_monitoring = False
        
        # GUI update queue
        self.gui_queue = queue.Queue()
        
        # Default template
        self.current_template = """^XA
^PW399
^LL240
^CI28
^MD15
~SD15

^FO0,25^BQN,2,4
^FDLA,STC:{STC};SN:{SERIAL_NUMBER};IMEI:{IMEI};IMSI:{IMSI};CCID:{CCID};MAC:{MAC_ADDRESS}^FS

^CF0,18,18
^FO155,2.5^FDSTC:^FS
^FO155,40^FDS/N:^FS
^FO155,77.5^FDIMEI:^FS
^FO155,115^FDIMSI:^FS
^FO155,152.5^FDCCID:^FS
^FO155,190^FDMAC:^FS

^CF0,22,16
^FO195,2.5^FD{STC}^FS
^FO195,40^FD{SERIAL_NUMBER}^FS
^FO195,77.5^FD{IMEI}^FS
^FO195,115^FD{IMSI}^FS
^FO195,152.5^FD{CCID}^FS
^FO195,190^FD{MAC_ADDRESS}^FS

^XZ"""
        
        self.setup_gui()
        self.update_printer_list()
        self.update_port_list()
        
        # Start GUI update timer
        self.root.after(100, self.process_gui_queue)
    
    def setup_gui(self):
        """Setup the GUI layout."""
        # Create main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main Control Tab
        self.setup_main_tab(notebook)
        
        # Template Tab
        self.setup_template_tab(notebook)
        
        # Logs Tab
        self.setup_logs_tab(notebook)
        
        # Settings Tab
        self.setup_settings_tab(notebook)
    
    def setup_main_tab(self, notebook):
        """Setup the main control tab."""
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Main Control")
        
        # Connection Settings
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings")
        conn_frame.pack(fill="x", padx=5, pady=5)
        
        # Printer selection
        ttk.Label(conn_frame, text="Printer:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.printer_combo = ttk.Combobox(conn_frame, width=40)
        self.printer_combo.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(conn_frame, text="Refresh", command=self.update_printer_list).grid(row=0, column=2, padx=5, pady=2)
        
        # Serial port selection
        ttk.Label(conn_frame, text="Serial Port:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.port_combo = ttk.Combobox(conn_frame, width=20)
        self.port_combo.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        ttk.Button(conn_frame, text="Refresh", command=self.update_port_list).grid(row=1, column=2, padx=5, pady=2)
        
        # Baud rate
        ttk.Label(conn_frame, text="Baud Rate:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.baud_combo = ttk.Combobox(conn_frame, values=["9600", "19200", "38400", "57600", "115200"], width=20)
        self.baud_combo.set("9600")
        self.baud_combo.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Control Buttons
        control_frame = ttk.LabelFrame(main_frame, text="Control")
        control_frame.pack(fill="x", padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side="left", padx=5, pady=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(side="left", padx=5, pady=5)
        
        self.test_button = ttk.Button(control_frame, text="Test Print", command=self.test_print)
        self.test_button.pack(side="left", padx=5, pady=5)
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status indicator
        self.status_label = ttk.Label(status_frame, text="Status: Ready", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=5)
        
        # Statistics
        stats_frame = ttk.Frame(status_frame)
        stats_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Devices Processed:").grid(row=0, column=0, sticky="w")
        self.processed_label = ttk.Label(stats_frame, text="0")
        self.processed_label.grid(row=0, column=1, sticky="w", padx=(5, 20))
        
        ttk.Label(stats_frame, text="Successful Prints:").grid(row=0, column=2, sticky="w")
        self.success_label = ttk.Label(stats_frame, text="0")
        self.success_label.grid(row=0, column=3, sticky="w", padx=(5, 20))
        
        ttk.Label(stats_frame, text="Failed Prints:").grid(row=1, column=0, sticky="w")
        self.failed_label = ttk.Label(stats_frame, text="0")
        self.failed_label.grid(row=1, column=1, sticky="w", padx=(5, 20))
        
        ttk.Label(stats_frame, text="Parse Errors:").grid(row=1, column=2, sticky="w")
        self.errors_label = ttk.Label(stats_frame, text="0")
        self.errors_label.grid(row=1, column=3, sticky="w", padx=(5, 20))
        
        # Live data preview
        preview_frame = ttk.LabelFrame(status_frame, text="Live Data Preview")
        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.data_text = scrolledtext.ScrolledText(preview_frame, height=8, font=("Consolas", 9))
        self.data_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Test data input
        test_frame = ttk.LabelFrame(main_frame, text="Test Data Input")
        test_frame.pack(fill="x", padx=5, pady=5)
        
        self.test_data_entry = ttk.Entry(test_frame, width=70)
        self.test_data_entry.insert(0, "##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##")
        self.test_data_entry.pack(side="left", padx=5, pady=5)
        
        ttk.Button(test_frame, text="Test Parse & Print", command=self.test_data_processing).pack(side="left", padx=5, pady=5)
    
    def setup_template_tab(self, notebook):
        """Setup the template editing tab."""
        template_frame = ttk.Frame(notebook)
        notebook.add(template_frame, text="ZPL Template")
        
        # Template controls
        controls_frame = ttk.Frame(template_frame)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Load Template", command=self.load_template).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Save Template", command=self.save_template).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Reset to Default", command=self.reset_template).pack(side="left", padx=5)
        
        # Template editor
        ttk.Label(template_frame, text="ZPL Template (use placeholders like {SERIAL_NUMBER}, {IMEI}, etc.):").pack(anchor="w", padx=5)
        
        self.template_text = scrolledtext.ScrolledText(template_frame, height=20, font=("Consolas", 10))
        self.template_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.template_text.insert("1.0", self.current_template)
        
        # Placeholders info
        info_frame = ttk.LabelFrame(template_frame, text="Available Placeholders")
        info_frame.pack(fill="x", padx=5, pady=5)
        
        placeholders_text = "Available placeholders: {STC}, {SERIAL_NUMBER}, {IMEI}, {IMSI}, {CCID}, {MAC_ADDRESS}, {TIMESTAMP}"
        ttk.Label(info_frame, text=placeholders_text, wraplength=800).pack(padx=5, pady=5)
    
    def setup_logs_tab(self, notebook):
        """Setup the logs tab."""
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Logs")
        
        # Log controls
        log_controls = ttk.Frame(logs_frame)
        log_controls.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(log_controls, text="Clear Logs", command=self.clear_logs).pack(side="left", padx=5)
        ttk.Button(log_controls, text="Save Logs", command=self.save_logs).pack(side="left", padx=5)
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_controls, text="Auto-scroll", variable=self.auto_scroll_var).pack(side="left", padx=5)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=25, font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def setup_settings_tab(self, notebook):
        """Setup the settings tab."""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        # Regex settings
        regex_frame = ttk.LabelFrame(settings_frame, text="Data Parsing (Regex)")
        regex_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(regex_frame, text="Current pattern for: ##SERIAL|IMEI|IMSI|CCID|MAC##").pack(anchor="w", padx=5, pady=2)
        
        self.regex_entry = ttk.Entry(regex_frame, width=80)
        self.regex_entry.insert(0, r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-F]+)\|([A-F0-9:]+)##')
        self.regex_entry.pack(padx=5, pady=5)
        
        ttk.Button(regex_frame, text="Test Regex", command=self.test_regex).pack(padx=5, pady=5)
        
        # Field mapping
        fields_frame = ttk.LabelFrame(settings_frame, text="Field Mapping")
        fields_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(fields_frame, text="Field order (comma-separated):").pack(anchor="w", padx=5, pady=2)
        self.fields_entry = ttk.Entry(fields_frame, width=80)
        self.fields_entry.insert(0, "SERIAL_NUMBER,IMEI,IMSI,CCID,MAC_ADDRESS")
        self.fields_entry.pack(padx=5, pady=5)
        
        # Printing settings
        print_frame = ttk.LabelFrame(settings_frame, text="Printing Settings")
        print_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(print_frame, text="Auto-print on data received:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.auto_print_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(print_frame, variable=self.auto_print_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(print_frame, text="Default copies:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.copies_var = tk.StringVar(value="1")
        ttk.Entry(print_frame, textvariable=self.copies_var, width=5).grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    def update_printer_list(self):
        """Update the printer dropdown list."""
        try:
            printers = self.printer.list_printers()
            self.printer_combo['values'] = printers
            
            # Auto-select Zebra printer if found
            for printer in printers:
                if any(x in printer.lower() for x in ['zebra', 'gc420', 'zdesigner']):
                    self.printer_combo.set(printer)
                    break
            else:
                if printers:
                    self.printer_combo.set(printers[0])
                
        except Exception as e:
            self.log_message(f"Error updating printer list: {e}", "ERROR")
    
    def update_port_list(self):
        """Update the serial port dropdown list."""
        try:
            ports = SerialPortMonitor.list_serial_ports()
            port_names = [port['device'] for port in ports]
            self.port_combo['values'] = port_names
            
            if port_names:
                self.port_combo.set(port_names[0])
                
        except Exception as e:
            self.log_message(f"Error updating port list: {e}", "ERROR")
    
    def start_monitoring(self):
        """Start serial port monitoring."""
        try:
            # Get settings
            printer_name = self.printer_combo.get()
            port = self.port_combo.get()
            baudrate = int(self.baud_combo.get())
            template = self.template_text.get("1.0", "end-1c")
            
            if not printer_name:
                messagebox.showerror("Error", "Please select a printer")
                return
            
            if not port:
                messagebox.showerror("Error", "Please select a serial port")
                return
            
            # Create auto-printer instance
            self.auto_printer = DeviceAutoPrinter(
                zpl_template=template,
                serial_port=port,
                baudrate=baudrate,
                printer_name=printer_name
            )
            
            # Override the data callback to update GUI
            original_callback = self.auto_printer._handle_serial_data
            def gui_callback(data):
                self.gui_queue.put(('data', data))
                original_callback(data)
                self.gui_queue.put(('stats', self.auto_printer.stats))
            
            self.auto_printer.serial_monitor.set_data_callback(gui_callback)
            
            # Start monitoring
            if self.auto_printer.start():
                self.is_monitoring = True
                self.start_button.config(state="disabled")
                self.stop_button.config(state="normal")
                self.status_label.config(text="Status: Monitoring", foreground="green")
                self.log_message(f"Started monitoring {port} at {baudrate} baud", "INFO")
            else:
                messagebox.showerror("Error", "Failed to start monitoring")
                
        except Exception as e:
            self.log_message(f"Error starting monitoring: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop serial port monitoring."""
        try:
            if self.auto_printer:
                self.auto_printer.stop()
                self.auto_printer = None
            
            self.is_monitoring = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.status_label.config(text="Status: Stopped", foreground="red")
            self.log_message("Monitoring stopped", "INFO")
            
        except Exception as e:
            self.log_message(f"Error stopping monitoring: {e}", "ERROR")
    
    def test_print(self):
        """Test print a simple label."""
        try:
            printer_name = self.printer_combo.get()
            if not printer_name:
                messagebox.showerror("Error", "Please select a printer")
                return
            
            printer = ZebraZPL(printer_name)
            success = printer.print_text_label("GUI TEST", ["Print test from GUI", f"Time: {datetime.now().strftime('%H:%M:%S')}"])
            
            if success:
                self.log_message("Test print successful", "INFO")
                messagebox.showinfo("Success", "Test print completed successfully!")
            else:
                self.log_message("Test print failed", "ERROR")
                messagebox.showerror("Error", "Test print failed")
                
        except Exception as e:
            self.log_message(f"Test print error: {e}", "ERROR")
            messagebox.showerror("Error", f"Test print failed: {e}")
    
    def test_data_processing(self):
        """Test data processing and printing."""
        try:
            test_data = self.test_data_entry.get()
            if not test_data:
                messagebox.showerror("Error", "Please enter test data")
                return
            
            # Parse data
            parser = DeviceDataParser()
            device_data = parser.parse_data(test_data)
            
            if not device_data:
                self.log_message(f"Failed to parse test data: {test_data}", "ERROR")
                messagebox.showerror("Error", "Failed to parse test data")
                return
            
            # Show parsed data
            self.log_message(f"Parsed data: {device_data}", "INFO")
            
            # Print if auto-print is enabled
            if self.auto_print_var.get():
                template = self.template_text.get("1.0", "end-1c")
                printer_name = self.printer_combo.get()
                
                if not printer_name:
                    messagebox.showerror("Error", "Please select a printer")
                    return
                
                zpl_template = ZPLTemplate(template)
                zpl_commands = zpl_template.render(device_data)
                
                printer = ZebraZPL(printer_name)
                success = printer.send_zpl(zpl_commands)
                
                if success:
                    self.log_message("Test print successful", "INFO")
                    messagebox.showinfo("Success", "Test data processed and printed successfully!")
                else:
                    self.log_message("Test print failed", "ERROR")
                    messagebox.showerror("Error", "Print failed")
            else:
                messagebox.showinfo("Success", "Test data parsed successfully! (Auto-print disabled)")
                
        except Exception as e:
            self.log_message(f"Test processing error: {e}", "ERROR")
            messagebox.showerror("Error", f"Test failed: {e}")
    
    def test_regex(self):
        """Test the regex pattern."""
        try:
            import re
            pattern = self.regex_entry.get()
            test_data = self.test_data_entry.get()
            
            regex = re.compile(pattern)
            match = regex.search(test_data)
            
            if match:
                groups = match.groups()
                result = f"Regex match successful!\nGroups found: {len(groups)}\nValues: {groups}"
                self.log_message(f"Regex test: {result}", "INFO")
                messagebox.showinfo("Regex Test", result)
            else:
                result = f"Regex pattern did not match test data"
                self.log_message(f"Regex test: {result}", "WARNING")
                messagebox.showwarning("Regex Test", result)
                
        except Exception as e:
            self.log_message(f"Regex test error: {e}", "ERROR")
            messagebox.showerror("Error", f"Regex test failed: {e}")
    
    def load_template(self):
        """Load ZPL template from file."""
        try:
            filename = filedialog.askopenfilename(
                title="Load ZPL Template",
                filetypes=[("ZPL files", "*.zpl"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    template = f.read()
                
                self.template_text.delete("1.0", "end")
                self.template_text.insert("1.0", template)
                self.current_template = template
                self.log_message(f"Template loaded from {filename}", "INFO")
                
        except Exception as e:
            self.log_message(f"Error loading template: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to load template: {e}")
    
    def save_template(self):
        """Save ZPL template to file."""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save ZPL Template",
                defaultextension=".zpl",
                filetypes=[("ZPL files", "*.zpl"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                template = self.template_text.get("1.0", "end-1c")
                with open(filename, 'w') as f:
                    f.write(template)
                
                self.log_message(f"Template saved to {filename}", "INFO")
                messagebox.showinfo("Success", f"Template saved to {filename}")
                
        except Exception as e:
            self.log_message(f"Error saving template: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to save template: {e}")
    
    def reset_template(self):
        """Reset template to default."""
        self.template_text.delete("1.0", "end")
        self.template_text.insert("1.0", self.current_template)
        self.log_message("Template reset to default", "INFO")
    
    def clear_logs(self):
        """Clear the log display."""
        self.log_text.delete("1.0", "end")
    
    def save_logs(self):
        """Save logs to file."""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Logs",
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                logs = self.log_text.get("1.0", "end-1c")
                with open(filename, 'w') as f:
                    f.write(logs)
                
                messagebox.showinfo("Success", f"Logs saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logs: {e}")
    
    def log_message(self, message, level="INFO"):
        """Add message to log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.gui_queue.put(('log', log_entry))
    
    def process_gui_queue(self):
        """Process GUI update queue."""
        try:
            while True:
                item = self.gui_queue.get_nowait()
                msg_type, data = item
                
                if msg_type == 'log':
                    self.log_text.insert("end", data)
                    if self.auto_scroll_var.get():
                        self.log_text.see("end")
                
                elif msg_type == 'data':
                    # Update data preview
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    preview_text = f"[{timestamp}] Received: {data}\n"
                    self.data_text.insert("end", preview_text)
                    self.data_text.see("end")
                    
                    # Keep only last 50 lines
                    lines = self.data_text.get("1.0", "end-1c").split('\n')
                    if len(lines) > 50:
                        self.data_text.delete("1.0", f"{len(lines)-50}.0")
                
                elif msg_type == 'stats':
                    # Update statistics
                    stats = data
                    self.processed_label.config(text=str(stats.get('devices_processed', 0)))
                    self.success_label.config(text=str(stats.get('successful_prints', 0)))
                    self.failed_label.config(text=str(stats.get('failed_prints', 0)))
                    self.errors_label.config(text=str(stats.get('parse_errors', 0)))
                
        except queue.Empty:
            pass
        except Exception as e:
            print(f"GUI queue error: {e}")
        
        # Schedule next update
        self.root.after(100, self.process_gui_queue)
    
    def on_closing(self):
        """Handle application closing."""
        if self.is_monitoring:
            self.stop_monitoring()
        self.root.destroy()


def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = AutoPrinterGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Set window icon (if available)
    try:
        root.iconbitmap(default="printer.ico")
    except:
        pass  # Icon file not found, continue without it
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()