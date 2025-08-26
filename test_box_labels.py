#!/usr/bin/env python3
"""
Test script for Box Label Generator
Demonstrates how to create box labels for 20-device packaging
"""

from box_label_generator import BoxLabelGenerator

def test_box_label_with_custom_data():
    """Test with custom device data"""
    print("🧪 Testing Box Label Generator with custom data...")
    
    generator = BoxLabelGenerator()
    
    # Create custom device list (example with different base)
    devices = []
    for i in range(20):
        device = {
            "SERIAL_NUMBER": f"DTS{555666777888 + i:012d}",
            "IMEI": f"{555666777888999 + i:015d}",
            "MAC_ADDRESS": f"DD:EE:FF:00:{11+i:02X}:{22+i:02X}"
        }
        devices.append(device)
    
    # Generate box label
    output_file = generator.generate_box_label(
        devices=devices,
        box_number="A001"
    )
    
    print(f"✅ Custom box label created: {output_file}")
    return output_file

def test_multiple_boxes():
    """Test creating multiple box labels"""
    print("📦 Creating multiple box labels...")
    
    generator = BoxLabelGenerator()
    
    # Create 3 different boxes
    box_files = []
    
    for box_num in range(1, 4):
        # Generate different devices for each box
        devices = generator.generate_sample_devices(f"BOX{box_num:03d}TEST{123456789:09d}")
        
        output_file = generator.generate_box_label(
            devices=devices,
            box_number=f"B{box_num:03d}"
        )
        
        box_files.append(output_file)
        print(f"📋 Box {box_num} label: {output_file}")
    
    return box_files

def show_device_info_sample():
    """Show what device information looks like"""
    print("📋 Sample device information structure:")
    
    generator = BoxLabelGenerator()
    devices = generator.generate_sample_devices("ATS542912923728")
    
    print(f"📦 Total devices: {len(devices)}")
    print("📱 First 3 devices:")
    for i in range(3):
        device = devices[i]
        print(f"   {i+1:02d}. S/N: {device['SERIAL_NUMBER']}")
        print(f"       IMEI: {device['IMEI']}")
        print(f"       MAC: {device['MAC_ADDRESS']}")
        print()
    
    print("📱 Last device:")
    device = devices[-1]
    print(f"   20. S/N: {device['SERIAL_NUMBER']}")
    print(f"       IMEI: {device['IMEI']}")
    print(f"       MAC: {device['MAC_ADDRESS']}")

if __name__ == "__main__":
    print("🏷️  Box Label Generator Test Suite")
    print("=" * 50)
    
    # Show sample data structure
    show_device_info_sample()
    print()
    
    # Test with custom data
    test_box_label_with_custom_data()
    print()
    
    # Test multiple boxes
    test_multiple_boxes()
    print()
    
    print("✅ All tests completed!")
    print("📁 Check the generated PDF files in the current directory")