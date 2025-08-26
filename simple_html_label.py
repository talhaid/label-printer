#!/usr/bin/env python3
"""
Simple HTML Box Label Generator
Create customizable HTML labels that you can design manually
"""

import os
import json
from datetime import datetime
from typing import List, Dict
import qrcode
import base64
from io import BytesIO

class SimpleBoxLabelGenerator:
    """Generate simple HTML box labels that are easy to customize"""
    
    def __init__(self):
        """Initialize the generator"""
        pass
    
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
        """Create QR code as base64 string for embedding in HTML"""
        # Create compact QR data
        qr_data = []
        for i, device in enumerate(devices, 1):
            qr_data.append(f"{i:02d}:{device['SERIAL_NUMBER']}:{device['IMEI']}:{device['MAC_ADDRESS']}")
        
        qr_string = "|".join(qr_data)
        
        # Generate QR code
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        # Create image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return qr_base64
    
    def generate_html_label(self, devices: List[Dict[str, str]], box_number: str = None) -> str:
        """Generate HTML label that you can customize manually"""
        
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
        
        if box_number:
            filename = f"box_label_{box_number}_{first_serial}_{last_serial}_{timestamp}.html"
        else:
            filename = f"box_label_{first_serial}_{last_serial}_{timestamp}.html"
        
        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Box Label - {box_number or 'Default'}</title>
    <style>
        @page {{
            size: 15cm 10cm;
            margin: 0;
        }}
        
        body {{
            margin: 0;
            padding: 3mm;
            font-family: Arial, sans-serif;
            font-size: 8px;
            width: 15cm;
            height: 10cm;
            box-sizing: border-box;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 3mm;
        }}
        
        .title {{
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 2mm;
        }}
        
        .info-line {{
            font-size: 8px;
            display: flex;
            justify-content: space-between;
            margin-bottom: 2mm;
        }}
        
        .content {{
            display: flex;
            gap: 3mm;
        }}
        
        .devices-section {{
            flex: 1;
            display: flex;
            gap: 2mm;
        }}
        
        .device-column {{
            flex: 1;
        }}
        
        .column-title {{
            font-size: 7px;
            font-weight: bold;
            margin-bottom: 1mm;
            text-align: center;
            background-color: #f0f0f0;
            padding: 1mm;
        }}
        
        .device-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 6px;
        }}
        
        .device-table th {{
            background-color: #e0e0e0;
            padding: 1mm;
            border: 0.5px solid #999;
            font-size: 5px;
        }}
        
        .device-table td {{
            padding: 0.5mm;
            border: 0.5px solid #ccc;
            text-align: left;
        }}
        
        .device-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        .qr-section {{
            width: 25mm;
            text-align: center;
        }}
        
        .qr-code {{
            width: 20mm;
            height: 20mm;
            margin: 0 auto 2mm auto;
        }}
        
        .qr-label {{
            font-size: 5px;
            margin-top: 1mm;
        }}
        
        .footer {{
            position: absolute;
            bottom: 2mm;
            left: 3mm;
            right: 3mm;
            text-align: center;
            font-size: 7px;
            font-weight: bold;
        }}
        
        /* Print styles */
        @media print {{
            body {{
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">Device Box Label{f" - Box #{box_number}" if box_number else ""}</div>
        <div class="info-line">
            <span>Date: {datetime.now().strftime('%d/%m/%Y')}</span>
            <span>Devices: {len(devices)} units</span>
        </div>
    </div>
    
    <div class="content">
        <div class="devices-section">
            <div class="device-column">
                <div class="column-title">Devices 1-10</div>
                <table class="device-table">
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>Serial Number</th>
                            <th>IMEI</th>
                            <th>MAC</th>
                        </tr>
                    </thead>
                    <tbody>"""
        
        # Add left column devices
        for i, device in enumerate(left_devices, 1):
            html_content += f"""
                        <tr>
                            <td>{i:02d}</td>
                            <td>{device['SERIAL_NUMBER'][-12:]}</td>
                            <td>{device['IMEI'][-12:]}</td>
                            <td>{device['MAC_ADDRESS']}</td>
                        </tr>"""
        
        html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="device-column">
                <div class="column-title">Devices 11-20</div>
                <table class="device-table">
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>Serial Number</th>
                            <th>IMEI</th>
                            <th>MAC</th>
                        </tr>
                    </thead>
                    <tbody>"""
        
        # Add right column devices
        for i, device in enumerate(right_devices, 11):
            html_content += f"""
                        <tr>
                            <td>{i:02d}</td>
                            <td>{device['SERIAL_NUMBER'][-12:]}</td>
                            <td>{device['IMEI'][-12:]}</td>
                            <td>{device['MAC_ADDRESS']}</td>
                        </tr>"""
        
        html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="qr-section">
            <img src="data:image/png;base64,{qr_base64}" class="qr-code" alt="QR Code">
            <div class="qr-label">QR: All Device Data</div>
        </div>
    </div>
    
    <div class="footer">
        S/N Range: {devices[0]['SERIAL_NUMBER']} → {devices[-1]['SERIAL_NUMBER']}
    </div>
</body>
</html>"""
        
        # Save HTML file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename

def create_sample_html_label():
    """Create a sample HTML label"""
    try:
        generator = SimpleBoxLabelGenerator()
        
        # Generate sample devices
        devices = generator.generate_sample_devices("DEV001TEST123")
        
        # Generate the HTML label
        html_file = generator.generate_html_label(
            devices=devices,
            box_number="HTML001"
        )
        
        print(f"✅ HTML box label created: {html_file}")
        print(f"📦 Contains {len(devices)} devices")
        print(f"🌐 Open in browser to view and customize")
        print(f"🖨️  Use browser's Print function to save as PDF")
        
        return html_file
        
    except Exception as e:
        print(f"Error creating HTML label: {e}")
        raise

if __name__ == "__main__":
    create_sample_html_label()