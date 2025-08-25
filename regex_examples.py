#!/usr/bin/env python3
"""
Regex Pattern Examples and Customization Guide
==============================================

This file shows how the regex patterns work in the serial auto-printer
and provides examples for different data formats.
"""

import re
from typing import Dict, Optional

# Current regex pattern being used
CURRENT_PATTERN = r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-F]+)\|([A-F0-9:]+)##'

def test_regex_patterns():
    """Test various regex patterns with sample data."""
    
    print("🔍 Regex Pattern Testing")
    print("=" * 50)
    
    # Sample data
    sample_data = "##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##"
    
    print(f"Sample Data: {sample_data}")
    print()
    
    # Current pattern breakdown
    print("📋 Current Pattern Breakdown:")
    print(f"Pattern: {CURRENT_PATTERN}")
    print()
    print("Pattern Components:")
    print("##                    - Literal start marker")
    print("([A-Z0-9]+)          - Group 1: Serial Number (alphanumeric)")
    print("\\|                   - Literal pipe separator")
    print("([0-9]+)             - Group 2: IMEI (digits only)")
    print("\\|                   - Literal pipe separator") 
    print("([0-9]+)             - Group 3: IMSI (digits only)")
    print("\\|                   - Literal pipe separator")
    print("([0-9A-F]+)          - Group 4: CCID (hex digits)")
    print("\\|                   - Literal pipe separator")
    print("([A-F0-9:]+)         - Group 5: MAC Address (hex with colons)")
    print("##                    - Literal end marker")
    print()
    
    # Test current pattern
    pattern = re.compile(CURRENT_PATTERN)
    match = pattern.search(sample_data)
    
    if match:
        print("✅ Current Pattern Match:")
        groups = match.groups()
        field_names = ['SERIAL_NUMBER', 'IMEI', 'IMSI', 'CCID', 'MAC_ADDRESS']
        
        for i, (field, value) in enumerate(zip(field_names, groups)):
            print(f"  {field}: {value}")
    else:
        print("❌ Current pattern did not match!")
    
    print()


def demo_alternative_patterns():
    """Demonstrate alternative regex patterns for different data formats."""
    
    print("🔧 Alternative Regex Patterns")
    print("=" * 50)
    
    # Pattern variations
    patterns = {
        "More flexible MAC": {
            "pattern": r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-F]+)\|([A-Fa-f0-9:-]+)##',
            "description": "Allows lowercase hex and hyphens in MAC address",
            "sample": "##ATS542912923728|866988074133496|286019876543210|8991101200003204510|aa-bb-cc-dd-ee-ff##"
        },
        "Case insensitive": {
            "pattern": r'##([A-Za-z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-Fa-f]+)\|([A-Fa-f0-9:]+)##',
            "description": "Allows lowercase letters in serial and hex fields",
            "sample": "##ats542912923728|866988074133496|286019876543210|8991101200003204510|aa:bb:cc:dd:ee:ff##"
        },
        "Optional spaces": {
            "pattern": r'##\s*([A-Z0-9]+)\s*\|\s*([0-9]+)\s*\|\s*([0-9]+)\s*\|\s*([0-9A-F]+)\s*\|\s*([A-F0-9:]+)\s*##',
            "description": "Allows optional whitespace around fields",
            "sample": "## ATS542912923728 | 866988074133496 | 286019876543210 | 8991101200003204510 | AA:BB:CC:DD:EE:FF ##"
        },
        "Named groups": {
            "pattern": r'##(?P<serial>[A-Z0-9]+)\|(?P<imei>[0-9]+)\|(?P<imsi>[0-9]+)\|(?P<ccid>[0-9A-F]+)\|(?P<mac>[A-F0-9:]+)##',
            "description": "Uses named groups for clearer code",
            "sample": "##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##"
        },
        "Multiline support": {
            "pattern": r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-F]+)\|([A-F0-9:]+)##',
            "description": "Standard pattern with multiline flag",
            "sample": "Some other data\n##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##\nMore data"
        }
    }
    
    for name, info in patterns.items():
        print(f"🔸 {name}:")
        print(f"  Pattern: {info['pattern']}")
        print(f"  Description: {info['description']}")
        print(f"  Sample: {info['sample']}")
        
        # Test the pattern
        try:
            pattern = re.compile(info['pattern'])
            match = pattern.search(info['sample'])
            if match:
                if 'serial' in match.groupdict():  # Named groups
                    print(f"  ✅ Match: {match.groupdict()}")
                else:  # Numbered groups
                    print(f"  ✅ Match: {match.groups()}")
            else:
                print(f"  ❌ No match")
        except re.error as e:
            print(f"  ❌ Pattern error: {e}")
        
        print()


