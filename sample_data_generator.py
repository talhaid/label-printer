#!/usr/bin/env python3
"""
Create Sample Device Data for Box Label Testing
Generates realistic device data to test the box label system
"""

import pandas as pd
import random
from datetime import datetime, timedelta

def generate_sample_devices(count=100):
    """Generate sample device data for testing"""
    
    devices = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        # Generate realistic serial numbers
        serial_base = "ATS542912923"
        serial_number = f"{serial_base}{700 + i:03d}"
        
        # Generate realistic IMEI (15 digits)
        imei = f"86997503300{1000 + i:04d}"
        
        # Generate realistic MAC addresses
        mac_base = "E4:5F:01:8D"
        mac_suffix1 = f"{(i // 256):02X}"
        mac_suffix2 = f"{(i % 256):02X}"
        mac_address = f"{mac_base}:{mac_suffix1}:{mac_suffix2}"
        
        # Generate IMSI (15 digits)
        imsi = f"28601987654{3000 + i:04d}"
        
        # Generate CCID (19 digits) 
        ccid = f"899110120000320{4000 + i:04d}"
        
        # STC counter
        stc = 7000 + i
        
        # Timestamp
        device_date = base_date + timedelta(hours=i*2)
        
        device = {
            'SERIAL_NUMBER': serial_number,
            'IMEI': imei,
            'MAC_ADDRESS': mac_address,
            'IMSI': imsi,
            'CCID': ccid,
            'STC': stc,
            'STATUS': 'Available',
            'TIMESTAMP': device_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        devices.append(device)
    
    return devices

def create_sample_csv():
    """Create sample CSV file for testing"""
    
    print("🔧 Generating sample device data...")
    
    # Generate 100 sample devices
    devices = generate_sample_devices(100)
    
    # Create DataFrame
    df = pd.DataFrame(devices)
    
    # Save to CSV
    filename = "sample_devices.csv"
    df.to_csv(filename, index=False)
    
    print(f"✅ Created {filename} with {len(devices)} sample devices")
    print(f"📦 Can create {len(devices) // 20} full boxes of 20 devices each")
    
    # Show sample
    print("\n📋 Sample devices:")
    print("=" * 80)
    for i in range(min(5, len(devices))):
        device = devices[i]
        print(f"{device['SERIAL_NUMBER']} | {device['IMEI']} | {device['MAC_ADDRESS']}")
    print("=" * 80)
    
    return filename

def merge_real_and_sample():
    """Merge real devices with sample data"""
    
    sample_devices = generate_sample_devices(98)  # Generate 98 more to make 100 total
    
    # Read cleaned real devices
    try:
        real_df = pd.read_csv("cleaned_devices.csv")
        print(f"📖 Found {len(real_df)} real devices")
        
        # Create sample DataFrame
        sample_df = pd.DataFrame(sample_devices)
        
        # Combine real and sample data
        combined_df = pd.concat([real_df, sample_df], ignore_index=True)
        
        # Save combined file
        combined_df.to_csv("combined_devices.csv", index=False)
        
        print(f"✅ Created combined_devices.csv with {len(combined_df)} devices")
        print(f"   • {len(real_df)} real devices")
        print(f"   • {len(sample_df)} sample devices")
        print(f"📦 Can create {len(combined_df) // 20} full boxes")
        
        return "combined_devices.csv"
        
    except FileNotFoundError:
        print("⚠️ cleaned_devices.csv not found, creating sample-only file")
        return create_sample_csv()

def main():
    """Main function"""
    print("📦 Sample Device Data Generator")
    print("=" * 50)
    
    # Create options
    print("Choose an option:")
    print("1. Create sample-only CSV (100 devices)")
    print("2. Merge real + sample data")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3) or press Enter for option 3: ").strip()
    
    if choice == "1":
        create_sample_csv()
    elif choice == "2":
        merge_real_and_sample()
    else:
        # Create both
        create_sample_csv()
        merge_real_and_sample()
        
    print("\n💡 Files created - you can now test the Box Labels tab!")
    print("   • Use sample_devices.csv for testing")
    print("   • Use combined_devices.csv for real + sample data")

if __name__ == "__main__":
    main()