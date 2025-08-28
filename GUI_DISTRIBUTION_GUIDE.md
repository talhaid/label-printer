# Zebra Printer GUI - Distribution Guide

## 📦 What Was Created

Your standalone executable has been successfully built! Here's what you have:

- **Main executable**: `dist/ZebraPrinterGUI.exe` (42.0 MB)
- **Supporting files** in the `dist` folder:
  - `device_label_template.zpl` - ZPL template for labels
  - `device_log.csv` - Device logging file
  - `cleaned_devices.csv` - Clean device data

## 🚀 How to Distribute

### For Distribution to Other Windows PCs:

1. **Copy the entire `dist` folder** to a USB drive or upload to cloud storage
2. On the target computer, copy the `dist` folder to any location (e.g., Desktop, Program Files)
3. Double-click `ZebraPrinterGUI.exe` to run the application

### Requirements on Target Computer:

- **Windows 7 or later** (Windows 10/11 recommended)
- **Zebra printer drivers** if using Zebra printers
- **No Python installation required** - everything is bundled!

## 🎯 What the GUI Does

The Zebra Printer GUI provides:

- **Serial Port Monitoring**: Automatically detects and monitors serial ports
- **Real-time Printer Status**: Shows printer connection and status
- **Live Data Preview**: Preview incoming device data before printing
- **Manual Test Printing**: Test print functionality
- **Template Management**: Customize ZPL label templates
- **Statistics and Logging**: Track printing statistics and logs
- **Easy Configuration**: User-friendly setup and configuration

## 🔧 Troubleshooting

### If the EXE doesn't start:

1. **Check antivirus**: Some antivirus software may block the executable
2. **Run as administrator**: Right-click and "Run as administrator"
3. **Check Windows Defender**: Add the folder to exclusions if needed

### If printer is not detected:

1. **Install printer drivers**: Make sure Zebra printer drivers are installed
2. **Check USB connection**: Ensure printer is connected and powered on
3. **Check Windows Device Manager**: Verify printer shows up in COM ports

### If serial port issues occur:

1. **Check COM port**: Verify the correct COM port in Device Manager
2. **Close other programs**: Make sure no other software is using the serial port
3. **Restart application**: Close and reopen the GUI application

## 📁 File Structure

```
dist/
├── ZebraPrinterGUI.exe          # Main application
├── device_label_template.zpl    # Label template
├── device_log.csv              # Device logs
└── cleaned_devices.csv         # Clean device data
```

## 🔄 Updates

To update the application:
1. Replace the old `dist` folder with the new one
2. Your settings and logs will be preserved

## 📞 Support

If you encounter any issues:
1. Check the application logs in the GUI
2. Verify printer drivers are installed
3. Ensure serial port permissions are correct
4. Contact the system administrator if running in a corporate environment

---

**Note**: This is a completely standalone application - no internet connection or additional software installation required on the target computer!
