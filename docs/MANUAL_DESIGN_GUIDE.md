# Manual Box Label Design Guide

## 🎨 Easy Manual Design Approach

Instead of fighting with complex PDF generation, here's a **simple HTML-based solution** you can customize manually:

### 📁 Files Created:
1. **`simple_html_label.py`** - Automatic generator using your device data
2. **`manual_box_label_template.html`** - Manual template for design customization

---

## 🚀 Quick Start - Auto Generation

```bash
# Generate HTML label with your data
python simple_html_label.py
```

This creates an HTML file like: `box_label_HTML001_DEV001TEST101_DEV001TEST120_20250826_105248.html`

---

## 🎨 Manual Design Process

### Step 1: Open the Template
```bash
# Open the manual template in any browser
start manual_box_label_template.html
```

### Step 2: Customize the Design
Open `manual_box_label_template.html` in any text editor and modify:

#### 🔧 Easy Changes:
```css
/* Change label size */
@page {
    size: 15cm 10cm;    /* Make it bigger/smaller */
}

/* Change colors */
.title {
    color: #000;        /* Title color */
    font-size: 14px;    /* Title size */
}

.device-table th {
    background-color: #e0e0e0;  /* Header background */
}

/* Change fonts */
body {
    font-family: Arial, sans-serif;  /* Try 'Courier New', 'Times', etc. */
}

/* Change spacing */
body {
    padding: 3mm;      /* Overall margins */
}
```

#### 🎯 What You Can Customize:
- **Colors**: Background, text, borders
- **Fonts**: Family, size, weight
- **Spacing**: Margins, padding, gaps
- **Borders**: Thickness, style, color
- **Layout**: Column widths, table sizes
- **Text**: Add logos, change labels

### Step 3: Add Your Data
Replace the dummy data in the HTML tables with your real device information.

### Step 4: Print to PDF
1. Open the HTML file in Chrome/Edge
2. Press `Ctrl+P` (Print)
3. Choose "Save as PDF"
4. Set "More settings" → Paper size: Custom (15cm x 10cm)
5. Save your PDF!

---

## 💡 Design Tips

### 🎨 Color Schemes:
```css
/* Professional Blue */
.header { background-color: #1e3a8a; color: white; }
.device-table th { background-color: #3b82f6; color: white; }

/* Clean Gray */
.header { background-color: #374151; color: white; }
.device-table th { background-color: #6b7280; color: white; }

/* Modern Green */
.header { background-color: #059669; color: white; }
.device-table th { background-color: #10b981; color: white; }
```

### 📏 Size Adjustments:
```css
/* Bigger text for easier reading */
body { font-size: 10px; }
.device-table { font-size: 8px; }

/* Smaller margins for more space */
body { padding: 2mm; }

/* Bigger QR code */
.qr-code { width: 25mm; height: 25mm; }
```

### 🎯 Layout Options:
```css
/* Single column layout (if you prefer) */
.devices-section { flex-direction: column; }

/* Horizontal layout */
.content { flex-direction: column; }

/* No borders (clean look) */
.device-table td, .device-table th { border: none; }
```

---

## 🔄 Integration with Your System

### Option 1: Use the Auto Generator
```python
from simple_html_label import SimpleBoxLabelGenerator

# Your device data
your_devices = [
    {"SERIAL_NUMBER": "ATS123", "IMEI": "866988...", "MAC_ADDRESS": "AA:BB:..."},
    # ... 19 more devices
]

# Generate HTML
generator = SimpleBoxLabelGenerator()
html_file = generator.generate_html_label(your_devices, box_number="PROD001")

print(f"HTML label created: {html_file}")
```

### Option 2: Manual Template Method
1. Copy `manual_box_label_template.html`
2. Edit the device data manually
3. Customize the styling
4. Print to PDF

---

## 🛠️ Advanced Customization

### Add Company Logo:
```html
<div class="header">
    <img src="your-logo.png" style="height: 15mm; margin-bottom: 2mm;">
    <div class="title">Your Company Box Label</div>
</div>
```

### Add Barcode (if needed):
```html
<div class="qr-section">
    <img src="data:image/png;base64,{qr_base64}" class="qr-code">
    <div>📊 Barcode: BOX123456</div>
</div>
```

### Custom Table Styles:
```css
/* Zebra stripes */
.device-table tr:nth-child(odd) { background-color: #f0f0f0; }

/* Rounded corners */
.device-table { border-radius: 3mm; overflow: hidden; }

/* Shadow effect */
.device-table { box-shadow: 0 2mm 4mm rgba(0,0,0,0.1); }
```

---

## ✅ Advantages of HTML Approach:

1. **Easy to customize** - Just edit CSS
2. **No complex libraries** - Works in any browser
3. **Perfect printing** - Browser handles PDF conversion
4. **Responsive design** - Adapts to different sizes
5. **Add images/logos** - Easy to embed graphics
6. **Version control** - Track changes easily
7. **Preview instantly** - See changes immediately

---

## 🖨️ Production Workflow:

1. **Design once** - Customize the template to your liking
2. **Generate data** - Use Python script with real device data
3. **Auto-print** - Set up batch printing if needed
4. **Quality check** - Easy to verify in browser first

---

**Ready to design?** Open `manual_box_label_template.html` and start customizing! 🎨