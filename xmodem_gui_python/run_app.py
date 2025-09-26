#!/usr/bin/env python3
"""
XMODEM Seri Port Uygulaması Başlatıcı
Bu script uygulamayı başlatmak için kullanılır.
"""

import sys
import os

# Mevcut dizini Python path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from main_app import MainApp
    from PyQt5.QtWidgets import QApplication
    
    if __name__ == "__main__":
        print("XMODEM Seri Port Uygulaması başlatılıyor...")
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        window = MainApp()
        window.show()
        
        print("Uygulama başarıyla başlatıldı!")
        sys.exit(app.exec_())
        
except ImportError as e:
    print(f"Hata: Gerekli paketler yüklenmemiş. {e}")
    print("Lütfen 'pip install -r requirements.txt' komutunu çalıştırın.")
    sys.exit(1)
except Exception as e:
    print(f"Uygulama başlatılırken hata oluştu: {e}")
    sys.exit(1)
