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
import csv
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
        
        # Initialize clean folder structure first
        self.initialize_folder_structure()
        
        # System components
        self.auto_printer = None
        self.printer = ZebraZPL()
        self.is_monitoring = False
        
        # GUI update queue
        self.gui_queue = queue.Queue()
        
        # Latest received data storage
        self.latest_device_data = {
            'STC': '',
            'SERIAL_NUMBER': '',
            'IMEI': '',
            'IMSI': '',
            'CCID': '',
            'MAC_ADDRESS': ''
        }
        
        # Default template
        self.current_template = """^XA
^PW399
^LL240
^CI28
^MD15
~SD15

^FO10,50^BQN,2,4
^FDLA,STC:{STC};SN:{SERIAL_NUMBER};IMEI:{IMEI};IMSI:{IMSI};CCID:{CCID};MAC:{MAC_ADDRESS}^FS

^CF0,18,18
^FO185,32.5^FDSTC:^FS
^FO185,70^FDS/N:^FS
^FO185,107.5^FDIMEI:^FS
^FO185,145^FDIMSI:^FS
^FO185,182.5^FDCCID:^FS
^FO185,220^FDMAC:^FS

^CF0,22,16
^FO225,32.5^FD{STC}^FS
^FO225,70^FD{SERIAL_NUMBER}^FS
^FO225,107.5^FD{IMEI}^FS
^FO225,145^FD{IMSI}^FS
^FO225,182.5^FD{CCID}^FS
^FO225,220^FD{MAC_ADDRESS}^FS

^XZ"""
        
        # Initialize basic CSV path first
        self.csv_file_path = os.path.join('save', 'csv', 'device_log.csv')
        
        self.setup_gui()
        self.update_printer_list()
        self.update_port_list()
        
        # Initialize STC counter from CSV
        self.initialize_stc_from_csv()
        
        # Initialize mode display
        self.update_mode_display()
        
        # Start GUI update timer
        self.root.after(100, self.process_gui_queue)
    
    def initialize_folder_structure(self):
        """Initialize clean, safe folder structure for all saves."""
        import shutil
        
        # Define the main save folder structure
        self.save_folders = {
            'main': 'save',
            'csv': os.path.join('save', 'csv'),
            'zpl_outputs': os.path.join('save', 'zpl_outputs'),
            'box_labels': os.path.join('save', 'box_labels'),
            'backups': os.path.join('save', 'backups')
        }
        
        # Clean old structure if exists and create fresh folders
        try:
            # Remove old save folder completely for fresh start
            if os.path.exists('save'):
                shutil.rmtree('save')
                print("🧹 Cleaned old save folder structure")
            
            # Create clean folder structure
            for folder_name, folder_path in self.save_folders.items():
                os.makedirs(folder_path, exist_ok=True)
                print(f"📁 Created folder: {folder_path}")
            
            # Initialize main CSV file with headers
            self.csv_file_path = os.path.join(self.save_folders['csv'], 'device_log.csv')
            self.initialize_main_csv()
            
            print("✅ Clean folder structure initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing folder structure: {e}")
            # Create minimal structure if error
            os.makedirs('save/csv', exist_ok=True)
            os.makedirs('save/zpl_outputs', exist_ok=True)
            os.makedirs('save/box_labels', exist_ok=True)
    
    def initialize_main_csv(self):
        """Initialize the main CSV file with proper headers."""
        csv_headers = [
            'timestamp', 'stc', 'serial_number', 'imei', 'imsi', 'ccid', 'mac_address',
            'print_status', 'parse_status', 'raw_data', 'zpl_filename', 'notes'
        ]
        
        # Create CSV with headers if it doesn't exist
        if not os.path.exists(self.csv_file_path):
            try:
                with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(csv_headers)
                print(f"📄 Initialized main CSV: {self.csv_file_path}")
            except Exception as e:
                print(f"❌ Error creating main CSV: {e}")
        else:
            # Check if existing CSV has proper format and fix if needed
            try:
                with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
                    first_line = csvfile.readline().strip()
                    expected_header = ','.join(csv_headers)
                    
                    # If headers don't match, backup and recreate
                    if first_line != expected_header:
                        # Create backup
                        backup_path = self.csv_file_path.replace('.csv', f'_backup_header_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
                        import shutil
                        shutil.copy2(self.csv_file_path, backup_path)
                        print(f"🔧 Fixed CSV headers - backup saved: {backup_path}")
                        
                        # Read existing data and rewrite with correct headers
                        import pandas as pd
                        try:
                            # Try to read with current headers
                            df = pd.read_csv(self.csv_file_path)
                            
                            # Map old columns to new format if possible
                            column_mapping = {}
                            for col in df.columns:
                                col_lower = col.lower().strip()
                                if 'timestamp' in col_lower or 'time' in col_lower:
                                    column_mapping[col] = 'timestamp'
                                elif 'stc' in col_lower:
                                    column_mapping[col] = 'stc'
                                elif 'serial' in col_lower:
                                    column_mapping[col] = 'serial_number'
                                elif 'imei' in col_lower:
                                    column_mapping[col] = 'imei'
                                elif 'imsi' in col_lower:
                                    column_mapping[col] = 'imsi'
                                elif 'ccid' in col_lower:
                                    column_mapping[col] = 'ccid'
                                elif 'mac' in col_lower:
                                    column_mapping[col] = 'mac_address'
                                elif 'status' in col_lower or 'print' in col_lower:
                                    column_mapping[col] = 'print_status'
                            
                            # Rename columns
                            df = df.rename(columns=column_mapping)
                            
                            # Add missing columns
                            for header in csv_headers:
                                if header not in df.columns:
                                    df[header] = ''
                            
                            # Reorder columns
                            df = df[csv_headers]
                            
                            # Write corrected CSV
                            df.to_csv(self.csv_file_path, index=False)
                            print(f"✅ CSV headers corrected successfully")
                            
                        except Exception as e:
                            # If pandas fails, just recreate with headers
                            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow(csv_headers)
                            print(f"⚠️ Recreated CSV with clean headers (data reading failed: {e})")
                        
            except Exception as e:
                print(f"❌ Error checking CSV format: {e}")
    
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
        
        # CSV Management Tab
        self.setup_csv_tab(notebook)
        
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
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now use scrollable_frame instead of main_frame for all content
        
        # Connection Settings
        conn_frame = ttk.LabelFrame(scrollable_frame, text="Connection Settings")
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
        stc_frame = ttk.LabelFrame(scrollable_frame, text="STC Counter Control")
        stc_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(stc_frame, text="Current STC:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.stc_label = ttk.Label(stc_frame, text="60000", font=("Arial", 12, "bold"))
        self.stc_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(stc_frame, text="Set STC:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.stc_entry = ttk.Entry(stc_frame, width=10)
        self.stc_entry.insert(0, "60000")
        self.stc_entry.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Button(stc_frame, text="Update STC", command=self.update_stc).grid(row=0, column=4, padx=5, pady=2)
        ttk.Button(stc_frame, text="Refresh from CSV", command=self.refresh_stc_from_csv).grid(row=0, column=5, padx=5, pady=2)
        
        # Printing Mode Control
        mode_frame = ttk.LabelFrame(scrollable_frame, text="Printing Mode")
        mode_frame.pack(fill="x", padx=5, pady=5)
        
        self.auto_print_mode = tk.BooleanVar(value=True)  # Default to auto-print
        ttk.Radiobutton(mode_frame, text="Auto Print (Print immediately when data received)", 
                       variable=self.auto_print_mode, value=True, command=self.update_mode_display).pack(anchor="w", padx=5, pady=2)
        ttk.Radiobutton(mode_frame, text="Queue Mode (Add to queue for manual confirmation)", 
                       variable=self.auto_print_mode, value=False, command=self.update_mode_display).pack(anchor="w", padx=5, pady=2)
        
        # Control Buttons
        control_frame = ttk.LabelFrame(scrollable_frame, text="Control")
        control_frame.pack(fill="x", padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side="left", padx=5, pady=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(side="left", padx=5, pady=5)
        
        self.test_button = ttk.Button(control_frame, text="Test Print", command=self.test_print)
        self.test_button.pack(side="left", padx=5, pady=5)
        
        # Status Frame
        status_frame = ttk.LabelFrame(scrollable_frame, text="Status")
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

        # Latest Received Data Table
        latest_data_frame = ttk.LabelFrame(status_frame, text="Latest Received Data")
        latest_data_frame.pack(fill="x", padx=5, pady=5)
        
        # Create table with clean layout
        self.setup_latest_data_table(latest_data_frame)

        # Live data preview
        preview_frame = ttk.LabelFrame(status_frame, text="Live Data Preview")
        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.data_text = scrolledtext.ScrolledText(preview_frame, height=8, font=("Consolas", 9))
        self.data_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Device Data Table with Queue Controls
        device_data_frame = ttk.LabelFrame(scrollable_frame, text="Device Data / Queue")
        device_data_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Queue control buttons frame
        queue_controls_frame = ttk.Frame(device_data_frame)
        queue_controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Queue control buttons (initially hidden, shown in queue mode)
        self.print_selected_btn = ttk.Button(queue_controls_frame, text="Print Selected", command=self.print_selected_device)
        self.print_selected_btn.pack(side="left", padx=5)
        
        self.print_all_btn = ttk.Button(queue_controls_frame, text="Print All Queue", command=self.print_all_devices)
        self.print_all_btn.pack(side="left", padx=5)
        
        self.remove_selected_btn = ttk.Button(queue_controls_frame, text="Remove Selected", command=self.remove_selected_device)
        self.remove_selected_btn.pack(side="left", padx=5)
        
        self.clear_queue_btn = ttk.Button(queue_controls_frame, text="Clear Queue", command=self.clear_device_queue)
        self.clear_queue_btn.pack(side="left", padx=5)
        
        # Device data table
        table_frame = ttk.Frame(device_data_frame)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for device data
        columns = ("STC", "Serial", "IMEI", "IMSI", "CCID", "MAC", "Status", "Time")
        self.data_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.data_tree.heading("STC", text="STC")
        self.data_tree.heading("Serial", text="Serial Number")
        self.data_tree.heading("IMEI", text="IMEI")
        self.data_tree.heading("IMSI", text="IMSI") 
        self.data_tree.heading("CCID", text="CCID")
        self.data_tree.heading("MAC", text="MAC Address")
        self.data_tree.heading("Status", text="Status")
        self.data_tree.heading("Time", text="Time")
        
        # Column widths
        self.data_tree.column("STC", width=60)
        self.data_tree.column("Serial", width=150)  # Increased for full serial numbers
        self.data_tree.column("IMEI", width=150)    # Increased for full IMEI
        self.data_tree.column("IMSI", width=150)    # Increased for full IMSI  
        self.data_tree.column("CCID", width=180)    # Increased for full CCID
        self.data_tree.column("MAC", width=140)     # Increased for full MAC address
        self.data_tree.column("Status", width=80)
        self.data_tree.column("Time", width=80)
        
        # Add scrollbar
        data_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=data_scrollbar.set)
        
        self.data_tree.pack(side="left", fill="both", expand=True)
        data_scrollbar.pack(side="right", fill="y")
        
        # For backward compatibility with queue methods
        self.queue_tree = self.data_tree
        
        # Initially hide queue controls (show in queue mode)
        self.queue_controls_frame = queue_controls_frame
        
        # Test data input
        test_frame = ttk.LabelFrame(scrollable_frame, text="Test Data Input")
        test_frame.pack(fill="x", padx=5, pady=5)
        
        self.test_data_entry = ttk.Entry(test_frame, width=70)
        self.test_data_entry.insert(0, "##TEST123456789|999888777666555|111222333444555|TEST1234567890ABCDEF|FF:EE:DD:CC:BB:AA##")
        self.test_data_entry.pack(side="left", padx=5, pady=5)
        
        ttk.Button(test_frame, text="Test Parse & Print", command=self.test_data_processing).pack(side="left", padx=5, pady=5)
        ttk.Button(test_frame, text="Test Table", command=self.test_table_data).pack(side="left", padx=5, pady=5)
    
    def setup_latest_data_table(self, parent_frame):
        """Setup the latest received data table with clean layout."""
        # Create a frame for the table
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill="x", padx=5, pady=5)
        
        # Data labels and values
        data_fields = [
            ('STC:', 'stc_value'),
            ('Serial Number:', 'sn_value'),
            ('IMEI:', 'imei_value'),
            ('IMSI:', 'imsi_value'),
            ('CCID:', 'ccid_value'),
            ('MAC Address:', 'mac_value')
        ]
        
        # Create the table layout
        self.latest_data_labels = {}
        for i, (label_text, var_name) in enumerate(data_fields):
            # Label
            ttk.Label(table_frame, text=label_text, font=("Arial", 9, "bold")).grid(
                row=i, column=0, sticky="w", padx=(5, 10), pady=2
            )
            # Value
            value_label = ttk.Label(table_frame, text="---", font=("Consolas", 9))
            value_label.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.latest_data_labels[var_name] = value_label
        
        # Configure column weights
        table_frame.columnconfigure(1, weight=1)
    
    def update_latest_data_display(self, device_data, stc):
        """Update the latest received data table."""
        try:
            self.latest_data_labels['stc_value'].config(text=str(stc))
            self.latest_data_labels['sn_value'].config(text=device_data.get('SERIAL_NUMBER', '---'))
            self.latest_data_labels['imei_value'].config(text=device_data.get('IMEI', '---'))
            self.latest_data_labels['imsi_value'].config(text=device_data.get('IMSI', '---'))
            self.latest_data_labels['ccid_value'].config(text=device_data.get('CCID', '---'))
            self.latest_data_labels['mac_value'].config(text=device_data.get('MAC_ADDRESS', '---'))
            
            # Store the data
            self.latest_device_data = device_data.copy()
            self.latest_device_data['STC'] = str(stc)
        except Exception as e:
            print(f"Error updating latest data display: {e}")

    def setup_box_labels_tab(self, notebook):
        """Setup the box labels creation tab with editing capabilities."""
        box_frame = ttk.Frame(notebook)
        notebook.add(box_frame, text="Box Labels")
        
        # Initialize box label variables
        self.box_devices_df = None
        self.box_current_page = 0
        self.box_devices_per_page = 20
        self.box_selected_devices = []
        
        # Top controls frame - File operations
        file_control_frame = ttk.LabelFrame(box_frame, text="CSV Data Source")
        file_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Main CSV info
        ttk.Label(file_control_frame, text="Using Main CSV:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.box_csv_path_var = tk.StringVar(value="save/csv/device_log.csv")
        csv_label = ttk.Label(file_control_frame, textvariable=self.box_csv_path_var, 
                             font=("Arial", 9, "bold"), foreground="green")
        csv_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # CSV control buttons
        ttk.Button(file_control_frame, text="🔄 Refresh", command=self.refresh_box_csv_data).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(file_control_frame, text="🧹 Clean CSV", command=self.clean_csv_data).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(file_control_frame, text="🗑️ Clear All CSV", command=self.clear_all_csv_data).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(file_control_frame, text="📂 Open CSV Folder", command=self.open_csv_folder).grid(row=0, column=5, padx=5, pady=5)
        
        # Data editing controls
        edit_control_frame = ttk.LabelFrame(box_frame, text="Data Editing")
        edit_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(edit_control_frame, text="➕ Add Row", command=self.add_box_device_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_control_frame, text="✏️ Edit Selected", command=self.edit_box_device_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_control_frame, text="🗑️ Delete Selected", command=self.delete_box_device_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_control_frame, text="📋 Duplicate Selected", command=self.duplicate_box_device_row).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(edit_control_frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        ttk.Button(edit_control_frame, text="🔍 Filter Data", command=self.filter_box_data).pack(side=tk.LEFT, padx=5)
        self.box_filter_var = tk.StringVar()
        filter_entry = ttk.Entry(edit_control_frame, textvariable=self.box_filter_var, width=20)
        filter_entry.pack(side=tk.LEFT, padx=5)
        # Bind filter to update display as user types
        self.box_filter_var.trace('w', lambda *args: self.filter_box_data())
        
        # Navigation and selection controls
        nav_control_frame = ttk.LabelFrame(box_frame, text="Navigation & Selection")
        nav_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Page navigation
        self.box_page_label = ttk.Label(nav_control_frame, text="Page: 0/0")
        self.box_page_label.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(nav_control_frame, text="◀ Prev", command=self.box_previous_page).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_control_frame, text="Next ▶", command=self.box_next_page).pack(side=tk.LEFT, padx=(0, 20))
        
        # Selection controls
        ttk.Button(nav_control_frame, text="Select All Page", command=self.select_all_box_devices).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_control_frame, text="Clear Selection", command=self.clear_all_box_devices).pack(side=tk.LEFT, padx=5)
        
        # Selection info
        self.box_selection_label = ttk.Label(nav_control_frame, text="Selected: 0/20")
        self.box_selection_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Box creation controls
        box_create_frame = ttk.LabelFrame(box_frame, text="Box Label Creation")
        box_create_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(box_create_frame, text="Box Number:").pack(side=tk.LEFT, padx=5)
        self.box_number_var = tk.StringVar(value="BOX001")
        ttk.Entry(box_create_frame, textvariable=self.box_number_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(box_create_frame, text="Create PDF Label", command=self.create_box_pdf_label).pack(side=tk.LEFT, padx=20)
        ttk.Button(box_create_frame, text="📁 Open Box Labels", command=self.open_box_labels_folder).pack(side=tk.LEFT, padx=5)
        
        # Device list frame with enhanced table
        list_frame = ttk.LabelFrame(box_frame, text="Device Data")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create device list with more columns and better editing
        columns = ("select", "stc", "serial", "imei", "imsi", "ccid", "mac", "status", "global_idx")
        self.box_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15, 
                                   displaycolumns=("select", "stc", "serial", "imei", "imsi", "ccid", "mac", "status"))
        
        # Configure columns
        self.box_tree.heading("select", text="☑")
        self.box_tree.heading("stc", text="STC")
        self.box_tree.heading("serial", text="Serial Number")
        self.box_tree.heading("imei", text="IMEI")
        self.box_tree.heading("imsi", text="IMSI")
        self.box_tree.heading("ccid", text="CCID")
        self.box_tree.heading("mac", text="MAC Address")
        self.box_tree.heading("status", text="Status")
        
        # Column widths
        self.box_tree.column("select", width=40, anchor=tk.CENTER)
        self.box_tree.column("stc", width=60, anchor=tk.CENTER)
        self.box_tree.column("serial", width=150)
        self.box_tree.column("imei", width=140)
        self.box_tree.column("imsi", width=140)
        self.box_tree.column("ccid", width=140)
        self.box_tree.column("mac", width=120)
        self.box_tree.column("status", width=80)
        
        # Scrollbars for device list
        box_v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.box_tree.yview)
        box_h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.box_tree.xview)
        self.box_tree.configure(yscrollcommand=box_v_scrollbar.set, xscrollcommand=box_h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.box_tree.grid(row=0, column=0, sticky="nsew")
        box_v_scrollbar.grid(row=0, column=1, sticky="ns")
        box_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events for selection and editing
        self.box_tree.bind("<Button-1>", self.on_box_tree_click)
        self.box_tree.bind("<Double-1>", self.on_box_tree_double_click)
        self.box_tree.bind("<Button-3>", self.on_box_tree_right_click)  # Right-click context menu
        
        # Status bar
        status_frame = ttk.Frame(box_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.box_status_label = ttk.Label(status_frame, text="Ready - Load or create CSV data to begin")
        self.box_status_label.pack(side=tk.LEFT)
        
        # Data count info
        self.box_data_info_label = ttk.Label(status_frame, text="Total: 0 | Filtered: 0")
        self.box_data_info_label.pack(side=tk.RIGHT)
        
        # Auto-load main CSV data when tab is initialized
        self.root.after(500, self.load_box_csv_data)  # Delay to ensure GUI is ready
    
    def setup_csv_tab(self, notebook):
        """Setup the CSV management tab."""
        csv_frame = ttk.Frame(notebook)
        notebook.add(csv_frame, text="CSV Manager")
        
        # CSV file info and controls
        csv_control_frame = ttk.Frame(csv_frame)
        csv_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Current CSV file display
        ttk.Label(csv_control_frame, text="Current CSV File:").pack(side=tk.LEFT)
        self.csv_file_label = ttk.Label(csv_control_frame, text="save/csv/device_log.csv", 
                                       font=("Arial", 10, "bold"), foreground="green")
        self.csv_file_label.pack(side=tk.LEFT, padx=(10, 20))
        
        # CSV control buttons
        ttk.Button(csv_control_frame, text="📂 Open CSV Folder", command=self.open_csv_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(csv_control_frame, text="📄 Open CSV File", command=self.open_csv_file_external).pack(side=tk.LEFT, padx=5)
        ttk.Button(csv_control_frame, text="🔄 Refresh View", command=self.refresh_csv_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(csv_control_frame, text="🧹 Clean CSV", command=self.clean_csv_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(csv_control_frame, text="🗑️ Clear All CSV", command=self.clear_all_csv_data).pack(side=tk.LEFT, padx=5)
        
        # CSV statistics
        csv_stats_frame = ttk.LabelFrame(csv_frame, text="CSV Statistics")
        csv_stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        stats_grid = ttk.Frame(csv_stats_frame)
        stats_grid.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(stats_grid, text="Total Records:").grid(row=0, column=0, sticky="w", padx=5)
        self.csv_total_label = ttk.Label(stats_grid, text="0", font=("Arial", 10, "bold"))
        self.csv_total_label.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="Valid Devices:").grid(row=0, column=2, sticky="w", padx=20)
        self.csv_valid_label = ttk.Label(stats_grid, text="0", font=("Arial", 10, "bold"), foreground="green")
        self.csv_valid_label.grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="Parse Errors:").grid(row=0, column=4, sticky="w", padx=20)
        self.csv_errors_label = ttk.Label(stats_grid, text="0", font=("Arial", 10, "bold"), foreground="red")
        self.csv_errors_label.grid(row=0, column=5, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="Latest STC:").grid(row=1, column=0, sticky="w", padx=5)
        self.csv_latest_stc_label = ttk.Label(stats_grid, text="60000", font=("Arial", 10, "bold"))
        self.csv_latest_stc_label.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="File Size:").grid(row=1, column=2, sticky="w", padx=20)
        self.csv_size_label = ttk.Label(stats_grid, text="0 KB", font=("Arial", 10, "bold"))
        self.csv_size_label.grid(row=1, column=3, sticky="w", padx=5)
        
        ttk.Label(stats_grid, text="Last Modified:").grid(row=1, column=4, sticky="w", padx=20)
        self.csv_modified_label = ttk.Label(stats_grid, text="Never", font=("Arial", 10, "bold"))
        self.csv_modified_label.grid(row=1, column=5, sticky="w", padx=5)
        
        # CSV data view with pagination
        csv_view_frame = ttk.LabelFrame(csv_frame, text="CSV Data Viewer")
        csv_view_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Pagination controls
        csv_nav_frame = ttk.Frame(csv_view_frame)
        csv_nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(csv_nav_frame, text="Show:").pack(side=tk.LEFT)
        self.csv_show_var = tk.StringVar(value="Latest 50")
        csv_show_combo = ttk.Combobox(csv_nav_frame, textvariable=self.csv_show_var, 
                                     values=["Latest 50", "Latest 100", "All Records", "Errors Only", "Valid Only"], 
                                     width=15, state="readonly")
        csv_show_combo.pack(side=tk.LEFT, padx=(5, 20))
        csv_show_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_csv_view())
        
        # Search box
        ttk.Label(csv_nav_frame, text="Search:").pack(side=tk.LEFT)
        self.csv_search_var = tk.StringVar()
        csv_search_entry = ttk.Entry(csv_nav_frame, textvariable=self.csv_search_var, width=20)
        csv_search_entry.pack(side=tk.LEFT, padx=(5, 10))
        csv_search_entry.bind("<KeyRelease>", lambda e: self.refresh_csv_view())
        
        ttk.Button(csv_nav_frame, text="Export Filtered", command=self.export_filtered_csv).pack(side=tk.RIGHT, padx=5)
        
        # CSV data table
        csv_table_frame = ttk.Frame(csv_view_frame)
        csv_table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for CSV data
        csv_columns = ("Time", "STC", "Serial", "IMEI", "IMSI", "CCID", "MAC", "Status")
        self.csv_tree = ttk.Treeview(csv_table_frame, columns=csv_columns, show="headings", height=15)
        
        # Configure columns
        self.csv_tree.heading("Time", text="Timestamp")
        self.csv_tree.heading("STC", text="STC")
        self.csv_tree.heading("Serial", text="Serial Number")
        self.csv_tree.heading("IMEI", text="IMEI")
        self.csv_tree.heading("IMSI", text="IMSI")
        self.csv_tree.heading("CCID", text="CCID")
        self.csv_tree.heading("MAC", text="MAC Address")
        self.csv_tree.heading("Status", text="Status")
        
        # Column widths
        self.csv_tree.column("Time", width=150)
        self.csv_tree.column("STC", width=80)
        self.csv_tree.column("Serial", width=150)
        self.csv_tree.column("IMEI", width=150)
        self.csv_tree.column("IMSI", width=150)
        self.csv_tree.column("CCID", width=150)
        self.csv_tree.column("MAC", width=130)
        self.csv_tree.column("Status", width=100)
        
        # Scrollbar for CSV table
        csv_scrollbar = ttk.Scrollbar(csv_table_frame, orient=tk.VERTICAL, command=self.csv_tree.yview)
        self.csv_tree.configure(yscrollcommand=csv_scrollbar.set)
        
        self.csv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        csv_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # CSV data is loaded initially
        self.csv_data = None
        self.refresh_csv_view()
    
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
                initial_stc=60000,
                csv_file_path=self.csv_file_path
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
            self.stc_entry.insert(0, "60000")
            self.stc_label.config(text="60000")
    
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
                initial_stc = 60000
                self.stc_entry.delete(0, "end")
                self.stc_entry.insert(0, "60000")
            
            # Create auto-printer instance
            self.auto_printer = DeviceAutoPrinter(
                zpl_template=template,
                serial_port=port,
                baudrate=baudrate,
                printer_name=printer_name,
                initial_stc=initial_stc,
                zpl_output_dir=self.save_folders['zpl_outputs'],
                csv_file_path=self.csv_file_path
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
                        # Update latest data display
                        self.gui_queue.put(('device_processed', (device_data, stc_assigned)))
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
                        self.log_message(f"Test device printed successfully!", "INFO")
                        # Update latest data display
                        self.gui_queue.put(('device_processed', (device_data, stc_assigned)))
                        messagebox.showinfo("Success", f"Test device printed successfully!")
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
    
    def test_table_data(self):
        """Test adding data directly to the unified table."""
        try:
            # Create test device data
            test_device_data = {
                'STC': '60001',
                'SERIAL_NUMBER': 'ATS542912923728',
                'IMEI': '866988074133496',
                'IMSI': '286019876543210',
                'CCID': '8991101200003204510',
                'MAC_ADDRESS': 'AA:BB:CC:DD:EE:FF'
            }
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add directly to table via GUI queue (same as normal processing)
            self.gui_queue.put(('add_to_table', (test_device_data, 'Manual Test', timestamp)))
            
            self.log_message(f"Added test data to table: {test_device_data['SERIAL_NUMBER']}", "INFO")
            messagebox.showinfo("Success", "Test data added to Device Data table!")
            
        except Exception as e:
            self.log_message(f"Test table error: {e}", "ERROR")
            messagebox.showerror("Error", f"Test table failed: {e}")
    
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
            zpl_folder = os.path.abspath(self.save_folders['zpl_outputs'])
            if os.path.exists(zpl_folder):
                subprocess.Popen(f'explorer "{zpl_folder}"')
            else:
                os.makedirs(zpl_folder, exist_ok=True)
                subprocess.Popen(f'explorer "{zpl_folder}"')
                messagebox.showinfo("Info", "ZPL outputs folder created and opened")
        except Exception as e:
            self.log_message(f"Error opening ZPL folder: {e}", "ERROR")
    
    def open_csv_file(self):
        """Open the CSV log file."""
        try:
            import subprocess
            csv_file = os.path.abspath(self.get_csv_path())
            if os.path.exists(csv_file):
                subprocess.Popen(f'start excel "{csv_file}"', shell=True)
            else:
                messagebox.showinfo("Info", "CSV log file will be created when first device is processed")
        except Exception as e:
            self.log_message(f"Error opening CSV file: {e}", "ERROR")
    
    def open_box_labels_folder(self):
        """Open the box labels folder."""
        try:
            import subprocess
            box_labels_folder = os.path.abspath(self.save_folders['box_labels'])
            if os.path.exists(box_labels_folder):
                subprocess.Popen(f'explorer "{box_labels_folder}"')
            else:
                os.makedirs(box_labels_folder, exist_ok=True)
                subprocess.Popen(f'explorer "{box_labels_folder}"')
                messagebox.showinfo("Info", "Box labels folder created and opened")
        except Exception as e:
            self.log_message(f"Error opening box labels folder: {e}", "ERROR")
    
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
                
                elif msg_type == 'device_processed':
                    # Update latest received data display
                    device_data, stc = data
                    self.update_latest_data_display(device_data, stc)
                
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
            
            csv_file = os.path.join("save", "csv", "device_log.csv")
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
            
            csv_file = os.path.join("save", "csv", "device_log.csv")
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
            
            # Get filtered data based on current view
            display_data = self.csv_data.copy()
            show_option = self.csv_show_var.get()
            
            if show_option == "Latest 50":
                display_data = display_data.tail(50)
            elif show_option == "Latest 100":
                display_data = display_data.tail(100)
            elif show_option == "Errors Only":
                if 'STATUS' in display_data.columns:
                    display_data = display_data[display_data['STATUS'] == 'PARSE_ERROR']
            elif show_option == "Valid Only":
                if 'STATUS' in display_data.columns:
                    display_data = display_data[display_data['STATUS'] != 'PARSE_ERROR']
            
            # Apply search filter
            search_term = self.csv_search_var.get().strip().lower()
            if search_term:
                mask = display_data.astype(str).apply(lambda x: x.str.lower().str.contains(search_term, na=False)).any(axis=1)
                display_data = display_data[mask]
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialdir=os.path.join("save", "csv"),
                initialname=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if filename:
                display_data.to_csv(filename, index=False)
                messagebox.showinfo("Export Complete", f"Filtered data exported to:\n{filename}\n\nRecords: {len(display_data)}")
                self.log_message(f"Exported {len(display_data)} filtered records to {filename}", "INFO")
        
        except Exception as e:
            self.log_message(f"Error exporting CSV: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
    
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
    
    def clear_pcb_log(self):
        """Clear the PCB log entries from the unified table."""
        try:
            # Clear all entries from the unified data table
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            self.log_message("Device log cleared", "INFO")
        except Exception as e:
            self.log_message(f"Error clearing device log: {e}", "ERROR")
    
    def add_pcb_to_table(self, serial_number, status, timestamp, device_stc):
        """Add a PCB entry to the unified device table."""
        try:
            # Format timestamp to show just time if it contains date
            time_display = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
            
            # Add to unified table with all columns, filling PCB-specific ones
            values = (device_stc, serial_number, "PCB", "PCB", "PCB", "PCB", f"PCB: {status}", time_display)
            self.data_tree.insert("", 0, values=values)  # Insert at top
            
            # Keep only last 100 entries
            children = self.data_tree.get_children()
            if len(children) > 100:
                for child in children[100:]:
                    self.data_tree.delete(child)
                    
        except Exception as e:
            self.log_message(f"Error adding PCB to table: {e}", "ERROR")

    # Box Label Methods
    def refresh_box_csv_data(self):
        """Refresh box CSV data from main CSV file."""
        self.load_box_csv_data()
        
    def browse_box_csv(self):
        """Browse for CSV file for box labels."""
        file_path = filedialog.askopenfilename(
            title="Select Device CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.box_csv_path_var.set(file_path)
            
    def load_box_csv_data(self):
        """Load data from main CSV file for box labels."""
        csv_path = self.get_csv_path()  # Use our main CSV
        
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", f"Main CSV file not found: {csv_path}")
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
                
            # Ensure all required columns exist
            # The CSV structure is: [timestamp, stc, serial_number, imei, imsi, ccid, mac_address, print_status, parse_status, ...]
            # Headers and data match correctly now
            if len(self.box_devices_df.columns) < 8:
                # Pad with empty columns if needed
                for i in range(len(self.box_devices_df.columns), 8):
                    self.box_devices_df[f'col_{i}'] = ''
            
            # Add status column if missing
            if len(self.box_devices_df.columns) < 7 or self.box_devices_df.iloc[:, 6].isna().all():
                if len(self.box_devices_df.columns) <= 6:
                    self.box_devices_df['status'] = 'Available'
                else:
                    self.box_devices_df.iloc[:, 6] = self.box_devices_df.iloc[:, 6].fillna('Available')
                
            self.box_current_page = 0
            self.box_selected_devices = []
            self.update_box_device_display()
            self.update_box_data_info()
            self.box_status_label.config(text=f"✅ Loaded {len(self.box_devices_df)} devices from CSV")
            self.log_message(f"Loaded {len(self.box_devices_df)} devices for box labels", "INFO")
            
        except Exception as e:
            self.box_status_label.config(text=f"❌ Error loading CSV: {str(e)}")
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
    
    def save_box_csv_data(self):
        """Save the current box data to CSV file."""
        if self.box_devices_df is None or len(self.box_devices_df) == 0:
            messagebox.showwarning("Warning", "No data to save")
            return
            
        csv_path = self.box_csv_path_var.get()
        if not csv_path:
            csv_path = filedialog.asksaveasfilename(
                title="Save CSV Data",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if csv_path:
                self.box_csv_path_var.set(csv_path)
        
        if csv_path:
            try:
                self.box_devices_df.to_csv(csv_path, index=False, encoding='utf-8')
                self.box_status_label.config(text=f"✅ Saved {len(self.box_devices_df)} devices to CSV")
                self.log_message(f"Saved box data to {csv_path}", "INFO")
                messagebox.showinfo("Success", f"Data saved to {csv_path}")
            except Exception as e:
                self.box_status_label.config(text=f"❌ Error saving CSV: {str(e)}")
                messagebox.showerror("Error", f"Failed to save CSV: {str(e)}")
    
    def create_new_box_csv(self):
        """Create a new empty CSV for box labels."""
        # Create empty DataFrame with required columns
        columns = ['STC', 'SERIAL_NUMBER', 'IMEI', 'IMSI', 'CCID', 'MAC_ADDRESS', 'STATUS']
        self.box_devices_df = pd.DataFrame(columns=columns)
        
        self.box_current_page = 0
        self.box_selected_devices = []
        self.box_csv_path_var.set("")
        
        self.update_box_device_display()
        self.update_box_data_info()
        self.box_status_label.config(text="📝 New CSV created - Add devices manually")
        self.log_message("Created new CSV for box labels", "INFO")
    
    def add_box_device_row(self):
        """Add a new device row."""
        dialog = self.create_device_edit_dialog("Add New Device")
        if dialog:
            try:
                # Add to DataFrame
                new_row = pd.DataFrame([dialog], columns=self.box_devices_df.columns)
                self.box_devices_df = pd.concat([self.box_devices_df, new_row], ignore_index=True)
                
                self.update_box_device_display()
                self.update_box_data_info()
                self.box_status_label.config(text="✅ Device added successfully")
                self.log_message("Added new device to box data", "INFO")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add device: {str(e)}")
    
    def edit_box_device_row(self):
        """Edit the selected device row."""
        selection = self.box_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a device to edit")
            return
        
        try:
            # Get the selected item data
            item = self.box_tree.item(selection[0])
            values = item['values']
            global_idx = int(values[8])  # global_idx is the last column
            
            # Get current data
            current_data = self.box_devices_df.iloc[global_idx].to_dict()
            
            # Show edit dialog
            dialog = self.create_device_edit_dialog("Edit Device", current_data)
            if dialog:
                # Update DataFrame
                for col, value in dialog.items():
                    self.box_devices_df.at[global_idx, col] = value
                
                self.update_box_device_display()
                self.box_status_label.config(text="✅ Device updated successfully")
                self.log_message("Updated device in box data", "INFO")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit device: {str(e)}")
    
    def delete_box_device_row(self):
        """Delete the selected device row(s)."""
        selection = self.box_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select device(s) to delete")
            return
        
        if len(selection) == 1:
            msg = "Delete the selected device?"
        else:
            msg = f"Delete {len(selection)} selected devices?"
            
        if messagebox.askyesno("Confirm Delete", msg):
            try:
                # Get global indices to delete
                indices_to_delete = []
                for item_id in selection:
                    item = self.box_tree.item(item_id)
                    values = item['values']
                    global_idx = int(values[8])
                    indices_to_delete.append(global_idx)
                
                # Sort in reverse order to delete from end to beginning
                indices_to_delete.sort(reverse=True)
                
                # Delete rows
                for idx in indices_to_delete:
                    self.box_devices_df = self.box_devices_df.drop(idx).reset_index(drop=True)
                
                # Clear selection
                for idx in indices_to_delete:
                    if idx in self.box_selected_devices:
                        self.box_selected_devices.remove(idx)
                
                self.update_box_device_display()
                self.update_box_data_info()
                self.box_status_label.config(text=f"✅ Deleted {len(indices_to_delete)} device(s)")
                self.log_message(f"Deleted {len(indices_to_delete)} devices from box data", "INFO")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete device(s): {str(e)}")
    
    def duplicate_box_device_row(self):
        """Duplicate the selected device row."""
        selection = self.box_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a device to duplicate")
            return
        
        try:
            # Get the selected item data
            item = self.box_tree.item(selection[0])
            values = item['values']
            global_idx = int(values[8])
            
            # Get current data and modify serial number
            current_data = self.box_devices_df.iloc[global_idx].to_dict()
            current_data['SERIAL_NUMBER'] = current_data['SERIAL_NUMBER'] + "_COPY"
            if 'STC' in current_data:
                # Auto-increment STC
                max_stc = self.box_devices_df['STC'].max() if len(self.box_devices_df) > 0 else 60000
                current_data['STC'] = max_stc + 1
            
            # Show edit dialog for the duplicated data
            dialog = self.create_device_edit_dialog("Duplicate Device", current_data)
            if dialog:
                # Add to DataFrame
                new_row = pd.DataFrame([dialog], columns=self.box_devices_df.columns)
                self.box_devices_df = pd.concat([self.box_devices_df, new_row], ignore_index=True)
                
                self.update_box_device_display()
                self.update_box_data_info()
                self.box_status_label.config(text="✅ Device duplicated successfully")
                self.log_message("Duplicated device in box data", "INFO")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to duplicate device: {str(e)}")
    
    def filter_box_data(self):
        """Filter the box data based on search term."""
        search_term = self.box_filter_var.get().strip().lower()
        self.box_current_page = 0  # Reset to first page
        self.update_box_device_display()
        
        if search_term:
            self.box_status_label.config(text=f"🔍 Filtered by: '{search_term}'")
        else:
            self.box_status_label.config(text="📋 Showing all data")
    
    def create_device_edit_dialog(self, title, current_data=None):
        """Create a dialog for editing device data."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = {}
        
        # Create form fields
        fields = ['STC', 'SERIAL_NUMBER', 'IMEI', 'IMSI', 'CCID', 'MAC_ADDRESS', 'STATUS']
        entries = {}
        
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form fields
        for i, field in enumerate(fields):
            ttk.Label(main_frame, text=f"{field}:").grid(row=i, column=0, sticky="w", padx=5, pady=5)
            
            if field == 'STATUS':
                # Combobox for status
                entry = ttk.Combobox(main_frame, values=['Available', 'Used', 'Reserved', 'Defective'], width=30)
                entry.set(current_data.get(field, 'Available') if current_data else 'Available')
            else:
                # Regular entry
                entry = ttk.Entry(main_frame, width=35)
                if current_data and field in current_data:
                    entry.insert(0, str(current_data[field]))
                elif field == 'STC' and not current_data:
                    # Auto-generate STC for new devices
                    max_stc = self.box_devices_df['STC'].max() if len(self.box_devices_df) > 0 else 60000
                    entry.insert(0, str(max_stc + 1))
            
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[field] = entry
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        def on_save():
            try:
                for field, entry in entries.items():
                    value = entry.get().strip()
                    if field in ['STC'] and value:
                        result[field] = int(value)
                    else:
                        result[field] = value
                
                # Validate required fields
                required = ['SERIAL_NUMBER', 'IMEI', 'MAC_ADDRESS']
                for field in required:
                    if not result.get(field):
                        messagebox.showerror("Error", f"{field} is required")
                        return
                
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
        
        def on_cancel():
            result.clear()
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=on_save).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=10)
        
        # Focus first field
        entries['SERIAL_NUMBER'].focus()
        
        dialog.wait_window()
        return result if result else None
    
    def on_box_tree_double_click(self, event):
        """Handle double-click on tree item for editing."""
        self.edit_box_device_row()
    
    def on_box_tree_right_click(self, event):
        """Handle right-click on tree item for context menu."""
        # Select the item under cursor
        item = self.box_tree.identify('item', event.x, event.y)
        if item:
            self.box_tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="✏️ Edit", command=self.edit_box_device_row)
            context_menu.add_command(label="📋 Duplicate", command=self.duplicate_box_device_row)
            context_menu.add_separator()
            context_menu.add_command(label="🗑️ Delete", command=self.delete_box_device_row)
            
            # Show context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def update_box_data_info(self):
        """Update the data information display."""
        if self.box_devices_df is None:
            self.box_data_info_label.config(text="Total: 0 | Filtered: 0")
            return
        
        total_count = len(self.box_devices_df)
        
        # Apply search filter to count filtered items
        search_term = self.box_filter_var.get().strip().lower()
        if search_term:
            mask = self.box_devices_df.astype(str).apply(
                lambda x: x.str.lower().str.contains(search_term, na=False)
            ).any(axis=1)
            filtered_count = len(self.box_devices_df[mask])
        else:
            filtered_count = total_count
        
        self.box_data_info_label.config(text=f"Total: {total_count} | Filtered: {filtered_count}")
            
    def update_box_device_display(self):
        """Update the box device list display for current page with filtering."""
        if self.box_devices_df is None:
            return
            
        # Clear existing items
        for item in self.box_tree.get_children():
            self.box_tree.delete(item)
        
        # Apply search filter
        search_term = self.box_filter_var.get().strip().lower()
        if search_term:
            # Search across all columns using positional data
            mask = self.box_devices_df.astype(str).apply(
                lambda x: x.str.lower().str.contains(search_term, na=False)
            ).any(axis=1)
            filtered_df = self.box_devices_df[mask].reset_index(drop=True)
        else:
            filtered_df = self.box_devices_df.copy()
            
        # Calculate page info
        total_devices = len(filtered_df)
        total_pages = (total_devices + self.box_devices_per_page - 1) // self.box_devices_per_page if total_devices > 0 else 1
        
        if total_devices == 0:
            self.box_page_label.config(text="Page: 0/0")
            return
            
        # Ensure current page is valid
        if self.box_current_page >= total_pages:
            self.box_current_page = max(0, total_pages - 1)
            
        # Get devices for current page
        start_idx = self.box_current_page * self.box_devices_per_page
        end_idx = min(start_idx + self.box_devices_per_page, total_devices)
        page_devices = filtered_df.iloc[start_idx:end_idx]
        
        # Add devices to tree
        for idx, (_, device) in enumerate(page_devices.iterrows()):
            global_idx = start_idx + idx
            is_selected = global_idx in self.box_selected_devices
            
            # Get all values for the enhanced table - CORRECTED for actual CSV structure:
            # CSV headers: [timestamp,stc,serial_number,imei,imsi,ccid,mac_address,print_status,parse_status,raw_data,zpl_filename,notes]
            # Data positions: [timestamp,stc,serial_number,imei,imsi,ccid,mac_address,print_status,parse_status,...]
            values = (
                "☑" if is_selected else "☐",
                str(device.iloc[1]) if len(device) > 1 else "N/A",  # STC (second column: index 1)
                str(device.iloc[2]) if len(device) > 2 else "",     # Serial (third column: index 2)
                str(device.iloc[3]) if len(device) > 3 else "",     # IMEI (fourth column: index 3)
                str(device.iloc[4]) if len(device) > 4 else "",     # IMSI (fifth column: index 4)
                str(device.iloc[5]) if len(device) > 5 else "",     # CCID (sixth column: index 5)
                str(device.iloc[6]) if len(device) > 6 else "",     # MAC (seventh column: index 6)
                str(device.iloc[7]) if len(device) > 7 else "Available",  # Print Status (eighth column: index 7)
                global_idx  # Hidden column for global index
            )
            
            self.box_tree.insert("", tk.END, values=values, 
                               tags=('selected' if is_selected else 'unselected',))
            
        # Configure tags
        self.box_tree.tag_configure('selected', background='lightblue')
        self.box_tree.tag_configure('unselected', background='white')
        
        # Update labels
        self.box_page_label.config(text=f"Page: {self.box_current_page + 1}/{total_pages}")
        self.box_selection_label.config(text=f"Selected: {len(self.box_selected_devices)}/20")
        self.update_box_data_info()
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
            
        try:
            # Get the global index from the hidden column
            values = self.box_tree.item(item, 'values')
            
            # Debug: Print values to understand structure
            print(f"Debug: Tree item values: {values}, length: {len(values)}")
            
            # The global_idx should be in the last column (index 8)
            # But let's be more flexible in case some rows have fewer values
            if len(values) == 0:
                print("Debug: No values in tree item")
                return
                
            # Try to get global_idx from the last position
            try:
                global_idx = int(values[-1])  # Get from last position instead of fixed index 8
                print(f"Debug: Got global_idx: {global_idx}")
            except (ValueError, IndexError) as e:
                print(f"Debug: Error getting global_idx: {e}")
                return
            
            # Toggle selection
            if global_idx in self.box_selected_devices:
                self.box_selected_devices.remove(global_idx)
                print(f"Debug: Removed {global_idx} from selection")
            else:
                if len(self.box_selected_devices) < 20:
                    self.box_selected_devices.append(global_idx)
                    print(f"Debug: Added {global_idx} to selection")
                else:
                    messagebox.showwarning("Selection Limit", "Maximum 20 devices can be selected for one box")
                    return
                    
            self.update_box_device_display()
            
        except Exception as e:
            print(f"Debug: Exception in on_box_tree_click: {e}")
            import traceback
            traceback.print_exc()
        
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
                
    def select_all_box_devices(self):
        """Select all devices on current page (up to 20 total)."""
        if self.box_devices_df is None:
            return
            
        # Calculate current page devices
        start_idx = self.box_current_page * self.box_devices_per_page
        end_idx = min(start_idx + self.box_devices_per_page, len(self.box_devices_df))
        
        # Add current page devices to selection (up to 20 total)
        for idx in range(start_idx, end_idx):
            if len(self.box_selected_devices) >= 20:
                messagebox.showinfo("Selection Limit", "Maximum 20 devices selected")
                break
            if idx not in self.box_selected_devices:
                self.box_selected_devices.append(idx)
        
        self.update_box_device_display()
        
    def clear_all_box_devices(self):
        """Clear all selected devices."""
        self.box_selected_devices = []
        self.update_box_device_display()
                
    def create_box_qr_with_devices(self, devices):
        """Create QR code with all device data for box label."""
        qr_data = []
        for device in devices:
            # Ensure all values are strings to avoid numpy type issues
            stc = str(device.get('STC', 'N/A'))
            serial = str(device.get('SERIAL_NUMBER', 'N/A'))
            imei = str(device.get('IMEI', 'N/A'))
            imsi = str(device.get('IMSI', 'N/A'))
            ccid = str(device.get('CCID', 'N/A'))
            mac = str(device.get('MAC_ADDRESS', 'N/A'))
            
            # Include ALL device information in QR code
            device_info = f"{stc}:{serial}:{imei}:{imsi}:{ccid}:{mac}"
            qr_data.append(device_info)
        
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
        
        # Ensure box labels folder exists
        box_labels_folder = os.path.join("save", "box_labels")
        os.makedirs(box_labels_folder, exist_ok=True)
        
        # Create filename with box number and date
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{box_number.lower()}_{timestamp}.pdf"
        filepath = os.path.join(box_labels_folder, filename)
        
        c = canvas.Canvas(filepath, pagesize=(width, height))
        
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
        c.drawString(3*mm, y, "STC")  # Changed from "No." to "STC"
        c.drawString(12*mm, y, "Serial Number")  # Shifted right to make room for STC
        c.drawString(42*mm, y, "IMEI")
        c.drawString(70*mm, y, "MAC")
        y -= 4*mm
        
        # Device entries
        c.setFont("Courier", 5.5)
        line_height = 3*mm
        
        for device in devices:  # Removed enumerate since we're using STC
            if y > 5*mm:
                stc = str(device.get('STC', 'N/A'))  # Get actual STC number
                c.drawString(3*mm, y, stc)  # Print STC instead of sequential number
                c.drawString(12*mm, y, str(device['SERIAL_NUMBER']))  # Shifted right
                c.drawString(42*mm, y, str(device['IMEI']))
                c.drawString(70*mm, y, str(device['MAC_ADDRESS']))
                y -= line_height
            else:
                c.setFont("Helvetica", 5)
                c.drawCentredString(width/2, y, "... (complete data in QR code)")
                break
                
        c.save()
        return filepath
        
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
                # CSV structure: timestamp,stc,serial_number,imei,imsi,ccid,mac_address,print_status,parse_status,raw_data,zpl_filename,notes
                device_dict = {
                    'STC': str(device_row.iloc[1]) if len(device_row) > 1 else 'N/A',  # STC (2nd column)
                    'SERIAL_NUMBER': str(device_row.iloc[2]) if len(device_row) > 2 else 'N/A',  # Serial (3rd column)
                    'IMEI': str(device_row.iloc[3]) if len(device_row) > 3 else 'N/A',  # IMEI (4th column)
                    'IMSI': str(device_row.iloc[4]) if len(device_row) > 4 else 'N/A',  # IMSI (5th column)
                    'CCID': str(device_row.iloc[5]) if len(device_row) > 5 else 'N/A',  # CCID (6th column)
                    'MAC_ADDRESS': str(device_row.iloc[6]) if len(device_row) > 6 else 'N/A'  # MAC (7th column)
                }
                selected_device_data.append(device_dict)
                
            # Generate PDF
            filepath = self.generate_box_label_pdf(selected_device_data, box_number)
            
            # Log success
            self.log_message(f"✅ Box label created: {os.path.basename(filepath)} ({len(selected_device_data)} devices)", "INFO")
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"Box label created successfully!\n\n"
                              f"File: {os.path.basename(filepath)}\n"
                              f"Location: save/box_labels/\n"
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
    
    # CSV Management Methods
    def get_csv_path(self):
        """Get the path to the CSV file."""
        return self.csv_file_path
    
    def open_csv_folder(self):
        """Open the CSV folder in file explorer."""
        csv_folder = self.save_folders['csv']
        if os.path.exists(csv_folder):
            os.startfile(csv_folder)
        else:
            messagebox.showerror("Error", f"CSV folder not found: {csv_folder}")
    
    def open_csv_file_external(self):
        """Open the CSV file in external application."""
        csv_path = self.get_csv_path()
        if os.path.exists(csv_path):
            os.startfile(csv_path)
        else:
            messagebox.showerror("Error", f"CSV file not found: {csv_path}")
    
    def refresh_csv_view(self):
        """Refresh the CSV data view."""
        csv_path = self.get_csv_path()
        
        try:
            # Read CSV data
            if os.path.exists(csv_path):
                import pandas as pd
                self.csv_data = pd.read_csv(csv_path)
                
                # Update statistics
                total_records = len(self.csv_data)
                # Check parse_status column (index 8) for errors
                valid_records = total_records  # Default to all valid
                if len(self.csv_data.columns) >= 9:
                    try:
                        parse_status_col = self.csv_data.iloc[:, 8]  # parse_status column (index 8)
                        valid_records = len(parse_status_col[parse_status_col != 'PARSE_ERROR'])
                    except:
                        valid_records = total_records
                
                error_records = total_records - valid_records
                # STC is in the second column (index 1)
                latest_stc = 60000  # Default value
                if len(self.csv_data) > 0 and len(self.csv_data.columns) > 1:
                    try:
                        stc_col = self.csv_data.iloc[:, 1]  # Second column has STC values
                        latest_stc = stc_col.max() if len(stc_col) > 0 else 60000
                    except:
                        latest_stc = 60000
                
                # File statistics
                file_size = os.path.getsize(csv_path) / 1024  # KB
                modified_time = datetime.fromtimestamp(os.path.getmtime(csv_path)).strftime('%Y-%m-%d %H:%M:%S')
                
                # Update labels
                self.csv_total_label.config(text=str(total_records))
                self.csv_valid_label.config(text=str(valid_records))
                self.csv_errors_label.config(text=str(error_records))
                self.csv_latest_stc_label.config(text=str(latest_stc))
                self.csv_size_label.config(text=f"{file_size:.1f} KB")
                self.csv_modified_label.config(text=modified_time)
                
                # Filter data based on selection
                display_data = self.csv_data.copy()
                show_option = self.csv_show_var.get()
                
                if show_option == "Latest 50":
                    display_data = display_data.tail(50)
                elif show_option == "Latest 100":
                    display_data = display_data.tail(100)
                elif show_option == "Errors Only":
                    if 'parse_status' in display_data.columns:
                        display_data = display_data[display_data['parse_status'] == 'PARSE_ERROR']
                elif show_option == "Valid Only":
                    if 'parse_status' in display_data.columns:
                        display_data = display_data[display_data['parse_status'] != 'PARSE_ERROR']
                
                # Apply search filter
                search_term = self.csv_search_var.get().strip().lower()
                if search_term:
                    mask = display_data.astype(str).apply(lambda x: x.str.lower().str.contains(search_term, na=False)).any(axis=1)
                    display_data = display_data[mask]
                
                # Clear and populate tree
                for item in self.csv_tree.get_children():
                    self.csv_tree.delete(item)
                
                for _, row in display_data.iterrows():
                    values = []
                    # CSV structure: timestamp,stc,serial_number,imei,imsi,ccid,mac_address,print_status,parse_status,raw_data,zpl_filename,notes
                    # Display order: Time, STC, Serial, IMEI, IMSI, CCID, MAC, Status
                    
                    # Map the correct data positions to display columns
                    if len(row) >= 8:
                        values.append(str(row.iloc[0]))  # timestamp
                        values.append(str(row.iloc[1]))  # stc
                        values.append(str(row.iloc[2]))  # serial_number
                        values.append(str(row.iloc[3]))  # imei
                        values.append(str(row.iloc[4]))  # imsi
                        values.append(str(row.iloc[5]))  # ccid
                        values.append(str(row.iloc[6]))  # mac_address
                        values.append(str(row.iloc[7]))  # print_status
                    else:
                        values = ["N/A"] * 8
                    
                    # Color code rows - check parse_status (column 8, index 7)
                    tag = "normal"
                    if len(row) >= 9 and str(row.iloc[8]) == "PARSE_ERROR":  # parse_status column
                        tag = "error"
                    
                    self.csv_tree.insert("", "end", values=values, tags=(tag,))
                
                # Configure row colors
                self.csv_tree.tag_configure("error", background="#ffcccc")
                self.csv_tree.tag_configure("normal", background="#ffffff")
                
            else:
                # No CSV file exists
                self.csv_total_label.config(text="0")
                self.csv_valid_label.config(text="0")
                self.csv_errors_label.config(text="0")
                self.csv_latest_stc_label.config(text="0")
                self.csv_size_label.config(text="0 KB")
                self.csv_modified_label.config(text="Never")
                
                # Clear tree
                for item in self.csv_tree.get_children():
                    self.csv_tree.delete(item)
                
        except Exception as e:
            self.log_message(f"Error refreshing CSV view: {e}", "ERROR")
    
    def clear_all_csv_data(self):
        """Clear all CSV data with double confirmation."""
        # First confirmation
        result1 = messagebox.askyesno(
            "⚠️ Warning - Clear All CSV Data", 
            "This will DELETE ALL device data from the CSV file!\n\n"
            "This action cannot be undone.\n\n"
            "Are you sure you want to continue?",
            icon='warning'
        )
        
        if not result1:
            return
        
        # Second confirmation
        result2 = messagebox.askyesno(
            "🚨 FINAL WARNING", 
            "THIS WILL PERMANENTLY DELETE:\n"
            "• All device records\n"
            "• All STC assignments\n"
            "• All printing history\n\n"
            "A backup will be created before clearing.\n\n"
            "Are you ABSOLUTELY SURE?",
            icon='warning'
        )
        
        if not result2:
            return
        
        csv_path = self.get_csv_path()
        
        if not os.path.exists(csv_path):
            messagebox.showinfo("Info", "CSV file does not exist - nothing to clear")
            return
        
        try:
            # Create backup before clearing
            backup_filename = f'device_log_backup_before_clear_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            backup_path = os.path.join(self.save_folders['backups'], backup_filename)
            import shutil
            shutil.copy2(csv_path, backup_path)
            
            # Clear CSV file - keep only headers
            csv_headers = [
                'timestamp', 'stc', 'serial_number', 'imei', 'imsi', 'ccid', 'mac_address',
                'print_status', 'parse_status', 'raw_data', 'zpl_filename', 'notes'
            ]
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_headers)
            
            # Reset STC counter in auto_printer if available
            if hasattr(self, 'auto_printer') and self.auto_printer:
                self.auto_printer.current_stc = 60000  # Reset to starting STC
                self.log_message("STC counter reset to 60000", "INFO")
            
            # Refresh displays
            self.refresh_csv_view()
            self.refresh_csv_data()
            if hasattr(self, 'refresh_stc_from_csv'):
                self.refresh_stc_from_csv()
            
            self.log_message(f"✅ CSV data cleared successfully. Backup saved: {backup_path}", "INFO")
            
            messagebox.showinfo(
                "Success", 
                f"CSV data cleared successfully!\n\n"
                f"Backup saved as:\n{backup_path}\n\n"
                f"STC counter reset to 60000"
            )
            
        except Exception as e:
            error_msg = f"Failed to clear CSV data: {str(e)}"
            self.log_message(error_msg, "ERROR")
            messagebox.showerror("Error", error_msg)

    def clean_csv_data(self):
        """Clean CSV data by removing parse errors and duplicates."""
        csv_path = self.get_csv_path()
        
        if not os.path.exists(csv_path):
            messagebox.showerror("Error", "CSV file not found")
            return
        
        try:
            import pandas as pd
            
            # Read current data
            df = pd.read_csv(csv_path)
            original_count = len(df)
            
            # Remove parse errors
            if 'STATUS' in df.columns:
                df_clean = df[df['STATUS'] != 'PARSE_ERROR'].copy()
            else:
                df_clean = df.copy()
            
            # Remove duplicates based on serial number
            if 'SERIAL_NUMBER' in df_clean.columns:
                df_clean = df_clean.drop_duplicates(subset=['SERIAL_NUMBER'], keep='last')
            
            cleaned_count = len(df_clean)
            removed_count = original_count - cleaned_count
            
            # Create backup
            backup_filename = f'device_log_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            backup_path = os.path.join(self.save_folders['backups'], backup_filename)
            df.to_csv(backup_path, index=False)
            
            # Save cleaned data
            df_clean.to_csv(csv_path, index=False)
            
            # Refresh view
            self.refresh_csv_view()
            
            messagebox.showinfo("CSV Cleaned", 
                              f"CSV cleaning completed!\n\n"
                              f"Original records: {original_count}\n"
                              f"Cleaned records: {cleaned_count}\n"
                              f"Removed records: {removed_count}\n\n"
                              f"Backup saved as: {os.path.basename(backup_path)}")
            
            self.log_message(f"CSV cleaned: {removed_count} records removed, backup saved", "INFO")
            
        except Exception as e:
            self.log_message(f"Error cleaning CSV: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to clean CSV: {e}")
    
    def export_filtered_csv(self):
        """Export the currently filtered view to a new CSV file."""
        if not hasattr(self, 'csv_data') or self.csv_data is None:
            messagebox.showerror("Error", "No CSV data loaded")
            return
        
        try:
            from tkinter import filedialog
            
            # Get filtered data based on current view
            display_data = self.csv_data.copy()
            show_option = self.csv_show_var.get()
            
            if show_option == "Latest 50":
                display_data = display_data.tail(50)
            elif show_option == "Latest 100":
                display_data = display_data.tail(100)
            elif show_option == "Errors Only":
                if 'STATUS' in display_data.columns:
                    display_data = display_data[display_data['STATUS'] == 'PARSE_ERROR']
            elif show_option == "Valid Only":
                if 'STATUS' in display_data.columns:
                    display_data = display_data[display_data['STATUS'] != 'PARSE_ERROR']
            
            # Apply search filter
            search_term = self.csv_search_var.get().strip().lower()
            if search_term:
                mask = display_data.astype(str).apply(lambda x: x.str.lower().str.contains(search_term, na=False)).any(axis=1)
                display_data = display_data[mask]
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialdir=os.path.join("save", "csv"),
                initialname=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if filename:
                display_data.to_csv(filename, index=False)
                messagebox.showinfo("Export Complete", f"Filtered data exported to:\n{filename}\n\nRecords: {len(display_data)}")
                self.log_message(f"Exported {len(display_data)} filtered records to {filename}", "INFO")
        
        except Exception as e:
            self.log_message(f"Error exporting CSV: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to export CSV: {e}")

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