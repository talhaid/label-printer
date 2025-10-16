#!/usr/bin/env python3
"""
🎯 Quick TSPL Templates for XPrinter PCB Testing
Various tested templates for different layouts and sizes
"""

# Template 1: Small and Compact (for fitting long serial numbers)
SMALL_COMPACT = """SIZE 40 mm, 20 mm
GAP 0 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 20, 15, "1", 0, 1, 1, "{serial_number}"
TEXT 20, 50, "1", 0, 1, 1, "STC:{stc}"
PRINT 1, 1
"""

# Template 2: Serial Bottom (as requested)
SERIAL_BOTTOM = """SIZE 40 mm, 20 mm
GAP 0 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 15, 20, "2", 0, 1, 1, "STC:{stc}"
TEXT 15, 55, "1", 0, 1, 1, "{serial_number}"
PRINT 1, 1
"""

# Template 3: Ultra Compact (very small fonts)
ULTRA_COMPACT = """SIZE 40 mm, 20 mm
GAP 0 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 10, 10, "1", 0, 1, 1, "{serial_number}"
TEXT 10, 35, "1", 0, 1, 1, "STC:{stc}"
PRINT 1, 1
"""

# Template 4: Medium Balanced
MEDIUM_BALANCED = """SIZE 40 mm, 20 mm
GAP 0 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 25, 25, "2", 0, 1, 1, "{serial_number}"
TEXT 25, 55, "2", 0, 1, 1, "STC:{stc}"
PRINT 1, 1
"""

# Template 5: Stacked Layout (vertical)
STACKED_LAYOUT = """SIZE 40 mm, 20 mm
GAP 0 mm, 0 mm
DIRECTION 1
REFERENCE 0, 0
OFFSET 0 mm
SET PEEL OFF
SET CUTTER OFF
SET PARTIAL_CUTTER OFF
SET TEAR ON
CLEAR
TEXT 30, 20, "2", 0, 1, 1, "{serial_number}"
TEXT 30, 45, "1", 0, 1, 1, "STC:{stc}"
PRINT 1, 1
"""

def get_all_templates():
    """Return all available templates"""
    return {
        "Small Compact": SMALL_COMPACT,
        "Serial Bottom": SERIAL_BOTTOM,
        "Ultra Compact": ULTRA_COMPACT,
        "Medium Balanced": MEDIUM_BALANCED,
        "Stacked Layout": STACKED_LAYOUT
    }

def test_template(template_name, serial_number="66182844496", stc="60000"):
    """Test a specific template with data"""
    templates = get_all_templates()
    
    if template_name not in templates:
        print(f"❌ Template '{template_name}' not found!")
        print(f"Available templates: {list(templates.keys())}")
        return None
    
    template = templates[template_name]
    return template.format(serial_number=serial_number, stc=stc)

if __name__ == "__main__":
    print("🎯 TSPL Template Collection")
    print("="*50)
    
    templates = get_all_templates()
    
    for name, template in templates.items():
        print(f"\n📋 {name}:")
        print("-" * 30)
        filled = test_template(name)
        print(filled)
        print()
        
    print("💡 Use these templates in the XPrinter PCB Studio!")
    print("   Just copy and paste the TSPL commands.")