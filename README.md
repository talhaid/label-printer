# Zebra GC420T Auto-Printer System# Zebra GC420T PDF Printer for Python



A professional GUI application for automatic printing of device labels using Zebra GC420T thermal printers. Supports serial data input, real-time processing, CSV logging, and box label creation.A Python application for printing PDF files to your Zebra GC420T thermal printer.



## 🚀 Quick Start## Features



### Option 1: Run Executable (Recommended)- 🖨️ Print PDF files directly to Zebra GC420T

1. Download `ZebraPrinterGUI.exe` from the `dist` folder- 📄 Convert PDF pages to thermal printer-compatible images

2. Connect your Zebra GC420T printer via USB- 🔧 Automatic printer detection

3. Install Zebra printer drivers if not already installed- 📋 Support for multiple copies

4. Double-click `ZebraPrinterGUI.exe` to launch- 🎯 Optimized for 203 DPI thermal printing

5. Select your printer and serial port in the GUI- 💾 Raw ZPL command support

6. Click "Start Monitoring" to begin- 🖥️ Windows printer integration



### Option 2: Run from Source## Requirements

1. Install Python 3.11+ 

2. Install dependencies: `pip install -r requirements.txt`- Windows OS (tested on Windows 10/11)

3. Run: `python printer_gui.py`- Python 3.7+

- Zebra GC420T printer connected via USB or network

## 📋 System Requirements- Zebra printer drivers installed



- **Operating System**: Windows 10/11## Installation

- **Python**: 3.11+ (if running from source)

- **Printer**: Zebra GC420T thermal printer1. **Clone or download this project**

- **Connection**: USB port for printer, Serial/USB port for data input2. **Install dependencies:**

- **Memory**: 4GB RAM minimum   ```bash

- **Storage**: 100MB free space   pip install -r requirements.txt

   ```

## 🖨️ Printer Setup

## Quick Start

### Zebra GC420T Configuration

