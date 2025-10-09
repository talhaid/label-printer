# 🚀 Kurulum ve Başlangıç Rehberi

## 📋 Sistem Gereksinimleri

### Minimum Gereksinimler
- **İşletim Sistemi**: Windows 10/11 (64-bit)
- **RAM**: 4 GB (8 GB önerilen)
- **Disk Alanı**: 500 MB boş alan
- **USB Port**: Yazıcı ve seri port bağlantısı için

### Gerekli Donanım
- **Zebra GC420T** termal yazıcı
- **USB-Serial** adaptör (CH340, FTDI vb.)
- **USB Kabloları** (yazıcı ve seri port için)

## 🔧 Hızlı Kurulum (EXE Kullanımı)

### 1. Hazır Dosyaları İndirin
```bash
# Sadece dist klasörünü hedef bilgisayara kopyalayın
printertest/
└── dist/
    ├── ZebraPrinterGUI.exe
    ├── device_label_template.zpl
    ├── device_log.csv
    └── cleaned_devices.csv
```

### 2. Yazıcı Sürücülerini Kurun
1. Zebra'nın resmi web sitesinden GC420T sürücülerini indirin
2. Kurulum dosyasını çalıştırın
3. Yazıcıyı USB ile bağlayın
4. Windows yazıcı listesinde görünmesini bekleyin

### 3. USB-Serial Sürücülerini Kurun
1. USB-Serial adaptörünü takın
2. Windows otomatik sürücü kurulumunu bekleyin
3. Device Manager'da COM port numarasını not edin

### 4. Uygulamayı Başlatın
```bash
cd dist/
ZebraPrinterGUI.exe
```

## 🛠️ Geliştirici Kurulumu (Kaynak Kod)

### 1. Python Kurulumu
```bash
# Python 3.8+ gerekli
python --version  # Kontrol edin

# Yoksa https://python.org adresinden indirin
```

### 2. Proje Dosyalarını İndirin
```bash
git clone [proje-repo-url]
cd printertest
```

### 3. Gerekli Kütüphaneleri Kurun
```bash
# Kütüphaneleri kur
pip install -r requirements_clean.txt

# Kurulum kontrolü
python -c "import tkinter, serial, reportlab, pandas"
```

### 4. Uygulamayı Çalıştırın
```bash
# Kolay yol
run_gui.bat

# Manuel yol
python src/printer_gui.py
```

## 🔍 Kurulum Kontrolü

### Yazıcı Testi
1. GUI'yi açın
2. **Main Tab** > **Printer** dropdown'dan Zebra'yı seçin
3. **Test Print** butonuna tıklayın
4. Yazıcıdan test etiketi çıkmalı

### Seri Port Testi
1. **Serial Port** dropdown'dan COM portunu seçin
2. **Baud Rate**: 115200 olarak ayarlayın
3. **Start Monitoring** butonuna tıklayın
4. Status: "Monitoring" olmalı

### Veri Parse Testi
1. **Test Data Input** alanında örnek veri var
2. **Test Parse & Print** butonuna tıklayın
3. Veri başarıyla parse edilmeli

## ⚠️ Yaygın Sorunlar ve Çözümler

### Problem: "Yazıcı bulunamıyor"
```bash
# Çözüm
1. Windows Settings > Printers & scanners
2. Zebra GC420T yazıcının listede olduğunu kontrol edin
3. Sürücüleri yeniden kurun
4. USB kablosunu değiştirin
```

### Problem: "COM port bağlanamıyor"
```bash
# Çözüm
1. Device Manager > Ports (COM & LPT)
2. USB-Serial adaptörün görünüp görünmediğini kontrol edin
3. Farklı USB porta takın
4. Sürücüleri güncelle
```

### Problem: "Python kütüphanesi bulunamıyor"
```bash
# Çözüm
pip install --upgrade pip
pip install -r requirements_clean.txt

# Eğer hala hata varsa
pip install tkinter pyserial reportlab pandas pillow
```

### Problem: "EXE çalışmıyor"
```bash
# Çözüm
1. Windows Defender exclusion ekleyin
2. Antivirus yazılımını geçici kapatın
3. Yönetici olarak çalıştırın
4. dist/ klasörünün tamamını kopyaladığınızdan emin olun
```

## 🏭 Üretim Ortamı Kurulumu

### Çoklu Bilgisayar Kurulumu
1. **Ana bilgisayarda** EXE oluşturun
2. **dist/** klasörünü tüm bilgisayarlara kopyalayın
3. Her bilgisayarda yazıcı sürücülerini kurun
4. COM port ayarlarını her bilgisayar için yapın

### Network Paylaşım (Opsiyonel)
```bash
# CSV dosyalarını network'te paylaşmak için
# save/csv/ klasörünü network drive'a yönlendirin
```

### Otomatik Başlatma
```bash
# Windows Startup klasörüne kısayol ekleyin
Win+R > shell:startup
# run_gui.bat'ın kısayolunu buraya kopyalayın
```

## 📊 Performans Ayarları

### Hız Optimizasyonu
- **Auto Print Mode** kullanın (Queue Mode daha yavaş)
- **CSV file size** kontrolü yapın (çok büyükse temizleyin)
- **ZPL outputs** klasörünü periyodik temizleyin

### Bellek Optimizasyonu
- Uzun süreli kullanımda uygulamayı restart edin
- **Clear Table** butonunu kullanın
- Log dosyalarını temizleyin

## 🔐 Güvenlik ve Backup

### Veri Yedekleme
```bash
# Önemli klasörler
save/csv/          # Ana veri
save/backups/      # Otomatik yedekler
templates/         # Şablonlar
```

### Sistem Yedekleme
```bash
# Tüm projeyi yedekle
xcopy printertest\ backup_folder\ /E /I
```

---

**💡 İpucu**: İlk kurulumda sorun yaşıyorsanız, `clean_project.py` scriptini çalıştırarak temiz bir başlangıç yapabilirsiniz.

**📞 Destek**: Teknik sorunlar için log dosyalarını ekleyerek rapor oluşturun.