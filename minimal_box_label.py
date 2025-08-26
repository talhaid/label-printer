#!/usr/bin/env python3
"""
Minimal HTML Box Label Generator - Super Clean Version
"""

import os
import base64
from datetime import datetime
from typing import List, Dict
import qrcode
from io import BytesIO

class MinimalBoxLabelGenerator:
    """Generate minimal HTML box labels - just QR and device data"""
    
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
        
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return qr_base64
    
    def generate_minimal_label(self, devices: List[Dict[str, str]], box_number: str = None) -> str:
        """Generate minimal HTML label"""
        
        if len(devices) != 20:
            raise ValueError(f"Expected 20 devices, got {len(devices)}")
        
        # Generate QR code
        qr_base64 = self.create_qr_code_base64(devices)
        
        # Split devices into two columns
        left_devices = devices[:10]
        right_devices = devices[10:]
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        first_serial = devices[0]['SERIAL_NUMBER']
        last_serial = devices[-1]['SERIAL_NUMBER']
        
        filename = f"minimal_box_{first_serial}_{last_serial}_{timestamp}.html"
        
        # Create minimal HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Box Label</title>
    <style>
        @page {{ size: 15cm 10cm; margin: 0; }}
        body {{ margin: 0; padding: 2mm; font-family: Arial, sans-serif; font-size: 5px; width: 15cm; height: 10cm; box-sizing: border-box; }}
        .content {{ display: flex; gap: 2mm; height: 100%; }}
        .devices {{ flex: 1; display: flex; gap: 1mm; }}
        .col {{ flex: 1; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 5px; }}
        th {{ background: #ddd; padding: 0.5mm; border: 0.3px solid #999; font-size: 4px; }}
        td {{ padding: 0.3mm; border: 0.3px solid #ccc; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .qr {{ width: 22mm; text-align: center; display: flex; align-items: center; justify-content: center; }}
        .qr img {{ width: 20mm; height: 20mm; }}
        @media print {{ body {{ print-color-adjust: exact; }} }}
    </style>
</head>
<body>
    <div class="content">
        <div class="devices">
            <div class="col">
                <table>
                    <tr><th>No</th><th>Serial</th><th>IMEI</th><th>MAC</th></tr>"""
        
        # Left column devices (1-10)
        for i, device in enumerate(left_devices, 1):
            html_content += f"""
                    <tr><td>{i:02d}</td><td>{device['SERIAL_NUMBER'][-8:]}</td><td>{device['IMEI'][-8:]}</td><td>{device['MAC_ADDRESS'][-8:]}</td></tr>"""
        
        html_content += """
                </table>
            </div>
            <div class="col">
                <table>
                    <tr><th>No</th><th>Serial</th><th>IMEI</th><th>MAC</th></tr>"""
        
        # Right column devices (11-20)
        for i, device in enumerate(right_devices, 11):
            html_content += f"""
                    <tr><td>{i:02d}</td><td>{device['SERIAL_NUMBER'][-8:]}</td><td>{device['IMEI'][-8:]}</td><td>{device['MAC_ADDRESS'][-8:]}</td></tr>"""
        
        html_content += f"""
                </table>
            </div>
        </div>
        <div class="qr">
            <img src="data:image/png;base64,{qr_base64}" alt="QR">
        </div>
    </div>
</body>
</html>"""
        
        # Save HTML file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename

def create_minimal_label():
    """Create minimal label"""
    try:
        generator = MinimalBoxLabelGenerator()
        
        # Generate sample devices
        devices = generator.generate_sample_devices("TEST12345678")
        
        # Generate minimal label
        html_file = generator.generate_minimal_label(devices, box_number="MIN001")
        
        print(f"✅ Minimal box label: {html_file}")
        print(f"📦 20 devices, QR code, no extra text")
        
        return html_file
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    create_minimal_label()