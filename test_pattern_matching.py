#!/usr/bin/env python3
"""
Test script for enhanced pattern matching in DeviceDataParser.
Tests various data formats that might be encountered.
"""

import sys
import os

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from serial_auto_printer import DeviceDataParser

def test_pattern_matching():
    """Test the enhanced pattern matching with various data formats."""
    parser = DeviceDataParser()
    
    # Test cases with different data formats
    test_cases = [
        # Original working format (should now remove ATS prefix)
        "##ATS986063608048|867315088718139|286016570186236 |8990011418220012368F|24:5D:F9:7D:78:50##",
        
        # Company side format (numeric only)
        "##986063608048|867315088718139|286016570186236 |8990011418220012368F|24:5D:F9:7D:78:50##",
        
        # Format with extra spaces
        "##612165404520|866988074129817|286016570017900  |8990011419260179000F|B8:46:52:25:67:68##",
        
        # Format without double ## delimiters
        "ATS986063608048|867315088718139|286016570186236|8990011418220012368F|24:5D:F9:7D:78:50",
        
        # Format with single # delimiters
        "#986063608048|867315088718139|286016570186236|8990011418220012368F|24:5D:F9:7D:78:50#",
        
        # Format with comma separators
        "##986063608048,867315088718139,286016570186236,8990011418220012368F,24:5D:F9:7D:78:50##",
        
        # Format with line ending characters
        "##986063608048|867315088718139|286016570186236|8990011418220012368F|24:5D:F9:7D:78:50##\r\n",
        
        # Invalid format (should fail)
        "invalid data format",
        
        # Incomplete format (should fail)
        "##986063608048|867315088718139##",
    ]
    
    print("Testing Enhanced DeviceDataParser Pattern Matching")
    print("=" * 60)
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {repr(test_data)}")
        
        result = parser.parse_data(test_data)
        
        if result:
            print("✅ PARSED SUCCESSFULLY")
            for key, value in result.items():
                if key != 'TIMESTAMP':  # Skip timestamp for cleaner output
                    print(f"  {key}: {value}")
        else:
            print("❌ PARSING FAILED")
    
    print("\n" + "=" * 60)
    print("Testing completed. Check the log output above for detailed parsing information.")

if __name__ == "__main__":
    test_pattern_matching()