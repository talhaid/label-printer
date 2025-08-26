#!/usr/bin/env python3
"""
Koli Box Label Creator - GUI for creating box labels from CSV data
Displays devices in pages of 20, allows selection and PDF generation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional
import qrcode
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

class KoliBoxLabelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Koli Box Label Creator")
        self.root.geometry("1200x800")
        
        # Data storage
        self.devices_df = None
        self.current_page = 0
        self.devices_per_page = 20
        self.selected_devices = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the main UI"""
        
        # Top frame for controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # CSV file selection
        ttk.Label(control_frame, text="CSV File:").pack(side=tk.LEFT)
        self.csv_path_var = tk.StringVar()
        self.csv_entry = ttk.Entry(control_frame, textvariable=self.csv_path_var, width=50)
        self.csv_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Button(control_frame, text="Browse CSV", command=self.browse_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Load Data", command=self.load_csv_data).pack(side=tk.LEFT, padx=(0, 20))
        
        # Page navigation
        self.page_label = ttk.Label(control_frame, text="Page: 0/0")
        self.page_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="◀ Previous", command=self.previous_page).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Next ▶", command=self.next_page).pack(side=tk.LEFT, padx=(0, 20))
        
        # Box number input
        ttk.Label(control_frame, text="Box Number:").pack(side=tk.LEFT, padx=(0, 5))
        self.box_number_var = tk.StringVar(value="BOX001")
        ttk.Entry(control_frame, textvariable=self.box_number_var, width=10).pack(side=tk.LEFT, padx=(0, 10))
        
        # Create label button
        ttk.Button(control_frame, text="Create Box Label", command=self.create_box_label, 
                  style="Accent.TButton").pack(side=tk.RIGHT)
        
        # Selection info
        self.selection_label = ttk.Label(control_frame, text="Selected: 0/20 devices")
        self.selection_label.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Main content frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Device list with checkboxes
        self.create_device_list(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Load CSV file to begin")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_device_list(self, parent):
        """Create the device list with checkboxes"""
        
        # Create treeview with checkboxes
        columns = ("select", "no", "serial", "imei", "mac", "status")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=22)
        
        # Configure columns
        self.tree.heading("select", text="☑")
        self.tree.heading("no", text="No.")
        self.tree.heading("serial", text="Serial Number")
        self.tree.heading("imei", text="IMEI")
        self.tree.heading("mac", text="MAC Address")
        self.tree.heading("status", text="Status")
        
        # Column widths
        self.tree.column("select", width=50, anchor=tk.CENTER)
        self.tree.column("no", width=50, anchor=tk.CENTER)
        self.tree.column("serial", width=200)
        self.tree.column("imei", width=200)
        self.tree.column("mac", width=150)
        self.tree.column("status", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind click events
        self.tree.bind("<Button-1>", self.on_tree_click)
        
    def browse_csv(self):
        """Browse for CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select Device CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.csv_path_var.set(file_path)
            
    def load_csv_data(self):
        """Load data from CSV file"""
        csv_path = self.csv_path_var.get()
        if not csv_path or not os.path.exists(csv_path):
            messagebox.showerror("Error", "Please select a valid CSV file")
            return
            
        try:
            # Try to load CSV with different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
            for encoding in encodings:
                try:
                    self.devices_df = pd.read_csv(csv_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise Exception("Could not decode CSV file with any encoding")
                
            # Validate required columns
            required_columns = ['SERIAL_NUMBER', 'IMEI', 'MAC_ADDRESS']
            missing_columns = [col for col in required_columns if col not in self.devices_df.columns]
            
            if missing_columns:
                messagebox.showerror("Error", f"CSV missing required columns: {', '.join(missing_columns)}")
                return
                
            # Add status column if not exists
            if 'STATUS' not in self.devices_df.columns:
                self.devices_df['STATUS'] = 'Available'
                
            self.current_page = 0
            self.selected_devices = []
            self.update_device_display()
            self.status_var.set(f"Loaded {len(self.devices_df)} devices from CSV")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
            
    def update_device_display(self):
        """Update the device list display for current page"""
        if self.devices_df is None:
            return
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Calculate page info
        total_devices = len(self.devices_df)
        total_pages = (total_devices + self.devices_per_page - 1) // self.devices_per_page
        
        if total_pages == 0:
            self.page_label.config(text="Page: 0/0")
            return
            
        # Get devices for current page
        start_idx = self.current_page * self.devices_per_page
        end_idx = min(start_idx + self.devices_per_page, total_devices)
        page_devices = self.devices_df.iloc[start_idx:end_idx]
        
        # Add devices to tree
        for idx, (_, device) in enumerate(page_devices.iterrows()):
            global_idx = start_idx + idx
            is_selected = global_idx in self.selected_devices
            
            self.tree.insert("", tk.END, values=(
                "☑" if is_selected else "☐",
                f"{global_idx + 1:02d}",
                device['SERIAL_NUMBER'],
                device['IMEI'],
                device['MAC_ADDRESS'],
                device.get('STATUS', 'Available')
            ), tags=('selected' if is_selected else 'unselected',))
            
        # Configure tags
        self.tree.tag_configure('selected', background='lightblue')
        self.tree.tag_configure('unselected', background='white')
        
        # Update page label
        self.page_label.config(text=f"Page: {self.current_page + 1}/{total_pages}")
        self.selection_label.config(text=f"Selected: {len(self.selected_devices)}/20 devices")
        
    def on_tree_click(self, event):
        """Handle tree item clicks for selection"""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
            
        # Get the global index
        values = self.tree.item(item, 'values')
        device_no = int(values[1]) - 1  # Convert to 0-based index
        
        # Toggle selection
        if device_no in self.selected_devices:
            self.selected_devices.remove(device_no)
        else:
            if len(self.selected_devices) < 20:
                self.selected_devices.append(device_no)
            else:
                messagebox.showwarning("Selection Limit", "Maximum 20 devices can be selected for one box")
                return
                
        self.update_device_display()
        
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_device_display()
            
    def next_page(self):
        """Go to next page"""
        if self.devices_df is not None:
            total_pages = (len(self.devices_df) + self.devices_per_page - 1) // self.devices_per_page
            if self.current_page < total_pages - 1:
                self.current_page += 1
                self.update_device_display()
                
    def create_qr_with_devices(self, devices: List[Dict[str, str]]) -> str:
        """Create QR code with all device data"""
        qr_data = []
        for i, device in enumerate(devices, 1):
            qr_data.append(f"{i:02d}:{device['SERIAL_NUMBER']}:{device['IMEI']}:{device['MAC_ADDRESS']}")
        
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
        temp_path = f"temp_koli_qr_{datetime.now().strftime('%H%M%S_%f')}.png"
        qr_image.save(temp_path)
        return temp_path
        
    def generate_box_label_pdf(self, devices: List[Dict[str, str]], box_number: str) -> str:
        """Generate box label PDF using our perfected template"""
        
        width = 10 * cm
        height = 15 * cm
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        first_serial = devices[0]['SERIAL_NUMBER']
        last_serial = devices[-1]['SERIAL_NUMBER']
        filename = f"koli_box_{box_number}_{first_serial}_{last_serial}_{timestamp}.pdf"
        
        c = canvas.Canvas(filename, pagesize=(width, height))
        
        # QR code first - at top, 1cm from edge
        y = height - 10*mm
        qr_path = self.create_qr_with_devices(devices)
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
                c.drawString(10*mm, y, device['SERIAL_NUMBER'])
                c.drawString(42*mm, y, device['IMEI'])
                c.drawString(70*mm, y, device['MAC_ADDRESS'])
                y -= line_height
            else:
                c.setFont("Helvetica", 5)
                c.drawCentredString(width/2, y, "... (complete data in QR code)")
                break
                
        c.save()
        return filename
        
    def create_box_label(self):
        """Create box label for selected devices"""
        if len(self.selected_devices) == 0:
            messagebox.showwarning("No Selection", "Please select devices for the box label")
            return
            
        if len(self.selected_devices) != 20:
            result = messagebox.askyesno("Partial Selection", 
                                       f"Only {len(self.selected_devices)} devices selected. "
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
            for idx in sorted(self.selected_devices):
                device_row = self.devices_df.iloc[idx]
                device_dict = {
                    'SERIAL_NUMBER': device_row['SERIAL_NUMBER'],
                    'IMEI': device_row['IMEI'],
                    'MAC_ADDRESS': device_row['MAC_ADDRESS']
                }
                selected_device_data.append(device_dict)
                
            # Generate PDF
            filename = self.generate_box_label_pdf(selected_device_data, box_number)
            
            # Update status
            self.status_var.set(f"✅ Box label created: {filename}")
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"Box label created successfully!\n\n"
                              f"File: {filename}\n"
                              f"Devices: {len(selected_device_data)}\n"
                              f"Box: {box_number}")
                              
            # Clear selection
            self.selected_devices = []
            self.update_device_display()
            
            # Auto-increment box number
            if box_number.startswith("BOX") and box_number[3:].isdigit():
                new_number = int(box_number[3:]) + 1
                self.box_number_var.set(f"BOX{new_number:03d}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create box label: {str(e)}")

def main():
    root = tk.Tk()
    app = KoliBoxLabelGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()