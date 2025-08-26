#!/usr/bin/env python3
"""
Text-Only Box Label Generator
No QR code - just text information
"""

from datetime import datetime
from typing import List, Dict
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

class TextOnlyBoxLabel:
    """Text-only box label - no QR code"""
    
    def generate_text_pdf(self, devices: List[Dict[str, str]], box_number: str = "BOX001") -> str:
        """Generate text-only PDF label"""
        
        # Paper size
        width = 10 * cm
        height = 15 * cm
        
        # Filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"text_box_{box_number}_{timestamp}.pdf"
        
        # Create PDF
        c = canvas.Canvas(filename, pagesize=(width, height))
        
        # Start from top with margin
        margin = 5*mm
        y_pos = height - margin - 5*mm
        
        # Title
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width/2, y_pos, "STC - SICAKLIK TAKIP CIHAZI")
        y_pos -= 8*mm
        
        # Date and box
        c.setFont("Helvetica", 9)
        c.drawCentredString(width/2, y_pos, f"{datetime.now().strftime('%d/%m/%Y')} - {box_number}")
        y_pos -= 10*mm
        
        # Device count
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, y_pos, f"CONTAINS {len(devices)} DEVICES")
        y_pos -= 12*mm
        
        # Serial number range
        first_sn = devices[0]['SERIAL_NUMBER']
        last_sn = devices[-1]['SERIAL_NUMBER']
        
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin, y_pos, "SERIAL NUMBERS:")
        y_pos -= 6*mm
        
        c.setFont("Courier", 7)
        c.drawString(margin, y_pos, f"FROM: {first_sn}")
        y_pos -= 5*mm
        c.drawString(margin, y_pos, f"TO:   {last_sn}")
        y_pos -= 10*mm
        
        # Device list - compact
        c.setFont("Helvetica-Bold", 7)
        c.drawString(margin, y_pos, "DEVICE LIST:")
        y_pos -= 6*mm
        
        # Show devices in compact format
        c.setFont("Courier", 5)
        line_height = 3*mm
        
        for i, device in enumerate(devices, 1):
            if y_pos > margin + 5*mm:  # Check if we have space
                device_text = f"{i:02d}. {device['SERIAL_NUMBER']}"
                c.drawString(margin, y_pos, device_text)
                y_pos -= line_height
            else:
                # If we run out of space, show "..."
                c.drawString(margin, y_pos, "...")
                break
        
        c.save()
        return filename

def main():
    """Test the text-only generator"""
    generator = TextOnlyBoxLabel()
    
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
        filename = generator.generate_text_pdf(devices, "BOX001")
        print(f"✅ Text-only box label: {filename}")
        print(f"📝 Contains: Company name, date, device count, S/N list")
        print(f"📏 Size: 10cm x 15cm portrait")
        print(f"🎯 Pure text - no graphics")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()