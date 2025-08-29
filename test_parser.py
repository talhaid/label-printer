#!/usr/bin/env python3
"""
Test the updated parser with the new data format
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from serial_auto_printer import DeviceDataParser

def test_parser():
    parser = DeviceDataParser()
    
    test_cases = [
        # Your actual format (numeric S/N)
        ("##612165404520|866988074129817|286016570017900  |8990011419260179000F|B8:46:52:25:67:68##", "Numeric S/N"),
        
        # Already has ATS prefix
        ("##ATS612165404520|866988074129817|286016570017900|8990011419260179000F|B8:46:52:25:67:68##", "ATS prefix already"),
        
        # Original format with ATS
        ("##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##", "Original ATS format"),
        
        # Different prefix (should convert to ATS)
        ("##DEV612165404520|866988074129817|286016570017900|8990011419260179000F|B8:46:52:25:67:68##", "Different prefix"),
    ]
    
    for i, (test_data, description) in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {description}")
        print(f"Input: {test_data}")
        
        result = parser.parse_data(test_data)
        if result:
            print("✅ PARSED SUCCESSFULLY!")
            print(f"  Serial Number: {result['SERIAL_NUMBER']}")
            print(f"  IMEI: {result['IMEI']}")
            print(f"  IMSI: {result['IMSI']}")
            print(f"  CCID: {result['CCID']}")
            print(f"  MAC: {result['MAC_ADDRESS']}")
        else:
            print("❌ PARSING FAILED!")
    
    print(f"\n{'='*50}")
    print("✅ All tests completed!")

if __name__ == "__main__":
    test_parser()
