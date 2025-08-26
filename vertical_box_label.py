#!/usr/bin/env python3
"""
Vertical Box Label Generator - PDF in Portrait Orientation
Paper: 10cm x 15cm (portrait), generates PDF directly
"""

import os
from datetime import datetime
from typing import List, Dict
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
import tempfile

class VerticalBoxLabelGenerator:
    """Generate vertical layout box labels like the sketch"""
    
    def generate_sample_devices(self, base_serial: str = "ATS542912923728") -> List[Dict[str, str]]:
        """Generate 20 sample devices"""
        devices = []
        
        for i in range(20):
            device = {
                "SERIAL_NUMBER": f"{base_serial[:-2]}{i+1:02d}",
                "IMEI": f"866988074133{i+100:03d}",
                "MAC_ADDRESS": f"AA:BB:CC:DD:EE:{i+10:02X}"
            }
            devices.append(device)
            
        return devices
    
    def generate_qr_code_image(self, devices: List[Dict[str, str]]) -> str:
        """Create QR code and save as temporary image file"""
        qr_data = []
        for i, device in enumerate(devices, 1):
            qr_data.append(f"{i:02d}:{device['SERIAL_NUMBER']}:{device['IMEI']}:{device['MAC_ADDRESS']}")
        
        qr_string = "|".join(qr_data)
        
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=1)
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save to temporary file
        temp_path = f"temp_qr_vertical_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        qr_image.save(temp_path)
        
        return temp_path
    
    def generate_vertical_pdf(self, devices: List[Dict[str, str]], box_number: str = "BOX001") -> str:
        """Generate vertical layout PDF label - Portrait orientation 10cm x 15cm"""
        
        if len(devices) != 20:
            raise ValueError(f"Expected 20 devices, got {len(devices)}")
        
        # Paper size: 10cm x 15cm (portrait)
        label_width = 10 * cm
        label_height = 15 * cm
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        first_serial = devices[0]['SERIAL_NUMBER']
        last_serial = devices[-1]['SERIAL_NUMBER']
        
        filename = f"vertical_box_pdf_{box_number}_{first_serial}_{last_serial}_{timestamp}.pdf"
        
        # Create PDF
        c = canvas.Canvas(filename, pagesize=(label_width, label_height))
        
        # Margins
        margin = 3 * mm
        
        # No border/frame - clean layout
        
        # Header section (top 2.5cm)
        header_height = 2.5 * cm
        header_y = label_height - margin - header_height
        
        # QR code section (top-left) - No frame
        qr_size = 32 * mm
        qr_x = margin + 2*mm
        qr_y = header_y + 2*mm
        
        # Generate QR code
        qr_image_path = self.generate_qr_code_image(devices)
        
        # Draw QR code without border/frame
        c.drawImage(qr_image_path, qr_x, qr_y, 
                   width=qr_size, height=qr_size)
        
        # Clean up QR temp file
        try:
            os.remove(qr_image_path)
        except:
            pass
        
        # Header text section (top-right) - Adjusted for larger QR
        text_x = qr_x + qr_size + 2*mm  # Reduced gap from 3mm to 2mm
        text_y = qr_y + qr_size - 4*mm  # Adjusted positioning
        
        # Company name
        c.setFont("Helvetica-Bold", 9)  # Slightly smaller font
        c.drawString(text_x, text_y, "STC - SICAKLIK TAKIP CIHAZI")
        
        # Date
        c.setFont("Helvetica", 7)  # Smaller date font
        c.drawString(text_x, text_y - 5*mm, datetime.now().strftime('%d/%m/%Y'))
        
        # Box number
        c.setFont("Helvetica-Bold", 8)
        c.drawString(text_x, text_y - 10*mm, box_number)
        
        # Device list section - No tables or frames
        device_section_y = header_y - 2*mm
        
        # Device header - Simple text, no background
        c.setFont("Helvetica-Bold", 7)
        header_text_y = device_section_y - 4*mm
        c.setFillColor(black)
        c.drawCentredString(label_width/2, header_text_y, "S/N | IMEI | MAC")
        
        # Device list - Simple text layout
        c.setFont("Courier", 5.5)
        current_y = header_text_y - 4*mm
        line_height = 3.2 * mm
        
        for i, device in enumerate(devices, 1):
            if current_y > margin + 5*mm:  # Make sure we don't go below margin
                device_line = f"{i:02d}- {device['SERIAL_NUMBER']} | {device['IMEI']} | {device['MAC_ADDRESS']}"
                c.drawString(margin + 2*mm, current_y, device_line)
                current_y -= line_height
        
        # Save PDF
        c.save()
        
        return filename

# Test the vertical PDF generator
if __name__ == "__main__":
    generator = VerticalBoxLabelGenerator()
    
    # Generate test devices
    devices = []
    for i in range(1, 21):
        device = {
            'SERIAL_NUMBER': f"ATS5429124237{i:02d}",
            'IMEI': f"869975033{i:06d}{i%10}",
            'MAC_ADDRESS': f"E4:5F:01:8D:{i:02X}:{(i*7)%256:02X}"
        }
        devices.append(device)
    
    # Generate PDF label
    try:
        filename = generator.generate_vertical_pdf(devices, box_number="BOX001")
        print(f"✅ Vertical PDF label generated: {filename}")
        print(f"� Paper size: 10cm x 15cm (Portrait)")
        print(f"📄 Contains 20 devices with QR code")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()