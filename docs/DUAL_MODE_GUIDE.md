# Dual-Mode Printing System Guide

## Overview
Your Zebra GC420T printer system now supports **dual-mode operation** with a unified data table display and default connection settings.

## Operating Modes

### 1. Auto-Print Mode (Default)
- **Behavior**: Automatically prints labels as soon as device data is received
- **Data Table**: Shows recently printed devices with "Printed" status
- **STC Assignment**: Automatic incremental assignment starting from CSV history
- **Controls**: No manual print buttons (automatic operation)

### 2. Queue Mode
- **Behavior**: Receives device data and adds to queue for manual review/printing
- **Data Table**: Shows pending devices with "Queued" status
- **STC Assignment**: Pre-assigned but can be modified before printing
- **Controls**: Manual print buttons available (Print Selected, Print All, etc.)

## Key Features

### Default Connection Settings
- **Port**: COM3 (automatically selected)
- **Baud Rate**: 115200 (automatically set)
- **Mode**: Auto-Print (default selection)

### Unified Data Table
- **Displays in both modes**: Shows device information regardless of operating mode
- **Columns**: STC, Serial Number, IMEI, IMSI, CCID, MAC Address, Status, Time
- **Status Column**: 
  - Auto-Print Mode: Shows "Printed" for processed devices
  - Queue Mode: Shows "Queued" for pending devices
- **Capacity**: Keeps last 100 entries to prevent memory issues
- **Sorting**: Most recent entries appear at the top

### STC Management
- **CSV-Based Persistence**: Reads existing CSV history to continue STC numbering
- **Auto-Increment**: Each device gets the next available STC number
- **Cross-Mode Consistency**: STC numbering continues seamlessly between modes

## Usage Instructions

### Starting the System
1. Launch the GUI: `python printer_gui.py` or double-click `launch_gui.bat`
2. Select operating mode (Auto-Print is default)
3. Click "Start Monitoring" (COM3 and 115200 baud are pre-selected)

### Switching Between Modes
1. **While Monitoring**: Stop monitoring first, then change mode
2. **Radio Buttons**: Use "Auto Print" or "Queue Mode" selection
3. **Data Persistence**: Data table continues to show information across mode switches

### Auto-Print Mode Operation
1. Connect device to serial port
2. System automatically detects, parses, and prints device data
3. Watch the data table populate with "Printed" status
4. Monitor statistics and logs in real-time

### Queue Mode Operation
1. Connect device to serial port
2. System receives and queues device data with "Queued" status
3. Review queued devices in the data table
4. Use manual controls:
   - **Print Selected**: Print highlighted device
   - **Print All**: Print all queued devices
   - **Remove Selected**: Remove device from queue
   - **Clear Queue**: Clear all pending devices

## File Outputs

### ZPL Files
- **Location**: `zpl_outputs/` folder
- **Format**: `SERIALNUMBER_YYYYMMDD_HHMMSS.zpl`
- **Content**: Raw ZPL commands sent to printer

### CSV Log
- **File**: `device_log.csv`
- **Purpose**: Complete audit trail of all processed devices
- **STC Persistence**: Used to maintain STC continuity across sessions

## Troubleshooting

### Common Issues
1. **CSV Permission Errors**: Close Excel/CSV file before running system
2. **Port Not Available**: Check if another application is using COM3
3. **Printer Not Found**: Ensure Zebra GC420T is connected and drivers installed

### Data Table Not Updating
- Check that monitoring is active (green status)
- Verify correct serial data format: `##SERIAL|IMEI|IMSI|CCID|MAC##`
- Check logs tab for parsing errors

### Mode Switching Issues
- Always stop monitoring before changing modes
- Allow GUI to update before starting new monitoring session

## Technical Details

### Serial Data Format
```
##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##
```

### Data Table Updates
- **Auto-Print Mode**: Updates immediately when device is printed
- **Queue Mode**: Updates when device is added to queue
- **Cross-Mode**: Table persists data when switching modes

### STC Assignment Logic
1. Read existing CSV file for latest STC number
2. Increment from highest found STC
3. Assign sequential numbers for new devices
4. Maintain continuity across application restarts

## Success Indicators
- ✅ Device data appears in table with correct status
- ✅ STC numbers increment properly
- ✅ ZPL files created in outputs folder
- ✅ Printer produces physical labels
- ✅ Statistics update in real-time
- ✅ Mode switching works without data loss

Your dual-mode system is now ready for production use with both automatic and manual printing workflows!