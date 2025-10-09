#!/usr/bin/env python3
"""
Proje Temizleme Scripti
Bu script, projeden gereksiz test dosyaları, eski yedekleri ve geçici dosyaları temizler.
"""

import os
import shutil
import glob
from pathlib import Path

def clean_project():
    """Projeyi temizle"""
    print("🧹 Proje temizleme başlıyor...")
    
    # Ana dizin
    base_dir = Path(__file__).parent
    
    # Silinecek dosya türleri
    test_files = [
        "test_*.py", "example.py", "*_test.py", "sample_*.py",
        "quick_*.py", "simple_*.py", "demo_*.py", "minimal_*.py",
        "alternative_*.py", "position_test.py", "regex_examples.py",
        "zpl_examples.py", "scrolling_demo.py", "save_structure_demo.py"
    ]
    
    # Silinecek geçici dosyalar
    temp_files = [
        "*.log", "device_log_*.csv", "device_printer.log",
        "*.spec", "runtime_hooks.py", "make_exe.py"
    ]
    
    # Silinecek çıktı dosyaları
    output_files = [
        "*.pdf", "*.html", "gui_box_*.pdf", "box_label_*.pdf",
        "combined_box_*.pdf", "centered_box_*.pdf", "simple_*.pdf",
        "vertical_*.pdf", "real_box_*.pdf", "text_*.pdf"
    ]
    
    # Silinecek klasörler
    temp_dirs = ["build", "__pycache__", ".pytest_cache", "zpl_outputs_backup"]
    
    files_removed = 0
    dirs_removed = 0
    
    # Test dosyalarını sil
    print("📝 Test dosyaları temizleniyor...")
    for pattern in test_files:
        for file_path in glob.glob(str(base_dir / pattern)):
            try:
                os.remove(file_path)
                print(f"   ✅ Silindi: {os.path.basename(file_path)}")
                files_removed += 1
            except Exception as e:
                print(f"   ❌ Silinemedi: {file_path} - {e}")
    
    # Geçici dosyaları sil
    print("🗂️ Geçici dosyalar temizleniyor...")
    for pattern in temp_files:
        for file_path in glob.glob(str(base_dir / pattern)):
            try:
                os.remove(file_path)
                print(f"   ✅ Silindi: {os.path.basename(file_path)}")
                files_removed += 1
            except Exception as e:
                print(f"   ❌ Silinemedi: {file_path} - {e}")
    
    # Çıktı dosyalarını sil
    print("📄 Çıktı dosyaları temizleniyor...")
    for pattern in output_files:
        for file_path in glob.glob(str(base_dir / pattern)):
            try:
                os.remove(file_path)
                print(f"   ✅ Silindi: {os.path.basename(file_path)}")
                files_removed += 1
            except Exception as e:
                print(f"   ❌ Silinemedi: {file_path} - {e}")
    
    # Geçici klasörleri sil
    print("📁 Geçici klasörler temizleniyor...")
    for dir_name in temp_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"   ✅ Silindi: {dir_name}/")
                dirs_removed += 1
            except Exception as e:
                print(f"   ❌ Silinemedi: {dir_path} - {e}")
    
    # Sonuçları göster
    print("\n✨ Temizleme tamamlandı!")
    print(f"📊 Silinen dosya sayısı: {files_removed}")
    print(f"📊 Silinen klasör sayısı: {dirs_removed}")
    
    # Kalan önemli dosyaları listele
    print("\n📋 Kalan önemli dosyalar:")
    important_files = [
        "src/", "templates/", "docs/", "dist/", "save/",
        "build_gui_exe.py", "requirements_clean.txt", "run_gui.bat",
        "README_TR.md", ".gitignore"
    ]
    
    for item in important_files:
        path = base_dir / item
        if path.exists():
            if path.is_dir():
                print(f"   📁 {item}")
            else:
                print(f"   📄 {item}")

if __name__ == "__main__":
    clean_project()
    print("\n🎉 Proje hazır! Artık repo'yu paylaşabilirsiniz.")
    input("Devam etmek için Enter'a basın...")