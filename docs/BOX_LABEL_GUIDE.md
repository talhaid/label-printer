# Box Label Generator Guide

## Overview
The Box Label Generator creates 15cm x 10cm PDF labels for packaging 20 devices. Each label includes:
- Device information table (S/N, IMEI, MAC for 20 devices)
- QR code containing all device data
- Box identification and date
- Serial number range summary

## Quick Start

### Basic Usage
```python
from box_label_generator import BoxLabelGenerator

# Create generator
generator = BoxLabelGenerator()

# Generate sample devices (for testing)
devices = generator.generate_sample_devices("ATS542912923728")

# Create box label
pdf_file = generator.generate_box_label(
    devices=devices,
    box_number="001"
)

print(f"Label created: {pdf_file}")
```

### Custom Device Data
```python
# Create your own device list
devices = []
for i in range(20):
    device = {
        "SERIAL_NUMBER": f"CUSTOM{i+1:03d}",
        "IMEI": f"123456789012{i+100:03d}",
        "MAC_ADDRESS": f"AA:BB:CC:DD:EE:{i+10:02X}"
    }
    devices.append(device)

# Generate label
pdf_file = generator.generate_box_label(devices, box_number="CUSTOM001")
```

## Label Specifications

### Physical Dimensions
- **Size**: 15cm x 10cm (150mm x 100mm)
- **Margins**: 5mm all around
- **Content area**: 140mm x 90mm

### Content Layout
- **Title**: Device Box Label + Box Number
- **Header**: Date and device count
- **Table**: 20 rows with device information
- **QR Code**: 3cm x 3cm, contains all device data
- **Footer**: Serial number range

### QR Code Data Format
```
01|SERIAL1|IMEI1|MAC1
02|SERIAL2|IMEI2|MAC2
...
20|SERIAL20|IMEI20|MAC20
```

## Integration with Existing System

### Option 1: Manual Integration
```python
# After processing 20 devices in your main system
from box_label_generator import BoxLabelGenerator

def create_box_label_for_batch(device_list, box_id):
    generator = BoxLabelGenerator()
    
    # Convert your device format to box label format
    formatted_devices = []
    for device in device_list:
        formatted_device = {
            "SERIAL_NUMBER": device["serial_number"],
            "IMEI": device["imei"], 
            "MAC_ADDRESS": device["mac_address"]
        }
        formatted_devices.append(formatted_device)
    
    # Generate label
    return generator.generate_box_label(formatted_devices, box_number=box_id)
```

### Option 2: Auto-trigger After 20 Devices
```python
# Add to your main printer system
class YourPrinterSystem:
    def __init__(self):
        self.processed_devices = []
        self.box_counter = 1
        self.box_generator = BoxLabelGenerator()
    
    def process_device(self, device_data):
        # Your existing device processing
        self.processed_devices.append(device_data)
        
        # Check if we have 20 devices
        if len(self.processed_devices) >= 20:
            self.create_box_label()
    
    def create_box_label(self):
        # Take first 20 devices
        batch = self.processed_devices[:20]
        self.processed_devices = self.processed_devices[20:]
        
        # Generate box label
        box_id = f"BOX{self.box_counter:03d}"
        pdf_file = self.box_generator.generate_box_label(batch, box_number=box_id)
        
        print(f"📦 Box label created: {pdf_file}")
        self.box_counter += 1
```

## File Organization

### Generated Files
- `box_label_[FIRST_SERIAL]_[LAST_SERIAL]_[TIMESTAMP].pdf`
- Example: `box_label_ATS542912923701_ATS542912923720_20250826_104552.pdf`

### Recommended Folder Structure
```
your_project/
├── box_labels/           # Store generated box labels
├── device_labels/        # Individual device labels (existing)
├── pcb_labels/          # PCB labels (existing)
└── box_label_generator.py
```

## Error Handling

### Common Issues
1. **Wrong device count**: Must have exactly 20 devices
2. **Missing data**: All devices must have SERIAL_NUMBER, IMEI, MAC_ADDRESS
3. **File permissions**: Ensure write access to output directory

### Validation Example
```python
def validate_devices(devices):
    if len(devices) != 20:
        raise ValueError(f"Expected 20 devices, got {len(devices)}")
    
    required_fields = ["SERIAL_NUMBER", "IMEI", "MAC_ADDRESS"]
    for i, device in enumerate(devices):
        for field in required_fields:
            if field not in device or not device[field]:
                raise ValueError(f"Device {i+1} missing {field}")
    
    return True
```

## Testing

### Run Tests
```bash
# Test with sample data
python box_label_generator.py

# Test multiple scenarios
python test_box_labels.py
```

### Manual Testing
1. Generate a sample label
2. Print to PDF printer
3. Verify dimensions (15cm x 10cm)
4. Check QR code readability
5. Validate all device data is present

## Dependencies
- `reportlab`: PDF generation
- `qrcode[pil]`: QR code generation
- `pillow`: Image processing

Install with:
```bash
pip install reportlab qrcode[pil] pillow
```