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
    
    # Test the new format
    test_data = "##612165404520|866988074129817|286016570017900  |8990011419260179000F|B8:46:52:25:67:68##"
    
    print("Testing new data format:")
    print(f"Input: {test_data}")
    
    result = parser.parse_data(test_data)
    if result:
        print("✅ PARSED SUCCESSFULLY!")
        for key, value in result.items():
            print(f"  {key}: {value}")
    else:
        print("❌ PARSING FAILED!")
    
    print("\n" + "="*50)
    
    # Test the original format too
    test_data_old = "##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##"
    
    print("Testing original data format:")
    print(f"Input: {test_data_old}")
    
    result_old = parser.parse_data(test_data_old)
    if result_old:
        print("✅ PARSED SUCCESSFULLY!")
        for key, value in result_old.items():
            print(f"  {key}: {value}")
    else:
        print("❌ PARSING FAILED!")

if __name__ == "__main__":
    test_parser()
