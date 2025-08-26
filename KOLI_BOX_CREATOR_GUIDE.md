# Koli Box Creator - User Guide

## 🎯 Overview
The Koli Box Creator is a GUI application that allows you to:
- Load device data from CSV files
- Browse devices in pages of 20
- Select devices for box labels
- Generate PDF box labels using our perfected template

## 📋 CSV File Requirements
Your CSV file must contain these columns:
- `SERIAL_NUMBER` - Device serial numbers
- `IMEI` - Device IMEI numbers  
- `MAC_ADDRESS` - Device MAC addresses
- `STATUS` (optional) - Device status

## 🎮 How to Use

### 1. Load CSV Data
- Click "Browse CSV" to select your device CSV file
- Click "Load Data" to import the devices
- Status bar will show how many devices were loaded

### 2. Navigate Pages
- Use "◀ Previous" and "Next ▶" buttons to browse pages
- Each page shows 20 devices maximum
- Page counter shows current page and total pages

### 3. Select Devices
- Click on any device row to select/deselect it
- Selected devices are highlighted in blue
- Checkbox (☑/☐) shows selection status
- Maximum 20 devices can be selected per box

### 4. Create Box Label
- Enter a box number (e.g., "BOX001", "BOX002")
- Click "Create Box Label" when you have selected devices
- PDF will be generated with our optimized template
- Box number will auto-increment after successful creation

## 📄 Generated PDF Features
- **40mm QR code** at top with all device data
- **Company header**: STC - SICAKLIK TAKIP CIHAZI
- **Date and box number**
- **Complete device list** with S/N, IMEI, MAC
- **10cm × 15cm portrait** format ready for printing

## 🔄 Workflow Example
1. Load `device_log.csv` → Shows 100 devices
2. Navigate to page 1 → Shows devices 1-20
3. Select all 20 devices → Blue highlights
4. Enter "BOX001" → Box number field
5. Click "Create Box Label" → Generates PDF
6. Box number auto-changes to "BOX002"
7. Navigate to page 2 for next batch

## 📁 Output Files
Generated PDFs are saved with format:
```
koli_box_BOX001_[FirstSerial]_[LastSerial]_[Timestamp].pdf
```

## 💡 Tips
- **Selection persists** across pages - you can select from multiple pages
- **Auto-increment** box numbers for sequential labeling
- **Status column** helps track which devices are available
- **QR codes** contain complete device data for scanning
- **PDF ready** for direct printing on 10×15cm labels

## 🚀 Launch Command
```bash
python koli_box_creator.py
```

The GUI will open and you can start creating box labels immediately!