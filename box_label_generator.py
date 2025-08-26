#!/usr/bin/env python3
"""
Box Label Generator for 20-device packaging
Creates 15cm x 10cm PDF labels with device information and QR code
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Tuple
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoxLabelGenerator:
    """Generate box labels for 20-device packaging"""
    
    def __init__(self):
        """Initialize the box label generator"""
        self.label_width = 15 * cm  # 15cm width
        self.label_height = 10 * cm  # 10cm height
        self.margin = 3 * mm  # 3mm margin (reduced)
        
        # Content area
        self.content_width = self.label_width - (2 * self.margin)
        self.content_height = self.label_height - (2 * self.margin)
        
        # QR code settings
        self.qr_size = 2.5 * cm  # 2.5cm QR code (smaller)
        
        # Font sizes
        self.title_font_size = 12  # Reduced
        self.header_font_size = 8   # Reduced
        self.data_font_size = 6     # Reduced
        
    def generate_sample_devices(self, base_serial: str = "ATS542912923728") -> List[Dict[str, str]]:
        """
        Generate 20 sample devices based on the working device data
        
        Args:
            base_serial: Base serial number to modify
            
        Returns:
            List of device dictionaries
        """
        devices = []
        
        # Base device info (from our working example)
        base_device = {
            "SERIAL_NUMBER": base_serial,
            "IMEI": "866988074133496",
            "MAC_ADDRESS": "AA:BB:CC:DD:EE:FF"
        }
        
        for i in range(20):
            # Create variations for each device
            device = {
                "SERIAL_NUMBER": f"{base_serial[:-2]}{i+1:02d}",  # Change last 2 digits
                "IMEI": f"{base_device['IMEI'][:-3]}{i+100:03d}",  # Change last 3 digits
                "MAC_ADDRESS": f"AA:BB:CC:DD:EE:{i+10:02X}"  # Change last MAC octet
            }
            devices.append(device)
            
        return devices
    
    def create_qr_data(self, devices: List[Dict[str, str]]) -> str:
        """
        Create compact QR code data containing all device information
        
        Args:
            devices: List of device dictionaries
            
        Returns:
            String containing all device data for QR code
        """
        # Use compact format for QR code
        qr_lines = []
        
        for i, device in enumerate(devices, 1):
            # Compact format: NUM:SERIAL:IMEI:MAC
            line = f"{i:02d}:{device['SERIAL_NUMBER']}:{device['IMEI']}:{device['MAC_ADDRESS']}"
            qr_lines.append(line)
            
        return "|".join(qr_lines)  # Use | as separator between devices
    
    def generate_qr_code(self, data: str) -> str:
        """
        Generate QR code image and save as temporary file
        
        Args:
            data: Data to encode in QR code
            
        Returns:
            Path to temporary PNG file
        """
        qr = qrcode.QRCode(
            version=None,  # Auto-size
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
            box_size=8,  # Smaller box size for compactness
            border=2,    # Smaller border
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save to temporary file
        temp_path = f"temp_qr_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        qr_image.save(temp_path)
        
        return temp_path
    
    def draw_device_table(self, c: canvas.Canvas, devices: List[Dict[str, str]], 
                         start_x: float, start_y: float, table_width: float, table_height: float) -> None:
        """
        Draw device information table in two columns
        
        Args:
            c: ReportLab canvas
            devices: List of device dictionaries
            start_x: Starting X position
            start_y: Starting Y position
            table_width: Width of the table
            table_height: Height available for table
        """
        # Split devices into two columns of 10 each
        left_devices = devices[:10]
        right_devices = devices[10:]
        
        # Column settings
        col_width = table_width / 2 - 2*mm  # Two columns with small gap
        row_height = 6 * mm  # Smaller rows
        header_height = 8 * mm
        
        # Column widths within each column
        num_width = 8 * mm
        serial_width = 35 * mm
        imei_width = 35 * mm
        mac_width = col_width - num_width - serial_width - imei_width
        
        col_widths = [num_width, serial_width, imei_width, mac_width]
        
        # Draw left column
        self._draw_column(c, left_devices, start_x, start_y, col_widths, 
                         row_height, header_height, "Column 1 (Devices 1-10)")
        
        # Draw right column
        right_start_x = start_x + col_width + 4*mm  # Small gap between columns
        self._draw_column(c, right_devices, right_start_x, start_y, col_widths, 
                         row_height, header_height, "Column 2 (Devices 11-20)", start_num=11)
    
    def _draw_column(self, c: canvas.Canvas, devices: List[Dict[str, str]], 
                    start_x: float, start_y: float, col_widths: List[float],
                    row_height: float, header_height: float, title: str, start_num: int = 1):
        """Draw a single column of device data"""
        
        # Column title
        c.setFont("Helvetica-Bold", 7)
        c.drawString(start_x, start_y + 2*mm, title)
        
        # Table headers
        c.setFont("Helvetica-Bold", 6)
        headers = ["No.", "Serial Number", "IMEI", "MAC"]
        
        current_y = start_y - header_height
        current_x = start_x
        
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            # Draw header cell background
            c.setFillColor((0.8, 0.8, 0.8))  # Gray
            c.rect(current_x, current_y, width, header_height, fill=1, stroke=1)
            
            # Draw header text
            c.setFillColor((0, 0, 0))  # Black
            text_x = current_x + width/2
            text_y = current_y + header_height/2 - 1
            c.drawCentredString(text_x, text_y, header)
            
            current_x += width
        
        # Draw device rows
        c.setFont("Helvetica", self.data_font_size)
        current_y -= header_height
        
        for i, device in enumerate(devices):
            current_x = start_x
            
            # Alternate row colors
            if i % 2 == 1:
                c.setFillColor((0.95, 0.95, 0.95))  # Very light gray
                c.rect(start_x, current_y, sum(col_widths), row_height, fill=1, stroke=0)
            
            # Device data - truncate if too long
            row_data = [
                f"{start_num + i:02d}",
                device['SERIAL_NUMBER'][-12:] if len(device['SERIAL_NUMBER']) > 12 else device['SERIAL_NUMBER'],  # Last 12 chars
                device['IMEI'][-12:] if len(device['IMEI']) > 12 else device['IMEI'],  # Last 12 chars
                device['MAC_ADDRESS']
            ]
            
            c.setFillColor((0, 0, 0))  # Black text
            for j, (data, width) in enumerate(zip(row_data, col_widths)):
                # Draw cell border
                c.rect(current_x, current_y, width, row_height, fill=0, stroke=1)
                
                # Draw text
                if j == 0:  # Center the number
                    text_x = current_x + width/2
                    c.drawCentredString(text_x, current_y + row_height/2 - 1, data)
                else:  # Left-align other data with small padding
                    text_x = current_x + 1 * mm
                    c.drawString(text_x, current_y + row_height/2 - 1, data)
                
                current_x += width
            
            current_y -= row_height
    
    def generate_box_label(self, devices: List[Dict[str, str]], 
                          output_path: str = None, 
                          box_number: str = None) -> str:
        """
        Generate a complete box label PDF
        
        Args:
            devices: List of 20 device dictionaries
            output_path: Output file path (auto-generated if None)
            box_number: Box identification number
            
        Returns:
            Path to generated PDF file
        """
        if len(devices) != 20:
            raise ValueError(f"Expected 20 devices, got {len(devices)}")
        
        # Generate output filename if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            first_serial = devices[0]['SERIAL_NUMBER']
            last_serial = devices[-1]['SERIAL_NUMBER']
            output_path = f"box_label_{first_serial}_{last_serial}_{timestamp}.pdf"
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=(self.label_width, self.label_height))
        
        # Title
        c.setFont("Helvetica-Bold", self.title_font_size)
        title_text = f"Device Box Label"
        if box_number:
            title_text += f" - Box #{box_number}"
        c.drawCentredString(self.label_width/2, self.label_height - 1.5*cm, title_text)
        
        # Date and device count
        c.setFont("Helvetica", self.header_font_size)
        date_text = f"Date: {datetime.now().strftime('%d/%m/%Y')}"
        count_text = f"Devices: {len(devices)} units"
        c.drawString(self.margin, self.label_height - 2.5*cm, date_text)
        c.drawRightString(self.label_width - self.margin, self.label_height - 2.5*cm, count_text)
        
        # QR code position (top right corner)
        qr_x = self.label_width - self.margin - self.qr_size
        qr_y = self.label_height - 1.2*cm - self.qr_size
        
        # Generate and place QR code first
        qr_data = self.create_qr_data(devices)
        qr_image_path = self.generate_qr_code(qr_data)
        
        # Draw QR code
        c.drawImage(qr_image_path, qr_x, qr_y, width=self.qr_size, height=self.qr_size)
        
        # Clean up temporary QR file
        try:
            os.remove(qr_image_path)
        except:
            pass
        
        # QR code label
        c.setFont("Helvetica", 6)
        c.drawCentredString(qr_x + self.qr_size/2, qr_y - 0.3*cm, "QR: All Device Data")
        
        # Calculate table layout (avoid QR code area)
        table_width = self.content_width - 0.5*cm  # Full width minus small margin
        table_height = self.content_height - 4*cm  # Space for headers and footer
        table_start_x = self.margin
        table_start_y = self.label_height - 3*cm
        
        # Draw device table
        self.draw_device_table(c, devices, table_start_x, table_start_y, table_width, table_height)
        
        # Footer with serial range
        c.setFont("Helvetica-Bold", 8)
        footer_text = f"S/N Range: {devices[0]['SERIAL_NUMBER']} → {devices[-1]['SERIAL_NUMBER']}"
        c.drawCentredString(self.label_width/2, self.margin + 2*mm, footer_text)
        
        # Save PDF
        c.save()
        
        logger.info(f"Box label generated: {output_path}")
        return output_path

def create_sample_box_label():
    """Create a sample box label with dummy data"""
    try:
        generator = BoxLabelGenerator()
        
        # Generate sample devices (based on our working device)
        devices = generator.generate_sample_devices("ATS542912923728")
        
        # Generate the label
        output_file = generator.generate_box_label(
            devices=devices,
            box_number="001"
        )
        
        print(f"✅ Sample box label created: {output_file}")
        print(f"📦 Contains {len(devices)} devices")
        print(f"📱 First device: {devices[0]['SERIAL_NUMBER']}")
        print(f"📱 Last device: {devices[-1]['SERIAL_NUMBER']}")
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error creating sample box label: {e}")
        raise

if __name__ == "__main__":
    # Create sample box label
    create_sample_box_label()