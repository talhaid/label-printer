# 📦 Enhanced Box Labels - User Guide

## 🆕 **New Features Added**

Your Box Labels tab is now **fully editable** with professional CSV management capabilities!

### ✨ **What's New:**

#### 📝 **Data Editing**
- **➕ Add Row** - Add new devices manually
- **✏️ Edit Selected** - Double-click or button to edit
- **🗑️ Delete Selected** - Remove unwanted rows  
- **📋 Duplicate Selected** - Copy existing devices
- **🔍 Filter Data** - Search and filter in real-time

#### 💾 **File Management**
- **Save** - Save changes to CSV file
- **New CSV** - Create fresh CSV from scratch
- **Enhanced Load** - Better CSV handling with auto-columns

#### 🎯 **Enhanced Table**
- **More Columns** - STC, Serial, IMEI, IMSI, CCID, MAC, Status
- **Right-Click Menu** - Context menu for quick actions
- **Real-time Search** - Filter as you type
- **Better Navigation** - Improved pagination

### 🚀 **How to Use:**

#### **Creating New Data:**
1. Click **"New CSV"** to start fresh
2. Click **"➕ Add Row"** to add devices
3. Fill in device information
4. Click **"Save"** when done

#### **Editing Existing Data:**
1. **Load CSV** with your device data
2. **Double-click** any row to edit
3. **Right-click** for context menu options
4. **Filter** to find specific devices quickly

#### **Creating Box Labels:**
1. **Load or create** your device data
2. **Select up to 20 devices** by clicking
3. **Enter box number** (e.g., BOX001)
4. **Click "Create PDF Label"**
5. **Files save to** `save/box_labels/`

### 📋 **CSV Format:**

Your CSV should have these columns:
```
STC,SERIAL_NUMBER,IMEI,IMSI,CCID,MAC_ADDRESS,STATUS
60001,ATS542912923701,866988074133496,286019876543210,8991101200003204510,AA:BB:CC:DD:EE:01,Available
60002,ATS542912923702,866988074133497,286019876543211,8991101200003204511,AA:BB:CC:DD:EE:02,Available
```

### 🎯 **Pro Tips:**

- **Double-click** to edit rows quickly
- **Right-click** for context menu
- **Type in filter box** to search instantly  
- **Use "Duplicate"** to create similar devices
- **Auto-save** your work frequently
- **STC numbers** auto-increment when adding new devices

### 📁 **File Organization:**

```
save/
├── box_labels/          ← Your PDF labels save here
│   ├── box001_20250828_143052.pdf
│   └── box002_20250828_143125.pdf
├── csv/                 ← Device logs
└── zpl_output/          ← ZPL files
```

### 🎮 **Keyboard Shortcuts:**

- **Enter** in dialog = Save
- **Esc** in dialog = Cancel
- **Delete** key = Delete selected rows
- **Ctrl+S** = Save CSV (if implemented)

### ✅ **Ready to Use!**

Your enhanced Box Labels tab is now a **powerful CSV editor** that makes creating box labels much easier and more professional. You can manage device data like a spreadsheet and generate perfect labels!

Try it out with the `test_box_data.csv` file included in your workspace.
