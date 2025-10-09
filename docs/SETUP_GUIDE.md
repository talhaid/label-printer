# Device Auto-Printer Setup Guide

## 🚀 Quick Start

Your serial auto-printer system is ready! Here's how to use it:

### 1. Test with Sample Data (Current Working Example)
```bash
python serial_auto_printer.py --test-data "##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##"
```

### 2. Start Auto-Printing from Serial Port
```bash
# List available serial ports first
python serial_auto_printer.py --list-ports

# Start monitoring (replace COM6 with your port)
python serial_auto_printer.py --port COM6
```

### 3. Advanced Usage
```bash
# Use custom baud rate
python serial_auto_printer.py --port COM6 --baudrate 115200

# Use specific printer
python serial_auto_printer.py --port COM6 --printer "ZDesigner GC420t (EPL)"

# Use custom template file
python serial_auto_printer.py --port COM6 --template-file my_template.zpl
```

## 📋 Data Format

The system expects data in this format:
```
##SERIAL_NUMBER|IMEI|IMSI|CCID|MAC_ADDRESS##
```

**Example:**
```
##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##
```

**Field Mapping:**
- `SERIAL_NUMBER`: Device serial number (e.g., ATS542912923728)
- `IMEI`: International Mobile Equipment Identity (15 digits)
- `IMSI`: International Mobile Subscriber Identity (15 digits)  
- `CCID`: Integrated Circuit Card Identifier (SIM card ID)
- `MAC_ADDRESS`: MAC address in format AA:BB:CC:DD:EE:FF
- `STC`: Automatically set to "6000" (as you specified)

## 🏷️ ZPL Template

Your current template includes:
- **QR Code** with all device information
- **Text fields** for each data point
- **STC value** defaulted to 6000
- **Formatted layout** optimized for your label size

The template uses placeholders like `{SERIAL_NUMBER}`, `{IMEI}`, etc. that get automatically replaced with actual device data.

## 🔧 System Components

### Files Created:
- `serial_auto_printer.py` - Main auto-printer system
- `zebra_zpl.py` - ZPL printing module  
- `device_label_template.zpl` - Your ZPL template
- `zpl_examples.py` - Interactive examples
- `requirements.txt` - Dependencies

### Key Features:
- ✅ **Automatic serial port monitoring**
- ✅ **Real-time data parsing with regex**
- ✅ **Template-based label generation**
- ✅ **Error handling and logging**
- ✅ **Statistics tracking**
- ✅ **Multi-threaded operation**

## 📊 Monitoring & Logs

The system creates a log file `device_printer.log` with:
- Received serial data
- Parsing results
- Print job status
- Error messages
- Performance statistics

## 🛠️ Troubleshooting

### No Serial Data Received
1. Check serial port connection
2. Verify baud rate (default: 9600)
3. Ensure data format matches expected pattern

### Printing Issues
1. Check printer is online: `python serial_auto_printer.py --list-printers`
2. Test manual printing: `python zebra_zpl.py --text "TEST" "Hello"`
3. Verify ZPL template syntax

### Parse Errors
1. Check data format matches: `##FIELD1|FIELD2|FIELD3|FIELD4|FIELD5##`
2. View log file for detailed error messages
3. Test with known good data using `--test-data`

## 🎯 Next Steps

1. **Connect your serial device** to an available COM port
2. **Start the monitor**: `python serial_auto_printer.py --port COMX`
3. **Send test data** from your device
4. **Watch labels print automatically!**

The system will run continuously, printing a label for each device data packet received on the serial port.

---

**Status: ✅ Ready for Production Use**