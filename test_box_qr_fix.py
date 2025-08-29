#!/usr/bin/env python3
"""
Test the box label QR code generation with complete data
"""

import pandas as pd

# Simulate the CSV data structure
test_data = {
    'STC': [60000, 60001, 60002],
    'SERIAL_NUMBER': ['ATS612165404520', 'ATS612165404521', 'ATS612165404522'],
    'IMEI': ['866988074129817', '866988074129818', '866988074129819'],
    'IMSI': ['286016570017900', '286016570017901', '286016570017902'],
    'CCID': ['8990011419260179000F', '8990011419260179001F', '8990011419260179002F'],
    'MAC_ADDRESS': ['B8:46:52:25:67:68', 'B8:46:52:25:67:69', 'B8:46:52:25:67:70'],
    'STATUS': ['Available', 'Available', 'Available']
}

df = pd.DataFrame(test_data)

def test_device_selection():
    print("🧪 TESTING BOX LABEL DATA SELECTION")
    print("=" * 50)
    
    # Simulate device selection (selecting first 3 devices)
    selected_indices = [0, 1, 2]
    selected_device_data = []
    
    for idx in selected_indices:
        device_row = df.iloc[idx]
        device_dict = {
            'STC': str(device_row.get('STC', 'N/A')),
            'SERIAL_NUMBER': str(device_row.get('SERIAL_NUMBER', 'N/A')),
            'IMEI': str(device_row.get('IMEI', 'N/A')),
            'IMSI': str(device_row.get('IMSI', 'N/A')),  # Now included
            'CCID': str(device_row.get('CCID', 'N/A')),  # Now included
            'MAC_ADDRESS': str(device_row.get('MAC_ADDRESS', 'N/A'))
        }
        selected_device_data.append(device_dict)
        
        print(f"Device {idx + 1}:")
        for key, value in device_dict.items():
            print(f"  {key}: {value}")
        print()
    
    # Generate QR data
    print("🔲 QR CODE CONTENT:")
    print("-" * 30)
    qr_data = []
    for device in selected_device_data:
        stc = device['STC']
        serial = device['SERIAL_NUMBER']
        imei = device['IMEI']
        imsi = device['IMSI']
        ccid = device['CCID']
        mac = device['MAC_ADDRESS']
        
        device_info = f"{stc}:{serial}:{imei}:{imsi}:{ccid}:{mac}"
        qr_data.append(device_info)
        print(f"{device_info}")
    
    qr_string = "|".join(qr_data)
    print("-" * 30)
    print(f"Complete QR: {qr_string}")
    print(f"✅ All fields present: {all('N/A' not in item for item in qr_data)}")

if __name__ == "__main__":
    test_device_selection()
