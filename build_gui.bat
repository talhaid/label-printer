@echo off
echo ========================================
echo Zebra Printer GUI - EXE Builder
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements_gui.txt

echo.
echo Building standalone EXE...
python build_gui_exe.py

echo.
echo Build process completed!
echo Check the 'dist' folder for your executable.
echo.
pause
