# Zebra Yazıcı Otomatik Etiket Sistemi

## 🎯 Proje Hakkında

Bu proje, Zebra GC420T ve XPrinter cihazları için otomatik etiket yazdırma sistemidir. Sistem, seri port üzerinden gelen cihaz verilerini okuyup, otomatik olarak etiket yazdırabilir veya manuel onay için kuyruğa alabilir.

## 📁 Proje Yapısı

```
printertest/
├── 📂 src/                          # Ana kaynak kodları
│   ├── printer_gui.py               # Ana GUI uygulaması
│   ├── serial_auto_printer.py       # Seri port otomatik yazdırma
│   ├── zebra_zpl.py                 # Zebra yazıcı kontrol modülü
│   └── xprinter_pcb.py              # XPrinter PCB yazdırma
├── 📂 templates/                    # Şablon dosyaları
│   ├── device_label_template.zpl    # ZPL etiket şablonu
│   └── manual_box_label_template.html # Box etiket HTML şablonu
├── 📂 dist/                         # Dağıtım dosyaları
│   └── ZebraPrinterGUI.exe          # Tek dosya çalıştırılabilir uygulama
├── 📂 save/                         # Veri saklama klasörleri
│   ├── csv/                         # CSV log dosyaları
│   ├── zpl_outputs/                 # ZPL çıktı dosyaları
│   ├── box_labels/                  # Box etiket PDF'leri
│   └── backups/                     # Yedek dosyalar
├── 📂 docs/                         # Dokümantasyon
│   ├── SETUP_GUIDE.md               # Kurulum rehberi
│   ├── GUI_GUIDE.md                 # GUI kullanım rehberi
│   └── DISTRIBUTION_GUIDE.md        # Dağıtım rehberi
├── build_gui_exe.py                 # EXE oluşturma scripti
├── requirements.txt                 # Python bağımlılıkları
└── README_TR.md                     # Bu dosya
```

## 🚀 Hızlı Başlangıç

### 1. Hazır EXE Kullanımı (Önerilen)
```bash
# Sadece dist klasörünü kopyalayın
cp -r dist/ hedef_bilgisayar/
cd hedef_bilgisayar/dist/
./ZebraPrinterGUI.exe
```

### 2. Kaynak Koddan Çalıştırma
```bash
# Gereksinimler
pip install -r requirements.txt

# Uygulamayı başlat
python src/printer_gui.py
```

## 🔧 Kurulum ve Kurgu

### Ön Gereksinimler
1. **Windows 10/11** (Zebra sürücüleri için)
2. **Zebra GC420T** yazıcı sürücüleri
3. **USB-Serial** adaptör sürücüleri
4. **Python 3.8+** (kaynak koddan çalıştırıyorsanız)

### Yazıcı Kurulumu
1. Zebra GC420T'yi USB ile bağlayın
2. Windows yazıcı listesinde görünmesini bekleyin
3. Test yazdırma yapın

### Seri Port Kurulumu
1. USB-Serial adaptörü takın
2. Device Manager'da COM port numarasını kontrol edin
3. Baud rate: **115200** (varsayılan)

## 💻 GUI Kullanımı

### Ana Sekmeler
1. **Main Tab**: Seri port izleme ve yazıcı kontrolü
2. **Box Labels**: Çoklu cihaz box etiket oluşturma
3. **CSV Manager**: Veri görüntüleme ve yönetimi
4. **ZPL Template**: Etiket şablonu düzenleme
5. **Logs**: Sistem logları

### Çalışma Modları
- **Auto Print**: Veri geldiğinde otomatik yazdır
- **Queue Mode**: Manuel onay için kuyruğa al

### Veri Formatı
```
##SERIAL_NUMBER|IMEI|IMSI|CCID|MAC_ADDRESS##
Örnek: ##ATS542912923728|866988074133496|286019876543210|8991101200003204510|AA:BB:CC:DD:EE:FF##
```

## 📊 Veri Yönetimi

### CSV Dosya Yapısı
CSV dosyaları şu sütunları içerir:
- **STC**: Sıra numarası (60000'den başlar)
- **Serial**: Seri numarası
- **IMEI**: Cihaz IMEI numarası
- **IMSI**: SIM kart IMSI numarası
- **CCID**: SIM kart CCID numarası
- **MAC**: WiFi MAC adresi
- **Status**: Yazdırma durumu (printed/failed)
- **Timestamp**: İşlem zamanı

### Veri Saklama
- **save/csv/**: Ana CSV log dosyaları
- **save/zpl_outputs/**: ZPL komut dosyaları
- **save/box_labels/**: Box etiket PDF'leri
- **save/backups/**: Otomatik yedekler

## 🏗️ Geliştirme

### Yeni EXE Oluşturma
```bash
python build_gui_exe.py
```

### Kod Yapısı
- **printer_gui.py**: Ana GUI sınıfı (AutoPrinterGUI)
- **serial_auto_printer.py**: Seri port ve yazdırma logic
- **zebra_zpl.py**: Zebra yazıcı ZPL komutları
- **xprinter_pcb.py**: XPrinter PCB yazdırma

### Önemli Sınıflar
- `AutoPrinterGUI`: Ana GUI kontrolcüsü
- `DeviceAutoPrinter`: Otomatik yazdırma yöneticisi
- `ZebraZPL`: Zebra yazıcı kontrolü
- `SerialPortMonitor`: Seri port izleyici

## 🔍 Sorun Giderme

### Yaygın Sorunlar
1. **Yazıcı bulunamıyor**
   - Windows yazıcı listesini kontrol edin
   - Zebra sürücülerini yeniden kurun

2. **Seri port bağlanamıyor**
   - COM port numarasını kontrol edin
   - USB-Serial sürücülerini güncelleyin

3. **Veri parselenmiyor**
   - Veri formatını kontrol edin
   - Regex ayarlarını kontrol edin

### Log Dosyaları
- **Logs sekmesi**: Gerçek zamanlı log görüntüleme
- **save/backups/**: Eski log dosyaları

## 📋 Değişiklik ve Güncelleme

### Yeni Özellik Ekleme
1. `printer_gui.py` dosyasında GUI değişiklikleri
2. `serial_auto_printer.py` dosyasında logic değişiklikleri
3. Yeni EXE oluşturun: `python build_gui_exe.py`

### ZPL Şablon Güncelleme
1. **ZPL Template** sekmesini kullanın
2. Veya `templates/device_label_template.zpl` dosyasını düzenleyin

### CSV Yapısı Değişikliği
1. Parser kodunu güncelleyin
2. CSV kolon yapısını güncelleyin
3. GUI display kodunu güncelleyin

## 🔒 Güvenlik ve Yedekleme

### Otomatik Yedekleme
- CSV dosyaları otomatik olarak `save/backups/` klasörüne yedeklenir
- ZPL çıktıları kalıcı olarak saklanır

### Veri Güvenliği
- Tüm işlemler local olarak yapılır
- Network bağlantısı gerektirmez
- Hassas veriler şifrelenmez (local kullanım)

## 📞 Destek ve İletişim

### Teknik Destek
- Log dosyalarını kontrol edin
- Problem raporlama için log dosyalarını ekleyin
- Sistem konfigürasyonunu belirtin

### Kod Geliştirme
- Python 3.8+ gerekli
- tkinter, serial, reportlab, pandas kütüphaneleri
- Windows ortamında test edilmiştir

---

**Son Güncelleme**: Eylül 2025
**Versiyon**: 2.0
**Geliştirici**: Zebra Printer Automation Team