def demo_custom_validation():
    """Show how to add custom validation with regex."""
    
    print("✅ Custom Validation Examples")
    print("=" * 50)
    
    validation_patterns = {
        "IMEI validation": {
            "pattern": r'^[0-9]{15}$',
            "description": "Exactly 15 digits",
            "valid": ["866988074133496"],
            "invalid": ["86698807413349", "866988074133496a", "866988074133496-"]
        },
        "MAC validation": {
            "pattern": r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$',
            "description": "Standard MAC format XX:XX:XX:XX:XX:XX",
            "valid": ["AA:BB:CC:DD:EE:FF", "00:11:22:33:44:55"],
            "invalid": ["AA-BB-CC-DD-EE-FF", "AA:BB:CC:DD:EE", "aa:bb:cc:dd:ee:ff"]
        },
        "Serial Number validation": {
            "pattern": r'^[A-Z]{3}[0-9]{12}$',
            "description": "3 letters followed by 12 digits",
            "valid": ["ATS542912923728"],
            "invalid": ["ATS54291292372", "ats542912923728", "AT542912923728"]
        }
    }
    
    for name, info in validation_patterns.items():
        print(f"🔸 {name}:")
        print(f"  Pattern: {info['pattern']}")
        print(f"  Description: {info['description']}")
        
        pattern = re.compile(info['pattern'])
        
        print("  Valid examples:")
        for example in info['valid']:
            match = pattern.match(example)
            status = "✅" if match else "❌"
            print(f"    {status} '{example}'")
        
        print("  Invalid examples:")
        for example in info['invalid']:
            match = pattern.match(example)
            status = "❌" if not match else "✅ (unexpected)"
            print(f"    {status} '{example}'")
        
        print()


def demo_advanced_parsing():
    """Demonstrate advanced parsing techniques."""
    
    print("🚀 Advanced Parsing Techniques")
    print("=" * 50)
    
    # Example of parsing with error recovery
    def robust_parse(data: str) -> Optional[Dict[str, str]]:
        """Parse with multiple pattern attempts and validation."""
        
        patterns = [
            # Primary pattern (current)
            r'##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-F]+)\|([A-F0-9:]+)##',
            # Fallback with case insensitive
            r'##([A-Za-z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-Fa-f]+)\|([A-Fa-f0-9:]+)##',
            # Fallback with optional spaces
            r'##\s*([A-Za-z0-9]+)\s*\|\s*([0-9]+)\s*\|\s*([0-9]+)\s*\|\s*([0-9A-Fa-f]+)\s*\|\s*([A-Fa-f0-9:]+)\s*##'
        ]
        
        field_names = ['SERIAL_NUMBER', 'IMEI', 'IMSI', 'CCID', 'MAC_ADDRESS']
        
        for i, pattern_str in enumerate(patterns):
            pattern = re.compile(pattern_str, re.IGNORECASE)
            match = pattern.search(data)
            
            if match:
                print(f"  ✅ Matched with pattern {i+1}")
                result = {}
                groups = match.groups()
                
                for field, value in zip(field_names, groups):
                    # Clean and validate each field
                    cleaned_value = value.strip().upper()
                    result[field] = cleaned_value
                
                return result
        
        print(f"  ❌ No pattern matched")
        return None
    
    # Test with various data formats
    test_cases = [
        "##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##",
        "##ats542912923728|866988074133496|286019876543210|8991101200003204510|aa:bb:cc:dd:ee:ff##",
        "## ATS542912923728 | 866988074133496 | 286019876543210 | 8991101200003204510 | AA:BB:CC:DD:EE:FF ##",
        "##INVALID|DATA|FORMAT##"
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_data}")
        result = robust_parse(test_data)
        if result:
            for field, value in result.items():
                print(f"    {field}: {value}")
        print()


def show_regex_tips():
    """Show regex tips and best practices."""
    
    print("💡 Regex Tips & Best Practices")
    print("=" * 50)
    
    tips = [
        "Use raw strings (r'pattern') to avoid escaping issues",
        "Compile patterns once and reuse for better performance", 
        "Use named groups (?P<name>) for clearer code",
        "Add the re.IGNORECASE flag for case-insensitive matching",
        "Use ^ and $ anchors to match entire strings",
        "Test patterns with various input samples",
        "Consider using re.VERBOSE for complex patterns with comments",
        "Use character classes [A-Z0-9] instead of multiple alternatives",
        "Escape special characters with backslash: \\| \\. \\+ \\* \\?",
        "Use quantifiers wisely: + (one or more), * (zero or more), {n} (exactly n)"
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"{i:2d}. {tip}")
    
    print()
    print("🔗 Useful Regex Resources:")
    print("  - regex101.com (online regex tester)")
    print("  - regexr.com (another great tester)")
    print("  - Python re module documentation")


def main():
    """Run all regex demonstrations."""
    print("🧪 Regex Patterns for Serial Auto-Printer")
    print("=" * 60)
    print()
    
    test_regex_patterns()
    demo_alternative_patterns()
    demo_custom_validation()
    demo_advanced_parsing()
    show_regex_tips()
    
    print("🎯 Summary:")
    print("Your current regex pattern is working perfectly!")
    print("Use the examples above to customize for different data formats.")
    print("The serial_auto_printer.py already implements robust regex parsing.")


if __name__ == "__main__":
    main()