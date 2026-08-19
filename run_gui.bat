@echo off
echo Starting Thermal Label Printer GUI...
echo Checking dependencies...

python -c "import tkinter, serial, pandas, qrcode, reportlab" 2>nul
if errorlevel 1 (
    echo ERROR: Required Python packages are missing.
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Dependencies OK. Launching...
python printer_gui.py

if errorlevel 1 (
    echo ERROR: The application exited with an error.
    pause
)
