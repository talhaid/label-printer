# Zebra Printer System - Enhanced Version with Debug Tools

## Version: Enhanced with Multiple Pattern Support & Debugging

### Recent Improvements (October 15, 2025)

#### 1. Enhanced Pattern Matching
- **Multiple Pattern Support**: Now handles various data formats from different systems
- **Backup Patterns**: If primary pattern fails, tries alternative formats
- **Flexible Delimiters**: Supports ##data##, #data#, and data without delimiters
- **Multiple Separators**: Handles both pipe (|) and comma (,) separators
- **Auto ATS Prefix**: Automatically adds "ATS" prefix if missing from serial numbers

#### 2. Improved Serial Monitoring
- **Enhanced Buffering**: Better handling of incomplete data transmission
- **Timeout Processing**: Processes data even without proper line endings
- **Multiple Line Endings**: Handles \n, \r\n, and \r line endings
- **Debug Logging**: Detailed logging of received data for troubleshooting

#### 3. Debug Tools Created

##### A. debug_serial_monitor.py
**Purpose**: Comprehensive serial communication debugging
**Features**:
- Tests multiple baud rates (9600, 19200, 38400, 57600, 115200)
- Raw data monitoring with hex and ASCII output
- Regex pattern testing with real data
- Live data analysis and validation
- Comprehensive logging for remote troubleshooting

**Usage**:
```bash
python debug_serial_monitor.py
```

##### B. test_pattern_matching.py
**Purpose**: Test enhanced pattern matching with various data formats
**Features**:
- Tests 9 different data format scenarios
- Validates parser flexibility
- Shows which patterns work with current implementation

**Usage**:
```bash
python test_pattern_matching.py
```

### Supported Data Formats

The system now handles these data formats:

1. **Original Format** (with ATS prefix):
   ```
   ##ATS986063608048|867315088718139|286016570186236|8990011418220012368F|24:5D:F9:7D:78:50##
   ```

2. **Numeric Serial Format** (auto-adds ATS):
   ```
   ##986063608048|867315088718139|286016570186236|8990011418220012368F|24:5D:F9:7D:78:50##
   ```

3. **Without Double Delimiters**:
   ```
   986063608048|867315088718139|286016570186236|8990011418220012368F|24:5D:F9:7D:78:50
   ```

4. **Single Delimiter**:
   ```
   #986063608048|867315088718139|286016570186236|8990011418220012368F|24:5D:F9:7D:78:50#
   ```

5. **Comma Separated**:
   ```
   ##986063608048,867315088718139,286016570186236,8990011418220012368F,24:5D:F9:7D:78:50##
   ```

6. **With Extra Spaces** (automatically cleaned):
   ```
   ##612165404520|866988074129817|286016570017900  |8990011419260179000F|B8:46:52:25:67:68##
   ```

### Troubleshooting Guide

#### If Automatic Printing Isn't Working:

1. **Check Mode Selection**:
   - Ensure "Auto Print" mode is selected in the GUI
   - "Queue Mode" requires manual printing via buttons

2. **Verify Serial Connection**:
   - Use debug_serial_monitor.py to check data reception
   - Test different baud rates (default: 115200)
   - Verify COM port selection

3. **Test Pattern Matching**:
   - Use test_pattern_matching.py to verify data formats
   - Check log output for parsing errors
   - Compare expected vs. actual data format

4. **Debug Steps for Company Side**:
   ```bash
   # Step 1: Run debug monitor
   python debug_serial_monitor.py
   
   # Step 2: Select correct COM port
   # Step 3: Test different baud rates
   # Step 4: Observe raw data output
   # Step 5: Check pattern matching results
   ```

### File Structure (Minimal Essential)

```
printertest/
├── ZebraPrinterGUI.exe          # Main executable (42MB)
├── printer_gui.py               # GUI application
├── serial_auto_printer.py       # Core printing logic (enhanced)
├── zebra_zpl.py                 # ZPL commands (with debug mode)
├── zebra_printer.py             # Printer management
├── debug_serial_monitor.py      # Serial debugging tool
├── test_pattern_matching.py     # Pattern testing tool
├── requirements.txt             # Python dependencies
├── templates/
│   ├── device_label_template.zpl
│   └── manual_box_label_template.html
└── save/
    ├── csv/                     # CSV logs
    ├── zpl_outputs/            # ZPL files
    └── backups/                # Label backups
```

### Remote Debugging Procedure

When system works locally but not on company side:

1. **Copy debug tools** to company computer:
   - debug_serial_monitor.py
   - test_pattern_matching.py

2. **Run serial debug monitor** on company system:
   ```bash
   python debug_serial_monitor.py
   ```

3. **Collect debug information**:
   - Raw serial data samples
   - Baud rate that works
   - Pattern matching results
   - Any error messages

4. **Compare with working system**:
   - Data format differences
   - Serial settings variations
   - Pattern recognition issues

### Technical Specifications

- **Python Version**: 3.11+
- **Printer**: Zebra GC420T (or compatible)
- **Communication**: Serial (115200 baud default)
- **Label Format**: ZPL commands
- **GUI Framework**: tkinter
- **Data Fields**: Serial Number, IMEI, IMSI, CCID, MAC Address
- **Executable Size**: 42.0 MB

### Support Contact

For additional support or custom modifications, provide:
1. Debug output from debug_serial_monitor.py
2. Sample raw data from the failing system
3. Current system configuration (OS, Python version, serial settings)
4. Screenshots of any error messages

This enhanced version should handle most data format variations and provide comprehensive debugging capabilities for remote troubleshooting.