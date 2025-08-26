#!/usr/bin/env python3
"""
Combined Box Label Generator
QR code + full device list in clean layout
"""

import os
from datetime import datetime
from typing import List, Dict
import qrcode
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

class CombinedBoxLabel:
    """Combined QR code and device list label"""
    
    def create_qr_with_devices(self, devices: List[Dict[str, str]]) -> str:
        """Create QR code with all device data"""
        # Include all device info in QR
        qr_data = []
        for i, device in enumerate(devices, 1):
            qr_data.append(f"{i:02d}:{device['SERIAL_NUMBER']}:{device['IMEI']}:{device['MAC_ADDRESS']}")
        
        qr_string = "|".join(qr_data)
        
        qr = qrcode.QRCode(
            version=None,  # Auto-size
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=1
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        temp_path = f"temp_combined_qr_{datetime.now().strftime('%H%M%S_%f')}.png"
        qr_image.save(temp_path)
        return temp_path
    
    def generate_combined_pdf(self, devices: List[Dict[str, str]], box_number: str = "BOX001") -> str:
        """Generate combined QR + device list PDF"""
        
        width = 10 * cm
        height = 15 * cm
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        first_serial = devices[0]['SERIAL_NUMBER']
        last_serial = devices[-1]['SERIAL_NUMBER']
        filename = f"combined_box_{box_number}_{first_serial}_{last_serial}_{timestamp}.pdf"
        
        c = canvas.Canvas(filename, pagesize=(width, height))
        
        # Header section - compact
        y = height - 6*mm
        
        # Company name - smaller to save space
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, y, "STC - SICAKLIK TAKIP CIHAZI")
        y -= 6*mm
        
        # Date and box - compact
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, y, f"{datetime.now().strftime('%d/%m/%Y')} - {box_number}")
        y -= 8*mm
        
        # QR code - centered horizontally
        qr_path = self.create_qr_with_devices(devices)
        qr_size = 40*mm  # Keep large size
        qr_x = (width - qr_size) / 2  # Center horizontally
        qr_y = y - qr_size
        
        c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size)
        
        # Clean up QR
        try:
            os.remove(qr_path)
        except:
            pass
        
        # Device list section - starts right after QR
        y = qr_y - 3*mm
        
        # Device list header - compact
        c.setFont("Helvetica-Bold", 7)  # Increased from 6
        c.drawCentredString(width/2, y, "DEVICE LIST")
        y -= 5*mm  # Increased spacing
        
        # Column headers - larger font for better readability
        c.setFont("Helvetica-Bold", 6)  # Increased from 5.5
        c.drawString(3*mm, y, "No.")
        c.drawString(10*mm, y, "Serial Number")
        c.drawString(42*mm, y, "IMEI")
        c.drawString(70*mm, y, "MAC")
        y -= 4*mm  # Increased spacing
        
        # Device entries - much larger font
        c.setFont("Courier", 5.5)  # Increased from 4.5 to 5.5
        line_height = 3*mm  # Increased from 2.5mm to 3mm
        
        for i, device in enumerate(devices, 1):
            if y > 6*mm:  # Adjusted space check for larger fonts
                c.drawString(3*mm, y, f"{i:02d}")
                c.drawString(10*mm, y, device['SERIAL_NUMBER'])
                c.drawString(42*mm, y, device['IMEI'])
                c.drawString(70*mm, y, device['MAC_ADDRESS'])
                y -= line_height
            else:
                # If we run out of space
                c.setFont("Helvetica", 5)  # Larger fallback font
                c.drawCentredString(width/2, y, "... (complete data in QR code)")
                break
        
        c.save()
        return filename

def main():
    """Test the combined generator"""
    generator = CombinedBoxLabel()
    
    # Generate test devices
    devices = []
    for i in range(1, 21):
        device = {
            'SERIAL_NUMBER': f"ATS5429124237{i:02d}",
            'IMEI': f"869975033{i:06d}{i%10}",
            'MAC_ADDRESS': f"E4:5F:01:8D:{i:02X}:{(i*7)%256:02X}"
        }
        devices.append(device)
    
    try:
        filename = generator.generate_combined_pdf(devices, "BOX001")
        print(f"✅ Combined box label: {filename}")
        print(f"📱 QR code contains all device data")
        print(f"📝 Visible device list for easy reading")
        print(f"📏 Optimized for 10cm x 15cm")
        print(f"🎯 Best of both worlds!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()