#!/usr/bin/env python3
"""
Ultra Simple Text-Based Box Label Generator
No tables, just text and QR code for 15x10cm paper
"""

import os
import base64
from datetime import datetime
from typing import List, Dict
import qrcode
from io import BytesIO

class SimpleTextBoxLabel:
    """Generate simple text-based box labels"""
    
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
    
    def create_qr_code_base64(self, devices: List[Dict[str, str]]) -> str:
        """Create QR code as base64 string"""
        qr_data = []
        for i, device in enumerate(devices, 1):
            qr_data.append(f"{i:02d}:{device['SERIAL_NUMBER']}:{device['IMEI']}:{device['MAC_ADDRESS']}")
        
        qr_string = "|".join(qr_data)
        
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=1)
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return qr_base64
    
    def generate_text_label(self, devices: List[Dict[str, str]], box_number: str = None) -> str:
        """Generate simple text-based HTML label"""
        
        if len(devices) != 20:
            raise ValueError(f"Expected 20 devices, got {len(devices)}")
        
        # Generate QR code
        qr_base64 = self.create_qr_code_base64(devices)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        first_serial = devices[0]['SERIAL_NUMBER']
        last_serial = devices[-1]['SERIAL_NUMBER']
        
        filename = f"simple_text_{first_serial}_{last_serial}_{timestamp}.html"
        
        # Create device text blocks
        left_text = ""
        right_text = ""
        
        # Left side (devices 1-10)
        for i, device in enumerate(devices[:10], 1):
            left_text += f"{i:02d} {device['SERIAL_NUMBER'][-8:]} {device['IMEI'][-8:]} {device['MAC_ADDRESS'][-8:]}\n"
        
        # Right side (devices 11-20)
        for i, device in enumerate(devices[10:], 11):
            right_text += f"{i:02d} {device['SERIAL_NUMBER'][-8:]} {device['IMEI'][-8:]} {device['MAC_ADDRESS'][-8:]}\n"
        
        # Create simple HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Simple Box Label</title>
    <style>
        @page {{ 
            size: 15cm 10cm; 
            margin: 0; 
        }}
        
        body {{ 
            margin: 0; 
            padding: 3mm; 
            font-family: 'Courier New', monospace; 
            font-size: 8px; 
            width: 15cm; 
            height: 10cm; 
            box-sizing: border-box;
            line-height: 1.1;
        }}
        
        .container {{
            display: flex;
            height: 100%;
            gap: 3mm;
        }}
        
        .devices {{
            flex: 1;
            display: flex;
            gap: 3mm;
        }}
        
        .left-column,
        .right-column {{
            flex: 1;
            white-space: pre-line;
            font-size: 7px;
        }}
        
        .qr-section {{
            width: 30mm;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .qr-code {{
            width: 28mm;
            height: 28mm;
        }}
        
        @media print {{ 
            body {{ 
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="devices">
            <div class="left-column">{left_text.strip()}</div>
            <div class="right-column">{right_text.strip()}</div>
        </div>
        <div class="qr-section">
            <img src="data:image/png;base64,{qr_base64}" class="qr-code" alt="QR">
        </div>
    </div>
</body>
</html>"""
        
        # Save HTML file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename

def create_simple_text_label():
    """Create simple text-based label"""
    try:
        generator = SimpleTextBoxLabel()
        
        # Generate sample devices
        devices = generator.generate_sample_devices("SIMPLE123456")
        
        # Generate text label
        html_file = generator.generate_text_label(devices, box_number="TXT001")
        
        print(f"✅ Simple text label: {html_file}")
        print(f"📦 Just text and QR - fits 15x10cm perfectly")
        
        return html_file
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    create_simple_text_label()