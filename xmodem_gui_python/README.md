# XMODEM Seri Port Uygulaması

Bu uygulama, seri port üzerinden XMODEM protokolü ile veri transferi yapmanızı sağlayan kapsamlı bir GUI uygulamasıdır.

## Özellikler

- **COM Port Yönetimi**: Seri port bağlantı ayarları ve yönetimi
- **XMODEM Hesaplamaları**: CRC32 hesaplamaları ve dosya işleme
- **Modern GUI**: Kullanıcı dostu arayüz
- **Gerçek Zamanlı Durum**: Bağlantı durumu takibi
- **Ayarlar Kaydetme**: Son kullanılan dosya yolu, port, baudrate ve pencere boyutu otomatik kaydedilir
- **Terminal Benzeri Arayüz**: XMODEM veri akışı için terminal görünümü

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:
```bash
python main_app.py
```

## Dosya Yapısı

### Ana Dosyalar
- `main_app.py` - Ana uygulama ve sayfa yönetimi (entegre edilmiş yapı)
- `gui_com_ayarlari.py` - COM port ayarları sayfası
- `serialiletisim.py` - Seri port iletişim yöneticisi (Singleton pattern)
- `xmodem_gui.py` - Orijinal XMODEM GUI (standalone versiyon)

### Yardımcı Dosyalar
- `run_app.py` - Uygulama başlatıcı script
- `run_app.bat` - Windows batch dosyası
- `test_integration.py` - Entegrasyon test scripti
- `config.py` - Ayarlar yönetimi (gizli config dosyası)
- `requirements.txt` - Python bağımlılıkları
- `README.md` - Bu dosya

## Kullanım

### Hızlı Başlangıç
```bash
# Windows için
run_app.bat

# Veya Python ile
python run_app.py

# Veya doğrudan
python main_app.py
```

### Uygulama Sayfaları

1. **Ana Sayfa**: 
   - Uygulamanın giriş noktası
   - Bağlantı durumu göstergesi
   - Diğer sayfalara geçiş butonları

2. **COM Port Ayarları**: 
   - Mevcut seri portları listele
   - Port, baudrate ve veri sıralaması ayarları
   - Bağlantı kurma/kesme işlemleri
   - Gerçek zamanlı durum takibi

3. **XMODEM İşlemleri**: 
   - Dosya seçimi ve yükleme
   - CRC32 hesaplamaları (Python ve C-style)
   - Padded dosya oluşturma
   - Detaylı hesaplama sonuçları

### Test Etme
```bash
python test_integration.py
```

## Teknik Detaylar

- PyQt5 tabanlı modern GUI
- Singleton pattern ile seri port yönetimi
- XMODEM protokolü için CRC32 hesaplamaları
- 128-byte blok yapısı ile veri işleme
- JSON tabanlı ayarlar kaydetme sistemi
- Gizli config dosyası: `~/.xmodem_gui_config.json`

## Gereksinimler

- Python 3.6+
- PyQt5
- pyserial
