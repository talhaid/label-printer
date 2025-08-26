#!/usr/bin/env python3
"""
Simple test for the improved box label generator
"""

from box_label_generator import BoxLabelGenerator

def test_improved_layout():
    print("🧪 Testing Improved Box Label Layout")
    print("=" * 40)
    
    generator = BoxLabelGenerator()
    
    # Generate test devices with shorter names for better display
    devices = []
    for i in range(20):
        device = {
            "SERIAL_NUMBER": f"DEV{i+1:03d}TEST123",
            "IMEI": f"86698807413{i+3400:04d}",
            "MAC_ADDRESS": f"AA:BB:CC:DD:{i+10:02X}:{i+20:02X}"
        }
        devices.append(device)
    
    print("📱 Sample device data:")
    print("   First 3 devices:")
    for i in range(3):
        d = devices[i]
        print(f"   {i+1:2d}. {d['SERIAL_NUMBER']} | {d['IMEI']} | {d['MAC_ADDRESS']}")
    
    print("   ...")
    print("   Last 3 devices:")
    for i in range(17, 20):
        d = devices[i]
        print(f"   {i+1:2d}. {d['SERIAL_NUMBER']} | {d['IMEI']} | {d['MAC_ADDRESS']}")
    
    # Generate improved label
    pdf_file = generator.generate_box_label(devices, box_number="IMPROVED001")
    
    print(f"\n✅ Improved box label created: {pdf_file}")
    print("\n🔧 Layout improvements:")
    print("   • Two-column layout (10 devices per column)")
    print("   • Smaller fonts to fit all data")
    print("   • QR code moved to top-right corner")
    print("   • Compact QR data format")
    print("   • Better spacing and margins")
    print("   • Truncated long serial numbers for display")
    
    return pdf_file

if __name__ == "__main__":
    test_improved_layout()