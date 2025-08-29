#!/usr/bin/env python3
"""
Test the updated QR code format for box labels
"""

# Sample device data (same format as your actual data)
sample_devices = [
    {
        'STC': '60000',
        'SERIAL_NUMBER': 'ATS612165404520',
        'IMEI': '866988074129817',
        'IMSI': '286016570017900',
        'CCID': '8990011419260179000F',
        'MAC_ADDRESS': 'B8:46:52:25:67:68'
    },
    {
        'STC': '60001',
        'SERIAL_NUMBER': 'ATS612165404521',
        'IMEI': '866988074129818',
        'IMSI': '286016570017901',
        'CCID': '8990011419260179001F',
        'MAC_ADDRESS': 'B8:46:52:25:67:69'
    },
    {
        'STC': '60002',
        'SERIAL_NUMBER': 'ATS612165404522',
        'IMEI': '866988074129819',
        'IMSI': '286016570017902',
        'CCID': '8990011419260179002F',
        'MAC_ADDRESS': 'B8:46:52:25:67:70'
    }
]

def show_qr_content():
    print("📱 NEW QR CODE FORMAT")
    print("=" * 50)
    print("🏷️  Label shows: STC, S/N, IMEI, MAC")
    print("🔲 QR contains: STC, S/N, IMEI, IMSI, CCID, MAC")
    print("=" * 50)
    
    qr_data = []
    for device in sample_devices:
        stc = str(device.get('STC', 'N/A'))
        serial = str(device.get('SERIAL_NUMBER', 'N/A'))
        imei = str(device.get('IMEI', 'N/A'))
        imsi = str(device.get('IMSI', 'N/A'))
        ccid = str(device.get('CCID', 'N/A'))
        mac = str(device.get('MAC_ADDRESS', 'N/A'))
        
        # Include ALL device information in QR code
        device_info = f"{stc}:{serial}:{imei}:{imsi}:{ccid}:{mac}"
        qr_data.append(device_info)
        
        print(f"Device {device['STC']}:")
        print(f"  📄 Label: STC={stc}, S/N={serial}, IMEI={imei}, MAC={mac}")
        print(f"  🔲 QR:    {device_info}")
        print()
    
    qr_string = "|".join(qr_data)
    print("🔲 COMPLETE QR CODE CONTENT:")
    print("-" * 50)
    print(qr_string)
    print("-" * 50)
    print(f"📊 Total QR length: {len(qr_string)} characters")
    print(f"📊 Number of devices: {len(sample_devices)}")
    
    # Show QR structure
    print("\n🔍 QR CODE STRUCTURE:")
    print("Format: STC:SERIAL:IMEI:IMSI:CCID:MAC|STC:SERIAL:IMEI:IMSI:CCID:MAC|...")
    print("Separator between devices: |")
    print("Separator within device: :")

if __name__ == "__main__":
    show_qr_content()
