#!/usr/bin/env python3
"""
Real Box Label Generator
========================

Creates box labels using real device data from CSV file,
showing actual STC numbers from the printed devices.
"""

import os
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict
import qrcode
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealBoxLabelGenerator:
    """Generate box labels using real CSV data."""
    
    def __init__(self):
        """Initialize the generator."""
        self.csv_path = os.path.join('save', 'csv', 'device_log.csv')
        self.label_width = 15 * cm  # 15cm width
        self.label_height = 10 * cm  # 10cm height
        self.margin = 3 * mm
        
    def load_devices_from_csv(self, limit=20) -> List[Dict[str, str]]:
        """
        Load real device data from CSV file.
        
        Args:
            limit: Maximum number of devices to load (default: 20)
            
        Returns:
            List of device dictionaries with real STC numbers
        """
        if not os.path.exists(self.csv_path):
            logger.error(f"CSV file not found: {self.csv_path}")
            return []
        
        try:
            # Read CSV with pandas
            df = pd.read_csv(self.csv_path)
            
            # Filter only printed devices
            printed_devices = df[df['STATUS'] == 'Printed'].head(limit)
            
            devices = []
            for _, row in printed_devices.iterrows():
                device = {
                    'STC': str(row['STC']),
                    'SERIAL_NUMBER': str(row['SERIAL_NUMBER']),
                    'IMEI': str(row['IMEI']),
                    'MAC_ADDRESS': str(row['MAC_ADDRESS']),
                    'TIMESTAMP': str(row['TIMESTAMP'])
                }
                devices.append(device)
            
            logger.info(f"Loaded {len(devices)} real devices from CSV")
            return devices
            
        except Exception as e:
            logger.error(f"Error loading devices from CSV: {e}")
            return []
    
    def create_qr_data(self, devices: List[Dict[str, str]]) -> str:
        """Create QR code data with real device information."""
        qr_lines = []
        
        for device in devices:
            # Format: STC:SERIAL:IMEI:MAC
            line = f"{device['STC']}:{device['SERIAL_NUMBER']}:{device['IMEI']}:{device['MAC_ADDRESS']}"
            qr_lines.append(line)
            
        return "|".join(qr_lines)
    
    def generate_qr_code(self, data: str) -> str:
        """Generate QR code image."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        temp_path = f"temp_real_qr_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        qr_image.save(temp_path)
        
        return temp_path
    
    def draw_device_table(self, c: canvas.Canvas, devices: List[Dict[str, str]], 
                         start_x: float, start_y: float, table_width: float) -> None:
        """Draw device information table showing real STC numbers."""
        
        # Split devices into two columns
        left_devices = devices[:10]
        right_devices = devices[10:] if len(devices) > 10 else []
        
        col_width = table_width / 2 - 2*mm
        row_height = 6 * mm
        header_height = 8 * mm
        
        # Column widths
        stc_width = 15 * mm
        serial_width = 30 * mm
        imei_width = 30 * mm
        mac_width = col_width - stc_width - serial_width - imei_width
        
        col_widths = [stc_width, serial_width, imei_width, mac_width]
        
        # Draw left column
        self._draw_column(c, left_devices, start_x, start_y, col_widths, 
                         row_height, header_height, "Real Devices (1-10)")
        
        # Draw right column if we have more devices
        if right_devices:
            right_start_x = start_x + col_width + 4*mm
            self._draw_column(c, right_devices, right_start_x, start_y, col_widths, 
                             row_height, header_height, "Real Devices (11-20)")
    
    def _draw_column(self, c: canvas.Canvas, devices: List[Dict[str, str]], 
                    start_x: float, start_y: float, col_widths: List[float],
                    row_height: float, header_height: float, title: str):
        """Draw a single column of real device data."""
        
        # Column title
        c.setFont("Helvetica-Bold", 7)
        c.drawString(start_x, start_y + 2*mm, title)
        
        # Table headers
        c.setFont("Helvetica-Bold", 6)
        headers = ["STC", "Serial Number", "IMEI", "MAC"]
        
        current_y = start_y - header_height
        current_x = start_x
        
        for header, width in zip(headers, col_widths):
            # Draw header cell
            c.setFillColor((0.8, 0.8, 0.8))
            c.rect(current_x, current_y, width, header_height, fill=1, stroke=1)
            
            c.setFillColor((0, 0, 0))
            text_x = current_x + width/2
            text_y = current_y + header_height/2 - 1
            c.drawCentredString(text_x, text_y, header)
            
            current_x += width
        
        # Draw device rows with real data
        c.setFont("Helvetica", 6)
        current_y -= header_height
        
        for i, device in enumerate(devices):
            current_x = start_x
            
            # Alternate row colors
            if i % 2 == 1:
                c.setFillColor((0.95, 0.95, 0.95))
                c.rect(start_x, current_y, sum(col_widths), row_height, fill=1, stroke=0)
            
            # Real device data
            row_data = [
                device['STC'],  # Real STC number!
                device['SERIAL_NUMBER'][-12:] if len(device['SERIAL_NUMBER']) > 12 else device['SERIAL_NUMBER'],
                device['IMEI'][-12:] if len(device['IMEI']) > 12 else device['IMEI'],
                device['MAC_ADDRESS']
            ]
            
            c.setFillColor((0, 0, 0))
            for j, (data, width) in enumerate(zip(row_data, col_widths)):
                c.rect(current_x, current_y, width, row_height, fill=0, stroke=1)
                
                if j == 0:  # Center STC number
                    text_x = current_x + width/2
                    c.drawCentredString(text_x, current_y + row_height/2 - 1, data)
                else:
                    text_x = current_x + 1 * mm
                    c.drawString(text_x, current_y + row_height/2 - 1, data)
                
                current_x += width
            
            current_y -= row_height
    
    def generate_real_box_label(self, box_number: str = None, device_count: int = 20) -> str:
        """Generate box label with real device data."""
        
        # Load real devices from CSV
        devices = self.load_devices_from_csv(limit=device_count)
        
        if not devices:
            logger.error("No devices found in CSV")
            return None
        
        if len(devices) < device_count:
            logger.warning(f"Only {len(devices)} devices available, requested {device_count}")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        first_stc = devices[0]['STC']
        last_stc = devices[-1]['STC']
        
        if box_number is None:
            box_number = f"STC{first_stc}-{last_stc}"
        
        output_path = f"real_box_label_{box_number}_{first_stc}_{last_stc}_{timestamp}.pdf"
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=(self.label_width, self.label_height))
        
        # Title
        c.setFont("Helvetica-Bold", 12)
        title_text = f"REAL Device Box Label - {box_number}"
        c.drawCentredString(self.label_width/2, self.label_height - 1.5*cm, title_text)
        
        # Date and device count
        c.setFont("Helvetica", 8)
        date_text = f"Date: {datetime.now().strftime('%d/%m/%Y')}"
        count_text = f"Devices: {len(devices)} units (REAL DATA)"
        c.drawString(self.margin, self.label_height - 2.5*cm, date_text)
        c.drawRightString(self.label_width - self.margin, self.label_height - 2.5*cm, count_text)
        
        # QR code with real data
        qr_size = 2.5 * cm
        qr_x = self.label_width - self.margin - qr_size
        qr_y = self.label_height - 1.2*cm - qr_size
        
        qr_data = self.create_qr_data(devices)
        qr_image_path = self.generate_qr_code(qr_data)
        
        c.drawImage(qr_image_path, qr_x, qr_y, width=qr_size, height=qr_size)
        
        # Clean up QR file
        try:
            os.remove(qr_image_path)
        except:
            pass
        
        # QR code label
        c.setFont("Helvetica", 6)
        c.drawCentredString(qr_x + qr_size/2, qr_y - 0.3*cm, "QR: Real Device Data")
        
        # Device table with real data
        table_width = self.label_width - 2*self.margin - 0.5*cm
        table_start_x = self.margin
        table_start_y = self.label_height - 3*cm
        
        self.draw_device_table(c, devices, table_start_x, table_start_y, table_width)
        
        # Footer with real STC range
        c.setFont("Helvetica-Bold", 8)
        footer_text = f"Real STC Range: {first_stc} → {last_stc} (Total: {len(devices)} devices)"
        c.drawCentredString(self.label_width/2, self.margin + 2*mm, footer_text)
        
        c.save()
        
        logger.info(f"Real box label generated: {output_path}")
        return output_path

def main():
    """Test the real box label generator."""
    try:
        generator = RealBoxLabelGenerator()
        
        # Generate real box label
        output_file = generator.generate_real_box_label()
        
        if output_file:
            print(f"✅ Real box label created: {output_file}")
            print("📦 Contains REAL device data from CSV")
            print("📱 Shows actual STC numbers from printed devices")
            print("🔍 QR code contains real device information")
        else:
            print("❌ Failed to create real box label")
        
    except Exception as e:
        logger.error(f"Error creating real box label: {e}")
        raise

if __name__ == "__main__":
    main()