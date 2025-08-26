#!/usr/bin/env python3
"""
Ultra Simple Box Label Generator
Minimal approach - just QR + basic device info
"""

import os
from datetime import datetime
from typing import List, Dict
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

class UltraSimpleBoxLabel:
    """Ultra minimal box label - just essentials"""
    
    def create_qr_image(self, devices: List[Dict[str, str]]) -> str:
        """Create QR code with just device count and first/last serial"""
        # Simple QR data - just key info
        first_sn = devices[0]['SERIAL_NUMBER']
        last_sn = devices[-1]['SERIAL_NUMBER']
        device_count = len(devices)
        
        qr_text = f"BOX:{device_count} devices|{first_sn} to {last_sn}"
        
        qr = qrcode.QRCode(
            version=1,  # Smallest version
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Low error correction
            box_size=8,
            border=1
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save temp file
        temp_path = f"temp_simple_qr_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        qr_image.save(temp_path)
        return temp_path
    
    def generate_simple_pdf(self, devices: List[Dict[str, str]], box_number: str = "BOX001") -> str:
        """Generate ultra simple PDF - 10cm x 15cm"""
        
        # Paper size
        width = 10 * cm
        height = 15 * cm
        
        # Filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simple_box_{box_number}_{timestamp}.pdf"
        
        # Create PDF
        c = canvas.Canvas(filename, pagesize=(width, height))
        
        # Start from top
        y_pos = height - 10*mm
        
        # Company name - top center
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width/2, y_pos, "STC - SICAKLIK TAKIP CIHAZI")
        y_pos -= 8*mm
        
        # Date and box - center
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, y_pos, f"{datetime.now().strftime('%d/%m/%Y')} - {box_number}")
        y_pos -= 12*mm
        
        # QR Code - center
        qr_path = self.create_qr_image(devices)
        qr_size = 30*mm
        qr_x = (width - qr_size) / 2
        c.drawImage(qr_path, qr_x, y_pos - qr_size, width=qr_size, height=qr_size)
        
        # Clean up QR
        try:
            os.remove(qr_path)
        except:
            pass
        
        y_pos -= qr_size + 8*mm
        
        # Device count
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, y_pos, f"Contains {len(devices)} devices")
        y_pos -= 8*mm
        
        # Serial range
        c.setFont("Helvetica", 9)
        first_sn = devices[0]['SERIAL_NUMBER']
        last_sn = devices[-1]['SERIAL_NUMBER']
        c.drawCentredString(width/2, y_pos, f"S/N: {first_sn}")
        y_pos -= 6*mm
        c.drawCentredString(width/2, y_pos, f"to: {last_sn}")
        
        c.save()
        return filename

def main():
    """Test the ultra simple generator"""
    generator = UltraSimpleBoxLabel()
    
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
        filename = generator.generate_simple_pdf(devices, "BOX001")
        print(f"✅ Ultra simple box label: {filename}")
        print(f"📦 Contains: Company name, date, QR code, device count, S/N range")
        print(f"📏 Size: 10cm x 15cm portrait")
        print(f"🎯 Minimal design - just essentials")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()