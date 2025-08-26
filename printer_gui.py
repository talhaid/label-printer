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
import pandas as pd
import qrcode
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

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
        
        # Initialize STC counter from CSV
        self.initialize_stc_from_csv()
        
        # Initialize mode display
        self.update_mode_display()
        
        # Start GUI update timer
        self.root.after(100, self.process_gui_queue)
    
    def setup_gui(self):
        """Setup the GUI layout."""
        # Create menu bar
        self.setup_menu()
        
        # Create main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main Control Tab
        self.setup_main_tab(notebook)
        
        # Box Labels Tab
        self.setup_box_labels_tab(notebook)
        
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
        self.baud_combo.set("115200")  # Default to 115200
        self.baud_combo.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # STC Counter Control
        stc_frame = ttk.LabelFrame(main_frame, text="STC Counter Control")
        stc_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(stc_frame, text="Current STC:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.stc_label = ttk.Label(stc_frame, text="6000", font=("Arial", 12, "bold"))
        self.stc_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(stc_frame, text="Set STC:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.stc_entry = ttk.Entry(stc_frame, width=10)
        self.stc_entry.insert(0, "6000")
        self.stc_entry.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Button(stc_frame, text="Update STC", command=self.update_stc).grid(row=0, column=4, padx=5, pady=2)
        ttk.Button(stc_frame, text="Refresh from CSV", command=self.refresh_stc_from_csv).grid(row=0, column=5, padx=5, pady=2)
        
        # Printing Mode Control
        mode_frame = ttk.LabelFrame(main_frame, text="Printing Mode")
        mode_frame.pack(fill="x", padx=5, pady=5)
        
        self.auto_print_mode = tk.BooleanVar(value=True)  # Default to auto-print
        ttk.Radiobutton(mode_frame, text="Auto Print (Print immediately when data received)", 
                       variable=self.auto_print_mode, value=True, command=self.update_mode_display).pack(anchor="w", padx=5, pady=2)
        ttk.Radiobutton(mode_frame, text="Queue Mode (Add to queue for manual confirmation)", 
                       variable=self.auto_print_mode, value=False, command=self.update_mode_display).pack(anchor="w", padx=5, pady=2)
        
        # Control Buttons
        control_frame = ttk.LabelFrame(main_frame, text="Control")
        control_frame.pack(fill="x", padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side="left", padx=5, pady=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(side="left", padx=5, pady=5)
        
        self.test_button = ttk.Button(control_frame, text="Test Print", command=self.test_print)
        self.test_button.pack(side="left", padx=5, pady=5)
        
        # Create notebook for dual tables
        tables_notebook = ttk.Notebook(main_frame)
        tables_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Device Labels Table Tab
        device_frame = ttk.Frame(tables_notebook)
        tables_notebook.add(device_frame, text="Device Labels (Zebra)")
        
        # Device data table
        device_table_frame = ttk.Frame(device_frame)
        device_table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for device data
        columns = ("STC", "Serial", "IMEI", "IMSI", "CCID", "MAC", "Status", "Time")
        self.data_tree = ttk.Treeview(device_table_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.data_tree.heading("STC", text="STC")
        self.data_tree.heading("Serial", text="Serial Number")
        self.data_tree.heading("IMEI", text="IMEI")
        self.data_tree.heading("IMSI", text="IMSI")
        self.data_tree.heading("CCID", text="CCID")
        self.data_tree.heading("MAC", text="MAC Address")
        self.data_tree.heading("Status", text="Status")
        self.data_tree.heading("Time", text="Time")
        
        self.data_tree.column("STC", width=80)
        self.data_tree.column("Serial", width=120)
        self.data_tree.column("IMEI", width=120)
        self.data_tree.column("IMSI", width=120)
        self.data_tree.column("CCID", width=120)
        self.data_tree.column("MAC", width=120)
        self.data_tree.column("Status", width=100)
        self.data_tree.column("Time", width=120)
        
        # Scrollbar for data table
        device_scrollbar = ttk.Scrollbar(device_table_frame, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=device_scrollbar.set)
        
        self.data_tree.pack(side="left", fill="both", expand=True)
        device_scrollbar.pack(side="right", fill="y")
        
        # Data control buttons (only show for queue mode)
        device_buttons_frame = ttk.Frame(device_frame)
        device_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self.print_selected_btn = ttk.Button(device_buttons_frame, text="Print Selected", command=self.print_selected_device)
        self.print_selected_btn.pack(side="left", padx=5)
        
        self.print_all_btn = ttk.Button(device_buttons_frame, text="Print All", command=self.print_all_devices)
        self.print_all_btn.pack(side="left", padx=5)
        
        self.remove_selected_btn = ttk.Button(device_buttons_frame, text="Remove Selected", command=self.remove_selected_device)
        self.remove_selected_btn.pack(side="left", padx=5)
        
        self.clear_queue_btn = ttk.Button(device_buttons_frame, text="Clear All", command=self.clear_device_queue)
        self.clear_queue_btn.pack(side="left", padx=5)
        
        self.clear_table_btn = ttk.Button(device_buttons_frame, text="Clear Table", command=self.clear_data_table)
        self.clear_table_btn.pack(side="left", padx=5)
        
        # PCB Labels Table Tab
        pcb_frame = ttk.Frame(tables_notebook)
        tables_notebook.add(pcb_frame, text="PCB Labels (XPrinter)")
        
        # PCB data table
        pcb_table_frame = ttk.Frame(pcb_frame)
        pcb_table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for PCB data (simpler - just serial number and status)
        pcb_columns = ("Serial", "Status", "Time", "Device STC")
        self.pcb_tree = ttk.Treeview(pcb_table_frame, columns=pcb_columns, show="headings", height=8)
        
        # Configure PCB columns
        self.pcb_tree.heading("Serial", text="Serial Number")
        self.pcb_tree.heading("Status", text="PCB Status")
        self.pcb_tree.heading("Time", text="Time")
        self.pcb_tree.heading("Device STC", text="Device STC")
        
        self.pcb_tree.column("Serial", width=150)
        self.pcb_tree.column("Status", width=120)
        self.pcb_tree.column("Time", width=120)
        self.pcb_tree.column("Device STC", width=100)
        
        # Scrollbar for PCB data table
        pcb_scrollbar = ttk.Scrollbar(pcb_table_frame, orient="vertical", command=self.pcb_tree.yview)
        self.pcb_tree.configure(yscrollcommand=pcb_scrollbar.set)
        
        self.pcb_tree.pack(side="left", fill="both", expand=True)
        pcb_scrollbar.pack(side="right", fill="y")
        
        # PCB control buttons
        pcb_buttons_frame = ttk.Frame(pcb_frame)
        pcb_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self.pcb_enable_btn = ttk.Button(pcb_buttons_frame, text="Disable PCB Printing", command=self.toggle_pcb_printing)
        self.pcb_enable_btn.pack(side="left", padx=5)
        
        self.pcb_test_btn = ttk.Button(pcb_buttons_frame, text="Test PCB Printer", command=self.test_pcb_printer)
        self.pcb_test_btn.pack(side="left", padx=5)
        
        self.pcb_clear_btn = ttk.Button(pcb_buttons_frame, text="Clear PCB Log", command=self.clear_pcb_log)
        self.pcb_clear_btn.pack(side="left", padx=5)
        
        # PCB printing status
        self.pcb_enabled = True  # Default enabled
        self.pcb_status_label = ttk.Label(pcb_buttons_frame, text="PCB Printing: Enabled", foreground="green")
        self.pcb_status_label.pack(side="right", padx=5)
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill="x", padx=5, pady=5)
        
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
        
        ttk.Label(stats_frame, text="In Queue/Processed:").grid(row=0, column=4, sticky="w")
        self.queue_size_label = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
        self.queue_size_label.grid(row=0, column=5, sticky="w", padx=(5, 20))
        
        # File output info
        files_frame = ttk.LabelFrame(status_frame, text="Output Files")
        files_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(files_frame, text="ZPL Files:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Button(files_frame, text="Open Folder", command=self.open_zpl_folder).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(files_frame, text="CSV Log:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Button(files_frame, text="Open CSV", command=self.open_csv_file).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
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
    
    def setup_box_labels_tab(self, notebook):
        """Setup the box labels creation tab."""
        box_frame = ttk.Frame(notebook)
        notebook.add(box_frame, text="Box Labels")
        
        # Initialize box label variables
        self.box_devices_df = None
        self.box_current_page = 0
        self.box_devices_per_page = 20
        self.box_selected_devices = []
        
        # Top controls frame
        box_control_frame = ttk.Frame(box_frame)
        box_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # CSV file selection
        ttk.Label(box_control_frame, text="CSV File:").pack(side=tk.LEFT)
        self.box_csv_path_var = tk.StringVar()
        self.box_csv_entry = ttk.Entry(box_control_frame, textvariable=self.box_csv_path_var, width=40)
        self.box_csv_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Button(box_control_frame, text="Browse", command=self.browse_box_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(box_control_frame, text="Load", command=self.load_box_csv_data).pack(side=tk.LEFT, padx=(0, 20))
        
        # Page navigation
        self.box_page_label = ttk.Label(box_control_frame, text="Page: 0/0")
        self.box_page_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(box_control_frame, text="◀ Prev", command=self.box_previous_page).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(box_control_frame, text="Next ▶", command=self.box_next_page).pack(side=tk.LEFT, padx=(0, 20))
        
        # Box number and create button
        ttk.Label(box_control_frame, text="Box:").pack(side=tk.LEFT, padx=(0, 5))
        self.box_number_var = tk.StringVar(value="BOX001")
        ttk.Entry(box_control_frame, textvariable=self.box_number_var, width=10).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(box_control_frame, text="Create PDF Label", command=self.create_box_pdf_label).pack(side=tk.RIGHT)
        
        # Selection info
        self.box_selection_label = ttk.Label(box_control_frame, text="Selected: 0/20")
        self.box_selection_label.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Device list frame
        list_frame = ttk.Frame(box_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create device list with checkboxes
        columns = ("select", "no", "serial", "imei", "mac", "status")
        self.box_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        self.box_tree.heading("select", text="☑")
        self.box_tree.heading("no", text="No.")
        self.box_tree.heading("serial", text="Serial Number")
        self.box_tree.heading("imei", text="IMEI")
        self.box_tree.heading("mac", text="MAC Address")
        self.box_tree.heading("status", text="Status")
        
        # Column widths
        self.box_tree.column("select", width=50, anchor=tk.CENTER)
        self.box_tree.column("no", width=50, anchor=tk.CENTER)
        self.box_tree.column("serial", width=180)
        self.box_tree.column("imei", width=180)
        self.box_tree.column("mac", width=140)
        self.box_tree.column("status", width=100)
        
        # Scrollbar for device list
        box_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.box_tree.yview)
        self.box_tree.configure(yscrollcommand=box_scrollbar.set)
        
        # Pack tree and scrollbar
        self.box_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        box_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind click events for selection
        self.box_tree.bind("<Button-1>", self.on_box_tree_click)
        
        # Instructions
        info_text = """📋 Instructions:
1. Load CSV file with device data (SERIAL_NUMBER, IMEI, MAC_ADDRESS columns required)
2. Browse through pages of 20 devices using Previous/Next buttons
3. Click on device rows to select them (max 20 per box)
4. Enter box number (e.g., BOX001, BOX002)
5. Click 'Create PDF Label' to generate box label with QR code and device list"""
        
        info_label = ttk.Label(box_frame, text=info_text, justify=tk.LEFT, wraplength=800)
        info_label.pack(padx=10, pady=5, anchor=tk.W)
    
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
    
    def initialize_stc_from_csv(self):
        """Initialize STC counter value from CSV file."""
        try:
            # Create a temporary auto-printer instance to check CSV
            temp_printer = DeviceAutoPrinter(
                zpl_template=self.current_template,
                initial_stc=6000
            )
            
            # Get the next STC value based on CSV
            next_stc = temp_printer.current_stc
            
            # Update GUI
            self.stc_entry.delete(0, "end")
            self.stc_entry.insert(0, str(next_stc))
            self.stc_label.config(text=str(next_stc))
            
            self.log_message(f"STC counter initialized to {next_stc} based on CSV history", "INFO")
            
        except Exception as e:
            self.log_message(f"Error initializing STC from CSV: {e}", "WARNING")
            # Use default value
            self.stc_entry.delete(0, "end")
            self.stc_entry.insert(0, "6000")
            self.stc_label.config(text="6000")
    
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
            
            # Try to set COM7 as default (USB-SERIAL device), then COM4, then COM3, otherwise use first available
            if 'COM7' in port_names:
                self.port_combo.set('COM7')
            elif 'COM4' in port_names:
                self.port_combo.set('COM4')
            elif 'COM3' in port_names:
                self.port_combo.set('COM3')
            elif port_names:
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
            
            # Get STC value
            try:
                initial_stc = int(self.stc_entry.get())
            except ValueError:
                initial_stc = 6000
                self.stc_entry.delete(0, "end")
                self.stc_entry.insert(0, "6000")
            
            # Create auto-printer instance
            self.auto_printer = DeviceAutoPrinter(
                zpl_template=template,
                serial_port=port,
                baudrate=baudrate,
                printer_name=printer_name,
                initial_stc=initial_stc
            )
            
            # Update GUI with actual STC value (may be different from input due to CSV detection)
            actual_stc = self.auto_printer.current_stc
            self.stc_entry.delete(0, "end")
            self.stc_entry.insert(0, str(actual_stc))
            self.stc_label.config(text=str(actual_stc))
            
            if actual_stc != initial_stc:
                self.log_message(f"STC auto-adjusted from {initial_stc} to {actual_stc} based on CSV history", "INFO")
            
            # Override the data callback to handle GUI mode switching
            def gui_callback(data):
                self.gui_queue.put(('data', data))
                
                # Check current mode and handle accordingly
                if self.auto_print_mode.get():
                    # Auto-print mode: use original behavior and add to table
                    result = self.auto_printer._handle_serial_data(data)
                    if result:  # If device was successfully processed
                        device_data, stc_assigned, pcb_success = result
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # Add to data table with STC and printed status
                        device_data['STC'] = stc_assigned
                        self.gui_queue.put(('add_to_table', (device_data, 'Printed', timestamp)))
                        
                        # Add PCB entry if PCB printing is enabled
                        if self.pcb_enabled:
                            serial_number = device_data.get('SERIAL_NUMBER', 'UNKNOWN')
                            pcb_status = "Printed" if pcb_success else "Failed"
                            self.gui_queue.put(('add_pcb_to_table', (serial_number, pcb_status, timestamp, stc_assigned)))
                else:
                    # Queue mode: parse data and add to queue manually
                    device_data = self.auto_printer.parser.parse_data(data)
                    if device_data:
                        self.auto_printer.stats['devices_processed'] += 1
                        stc_assigned = self.auto_printer.add_device_to_queue(device_data, data)
                        if stc_assigned:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            device_data['STC'] = stc_assigned
                            self.gui_queue.put(('add_to_table', (device_data, 'Queued', timestamp)))
                    else:
                        self.auto_printer.stats['parse_errors'] += 1
                
                self.gui_queue.put(('stats', self.auto_printer.stats))
                # Update STC display
                self.gui_queue.put(('stc', self.auto_printer.current_stc))
                # Update queue display
                self.gui_queue.put(('queue_update', None))
            
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
            
            # Check current mode - if monitoring is active, use the same mode as monitoring
            if self.is_monitoring and self.auto_printer:
                if self.auto_print_mode.get():
                    # Auto-print mode: print immediately
                    success, zpl_filename, stc_assigned, pcb_success = self.auto_printer.print_device_label_with_save(device_data, test_data)
                    if success:
                        pcb_status_text = " and PCB" if pcb_success else " (PCB failed)" if self.pcb_enabled else ""
                        self.log_message(f"Test device printed successfully{pcb_status_text}!", "INFO")
                        messagebox.showinfo("Success", f"Test device printed successfully{pcb_status_text}!")
                    else:
                        self.log_message("Test device print failed", "ERROR")
                        messagebox.showerror("Error", "Test device print failed")
                else:
                    # Queue mode: add to queue
                    self.auto_printer.add_device_to_queue(device_data, test_data)
                    self.update_device_queue_display()
                    self.update_queue_display()
                    messagebox.showinfo("Success", "Test device added to queue for manual printing!")
                return
            
            # If not monitoring, use the old direct print logic
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
    
    def open_zpl_folder(self):
        """Open the ZPL outputs folder."""
        try:
            import subprocess
            zpl_folder = os.path.abspath("zpl_outputs")
            if os.path.exists(zpl_folder):
                subprocess.Popen(f'explorer "{zpl_folder}"')
            else:
                messagebox.showinfo("Info", "ZPL output folder will be created when first device is processed")
        except Exception as e:
            self.log_message(f"Error opening ZPL folder: {e}", "ERROR")
    
    def open_csv_file(self):
        """Open the CSV log file."""
        try:
            import subprocess
            csv_file = os.path.abspath("device_log.csv")
            if os.path.exists(csv_file):
                subprocess.Popen(f'start excel "{csv_file}"', shell=True)
            else:
                messagebox.showinfo("Info", "CSV log file will be created when first device is processed")
        except Exception as e:
            self.log_message(f"Error opening CSV file: {e}", "ERROR")
    
    def refresh_stc_from_csv(self):
        """Refresh STC counter from CSV file."""
        try:
            if self.is_monitoring:
                messagebox.showwarning("Warning", "Cannot refresh STC while monitoring. Stop monitoring first.")
                return
            
            self.initialize_stc_from_csv()
            messagebox.showinfo("Success", f"STC counter refreshed from CSV. Next STC: {self.stc_label.cget('text')}")
            
        except Exception as e:
            self.log_message(f"Error refreshing STC from CSV: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to refresh STC: {e}")
    
    def update_stc(self):
        """Update the STC counter value."""
        try:
            new_stc = int(self.stc_entry.get())
            if new_stc < 0:
                messagebox.showerror("Error", "STC value must be non-negative")
                return
            
            if self.auto_printer:
                self.auto_printer.set_stc_value(new_stc)
                self.stc_label.config(text=str(new_stc))
                self.log_message(f"STC counter updated to {new_stc}", "INFO")
            else:
                messagebox.showwarning("Warning", "Auto-printer not started. STC will be set when monitoring starts.")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for STC")
    
    def print_selected_device(self):
        """Print the selected device from the queue."""
        try:
            selection = self.queue_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a device to print")
                return
            
            item = self.queue_tree.item(selection[0])
            device_data = item['values']
            
            if not device_data:
                messagebox.showerror("Error", "Invalid device data")
                return
            
            # Get device info from queue
            stc = device_data[0]
            serial = device_data[1]
            
            # Ask for confirmation and allow STC editing
            result = self.show_print_confirmation_dialog(device_data)
            if result:
                final_stc, should_print = result
                if should_print and self.auto_printer:
                    # Find device in queue and print it
                    for i, device_entry in enumerate(self.auto_printer.pending_devices):
                        if device_entry['device_data'].get('SERIAL_NUMBER') == serial:
                            # Update STC if changed
                            if final_stc != stc:
                                device_entry['stc_assigned'] = final_stc
                            
                            success, zpl_filename = self.auto_printer.print_device_from_queue(i, final_stc)
                            if success:
                                self.log_message(f"Printed device {serial} with STC {final_stc}", "INFO")
                                # Remove from GUI queue
                                self.queue_tree.delete(selection[0])
                                self.update_queue_display()
                            else:
                                self.log_message(f"Failed to print device {serial}", "ERROR")
                            break
                    
        except Exception as e:
            self.log_message(f"Error printing selected device: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to print device: {e}")
    
    def print_all_devices(self):
        """Print all devices in the queue."""
        try:
            if not self.auto_printer or not self.auto_printer.pending_devices:
                messagebox.showinfo("Info", "No devices in queue")
                return
            
            result = messagebox.askyesno("Confirm", 
                f"Print all {len(self.auto_printer.pending_devices)} devices in queue?")
            
            if result:
                printed_count = 0
                failed_count = 0
                
                # Print all devices (process in reverse order to maintain indices)
                for i in range(len(self.auto_printer.pending_devices) - 1, -1, -1):
                    device_entry = self.auto_printer.pending_devices[i]
                    stc = device_entry['stc_assigned']
                    success, zpl_filename = self.auto_printer.print_device_from_queue(i, stc)
                    
                    if success:
                        printed_count += 1
                    else:
                        failed_count += 1
                
                # Clear GUI queue
                for item in self.queue_tree.get_children():
                    self.queue_tree.delete(item)
                
                self.update_queue_display()
                self.log_message(f"Batch print completed: {printed_count} success, {failed_count} failed", "INFO")
                messagebox.showinfo("Complete", 
                    f"Batch print completed:\n{printed_count} printed successfully\n{failed_count} failed")
                
        except Exception as e:
            self.log_message(f"Error printing all devices: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to print all devices: {e}")
    
    def remove_selected_device(self):
        """Remove the selected device from the queue."""
        try:
            selection = self.queue_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a device to remove")
                return
            
            item = self.queue_tree.item(selection[0])
            device_data = item['values']
            serial = device_data[1]
            
            result = messagebox.askyesno("Confirm", f"Remove device {serial} from queue?")
            if result:
                # Remove from auto-printer queue
                if self.auto_printer:
                    for i, device_entry in enumerate(self.auto_printer.pending_devices):
                        if device_entry['device_data'].get('SERIAL_NUMBER') == serial:
                            del self.auto_printer.pending_devices[i]
                            break
                
                # Remove from GUI
                self.queue_tree.delete(selection[0])
                self.update_queue_display()
                self.log_message(f"Removed device {serial} from queue", "INFO")
                
        except Exception as e:
            self.log_message(f"Error removing device: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to remove device: {e}")
    
    def clear_device_queue(self):
        """Clear all devices from the queue."""
        try:
            if not self.auto_printer or not self.auto_printer.pending_devices:
                messagebox.showinfo("Info", "Queue is already empty")
                return
            
            count = len(self.auto_printer.pending_devices)
            result = messagebox.askyesno("Confirm", f"Clear all {count} devices from queue?")
            
            if result:
                self.auto_printer.pending_devices.clear()
                for item in self.queue_tree.get_children():
                    self.queue_tree.delete(item)
                self.update_queue_display()
                self.log_message(f"Cleared {count} devices from queue", "INFO")
                
        except Exception as e:
            self.log_message(f"Error clearing queue: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to clear queue: {e}")
    
    def show_print_confirmation_dialog(self, device_data):
        """Show a dialog for print confirmation with STC editing."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Print Confirmation")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()  # Make it modal
        
        # Center the dialog
        dialog.transient(self.root)
        
        result = {'stc': device_data[0], 'print': False}
        
        # Device info
        info_frame = ttk.LabelFrame(dialog, text="Device Information")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        labels = ["STC:", "Serial:", "IMEI:", "IMSI:", "CCID:", "MAC:"]
        for i, (label, value) in enumerate(zip(labels, device_data[:6])):
            ttk.Label(info_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=str(value), font=("Consolas", 9)).grid(row=i, column=1, sticky="w", padx=5, pady=2)
        
        # STC editing
        stc_frame = ttk.LabelFrame(dialog, text="STC Value")
        stc_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(stc_frame, text="STC Value:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        stc_entry = ttk.Entry(stc_frame, width=10)
        stc_entry.insert(0, str(device_data[0]))
        stc_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def on_print():
            try:
                result['stc'] = int(stc_entry.get())
                result['print'] = True
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid STC number")
        
        def on_cancel():
            result['print'] = False
            dialog.destroy()
        
        ttk.Button(button_frame, text="Print", command=on_print).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=5)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        if result['print']:
            return result['stc'], True
        return None
    
    def update_device_queue_display(self):
        """Update the device data table display based on current mode."""
        try:
            # Clear existing items
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            if not self.auto_printer:
                return
                
            if self.auto_print_mode.get():
                # Auto-print mode: We don't maintain a queue, but we can show recent activity
                # This will be updated through the add_device_to_data_table method
                pass
            else:
                # Queue mode: Show pending devices from queue
                if self.auto_printer.pending_devices:
                    for device_entry in self.auto_printer.pending_devices:
                        device_data = device_entry['device_data']
                        stc = device_entry['stc_assigned']
                        timestamp = device_entry['timestamp']
                        status = device_entry['status']
                        
                        values = (
                            stc,
                            device_data.get('SERIAL_NUMBER', ''),
                            device_data.get('IMEI', ''),
                            device_data.get('IMSI', ''),
                            device_data.get('CCID', ''),
                            device_data.get('MAC_ADDRESS', ''),
                            status,
                            timestamp.split(' ')[1] if ' ' in timestamp else timestamp  # Just time part
                        )
                        self.data_tree.insert("", "end", values=values)
                    
        except Exception as e:
            self.log_message(f"Error updating device queue display: {e}", "ERROR")
    
    def update_mode_display(self):
        """Update the display based on current mode (auto-print vs queue)."""
        try:
            is_queue_mode = not self.auto_print_mode.get()
            
            # Show/hide queue control buttons based on mode
            if is_queue_mode:
                self.print_selected_btn.pack(side="left", padx=5)
                self.print_all_btn.pack(side="left", padx=5)
                self.remove_selected_btn.pack(side="left", padx=5)
                self.clear_queue_btn.pack(side="left", padx=5)
            else:
                self.print_selected_btn.pack_forget()
                self.print_all_btn.pack_forget()
                self.remove_selected_btn.pack_forget()
                self.clear_queue_btn.pack_forget()
            
            # Update data table title and column headers
            if is_queue_mode:
                # Queue mode - show pending devices
                self.data_tree.heading("Status", text="Status")
            else:
                # Auto-print mode - show processed devices
                self.data_tree.heading("Status", text="Print Status")
            
            self.log_message(f"Mode changed to: {'Queue Mode' if is_queue_mode else 'Auto Print Mode'}", "INFO")
                
        except Exception as e:
            self.log_message(f"Error updating mode display: {e}", "ERROR")
    
    def add_device_to_data_table(self, device_data, status, timestamp):
        """Add a device to the data table display."""
        try:
            values = (
                device_data.get('STC', ''),
                device_data.get('SERIAL_NUMBER', ''),
                device_data.get('IMEI', ''),
                device_data.get('IMSI', ''),
                device_data.get('CCID', ''),
                device_data.get('MAC_ADDRESS', ''),
                status,
                timestamp.split(' ')[1] if ' ' in timestamp else timestamp  # Just time part
            )
            
            # Insert at the top of the table (most recent first)
            self.data_tree.insert("", 0, values=values)
            
            # Keep only last 100 entries to prevent memory issues
            children = self.data_tree.get_children()
            if len(children) > 100:
                for child in children[100:]:
                    self.data_tree.delete(child)
                    
        except Exception as e:
            self.log_message(f"Error adding device to data table: {e}", "ERROR")
    
    def clear_data_table(self):
        """Clear all entries from the data table."""
        try:
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            self.log_message("Data table cleared", "INFO")
        except Exception as e:
            self.log_message(f"Error clearing data table: {e}", "ERROR")
    
    def update_queue_display(self):
        """Update the device queue display."""
        try:
            if self.auto_printer:
                self.queue_size_label.config(text=str(len(self.auto_printer.pending_devices)))
            else:
                self.queue_size_label.config(text="0")
        except Exception as e:
            self.log_message(f"Error updating queue display: {e}", "ERROR")
    
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
                
                elif msg_type == 'stc':
                    # Update STC display
                    self.stc_label.config(text=str(data))
                
                elif msg_type == 'queue_update':
                    # Update device queue display
                    self.update_device_queue_display()
                    self.update_queue_display()
                
                elif msg_type == 'add_to_table':
                    # Add device to data table
                    device_data, status, timestamp = data
                    self.add_device_to_data_table(device_data, status, timestamp)
                
                elif msg_type == 'add_pcb_to_table':
                    # Add PCB entry to PCB table
                    serial_number, status, timestamp, device_stc = data
                    self.add_pcb_to_table(serial_number, status, timestamp, device_stc)
                
        except queue.Empty:
            pass
        except Exception as e:
            print(f"GUI queue error: {e}")
        
        # Schedule next update
        self.root.after(100, self.process_gui_queue)
    
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Windows menu
        windows_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Windows", menu=windows_menu)
        windows_menu.add_command(label="Koli", command=self.open_koli_window)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def open_koli_window(self):
        """Open the Koli window."""
        if hasattr(self, 'koli_window') and self.koli_window.winfo_exists():
            self.koli_window.lift()
            return
        
        self.create_koli_window()
    
    def create_koli_window(self):
        """Create the Koli window with CSV data table."""
        self.koli_window = tk.Toplevel(self.root)
        self.koli_window.title("Koli - CSV Data Viewer")
        self.koli_window.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.koli_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="CSV Data Viewer", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(control_frame, text="Refresh Data", command=self.refresh_csv_data).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Export CSV", command=self.export_csv_data).pack(side="left", padx=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.csv_search_var = tk.StringVar()
        self.csv_search_var.trace('w', self.filter_csv_data)
        search_entry = ttk.Entry(search_frame, textvariable=self.csv_search_var, width=30)
        search_entry.pack(side="left", padx=(0, 10))
        
        # Info label
        self.csv_info_label = ttk.Label(search_frame, text="")
        self.csv_info_label.pack(side="right")
        
        # Create treeview for CSV data
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Define columns based on CSV structure
        columns = ("Timestamp", "Serial Number", "IMEI", "IMSI", "CCID", "MAC Address", "STC", "Status", "ZPL File", "Raw Data")
        
        self.csv_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        # Configure column headings and widths
        self.csv_tree.heading("Timestamp", text="Timestamp")
        self.csv_tree.heading("Serial Number", text="Serial Number")
        self.csv_tree.heading("IMEI", text="IMEI")
        self.csv_tree.heading("IMSI", text="IMSI")
        self.csv_tree.heading("CCID", text="CCID")
        self.csv_tree.heading("MAC Address", text="MAC Address")
        self.csv_tree.heading("STC", text="STC")
        self.csv_tree.heading("Status", text="Status")
        self.csv_tree.heading("ZPL File", text="ZPL File")
        self.csv_tree.heading("Raw Data", text="Raw Data")
        
        # Set column widths
        self.csv_tree.column("Timestamp", width=120)
        self.csv_tree.column("Serial Number", width=120)
        self.csv_tree.column("IMEI", width=120)
        self.csv_tree.column("IMSI", width=120)
        self.csv_tree.column("CCID", width=120)
        self.csv_tree.column("MAC Address", width=120)
        self.csv_tree.column("STC", width=60)
        self.csv_tree.column("Status", width=80)
        self.csv_tree.column("ZPL File", width=150)
        self.csv_tree.column("Raw Data", width=200)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.csv_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.csv_tree.xview)
        self.csv_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.csv_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=(10, 0))
        self.csv_status_label = ttk.Label(status_frame, text="Ready")
        self.csv_status_label.pack(side="left")
        
        # Load initial data
        self.refresh_csv_data()
    
    def refresh_csv_data(self):
        """Refresh the CSV data in the table."""
        try:
            import csv
            
            # Clear existing data
            for item in self.csv_tree.get_children():
                self.csv_tree.delete(item)
            
            csv_file = "device_log.csv"
            if not os.path.exists(csv_file):
                self.csv_status_label.config(text="CSV file not found")
                self.csv_info_label.config(text="No data")
                return
            
            # Read CSV data
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                rows = list(csv_reader)
                
                # Sort by timestamp (most recent first)
                rows.sort(key=lambda x: x.get('TIMESTAMP', ''), reverse=True)
                
                # Insert data into treeview
                for row in rows:
                    values = (
                        row.get('timestamp', ''),
                        row.get('serial_number', ''),
                        row.get('imei', ''),
                        row.get('imsi', ''),
                        row.get('ccid', ''),
                        row.get('mac_address', ''),
                        row.get('stc', ''),
                        row.get('print_status', ''),
                        row.get('zpl_file', ''),
                        row.get('raw_data', '')
                    )
                    self.csv_tree.insert("", "end", values=values)
                
                self.csv_status_label.config(text=f"Loaded {len(rows)} records")
                self.csv_info_label.config(text=f"Total: {len(rows)} records")
                
        except Exception as e:
            self.csv_status_label.config(text=f"Error loading CSV: {e}")
            messagebox.showerror("Error", f"Failed to load CSV data: {e}")
    
    def filter_csv_data(self, *args):
        """Filter CSV data based on search term."""
        try:
            search_term = self.csv_search_var.get().lower()
            
            # If no search term, refresh all data
            if not search_term:
                self.refresh_csv_data()
                return
            
            # Clear current display
            for item in self.csv_tree.get_children():
                self.csv_tree.delete(item)
            
            csv_file = "device_log.csv"
            if not os.path.exists(csv_file):
                return
            
            # Read and filter CSV data
            import csv
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                filtered_rows = []
                
                for row in csv_reader:
                    # Search in all relevant fields
                    searchable_text = ' '.join([
                        row.get('timestamp', ''),
                        row.get('serial_number', ''),
                        row.get('imei', ''),
                        row.get('imsi', ''),
                        row.get('ccid', ''),
                        row.get('mac_address', ''),
                        row.get('stc', ''),
                        row.get('print_status', '')
                    ]).lower()
                    
                    if search_term in searchable_text:
                        filtered_rows.append(row)
                
                # Sort by timestamp (most recent first)
                filtered_rows.sort(key=lambda x: x.get('TIMESTAMP', ''), reverse=True)
                
                # Insert filtered data
                for row in filtered_rows:
                    values = (
                        row.get('timestamp', ''),
                        row.get('serial_number', ''),
                        row.get('imei', ''),
                        row.get('imsi', ''),
                        row.get('ccid', ''),
                        row.get('mac_address', ''),
                        row.get('stc', ''),
                        row.get('print_status', ''),
                        row.get('zpl_file', ''),
                        row.get('raw_data', '')
                    )
                    self.csv_tree.insert("", "end", values=values)
                
                self.csv_info_label.config(text=f"Showing: {len(filtered_rows)} records")
                
        except Exception as e:
            self.csv_status_label.config(text=f"Error filtering data: {e}")
    
    def export_csv_data(self):
        """Export filtered CSV data to a new file."""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export CSV Data",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            # Get current displayed data from treeview
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ["timestamp", "serial_number", "imei", "imsi", "ccid", "mac_address", "stc", "print_status", "zpl_file", "raw_data"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for item in self.csv_tree.get_children():
                    values = self.csv_tree.item(item)['values']
                    row_dict = dict(zip(fieldnames, values))
                    writer.writerow(row_dict)
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """Zebra GC420T Auto-Printer GUI
        
Version: 2.0
Date: August 2025

Features:
- Dual-mode operation (Auto-Print / Queue)
- Real-time serial monitoring  
- CSV data logging and viewing
- ZPL template management
- Comprehensive statistics

For support and updates, check the project documentation."""
        
        messagebox.showinfo("About", about_text)
    
    def toggle_pcb_printing(self):
        """Toggle PCB printing on/off."""
        try:
            if self.auto_printer:
                self.pcb_enabled = not self.pcb_enabled
                self.auto_printer.enable_pcb_printing(self.pcb_enabled)
                
                if self.pcb_enabled:
                    self.pcb_enable_btn.config(text="Disable PCB Printing")
                    self.pcb_status_label.config(text="PCB Printing: Enabled", foreground="green")
                else:
                    self.pcb_enable_btn.config(text="Enable PCB Printing")
                    self.pcb_status_label.config(text="PCB Printing: Disabled", foreground="red")
                
                self.log_message(f"PCB printing {'enabled' if self.pcb_enabled else 'disabled'}", "INFO")
            else:
                messagebox.showwarning("Warning", "Auto-printer not initialized")
                
        except Exception as e:
            self.log_message(f"Error toggling PCB printing: {e}", "ERROR")
    
    def test_pcb_printer(self):
        """Test the PCB printer."""
        try:
            if self.auto_printer:
                if self.auto_printer.is_pcb_printer_available():
                    success = self.auto_printer.test_pcb_printer()
                    if success:
                        self.log_message("PCB printer test successful", "INFO")
                        messagebox.showinfo("Success", "PCB printer test completed successfully!")
                    else:
                        self.log_message("PCB printer test failed", "ERROR")
                        messagebox.showerror("Error", "PCB printer test failed")
                else:
                    messagebox.showwarning("Warning", "XPrinter XP-470B not found")
            else:
                messagebox.showwarning("Warning", "Auto-printer not initialized")
                
        except Exception as e:
            self.log_message(f"Error testing PCB printer: {e}", "ERROR")
            messagebox.showerror("Error", f"PCB printer test error: {e}")
    
    def clear_pcb_log(self):
        """Clear the PCB log table."""
        try:
            for item in self.pcb_tree.get_children():
                self.pcb_tree.delete(item)
            self.log_message("PCB log cleared", "INFO")
        except Exception as e:
            self.log_message(f"Error clearing PCB log: {e}", "ERROR")
    
    def add_pcb_to_table(self, serial_number, status, timestamp, device_stc):
        """Add a PCB entry to the PCB table."""
        try:
            values = (serial_number, status, timestamp.split(' ')[1] if ' ' in timestamp else timestamp, device_stc)
            self.pcb_tree.insert("", 0, values=values)  # Insert at top
            
            # Keep only last 100 entries
            children = self.pcb_tree.get_children()
            if len(children) > 100:
                for child in children[100:]:
                    self.pcb_tree.delete(child)
                    
        except Exception as e:
            self.log_message(f"Error adding PCB to table: {e}", "ERROR")

    # Box Label Methods
    def browse_box_csv(self):
        """Browse for CSV file for box labels."""
        file_path = filedialog.askopenfilename(
            title="Select Device CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.box_csv_path_var.set(file_path)
            
    def load_box_csv_data(self):
        """Load data from CSV file for box labels."""
        csv_path = self.box_csv_path_var.get()
        if not csv_path or not os.path.exists(csv_path):
            messagebox.showerror("Error", "Please select a valid CSV file")
            return
            
        try:
            # Try to load CSV with different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
            for encoding in encodings:
                try:
                    self.box_devices_df = pd.read_csv(csv_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise Exception("Could not decode CSV file with any encoding")
                
            # Validate required columns
            required_columns = ['SERIAL_NUMBER', 'IMEI', 'MAC_ADDRESS']
            missing_columns = [col for col in required_columns if col not in self.box_devices_df.columns]
            
            if missing_columns:
                messagebox.showerror("Error", f"CSV missing required columns: {', '.join(missing_columns)}")
                return
                
            # Add status column if not exists
            if 'STATUS' not in self.box_devices_df.columns:
                self.box_devices_df['STATUS'] = 'Available'
                
            self.box_current_page = 0
            self.box_selected_devices = []
            self.update_box_device_display()
            self.log_message(f"Loaded {len(self.box_devices_df)} devices for box labels", "INFO")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
            
    def update_box_device_display(self):
        """Update the box device list display for current page."""
        if self.box_devices_df is None:
            return
            
        # Clear existing items
        for item in self.box_tree.get_children():
            self.box_tree.delete(item)
            
        # Calculate page info
        total_devices = len(self.box_devices_df)
        total_pages = (total_devices + self.box_devices_per_page - 1) // self.box_devices_per_page
        
        if total_pages == 0:
            self.box_page_label.config(text="Page: 0/0")
            return
            
        # Get devices for current page
        start_idx = self.box_current_page * self.box_devices_per_page
        end_idx = min(start_idx + self.box_devices_per_page, total_devices)
        page_devices = self.box_devices_df.iloc[start_idx:end_idx]
        
        # Add devices to tree
        for idx, (_, device) in enumerate(page_devices.iterrows()):
            global_idx = start_idx + idx
            is_selected = global_idx in self.box_selected_devices
            
            self.box_tree.insert("", tk.END, values=(
                "☑" if is_selected else "☐",
                f"{global_idx + 1:02d}",
                device['SERIAL_NUMBER'],
                device['IMEI'],
                device['MAC_ADDRESS'],
                device.get('STATUS', 'Available')
            ), tags=('selected' if is_selected else 'unselected',))
            
        # Configure tags
        self.box_tree.tag_configure('selected', background='lightblue')
        self.box_tree.tag_configure('unselected', background='white')
        
        # Update labels
        self.box_page_label.config(text=f"Page: {self.box_current_page + 1}/{total_pages}")
        self.box_selection_label.config(text=f"Selected: {len(self.box_selected_devices)}/20")
        
    def on_box_tree_click(self, event):
        """Handle box tree item clicks for selection."""
        item = self.box_tree.identify('item', event.x, event.y)
        if not item:
            return
            
        # Get the global index
        values = self.box_tree.item(item, 'values')
        device_no = int(values[1]) - 1  # Convert to 0-based index
        
        # Toggle selection
        if device_no in self.box_selected_devices:
            self.box_selected_devices.remove(device_no)
        else:
            if len(self.box_selected_devices) < 20:
                self.box_selected_devices.append(device_no)
            else:
                messagebox.showwarning("Selection Limit", "Maximum 20 devices can be selected for one box")
                return
                
        self.update_box_device_display()
        
    def box_previous_page(self):
        """Go to previous page in box device list."""
        if self.box_current_page > 0:
            self.box_current_page -= 1
            self.update_box_device_display()
            
    def box_next_page(self):
        """Go to next page in box device list."""
        if self.box_devices_df is not None:
            total_pages = (len(self.box_devices_df) + self.box_devices_per_page - 1) // self.box_devices_per_page
            if self.box_current_page < total_pages - 1:
                self.box_current_page += 1
                self.update_box_device_display()
                
    def create_box_qr_with_devices(self, devices):
        """Create QR code with all device data for box label."""
        qr_data = []
        for i, device in enumerate(devices, 1):
            # Ensure all values are strings to avoid numpy type issues
            serial = str(device['SERIAL_NUMBER'])
            imei = str(device['IMEI'])
            mac = str(device['MAC_ADDRESS'])
            qr_data.append(f"{i:02d}:{serial}:{imei}:{mac}")
        
        qr_string = "|".join(qr_data)
        
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=1
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        temp_path = f"temp_gui_qr_{datetime.now().strftime('%H%M%S_%f')}.png"
        qr_image.save(temp_path)
        return temp_path
        
    def generate_box_label_pdf(self, devices, box_number):
        """Generate box label PDF using optimized template."""
        width = 10 * cm
        height = 15 * cm
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        first_serial = str(devices[0]['SERIAL_NUMBER'])
        last_serial = str(devices[-1]['SERIAL_NUMBER'])
        filename = f"gui_box_{box_number}_{first_serial}_{last_serial}_{timestamp}.pdf"
        
        c = canvas.Canvas(filename, pagesize=(width, height))
        
        # QR code at top, 1cm from edge
        y = height - 10*mm
        qr_path = self.create_box_qr_with_devices(devices)
        qr_size = 40*mm
        qr_x = (width - qr_size) / 2
        qr_y = y - qr_size
        
        c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size)
        
        # Clean up QR
        try:
            os.remove(qr_path)
        except:
            pass
            
        # Header section below QR
        y = qr_y - 6*mm
        
        # Company name
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, y, "STC - SICAKLIK TAKIP CIHAZI")
        y -= 6*mm
        
        # Date and box
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, y, f"{datetime.now().strftime('%d/%m/%Y')} - {box_number}")
        y -= 6*mm
        
        # Device list section
        y -= 3*mm
        
        # Device list header
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(width/2, y, "DEVICE LIST")
        y -= 5*mm
        
        # Column headers
        c.setFont("Helvetica-Bold", 6)
        c.drawString(3*mm, y, "No.")
        c.drawString(10*mm, y, "Serial Number")
        c.drawString(42*mm, y, "IMEI")
        c.drawString(70*mm, y, "MAC")
        y -= 4*mm
        
        # Device entries
        c.setFont("Courier", 5.5)
        line_height = 3*mm
        
        for i, device in enumerate(devices, 1):
            if y > 5*mm:
                c.drawString(3*mm, y, f"{i:02d}")
                c.drawString(10*mm, y, str(device['SERIAL_NUMBER']))
                c.drawString(42*mm, y, str(device['IMEI']))
                c.drawString(70*mm, y, str(device['MAC_ADDRESS']))
                y -= line_height
            else:
                c.setFont("Helvetica", 5)
                c.drawCentredString(width/2, y, "... (complete data in QR code)")
                break
                
        c.save()
        return filename
        
    def create_box_pdf_label(self):
        """Create box label PDF for selected devices."""
        if len(self.box_selected_devices) == 0:
            messagebox.showwarning("No Selection", "Please select devices for the box label")
            return
            
        if len(self.box_selected_devices) != 20:
            result = messagebox.askyesno("Partial Selection", 
                                       f"Only {len(self.box_selected_devices)} devices selected. "
                                       f"Create label anyway?")
            if not result:
                return
                
        box_number = self.box_number_var.get().strip()
        if not box_number:
            messagebox.showerror("Error", "Please enter a box number")
            return
            
        try:
            # Get selected device data
            selected_device_data = []
            for idx in sorted(self.box_selected_devices):
                device_row = self.box_devices_df.iloc[idx]
                device_dict = {
                    'SERIAL_NUMBER': str(device_row['SERIAL_NUMBER']),
                    'IMEI': str(device_row['IMEI']),
                    'MAC_ADDRESS': str(device_row['MAC_ADDRESS'])
                }
                selected_device_data.append(device_dict)
                
            # Generate PDF
            filename = self.generate_box_label_pdf(selected_device_data, box_number)
            
            # Log success
            self.log_message(f"✅ Box label created: {filename} ({len(selected_device_data)} devices)", "INFO")
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"Box label created successfully!\n\n"
                              f"File: {filename}\n"
                              f"Devices: {len(selected_device_data)}\n"
                              f"Box: {box_number}")
                              
            # Clear selection
            self.box_selected_devices = []
            self.update_box_device_display()
            
            # Auto-increment box number
            if box_number.startswith("BOX") and box_number[3:].isdigit():
                new_number = int(box_number[3:]) + 1
                self.box_number_var.set(f"BOX{new_number:03d}")
                
        except Exception as e:
            error_msg = f"Failed to create box label: {str(e)}"
            self.log_message(error_msg, "ERROR")
            messagebox.showerror("Error", error_msg)

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