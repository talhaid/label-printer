# 📁 File Output System for Zebra GC420T Auto-Printer

## 🎯 Overview

The auto-printer system now automatically saves all processed data and generated ZPL files for complete audit trails and record keeping.

## 📂 Output Structure

```
printertest/
├── zpl_outputs/                    # ZPL files folder
│   ├── ATS542912923728_20250825_120540.zpl
│   ├── BTS987654321123_20250825_120602.zpl
│   └── [SERIAL_NUMBER]_[TIMESTAMP].zpl
├── device_log.csv                  # Complete device log
└── device_printer.log              # System activity log
```

## 📄 ZPL Files

### Naming Convention
```
[SERIAL_NUMBER]_[YYYYMMDD_HHMMSS].zpl
```

**Examples:**
- `ATS542912923728_20250825_120540.zpl`
- `BTS987654321123_20250825_120602.zpl`

### Content
Each ZPL file contains the exact commands sent to the printer for that specific device, making it possible to:
- **Reprint labels** by sending the ZPL file again
- **Verify print content** without accessing the original data
- **Debug printing issues** by examining the generated ZPL
- **Archive label designs** for compliance or records

## 📊 CSV Log File

### Location
`device_log.csv` in the main project folder

### CSV Columns
| Column | Description | Example |
|--------|-------------|---------|
| `timestamp` | When the device was processed | 2025-08-25 12:05:40 |
| `serial_number` | Device serial number | ATS542912923728 |
| `imei` | International Mobile Equipment Identity | 866988074133496 |
| `imsi` | International Mobile Subscriber Identity | 286019876543210 |
| `ccid` | SIM card identifier | 8991101200003204510 |
| `mac_address` | MAC address | AA:BB:CC:DD:EE:FF |
| `stc` | STC value (default: 6000) | 6000 |
| `print_status` | Print result | SUCCESS/FAILED/ERROR |
| `zpl_file` | Name of saved ZPL file | ATS542912923728_20250825_120540.zpl |
| `raw_data` | Original serial data received | ##ATS542912923728\|866988... |

### Print Status Values
- **SUCCESS** - Label printed successfully
- **FAILED** - Printer communication failed
- **PARSE_ERROR** - Could not parse serial data
- **TEMPLATE_ERROR** - ZPL template validation failed
- **ERROR: [message]** - Other errors with description

## 🔧 Features

### Automatic File Management
- **Creates directories** automatically when first device is processed
- **Unique filenames** prevent overwrites using timestamp
- **CSV headers** added automatically on first run
- **Appends data** to existing CSV file for continuous logging

### Error Handling
- **Parse errors** are logged to CSV with status "PARSE_ERROR"
- **Print failures** are recorded with detailed status
- **File save errors** are logged but don't stop processing
- **Missing data** is handled gracefully

### Data Integrity
- **All raw data preserved** in CSV for troubleshooting
- **Exact ZPL commands saved** for each device
- **Timestamps** for complete audit trail
- **UTF-8 encoding** for international character support

## 🖥️ GUI Integration

### File Access Buttons
- **"Open Folder"** - Opens ZPL outputs folder in Windows Explorer
- **"Open CSV"** - Opens CSV log in Excel (if available)
- **Automatic updates** when files are created

### Real-time Updates
- Files are created immediately when devices are processed
- GUI shows file counts and status
- No need to restart for file access

## 📈 Usage Examples

### 1. Reprint a Label
```bash
# Find the ZPL file for device ATS542912923728
# Copy the ZPL content and send to printer
python zebra_zpl.py --raw-zpl "^XA^PW399^LL240..."
```

### 2. Analyze Device Data
```python
import pandas as pd

# Load CSV data
df = pd.read_csv('device_log.csv')

# Show all successful prints
successful = df[df['print_status'] == 'SUCCESS']
print(f"Total successful prints: {len(successful)}")

# Find specific device
device = df[df['serial_number'] == 'ATS542912923728']
print(device)
```

### 3. Bulk Operations
```bash
# Print all ZPL files in folder
for file in zpl_outputs/*.zpl; do
    python zebra_zpl.py --zpl-file "$file"
done
```

## 🔍 Monitoring & Analytics

### Daily Reports
```python
# Generate daily device count
df = pd.read_csv('device_log.csv')
df['date'] = pd.to_datetime(df['timestamp']).dt.date
daily_counts = df.groupby('date').size()
print(daily_counts)
```

### Error Analysis
```python
# Find and analyze errors
errors = df[df['print_status'] != 'SUCCESS']
error_types = errors['print_status'].value_counts()
print("Error breakdown:", error_types)
```

### Device Tracking
```python
# Track specific device history
device_history = df[df['serial_number'] == 'ATS542912923728']
print(f"Device processed {len(device_history)} times")
```

## 🛠️ Maintenance

### File Cleanup
- **ZPL files** can be archived or deleted after a retention period
- **CSV logs** can be rotated monthly/yearly for large volumes
- **Log rotation** can be implemented for continuous operation

### Backup Strategy
- **Regular CSV backups** for compliance requirements
- **ZPL file archives** for reprinting capabilities
- **Database import** for advanced analytics

## 📋 Benefits

### Compliance & Audit
- ✅ **Complete audit trail** of all processed devices
- ✅ **Exact print data** preserved for compliance
- ✅ **Timestamped records** for tracking
- ✅ **Error documentation** for quality control

### Operational Benefits  
- ✅ **Reprint capability** without re-processing devices
- ✅ **Troubleshooting data** for technical issues
- ✅ **Performance metrics** for system optimization
- ✅ **Data export** for reporting and analysis

### Quality Control
- ✅ **Print verification** by examining ZPL files
- ✅ **Error tracking** and resolution
- ✅ **Process monitoring** through CSV logs
- ✅ **Historical data** for trend analysis

---

**Your Zebra GC420T auto-printer now provides complete data management and audit capabilities! 📊✨**