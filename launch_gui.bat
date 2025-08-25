@echo off
echo Starting Zebra GC420T Auto-Printer GUI...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python printer_gui.py
pause