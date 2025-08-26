#!/usr/bin/env python3
"""
Centered Box Label Generator
Everything centered, simple layout
"""

import os
from datetime import datetime
from typing import List, Dict
import qrcode
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas

class CenteredBoxLabel:
    """Centered layout box label"""
    
    def create_qr(self, devices: List[Dict[str, str]]) -> str:
        """Create small QR with basic info"""
        qr_text = f"BOX-{len(devices)}-DEVICES"
        
        qr = qrcode.QRCode(version=1, box_size=6, border=1)
        qr.add_data(qr_text)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        temp_path = f"temp_centered_qr_{datetime.now().strftime('%H%M%S')}.png"
        qr_image.save(temp_path)
        return temp_path
    
    def generate_centered_pdf(self, devices: List[Dict[str, str]], box_number: str = "BOX001") -> str:
        """Generate centered layout PDF"""
        
        width = 10 * cm
        height = 15 * cm
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"centered_box_{box_number}_{timestamp}.pdf"
        
        c = canvas.Canvas(filename, pagesize=(width, height))
        
        # Everything centered
        center_x = width / 2
        y = height - 15*mm
        
        # Company - large, centered
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(center_x, y, "STC")
        y -= 8*mm
        
        c.setFont("Helvetica", 10)
        c.drawCentredString(center_x, y, "SICAKLIK TAKIP CIHAZI")
        y -= 15*mm
        
        # Date and box
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(center_x, y, f"{box_number}")
        y -= 6*mm
        
        c.setFont("Helvetica", 9)
        c.drawCentredString(center_x, y, datetime.now().strftime('%d/%m/%Y'))
        y -= 15*mm
        
        # QR code - centered
        qr_path = self.create_qr(devices)
        qr_size = 25*mm
        qr_x = center_x - qr_size/2
        c.drawImage(qr_path, qr_x, y - qr_size, width=qr_size, height=qr_size)
        
        try:
            os.remove(qr_path)
        except:
            pass
        
        y -= qr_size + 10*mm
        
        # Device info
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(center_x, y, f"{len(devices)} DEVICES")
        y -= 8*mm
        
        # Serial range
        first_sn = devices[0]['SERIAL_NUMBER']
        last_sn = devices[-1]['SERIAL_NUMBER']
        
        c.setFont("Courier", 8)
        c.drawCentredString(center_x, y, first_sn)
        y -= 6*mm
        c.drawCentredString(center_x, y, "to")
        y -= 6*mm
        c.drawCentredString(center_x, y, last_sn)
        
        c.save()
        return filename

def main():
    generator = CenteredBoxLabel()
    
    devices = []
    for i in range(1, 21):
        device = {
            'SERIAL_NUMBER': f"ATS5429124237{i:02d}",
            'IMEI': f"869975033{i:06d}{i%10}",
            'MAC_ADDRESS': f"E4:5F:01:8D:{i:02X}:{(i*7)%256:02X}"
        }
        devices.append(device)
    
    try:
        filename = generator.generate_centered_pdf(devices, "BOX001")
        print(f"✅ Centered box label: {filename}")
        print(f"📏 Everything centered on 10x15cm")
        print(f"🎯 Clean, simple design")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()