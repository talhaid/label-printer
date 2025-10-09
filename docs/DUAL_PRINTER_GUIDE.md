# Dual-Printer System Guide - Zebra GC420T + XPrinter XP-470B

## Overview
Your system now supports **dual-printer operation** with simultaneous printing on both Zebra GC420T (main device labels) and XPrinter XP-470B (PCB labels). This enables complete device tracking with two different label types.

## Printer Configuration

### Zebra GC420T (Device Labels)
- **Purpose**: Main device labels with complete information
- **Content**: STC, Serial Number, IMEI, IMSI, CCID, MAC Address
- **Label Size**: Standard device label format
- **QR Code**: Contains all device data for scanning

### XPrinter XP-470B (PCB Labels)  
- **Purpose**: Simple PCB labels with serial number only
- **Content**: Serial Number (for PCB identification)
- **Label Size**: 4cm x 2cm (small PCB label)
- **Format**: Simple text-based label

## GUI Features

### Dual Table Display
The GUI now features **two separate tabs** for monitoring both types of labels:

#### Device Labels Tab (Zebra)
- **Columns**: STC, Serial, IMEI, IMSI, CCID, MAC, Status, Time
- **Status Values**: 
  - `Printed` - Device label printed successfully
  - `Queued` - Device waiting in queue mode
  - `Failed` - Device label printing failed

#### PCB Labels Tab (XPrinter)
- **Columns**: Serial, PCB Status, Time, Device STC
- **Status Values**:
  - `Printed` - PCB label printed successfully  
  - `Failed` - PCB label printing failed
- **Reference**: Device STC links PCB to main device label

### PCB Control Features
- **Enable/Disable**: Toggle PCB printing on/off
- **Test Function**: Test PCB printer connectivity
- **Clear Log**: Clear PCB printing history
- **Status Indicator**: Real-time PCB printing status

## Operational Modes

### Auto-Print Mode (Both Printers)
When device data is received:
1. **Parse Data**: Extract device information from serial data
2. **Assign STC**: Generate sequential tracking number
3. **Print Device Label**: Send full label to Zebra GC420T
4. **Print PCB Label**: Send serial number to XPrinter XP-470B
5. **Update Tables**: Add entries to both device and PCB tables
6. **Log Results**: Record success/failure for both prints

### Queue Mode (Both Printers)
When device data is received:
1. **Parse Data**: Extract device information 
2. **Queue Device**: Add to pending devices list
3. **Manual Control**: User decides when to print
4. **Dual Printing**: Both labels print when triggered
5. **Status Tracking**: Monitor both print operations

## Label Synchronization

### Matching System
- **Device STC**: Primary identifier for device labels
- **PCB Reference**: PCB table shows corresponding device STC
- **Time Correlation**: Both tables show print timestamps
- **Status Comparison**: Compare success/failure across printers

### Workflow Example
```
Device: ATS123456789
1. Device Label (Zebra): STC 6001, Full Info → SUCCESS
2. PCB Label (XPrinter): Serial ATS123456789 → SUCCESS
3. Tables Updated: Both show successful print at same timestamp
```

## Print Status Combinations

### Success Scenarios
- **`SUCCESS_WITH_PCB`**: Both device and PCB labels printed successfully
- **Device: Printed, PCB: Printed**: Perfect dual-print operation

### Partial Success
- **`SUCCESS_PCB_FAILED`**: Device label printed, PCB label failed
- **Device: Printed, PCB: Failed**: Main label available, PCB missing

### Failure Scenarios
- **`PRINT_FAILED`**: Device label failed (PCB may succeed independently)
- **Device: Failed, PCB: Failed**: Complete printing failure

## Quality Control Features

### Comparison View
- **Side-by-Side Tables**: Compare device and PCB printing results
- **Status Correlation**: Identify mismatched print results
- **Time Synchronization**: Verify simultaneous printing
- **STC Linking**: Connect PCB labels to device records

### Troubleshooting
- **Missing PCB Labels**: Check XPrinter status and connectivity
- **Partial Failures**: Review individual printer error logs
- **Sync Issues**: Verify both printers are responding correctly

## Statistics Tracking

### Device Statistics (Existing)
- Devices Processed
- Successful Prints
- Failed Prints
- Parse Errors

### PCB Statistics (New)
- PCB Prints Attempted
- PCB Prints Successful  
- PCB Prints Failed
- PCB Success Rate

## Configuration Options

### PCB Printing Control
```python
# Enable/disable PCB printing
auto_printer.enable_pcb_printing(True)  # Enable
auto_printer.enable_pcb_printing(False) # Disable

# Check PCB printer availability
is_available = auto_printer.is_pcb_printer_available()

# Test PCB printer
success = auto_printer.test_pcb_printer()
```

### Print Status Monitoring
```python
# Get PCB statistics
pcb_stats = auto_printer.get_pcb_stats()
print(f"PCB Success Rate: {pcb_stats['pcb_prints_successful']}/{pcb_stats['pcb_prints_attempted']}")
```

## File Outputs

### Device Labels
- **ZPL Files**: Full device label data saved to `zpl_outputs/`
- **CSV Logging**: Complete device records in `device_log.csv`

### PCB Labels
- **ESC/POS Commands**: Simple text commands for XPrinter
- **Table Logging**: PCB print history in GUI tables
- **Status Correlation**: PCB results linked to device STC

## Troubleshooting Guide

### Common Issues

#### XPrinter Not Found
```
Error: XPrinter XP-470B not found
Solution: Check printer connection and driver installation
```

#### PCB Printing Disabled
```
Status: PCB Printing: Disabled
Solution: Click "Enable PCB Printing" button
```

#### Partial Print Success
```
Device: SUCCESS, PCB: FAILED
Solution: Check XPrinter paper, connection, and power
```

### Diagnostic Steps
1. **Test Both Printers**: Use test print functions
2. **Check Status Indicators**: Verify printer availability
3. **Review Print Logs**: Check for error messages
4. **Compare Tables**: Identify missing entries

## Production Benefits

### Complete Traceability
- **Device Labels**: Full information for quality control
- **PCB Labels**: Simple identification for assembly
- **Linked Records**: Complete tracking from device to PCB

### Quality Assurance
- **Dual Verification**: Two labels confirm device processing
- **Error Detection**: Identify single-printer failures
- **Process Monitoring**: Real-time status of both operations

### Operational Efficiency
- **Simultaneous Printing**: No additional time for PCB labels
- **Automatic Correlation**: STC links maintain relationships
- **Centralized Control**: Single interface for dual printers

## Example Workflow

### Complete Device Processing
1. **Device Connected**: Serial data received
2. **Data Parsed**: Extract device information
3. **STC Assigned**: Sequential tracking number (e.g., 6001)
4. **Device Label Printed**: Full label on Zebra GC420T
5. **PCB Label Printed**: Serial number on XPrinter XP-470B
6. **Tables Updated**: 
   - Device table: STC 6001, Full data, Status: Printed
   - PCB table: Serial number, Status: Printed, Device STC: 6001
7. **Files Saved**: ZPL file and CSV log entry created

Your dual-printer system provides comprehensive device labeling with full traceability and quality control capabilities!