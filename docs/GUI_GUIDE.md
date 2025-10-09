# 🖥️ Zebra GC420T Auto-Printer GUI

## 🚀 Quick Start

**Double-click `launch_gui.bat` to start the GUI!**

Or run manually:
```bash
python printer_gui.py
```

## 📋 GUI Features

### Main Control Tab
- **🖨️ Printer Selection** - Auto-detects your Zebra GC420T
- **📡 Serial Port Setup** - Lists available COM ports  
- **⚡ Real-time Monitoring** - Start/stop monitoring with one click
- **📊 Live Statistics** - See processed devices, successful prints, errors
- **👀 Data Preview** - Watch incoming serial data in real-time
- **🧪 Test Functions** - Test printing and data parsing

### ZPL Template Tab
- **📝 Template Editor** - Edit your ZPL template with syntax highlighting
- **💾 Load/Save Templates** - Manage multiple template files
- **🔄 Reset to Default** - Restore original template
- **📖 Placeholder Reference** - Built-in help for available placeholders

### Logs Tab
- **📜 Real-time Logging** - All system activity logged
- **💾 Save Logs** - Export logs for troubleshooting
- **🧹 Clear Logs** - Clean up display
- **📜 Auto-scroll** - Follow new log entries

### Settings Tab
- **🔍 Regex Configuration** - Customize data parsing patterns
- **🏷️ Field Mapping** - Configure field order and names
- **⚙️ Print Settings** - Auto-print options and copy count

## 🎯 How to Use

### 1. **Setup Connection**
   - Select your **Zebra GC420T** printer from the dropdown
   - Choose your **serial port** (e.g., COM6)
   - Set **baud rate** (default: 9600)

### 2. **Configure Template**
   - Go to **ZPL Template** tab
   - Your template is already loaded with placeholders:
     - `{SERIAL_NUMBER}` - Device serial number
     - `{IMEI}` - IMEI number
     - `{IMSI}` - IMSI number  
     - `{CCID}` - SIM card ID
     - `{MAC_ADDRESS}` - MAC address
     - `{STC}` - Automatically set to "6000"

### 3. **Test Everything**
   - Use **Test Print** to verify printer connection
   - Use **Test Parse & Print** with sample data
   - Default test data: `##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##`

### 4. **Start Monitoring**
   - Click **Start Monitoring**
   - Connect your device to the serial port
   - Watch labels print automatically!

## 🔧 Advanced Features

### Custom Regex Patterns
- Default pattern: `##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-F]+)\|([A-F0-9:]+)##`
- Modify in **Settings** tab for different data formats
- Test patterns with the **Test Regex** button

### Template Management
- Save templates for different device types
- Load templates from `.zpl` files
- Real-time template validation

### Monitoring Control
- **Start/Stop** monitoring anytime
- **Real-time statistics** tracking
- **Error handling** with detailed logs

## 📊 Status Indicators

- **🟢 Status: Monitoring** - Actively watching serial port
- **🔴 Status: Stopped** - Not monitoring
- **🟡 Status: Ready** - Ready to start

## 📈 Statistics Display

- **Devices Processed** - Total devices detected
- **Successful Prints** - Labels printed successfully  
- **Failed Prints** - Print failures
- **Parse Errors** - Data format errors

## 🛠️ Troubleshooting

### GUI Won't Start
```bash
# Try running directly
python printer_gui.py
```

### No Printers Found
1. Check printer is connected and powered on
2. Verify drivers are installed
3. Click **Refresh** button

### No Serial Ports
1. Check device is connected
2. Install device drivers if needed
3. Click **Refresh** button

### Data Not Parsing
1. Check data format matches expected pattern
2. Test regex in **Settings** tab
3. View detailed logs in **Logs** tab

## 💡 Tips

- **Keep GUI open** while monitoring for real-time feedback
- **Use Test functions** before starting production monitoring  
- **Save logs** for troubleshooting issues
- **Backup templates** before making changes
- **Monitor statistics** to track system performance

## 🎯 Production Workflow

1. **Launch GUI**: Double-click `launch_gui.bat`
2. **Verify Setup**: Test print and data parsing
3. **Start Monitoring**: Click Start Monitoring
4. **Monitor Operation**: Watch statistics and logs
5. **Handle Issues**: Use logs to troubleshoot problems

---

**The GUI provides a complete visual interface for your Zebra GC420T auto-printing system! 🎉**