1. **Install Zebra Drivers**:### 1. Basic Usage (Command Line)

   - Download from [Zebra Support](https://www.zebra.com/us/en/support-downloads.html)

   - Install the latest Windows driver package```bash

   - Restart after installation# Print a PDF file

python zebra_printer.py your_document.pdf

2. **Printer Settings**:

   - **Label Size**: 2" x 1" (50mm x 25mm)# Print multiple copies

   - **Print Method**: Thermal Transfer or Direct Thermalpython zebra_printer.py your_document.pdf --copies 3

   - **Speed**: Medium (2-4 IPS recommended)

   - **Darkness**: 10-15 (adjust based on label quality)# List available printers

python zebra_printer.py --list-printers

3. **Connection**:

   - Connect via USB cable# Specify printer manually

   - Power on the printerpython zebra_printer.py your_document.pdf --printer "Zebra GC420T"

   - Verify it appears in Windows "Devices and Printers"```



## 📡 Serial Data Input### 2. Using the Python Module



### Data Format```python

The system expects serial data in this format:from zebra_printer import ZebraPrinter

```

##SERIAL|IMEI|IMSI|CCID|MAC### Initialize printer (auto-detects Zebra)

```printer = ZebraPrinter()



**Example**:# Or specify printer name

```printer = ZebraPrinter("Zebra GC420T (ZPL)")

##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##

```# Print a PDF

success = printer.print_pdf("label.pdf", copies=2)

### Serial Port Configuration

- **Baud Rate**: 115200 (configurable)# Check printer status

- **Data Bits**: 8status = printer.get_printer_status()

- **Stop Bits**: 1print(status)

- **Parity**: None```

- **Flow Control**: None

### 3. Run Examples

### Supported Devices

- USB-to-Serial adapters```bash

- Arduino/Microcontroller serial output# Run all demos

- Direct serial ports (COM1, COM2, etc.)python example.py



## 🎛️ GUI Interface Guide# Print specific PDF

python example.py my_label.pdf

### Main Control Tab

- **Connection Settings**: Select printer and serial port# Print multiple copies

- **STC Counter**: Set starting STC number (auto-increments)python example.py my_label.pdf --copies 5

- **Printing Mode**: ```

  - **Auto Print**: Prints immediately when data received

  - **Queue Mode**: Add to queue for manual confirmation## Printer Setup

- **Test Functions**: Test printer and data parsing

1. **Connect your Zebra GC420T:**

### Box Labels Tab   - USB: Connect via USB cable

- Create box labels containing multiple devices   - Network: Configure IP settings

- Import/export CSV data

- Edit device information2. **Install Zebra drivers:**

- Generate PDF labels for shipping boxes   - Download from [zebra.com](https://www.zebra.com/us/en/support-downloads.html)

   - Install the GC420T drivers for Windows

### CSV Manager Tab

- View all processed devices3. **Verify printer in Windows:**

- Export filtered data   - Go to Settings > Printers & Scanners

- Clean duplicate entries   - Ensure your Zebra printer appears in the list

- Monitor system statistics   - Print a test page to confirm connectivity



### ZPL Template Tab## Supported Features

- Edit label template design

- Available placeholders: `{STC}`, `{SERIAL_NUMBER}`, `{IMEI}`, `{IMSI}`, `{CCID}`, `{MAC_ADDRESS}`### PDF Processing

- Save/load custom templates- ✅ Multi-page PDF support

- ✅ Automatic image conversion

### Logs Tab- ✅ DPI optimization (203 DPI for GC420T)

- View real-time system logs- ✅ Monochrome conversion for thermal printing

- Save logs to file

- Monitor errors and status### Printer Communication

- ✅ Windows printer spooler integration

### Settings Tab- ✅ Raw data printing

- Configure data parsing regex- ✅ ZPL command support

- Adjust field mapping- ✅ Error handling and logging

- Set print preferences

### Print Settings

## 📁 File Structure- ✅ Copy count control

- ✅ Resolution settings

```- ✅ Image resizing for printer width

printertest/- ✅ Automatic paper size detection

├── dist/

│   └── ZebraPrinterGUI.exe    # Main executable## Troubleshooting

├── printer_gui.py             # Main GUI application

├── serial_auto_printer.py     # Core printing logic### Common Issues

├── zebra_zpl.py               # ZPL command handling

├── zebra_printer.py           # Printer interface1. **"No Zebra printer found"**

├── build_gui_exe.py           # Executable builder   - Check printer is connected and powered on

├── run_gui.bat                # Quick launcher batch file   - Verify drivers are installed

├── requirements.txt           # Python dependencies   - Run `python zebra_printer.py --list-printers` to see available printers

├── templates/                 # Label templates

│   ├── device_label_template.zpl2. **"Print job failed"**

│   └── manual_box_label_template.html   - Ensure printer has paper loaded

└── save/                      # Output folder (auto-created)   - Check for paper jams

    ├── csv/                  # CSV logs   - Verify printer is online in Windows

    ├── zpl_outputs/          # ZPL files

    ├── box_labels/           # Box label PDFs3. **"win32print not available"**

    └── backups/              # Backup files   - Install pywin32: `pip install pywin32`

```   - This is required for Windows printer communication



## ⚙️ Configuration4. **Poor print quality**

   - Verify you're using thermal transfer or direct thermal labels

### STC Counter   - Check print density settings on the printer

- STC numbers auto-increment starting from 60000   - Ensure PDF resolution matches printer (203 DPI)

- The system remembers the last used STC from CSV history

- Manual STC adjustment available in GUI### Printer Configuration



### Label Template Customization- **Media Type:** Direct thermal or thermal transfer labels

1. Go to "ZPL Template" tab- **Print Method:** Thermal transfer (for durability) or direct thermal

2. Modify the ZPL code using available placeholders- **Print Width:** Up to 4.09" (104mm)

3. Test with "Test Parse & Print" function- **Resolution:** 203 dpi (8 dots/mm)

4. Save custom templates for future use- **Print Speed:** 2-5 ips (50-127 mm/sec)



### Regex Pattern Configuration## Label Design Tips

Default pattern: `##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\|([0-9A-F]+)\|([A-F0-9:]+)##`

1. **Size:** Design labels to match your media (common: 4"x6", 4"x3", 2"x1")

Modify in Settings tab for different data formats.2. **Resolution:** Use 203 DPI for crisp text and graphics

3. **Colors:** Use black and white only (thermal printers don't support color)

## 🔧 Troubleshooting4. **Fonts:** Use clear, readable fonts (Arial, Helvetica work well)

5. **Margins:** Leave 0.1" margins for reliable printing

### Common Issues

## Advanced Usage

#### Printer Not Found

- Verify USB connection### Custom ZPL Commands

- Check Windows Device Manager

- Reinstall Zebra drivers```python

- Try different USB portprinter = ZebraPrinter()



#### Serial Port Issues# Send raw ZPL commands

- Check COM port availability in Device Managerzpl = """

- Verify baud rate matches data source^XA

- Try different USB ports^FO50,50^ADN,36,20^FDHello World^FS

- Check cable connections^XZ

"""

#### Print Quality Issuesprinter.send_raw_zpl(zpl)

- Adjust printer darkness setting```

- Check label alignment

- Clean print head### Batch Printing

- Verify label size settings

```python

#### Data Parsing Errorsimport os

- Verify data format matches expected patternfrom zebra_printer import ZebraPrinter

- Check regex configuration in Settings

- Use "Test Parse & Print" to debugprinter = ZebraPrinter()

- Monitor Logs tab for error details

# Print all PDFs in a folder

### Error Messagespdf_folder = "labels"

for filename in os.listdir(pdf_folder):

| Error | Solution |    if filename.endswith('.pdf'):

|-------|----------|        pdf_path = os.path.join(pdf_folder, filename)

| "Printer not found" | Install drivers, check USB connection |        print(f"Printing {filename}...")

| "Serial port busy" | Close other applications using the port |        printer.print_pdf(pdf_path)

| "Parse error" | Check data format and regex pattern |```

| "Print failed" | Check printer status and paper |

## File Structure

## 📊 Features

```

### Auto-Print Modeprintertest/

- Processes data immediately when received├── zebra_printer.py    # Main printer module

- Auto-increments STC numbers├── example.py          # Usage examples and demos

- Logs all transactions to CSV├── requirements.txt    # Python dependencies

- Real-time status updates└── README.md          # This file

```

### Queue Mode

- Manual confirmation before printing## Dependencies

- Edit STC values before printing

- Batch print multiple devices- **PyMuPDF** - PDF processing and image extraction

- Preview data before processing- **Pillow** - Image manipulation and conversion

- **pywin32** - Windows printer communication

### CSV Management

- Automatic logging of all processed devices## License

- Export capabilities

- Data cleaning toolsThis project is provided as-is for educational and commercial use.

- Statistics tracking

## Support

### Box Label Creation

- Multi-device box labelsFor issues with:

- QR code generation- **Printer hardware:** Contact Zebra support

- PDF output- **Driver issues:** Download latest drivers from zebra.com

- Customizable layouts- **Software issues:** Check printer connection and Windows settings



## 🛠️ Development---



### Building from Source**Happy Printing! 🏷️**
```bash
# Install dependencies
pip install -r requirements.txt

# Run development version
python printer_gui.py

# Build executable
python build_gui_exe.py
```

### Modifying Templates
- Edit ZPL templates in `templates/` folder
- Use ZPL commands for layout control
- Test changes with GUI template editor

### Adding Features
- Main logic in `printer_gui.py`
- Printer interface in `zebra_zpl.py`
- Serial handling in `serial_auto_printer.py`

## 📝 License

This software is provided as-is for internal use. All rights reserved.

## 🆘 Support

For technical support:
1. Check the troubleshooting section above
2. Review the Logs tab for error details
3. Verify all connections and driver installations
4. Test with sample data first

---

**Version**: 3.0  
**Last Updated**: October 2025  
**Compatible**: Windows 10/11, Zebra GC420T