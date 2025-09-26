#!/usr/bin/env python3
"""
Entegrasyon test scripti
Bu script tüm modüllerin doğru şekilde import edilip edilemediğini test eder.
"""

import sys
import os

# Mevcut dizini Python path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Tüm modülleri import etmeyi test et"""
    print("Modül import testleri başlatılıyor...")
    
    try:
        print("✓ PyQt5 import ediliyor...")
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        print("✓ serialiletisim modülü import ediliyor...")
        from serialiletisim import SerialManager
        
        print("✓ gui_com_ayarlari modülü import ediliyor...")
        from gui_com_ayarlari import ComAyarlariSayfasi
        
        print("✓ main_app modülü import ediliyor...")
        from main_app import MainApp, AnaSayfa, XmodemSayfasi
        
        print("✓ xmodem_gui modülü import ediliyor...")
        from xmodem_gui import XmodemGui
        
        print("\n✅ Tüm modüller başarıyla import edildi!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import hatası: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        return False

def test_serial_manager():
    """SerialManager singleton testini yap"""
    print("\nSerialManager singleton testi...")
    
    try:
        from serialiletisim import SerialManager
        
        # İki instance oluştur
        manager1 = SerialManager.get_instance()
        manager2 = SerialManager.get_instance()
        
        # Aynı instance olup olmadığını kontrol et
        if manager1 is manager2:
            print("✅ SerialManager singleton pattern çalışıyor!")
            return True
        else:
            print("❌ SerialManager singleton pattern çalışmıyor!")
            return False
            
    except Exception as e:
        print(f"❌ SerialManager test hatası: {e}")
        return False

def test_port_detection():
    """Port tespit testini yap"""
    print("\nPort tespit testi...")
    
    try:
        from serialiletisim import SerialManager
        
        manager = SerialManager.get_instance()
        ports = manager.get_available_ports()
        
        print(f"✅ Tespit edilen portlar: {ports}")
        return True
        
    except Exception as e:
        print(f"❌ Port tespit hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("=" * 50)
    print("XMODEM Seri Port Uygulaması - Entegrasyon Testi")
    print("=" * 50)
    
    tests = [
        ("Modül Import Testleri", test_imports),
        ("SerialManager Singleton Testi", test_serial_manager),
        ("Port Tespit Testi", test_port_detection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Sonuçları: {passed}/{total} test başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Uygulama çalışmaya hazır.")
        return True
    else:
        print("⚠️  Bazı testler başarısız. Lütfen hataları kontrol edin.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
