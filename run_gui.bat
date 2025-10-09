@echo off
echo Zebra Yazici GUI Baslatiliyor...
echo Gerekli kutuphaneler kontrol ediliyor...

python -c "import tkinter, serial, reportlab, pandas" 2>nul
if errorlevel 1 (
    echo HATA: Gerekli Python kutuphaneleri bulunamadi!
    echo Lutfen once: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Tum kutuphaneler hazir.
echo GUI baslatiliyor...
python src\printer_gui.py

if errorlevel 1 (
    echo HATA: Uygulama calistirilirken hata olustu!
    pause
)