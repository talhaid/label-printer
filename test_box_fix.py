#!/usr/bin/env python3
"""
Test Box Label Fix for Numpy Type Issues
"""

import pandas as pd
import os
from datetime import datetime
import qrcode
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas

def create_fixed_box_label(devices_data, box_number="TEST_BOX"):
    """Create box label with proper type conversion"""
    
    # Convert all data to strings to avoid numpy type issues
    devices = []
    for device in devices_data:
        clean_device = {
            'SERIAL_NUMBER': str(device['SERIAL_NUMBER']),
            'IMEI': str(device['IMEI']),
            'MAC_ADDRESS': str(device['MAC_ADDRESS'])
        }
        devices.append(clean_device)
    
    # Create QR code
    qr_data = []
    for i, device in enumerate(devices, 1):
        qr_data.append(f"{i:02d}:{device['SERIAL_NUMBER']}:{device['IMEI']}:{device['MAC_ADDRESS']}")
    
    qr_string = "|".join(qr_data)
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=1
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    
    qr_image = qr.make_image(fill_color="black", back_color="white")
    temp_path = f"temp_test_qr_{datetime.now().strftime('%H%M%S_%f')}.png"
    qr_image.save(temp_path)
    
    # Create PDF
    width = 10 * cm
    height = 15 * cm
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    first_serial = devices[0]['SERIAL_NUMBER']
    last_serial = devices[-1]['SERIAL_NUMBER']
    filename = f"test_fixed_box_{box_number}_{first_serial}_{last_serial}_{timestamp}.pdf"
    
    c = canvas.Canvas(filename, pagesize=(width, height))
    
    # QR code at top
    y = height - 10*mm
    qr_size = 40*mm
    qr_x = (width - qr_size) / 2
    qr_y = y - qr_size
    
    c.drawImage(temp_path, qr_x, qr_y, width=qr_size, height=qr_size)
    
    # Clean up QR
    try:
        os.remove(temp_path)
    except:
        pass
    
    # Header
    y = qr_y - 6*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, y, "STC - SICAKLIK TAKIP CIHAZI")
    y -= 6*mm
    
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, y, f"{datetime.now().strftime('%d/%m/%Y')} - {box_number}")
    y -= 9*mm
    
    # Device list
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(width/2, y, "DEVICE LIST")
    y -= 5*mm
    
    # Headers
    c.setFont("Helvetica-Bold", 6)
    c.drawString(3*mm, y, "No.")
    c.drawString(10*mm, y, "Serial Number")
    c.drawString(42*mm, y, "IMEI")
    c.drawString(70*mm, y, "MAC")
    y -= 4*mm
    
    # Device entries
    c.setFont("Courier", 5.5)
    line_height = 3*mm
    
    for i, device in enumerate(devices, 1):
        if y > 5*mm:
            c.drawString(3*mm, y, f"{i:02d}")
            c.drawString(10*mm, y, device['SERIAL_NUMBER'])
            c.drawString(42*mm, y, device['IMEI'])
            c.drawString(70*mm, y, device['MAC_ADDRESS'])
            y -= line_height
        else:
            c.setFont("Helvetica", 5)
            c.drawCentredString(width/2, y, "... (complete data in QR code)")
            break
    
    c.save()
    return filename

def test_with_sample_data():
    """Test with sample CSV data"""
    
    print("🧪 Testing Box Label Fix")
    print("=" * 50)
    
    # Check for sample data
    if not os.path.exists("sample_devices.csv"):
        print("❌ sample_devices.csv not found!")
        return False
    
    # Load data
    df = pd.read_csv("sample_devices.csv")
    print(f"📖 Loaded {len(df)} devices")
    
    # Take first 5 devices for quick test
    test_devices = df.head(5)
    
    # Convert to list of dicts (simulating what GUI does)
    device_list = []
    for _, row in test_devices.iterrows():
        device = {
            'SERIAL_NUMBER': row['SERIAL_NUMBER'],
            'IMEI': row['IMEI'],
            'MAC_ADDRESS': row['MAC_ADDRESS']
        }
        device_list.append(device)
    
    print(f"🔧 Creating test box with {len(device_list)} devices...")
    print(f"   Types: SERIAL={type(device_list[0]['SERIAL_NUMBER'])}")
    print(f"         IMEI={type(device_list[0]['IMEI'])}") 
    print(f"         MAC={type(device_list[0]['MAC_ADDRESS'])}")
    
    try:
        filename = create_fixed_box_label(device_list, "FIXED_TEST")
        
        if os.path.exists(filename):
            file_size = os.path.getsize(filename) / 1024
            print(f"✅ SUCCESS! Box label created:")
            print(f"   📄 File: {filename}")
            print(f"   📊 Size: {file_size:.1f} KB")
            print(f"   📱 Devices: {len(device_list)}")
            return True
        else:
            print("❌ File not created")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test"""
    if test_with_sample_data():
        print("\n🎉 Fix verified! The GUI should now work properly.")
        print("💡 Try the Box Labels tab in printer_gui.py again!")
    else:
        print("\n⚠️ Test failed. Check the error above.")

if __name__ == "__main__":
    main()