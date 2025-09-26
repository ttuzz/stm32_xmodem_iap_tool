import sys
import os
import binascii
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFrame, QStackedWidget, QMessageBox, QTextEdit, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from gui_com_ayarlari import ComAyarlariSayfasi
from serialiletisim import SerialManager
from config import config


class AnaSayfa(QWidget):
    """Ana sayfa widget'ı"""
    
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Üst bar
        ust_bar = QFrame()
        ust_bar.setStyleSheet("""
            QFrame { 
                background-color: rgba(40, 40, 40, 0.9);
                min-height: 60px;
            }
        """)
        ust_bar_layout = QHBoxLayout(ust_bar)
        ust_bar_layout.setContentsMargins(20, 0, 20, 0)
        
        # Başlık
        baslik = QLabel("XMODEM SERİ PORT UYGULAMASI")
        baslik.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 3px;
        """)
        
        ust_bar_layout.addWidget(baslik, alignment=Qt.AlignCenter)
        ust_bar_layout.addStretch()
        
        # Bağlantı durumu göstergesi
        self.connection_status = QLabel("●")
        self.connection_status.setStyleSheet("""
            color: #ff4444;
            font-size: 24px;
            font-weight: bold;
        """)
        self.connection_status.setToolTip("Bağlantı Durumu")
        
        ust_bar_layout.addWidget(self.connection_status)
        
        layout.addWidget(ust_bar)
        
        # Ana içerik
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background-color: #1a1a1a;
            color: white;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Hoş geldin mesajı
        welcome_label = QLabel("Hoş Geldiniz!")
        welcome_label.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        
        # Açıklama
        desc_label = QLabel("""
        Bu uygulama ile seri port üzerinden XMODEM protokolü ile veri transferi yapabilirsiniz.
        Önce COM port ayarlarını yapılandırın, sonra XMODEM işlemlerini gerçekleştirin.
        """)
        desc_label.setStyleSheet("""
            color: #cccccc;
            font-size: 16px;
            line-height: 1.5;
            margin-bottom: 30px;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        
        # COM Bilgileri ve Bağlantı
        com_frame = QFrame()
        com_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 0.6);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        com_layout = QVBoxLayout(com_frame)
        
        # COM bilgileri
        com_info_layout = QHBoxLayout()
        
        # Son bağlantı bilgilerini yükle
        last_conn = config.get_last_connection()
        
        # Port bilgisi
        port_text = f"Port: {last_conn['port']}" if last_conn['port'] else "Port: Seçilmedi"
        self.port_info_label = QLabel(port_text)
        self.port_info_label.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        """)
        
        # Baudrate bilgisi
        self.baudrate_info_label = QLabel(f"Baudrate: {last_conn['baudrate']}")
        self.baudrate_info_label.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        """)
        
        com_info_layout.addWidget(self.port_info_label)
        com_info_layout.addWidget(self.baudrate_info_label)
        com_info_layout.addStretch()
        
        com_layout.addLayout(com_info_layout)
        
        # Bağlantı butonları
        connect_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff00;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #33ff33;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #cccccc;
            }
        """)
        self.connect_btn.clicked.connect(self.quick_connect)
        
        self.disconnect_btn = QPushButton("Bağlantıyı Kes")
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #cccccc;
            }
        """)
        self.disconnect_btn.clicked.connect(self.quick_disconnect)
        self.disconnect_btn.setEnabled(False)
        
        connect_layout.addWidget(self.connect_btn)
        connect_layout.addWidget(self.disconnect_btn)
        connect_layout.addStretch()
        
        com_layout.addLayout(connect_layout)
        
        # Butonlar - daha küçük
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 0.6);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(10)
        
        # COM Ayarları butonu
        self.com_settings_btn = QPushButton("COM Port Ayarları")
        self.com_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ffff;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #33ffff;
            }
        """)
        self.com_settings_btn.clicked.connect(self.ana_pencere.com_ayarlarina_git)
        
        # XMODEM İşlemleri butonu
        self.xmodem_btn = QPushButton("XMODEM İşlemleri")
        self.xmodem_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b35;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff8c5a;
            }
        """)
        self.xmodem_btn.clicked.connect(self.ana_pencere.xmodem_sayfasina_git)
        
        button_layout.addWidget(self.com_settings_btn)
        button_layout.addWidget(self.xmodem_btn)
        
        # Ana layout'a ekle
        content_layout.addWidget(welcome_label)
        content_layout.addWidget(desc_label)
        content_layout.addWidget(com_frame)
        content_layout.addWidget(button_frame)
        content_layout.addStretch()
        
        layout.addWidget(content_widget)
        self.setLayout(layout)
    
    def update_connection_status(self, connected):
        """Bağlantı durumunu güncelle"""
        if connected:
            self.connection_status.setStyleSheet("""
                color: #44ff44;
                font-size: 24px;
                font-weight: bold;
            """)
            self.connection_status.setToolTip("Bağlı")
        else:
            self.connection_status.setStyleSheet("""
                color: #ff4444;
                font-size: 24px;
                font-weight: bold;
            """)
            self.connection_status.setToolTip("Bağlı değil")
    
    def quick_connect(self):
        """Hızlı bağlantı - son kullanılan ayarları kullan"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Son bağlantı bilgilerini al
        last_connection = config.get_last_connection()
        port = last_connection.get("port", "")
        baudrate = last_connection.get("baudrate", "115200")
        
        # Eğer daha önce kaydedilmiş port yoksa, kullanıcıdan iste
        if not port:
            from PyQt5.QtWidgets import QInputDialog
            ports = self.ana_pencere.serial_manager.get_available_ports()
            if not ports:
                QMessageBox.warning(self, "Uyarı", "Hiçbir COM port bulunamadı!")
                return
            
            port, ok = QInputDialog.getItem(self, "Port Seç", "COM Port seçin:", ports, 0, False)
            if not ok:
                return
        
        # Bağlantı kur
        success, message = self.ana_pencere.serial_manager.connect(port, int(baudrate))
        if success:
            # Bağlantı bilgilerini kaydet
            config.set_last_connection(port, baudrate)
            
            self.port_info_label.setText(f"Port: {port}")
            self.port_info_label.setStyleSheet("""
                color: #00ff00;
                font-size: 12px;
                font-family: 'Courier New', monospace;
            """)
            self.baudrate_info_label.setText(f"Baudrate: {baudrate}")
            self.baudrate_info_label.setStyleSheet("""
                color: #00ff00;
                font-size: 12px;
                font-family: 'Courier New', monospace;
            """)
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Bağlantı Hatası", message)
    
    def quick_disconnect(self):
        """Hızlı bağlantı kesme"""
        self.ana_pencere.serial_manager.disconnect()
        self.port_info_label.setText("Port: Bağlı değil")
        self.port_info_label.setStyleSheet("""
            color: #ff4444;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        """)
        self.baudrate_info_label.setText("Baudrate: -")
        self.baudrate_info_label.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        """)
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)


class XmodemSayfasi(QWidget):
    """XMODEM işlemleri sayfası"""
    
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.serial_manager = SerialManager.get_instance()
        self.initUI()
        
        # Keyboard event'ları yakalamak için focus policy ayarla
        self.setFocusPolicy(Qt.StrongFocus)
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Üst bar
        ust_bar = QFrame()
        ust_bar.setStyleSheet("""
            QFrame { 
                background-color: rgba(40, 40, 40, 0.9);
                min-height: 50px;
            }
        """)
        ust_bar_layout = QHBoxLayout(ust_bar)
        ust_bar_layout.setContentsMargins(10, 0, 10, 0)
        
        # Geri butonu
        geri_buton = QPushButton("←")
        geri_buton.setFixedSize(40, 40)
        geri_buton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 24px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.1);
                border-radius: 20px;
            }
        """)
        geri_buton.clicked.connect(self.ana_pencere.ana_sayfaya_don)
        
        # XMODEM İşlemleri yazısı (geri butonun yanında)
        xmodem_label = QLabel("XMODEM İşlemleri")
        xmodem_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            margin-left: 10px;
        """)
        
        # Başlık - dosya yolu gösterilecek
        self.baslik_label = QLabel("Dosya Seçilmedi")
        self.baslik_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        
        ust_bar_layout.addWidget(geri_buton)
        ust_bar_layout.addWidget(xmodem_label)
        ust_bar_layout.addStretch()
        
        layout.addWidget(ust_bar)
        
        # Ana içerik - XMODEM GUI'den alınan içerik
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background-color: #1a1a1a;
            color: white;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # XMODEM bilgileri - küçük puntoda
        self.dosya_adi_label = QLabel("Dosya Seçilmedi")
        self.dosya_adi_label.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        content_layout.addWidget(self.dosya_adi_label)
        
        # Dosya seçme butonu - küçük
        self.select_btn = QPushButton("Dosya Seç")
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ffff;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #33ffff;
            }
        """)
        self.select_btn.clicked.connect(self.select_file)
        content_layout.addWidget(self.select_btn)
        
        # XMODEM bilgileri küçük puntoda - başlangıçta gizli
        self.xmodem_info_label = QLabel("")
        self.xmodem_info_label.setStyleSheet("""
            color: #888888;
            font-size: 10px;
            font-family: 'Courier New', monospace;
            background-color: #2a2a2a;
            padding: 8px;
            border-radius: 5px;
            margin-bottom: 15px;
        """)
        self.xmodem_info_label.setWordWrap(True)
        self.xmodem_info_label.hide()  # Başlangıçta gizle
        content_layout.addWidget(self.xmodem_info_label)
        
        # Terminal alanı - Putty benzeri
        terminal_frame = QFrame()
        terminal_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 0.6);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        terminal_layout = QVBoxLayout(terminal_frame)
        
        # Terminal başlığını kaldırdık
        
        # Terminal çıktı alanı
        self.terminal_box = QTextEdit()
        self.terminal_box.setReadOnly(True)
        self.terminal_box.setMinimumHeight(300)
        self.terminal_box.setAcceptRichText(True)  # HTML desteği
        self.terminal_box.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00ff00;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }
        """)
        terminal_layout.addWidget(self.terminal_box)
        
        # Input alanı ve gönder butonu
        input_layout = QVBoxLayout()
        
        # Hex/Text seçimi
        checkbox_layout = QHBoxLayout()
        self.hex_mode_checkbox = QCheckBox("Hex Modu")
        self.hex_mode_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #555555;
                background-color: #333333;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #00ffff;
                background-color: #00ffff;
                border-radius: 3px;
            }
        """)
        self.hex_mode_checkbox.stateChanged.connect(self.update_input_placeholder)
        checkbox_layout.addWidget(self.hex_mode_checkbox)
        checkbox_layout.addStretch()
        input_layout.addLayout(checkbox_layout)
        
        # Input ve gönder butonu
        input_row_layout = QHBoxLayout()
        
        self.terminal_input = QLineEdit()
        self.terminal_input.setPlaceholderText("Komut girin...")
        self.terminal_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #00ffff;
            }
        """)
        self.terminal_input.returnPressed.connect(self.send_terminal_data)
        
        self.send_button = QPushButton("Gönder")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #00ffff;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #33ffff;
            }
        """)
        self.send_button.clicked.connect(self.send_terminal_data)
        
        input_row_layout.addWidget(self.terminal_input)
        input_row_layout.addWidget(self.send_button)
        input_layout.addLayout(input_row_layout)
        terminal_layout.addLayout(input_layout)
        
        # Terminal kontrol butonları
        terminal_buttons_layout = QHBoxLayout()
        
        self.clear_terminal_btn = QPushButton("Terminali Temizle")
        self.clear_terminal_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        self.clear_terminal_btn.clicked.connect(self.clear_terminal)
        
        self.start_xmodem_btn = QPushButton("XMODEM Transfer Başlat")
        self.start_xmodem_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b35;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff8c5a;
            }
        """)
        self.start_xmodem_btn.clicked.connect(self.start_xmodem_transfer)
        self.start_xmodem_btn.setEnabled(False)
        
        terminal_buttons_layout.addWidget(self.clear_terminal_btn)
        terminal_buttons_layout.addWidget(self.start_xmodem_btn)
        terminal_buttons_layout.addStretch()
        
        terminal_layout.addLayout(terminal_buttons_layout)
        
        content_layout.addWidget(terminal_frame)
        
        layout.addWidget(content_widget)
        self.setLayout(layout)
    
    def select_file(self):
        """Dosya seçme işlemi - XMODEM GUI'den alınan kod"""
        from PyQt5.QtWidgets import QFileDialog
        
        # Son kullanılan dizini al
        last_file = config.get_last_file_path()
        start_dir = os.path.dirname(last_file) if last_file and os.path.exists(last_file) else ""
        
        path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", start_dir, "All Files (*)")
        if not path:
            return

        # Dosya yolunu gizli olarak kaydet
        config.set_last_file_path(path)

        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okunamadı:\n{e}")
            return

        # XMODEM hesaplamaları
        BLOCK_SIZE = 128
        PADDING_BYTE = 0x1A
        
        orig_len = len(data)
        blocks = self.split_and_pad(data, BLOCK_SIZE, PADDING_BYTE)
        padded_len = len(blocks) * BLOCK_SIZE
        packet_count = len(blocks)

        overall_crc32 = self.compute_crc32_stream(blocks)
        crc_orig = binascii.crc32(data) & 0xFFFFFFFF
        
        # C-style CRC32 hesapla (padded data için)
        padded_data = b''.join(blocks)
        crc32b_padded = self.crc32b_style(padded_data)
        crc32b_orig = self.crc32b_style(data)

        # XMODEM bilgilerini küçük label'a yaz ve göster
        info_text = f"<span style='font-size: 14px;'>Orijinal boyut: {orig_len} byte | Padded boyut: {padded_len} byte | Paket sayısı: {packet_count} adet | CRC32: 0x{overall_crc32:08X}</span>"
        self.xmodem_info_label.setText(info_text)
        self.xmodem_info_label.setStyleSheet("""
            color: #00ff00;
            font-size: 10px;
            font-family: 'Courier New', monospace;
            background-color: #2a2a2a;
            padding: 8px;
            border-radius: 5px;
            margin-bottom: 15px;
        """)
        self.xmodem_info_label.show()  # Göster

        # XMODEM transfer butonunu aktif et
        self.start_xmodem_btn.setEnabled(True)
        
        # Başlığı güncelle
        self.update_title(path)
        
        # Terminal'e bilgi ekle
        self.add_to_terminal(f"[INFO] Dosya seçildi: {os.path.basename(path)}", "info")
        self.add_to_terminal(f"[INFO] Boyut: {orig_len} byte, Paket sayısı: {packet_count}", "info")
        self.add_to_terminal(f"[INFO] CRC32: 0x{overall_crc32:08X}", "info")
        self.add_to_terminal("", "info")
    
    def auto_load_file(self, file_path):
        """Dosyayı otomatik olarak yükle (XMODEM sayfası açıldığında)"""
        if not file_path or not os.path.exists(file_path):
            return
        
        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except Exception:
            return  # Hata varsa sessizce geç

        # XMODEM hesaplamaları (select_file ile aynı)
        BLOCK_SIZE = 128
        PADDING_BYTE = 0x1A
        
        orig_len = len(data)
        blocks = self.split_and_pad(data, BLOCK_SIZE, PADDING_BYTE)
        padded_len = len(blocks) * BLOCK_SIZE
        packet_count = len(blocks)

        overall_crc32 = self.compute_crc32_stream(blocks)
        
        # XMODEM bilgilerini küçük label'a yaz ve göster
        info_text = f"<span style='font-size: 14px;'>Orijinal boyut: {orig_len} byte | Padded boyut: {padded_len} byte | Paket sayısı: {packet_count} adet | CRC32: 0x{overall_crc32:08X}</span>"
        self.xmodem_info_label.setText(info_text)
        self.xmodem_info_label.setStyleSheet("""
            color: #00ff00;
            font-size: 10px;
            font-family: 'Courier New', monospace;
            background-color: #2a2a2a;
            padding: 8px;
            border-radius: 5px;
            margin-bottom: 15px;
        """)
        self.xmodem_info_label.show()

        # XMODEM transfer butonunu aktif et
        self.start_xmodem_btn.setEnabled(True)
        
        # Terminal'e sessizce bilgi ekle (son dosya otomatik yüklendi)
        filename = os.path.basename(file_path)
        self.add_to_terminal(f"Otomatik yüklendi: {filename} ({orig_len} byte, {packet_count} paket)", "info")
    
    def add_to_terminal(self, message, message_type="info", update_last=False):
        """Terminal'e mesaj ekle"""
        # Renk kodlaması
        if message_type == "rx":
            # Gelen veri - yeşil
            formatted_message = f'<span style="color: #00ff00;">{message}</span>'
        elif message_type == "tx":
            # Giden veri - mavi
            formatted_message = f'<span style="color: #00ffff;">{message}</span>'
        elif message_type == "tx_progress":
            # Transfer progress - sarı
            formatted_message = f'<span style="color: #ffff00;">{message}</span>'
        elif message_type == "error":
            # Hata - kırmızı
            formatted_message = f'<span style="color: #ff4444;">{message}</span>'
        elif message_type == "success":
            # Başarı - sarı
            formatted_message = f'<span style="color: #ffff00;">{message}</span>'
        else:
            # Bilgi - beyaz
            formatted_message = f'<span style="color: #ffffff;">{message}</span>'
        
        if update_last and hasattr(self, '_last_progress_line'):
            # Son satırı güncelle (progress için)
            cursor = self.terminal_box.textCursor()
            cursor.movePosition(cursor.End)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.insertHtml(formatted_message + "<br>")
        else:
            self.terminal_box.append(formatted_message)
            if message_type == "tx_progress":
                self._last_progress_line = True
        
        # Otomatik scroll
        cursor = self.terminal_box.textCursor()
        cursor.movePosition(cursor.End)
        self.terminal_box.setTextCursor(cursor)
    
    def update_last_terminal_line(self, message, message_type="info"):
        """Son terminal satırını güncelle (progress bar için)"""
        # Renk kodlaması
        if message_type == "tx_progress":
            formatted_message = f'<span style="color: #ffff00;">{message}</span>'
        else:
            formatted_message = f'<span style="color: #ffffff;">{message}</span>'
        
        # Progress bar için özel mantık - sadece kendi satırını güncelle
        if hasattr(self, '_has_progress_line') and self._has_progress_line:
            # Son progress satırını bul ve güncelle
            cursor = self.terminal_box.textCursor()
            cursor.movePosition(cursor.End)
            
            # Sondan başlayarak progress satırını bul
            document = self.terminal_box.document()
            block = document.lastBlock()
            
            while block.isValid():
                block_text = block.text()
                if "Progress:" in block_text:
                    # Bu progress satırı, güncelle
                    cursor.setPosition(block.position())
                    cursor.select(cursor.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.insertHtml(formatted_message)
                    break
                block = block.previous()
            else:
                # Progress satırı bulunamadı, yeni satır ekle
                self.terminal_box.append(formatted_message)
        else:
            # İlk progress satırı veya normal mesaj
            self.terminal_box.append(formatted_message)
            if message_type == "tx_progress":
                self._has_progress_line = True
        
        # Otomatik scroll
        cursor = self.terminal_box.textCursor()
        cursor.movePosition(cursor.End)
        self.terminal_box.setTextCursor(cursor)
    
    def update_title(self, file_path):
        """Başlığı dosya yolu ile güncelle"""
        if file_path and os.path.exists(file_path):
            filename = os.path.basename(file_path)
            # Dosya adı çok uzunsa kısalt
            if len(filename) > 40:
                filename = filename[:37] + "..."
            self.dosya_adi_label.setText(filename)
        else:
            self.dosya_adi_label.setText("Dosya Seçilmedi")
    
    def clear_terminal(self):
        """Terminal'i temizle"""
        self.terminal_box.clear()
    
    def update_input_placeholder(self):
        """Input placeholder'ını güncelle"""
        if self.hex_mode_checkbox.isChecked():
            self.terminal_input.setPlaceholderText("Hex veri (örn: 01 02 03)")
        else:
            self.terminal_input.setPlaceholderText("Komut girin...")
    
    def send_terminal_data(self):
        """Terminal'den veri gönder"""
        if not self.serial_manager.is_connected:
            self.add_to_terminal("[ERROR] Seri port bağlantısı yok!", "error")
            return
        
        data_text = self.terminal_input.text().strip()
        if not data_text:
            return
        
        try:
            if self.hex_mode_checkbox.isChecked():
                # Hex modu
                hex_values = data_text.replace(' ', '').replace('\t', '')
                if len(hex_values) % 2 == 0:
                    data_bytes = bytes.fromhex(hex_values)
                    self.add_to_terminal(f"{data_text.upper()}", "tx")
                else:
                    self.add_to_terminal("[ERROR] Geçersiz hex formatı!", "error")
                    return
            else:
                # Text modu - CR/LF duyarlı
                if '\\n' in data_text:
                    data_text = data_text.replace('\\n', '\n')
                if '\\r' in data_text:
                    data_text = data_text.replace('\\r', '\r')
                if '\\t' in data_text:
                    data_text = data_text.replace('\\t', '\t')
                
                data_bytes = data_text.encode('utf-8')
                self.add_to_terminal(f"{data_text}", "tx")
            
            # Veriyi gönder
            if not self.serial_manager.send_data(data_bytes):
                self.add_to_terminal("[ERROR] Veri gönderilemedi", "error")
            
            # Input'u temizle
            self.terminal_input.clear()
            
        except ValueError as e:
            self.add_to_terminal(f"[ERROR] Geçersiz veri formatı: {e}", "error")
        except Exception as e:
            self.add_to_terminal(f"[ERROR] Gönderim hatası: {e}", "error")
    
    def start_xmodem_transfer(self):
        """XMODEM transfer başlat"""
        if not self.serial_manager.is_connected:
            QMessageBox.warning(self, "Uyarı", "Önce seri port bağlantısı kurun!")
            return
        
        # Son yüklenen dosyayı kontrol et
        last_file = config.get_last_file_path()
        if not last_file or not os.path.exists(last_file):
            QMessageBox.warning(self, "Uyarı", "Önce bir dosya seçin!")
            return
        
        # XMODEM transfer öncesi terminali temizle
        self.clear_terminal()
        
        # Dosyayı oku ve bloklara böl
        try:
            with open(last_file, "rb") as f:
                data = f.read()
            
            blocks = self.split_and_pad(data)
            
            # XMODEM transfer'i başlat
            self.current_blocks = blocks
            self.current_block_index = 0
            self.transfer_active = True
            self._last_progress = False
            self._has_progress_line = False  # Progress satır takibi sıfırla
            
            # İlk bloğu gönder
            self.send_next_block()
            
        except Exception as e:
            self.add_to_terminal(f"[ERROR] Dosya okuma hatası: {e}", "error")
    
    def send_next_block(self):
        """Sonraki XMODEM bloğunu gönder"""
        if not hasattr(self, 'current_blocks') or self.current_block_index >= len(self.current_blocks):
            return
        
        block_data = self.current_blocks[self.current_block_index]
        block_num = (self.current_block_index + 1) & 0xFF
        block_num_complement = (255 - block_num) & 0xFF
        
        # CRC-16 hesapla
        crc = self.calculate_crc16(block_data)
        
        # XMODEM paketi oluştur: SOH + block_num + complement + data + CRC
        packet = bytes([0x01, block_num, block_num_complement]) + block_data + bytes([crc >> 8, crc & 0xFF])
        
        # Paketi gönder
        if self.serial_manager.send_data(packet):
            # Progress hesapla
            total_blocks = len(self.current_blocks)
            percent = (block_num * 100) // total_blocks
            
            # Sadece belirli durumlarda progress göster:
            # - İlk blok, son blok, %10'un katları veya her 10 blokta bir
            should_show = (
                block_num == 1 or  # İlk blok
                block_num == total_blocks or  # Son blok  
                percent % 10 == 0 or  # %10, %20, %30... 
                block_num % 10 == 0  # Her 10 blokta bir
            )
            
            if should_show:
                # Progress bar oluştur
                bar_length = 30
                filled_length = int(bar_length * percent // 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                progress_msg = f"Progress: [{bar}] {percent}% ({block_num}/{total_blocks})"
                
                if hasattr(self, '_last_progress') and self._last_progress:
                    self.update_last_terminal_line(progress_msg, "tx_progress")
                else:
                    self.add_to_terminal(progress_msg, "tx_progress")
                    self._last_progress = True
            
            self.current_block_index += 1
        else:
            self.add_to_terminal("[ERROR] Blok gönderilemedi", "error")
    
    def calculate_crc16(self, data):
        """CRC-16 hesapla (XMODEM)"""
        crc = 0
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return crc
    
    def send_current_block_again(self):
        """Mevcut bloğu tekrar gönder (NAK alındığında)"""
        if self.current_block_index > 0:
            self.current_block_index -= 1
            self.send_next_block()
    
    def send_eot(self):
        """EOT (End of Transmission) gönder"""
        eot_byte = bytes([0x04])
        if self.serial_manager.send_data(eot_byte):
            self.add_to_terminal("Transfer tamamlandı - EOT gönderildi", "success")
            self.transfer_active = False
        else:
            self.add_to_terminal("[ERROR] EOT gönderilemedi", "error")
    
    def split_and_pad(self, data: bytes, block_size=128, pad_byte=0x1A):
        """XMODEM GUI'den alınan fonksiyon"""
        blocks = []
        total_len = len(data)
        full_blocks = total_len // block_size
        remainder = total_len % block_size

        for i in range(full_blocks):
            start = i * block_size
            blocks.append(data[start:start + block_size])

        if remainder != 0:
            last = data[full_blocks * block_size:]
            padded_last = last + bytes([pad_byte]) * (block_size - remainder)
            blocks.append(padded_last)

        return blocks

    def compute_crc32_stream(self, blocks):
        """XMODEM GUI'den alınan fonksiyon"""
        crc = 0
        for b in blocks:
            crc = binascii.crc32(b, crc)
        return crc & 0xFFFFFFFF

    def crc32b_style(self, data: bytes):
        """XMODEM GUI'den alınan fonksiyon"""
        total_bytes = len(data)
        crc = 0xFFFFFFFF
        
        word_count = (total_bytes + 3) // 4
        
        for i in range(word_count):
            word_start = i * 4
            word_bytes = data[word_start:word_start + 4]
            
            while len(word_bytes) < 4:
                word_bytes += b'\x00'
            
            word = (word_bytes[0] << 24) | (word_bytes[1] << 16) | (word_bytes[2] << 8) | word_bytes[3]
            
            bytes_array = [
                (word >> 24) & 0xFF,
                (word >> 16) & 0xFF,
                (word >> 8) & 0xFF,
                word & 0xFF
            ]
            
            limit = 4
            if i == word_count - 1 and (total_bytes % 4 != 0):
                limit = total_bytes % 4
            
            for j in range(limit):
                crc ^= (bytes_array[j] << 24)
                for k in range(8):
                    msb = crc >> 31
                    crc = (crc << 1) & 0xFFFFFFFF
                    crc ^= (0 - msb) & 0x04C11DB7
        
        return crc
    
    def keyPressEvent(self, event):
        """Klavye tuşu basıldığında çağrılır"""
        # Enter tuşu kontrolü
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Enter basıldığında veri gönder
            self.send_terminal_data()
        else:
            # Diğer tuşlar için karakteri input'a ekle
            text = event.text()
            if text and text.isprintable():
                # Mevcut text al
                current_text = self.terminal_input.text()
                # Cursor pozisyonunu al
                cursor_pos = self.terminal_input.cursorPosition()
                # Yeni karakteri cursor pozisyonuna ekle
                new_text = current_text[:cursor_pos] + text + current_text[cursor_pos:]
                self.terminal_input.setText(new_text)
                # Cursor'ı yeni pozisyona ayarla
                self.terminal_input.setCursorPosition(cursor_pos + 1)
                # Input'a focus ver
                self.terminal_input.setFocus()
        
        # Event'ı parent'a gönder
        super().keyPressEvent(event)


class MainApp(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        self.serial_manager = SerialManager.get_instance()
        self.initUI()
        self.setup_connections()
    
    def initUI(self):
        self.setWindowTitle("XMODEM Seri Port Uygulaması")
        
        # Son pencere geometrisini yükle
        geometry = config.get_window_geometry()
        self.setGeometry(geometry["x"], geometry["y"], geometry["width"], geometry["height"])
        self.setMinimumSize(800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Stacked widget - sayfa yöneticisi
        self.stacked_widget = QStackedWidget()
        
        # Sayfaları oluştur
        self.ana_sayfa = AnaSayfa(self)
        self.com_ayarlari_sayfasi = ComAyarlariSayfasi(self)
        self.xmodem_sayfasi = XmodemSayfasi(self)
        
        # Sayfaları ekle
        self.stacked_widget.addWidget(self.ana_sayfa)
        self.stacked_widget.addWidget(self.com_ayarlari_sayfasi)
        self.stacked_widget.addWidget(self.xmodem_sayfasi)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_widget)
        
        # Başlangıçta ana sayfayı göster
        self.stacked_widget.setCurrentWidget(self.ana_sayfa)
        
        # Pencere stilini ayarla
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
        """)
    
    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        self.serial_manager.connection_changed.connect(self.on_connection_changed)
        self.serial_manager.error_occurred.connect(self.on_error_occurred)
        self.serial_manager.data_received.connect(self.on_data_received)
    
    def ana_sayfaya_don(self):
        """Ana sayfaya dön"""
        self.stacked_widget.setCurrentWidget(self.ana_sayfa)
    
    def com_ayarlarina_git(self):
        """COM ayarları sayfasına git"""
        self.stacked_widget.setCurrentWidget(self.com_ayarlari_sayfasi)
    
    def xmodem_sayfasina_git(self):
        """XMODEM sayfasına git"""
        self.stacked_widget.setCurrentWidget(self.xmodem_sayfasi)
        
        # Keyboard event'ları yakalamak için focus ver
        self.xmodem_sayfasi.setFocus()
        
        # Son açılmış dosya varsa başlığı güncelle ve otomatik yükle
        last_file = config.get_last_file_path()
        if last_file and os.path.exists(last_file):
            # Başlığı güncelle
            self.xmodem_sayfasi.update_title(last_file)
            # Dosyayı otomatik olarak yükle
            self.xmodem_sayfasi.auto_load_file(last_file)
        else:
            # Dosya yoksa varsayılan başlığı göster
            self.xmodem_sayfasi.update_title(None)
    
    def on_error_occurred(self, error_message):
        """Hata oluştuğunda"""
        QMessageBox.warning(self, "Hata", error_message)
    
    def on_data_received(self, data):
        """Seri porttan veri alındığında"""
        # XMODEM sayfasındaysa terminal'e ekle
        if self.stacked_widget.currentWidget() == self.xmodem_sayfasi:
            # XMODEM protokol kontrolü
            if hasattr(self.xmodem_sayfasi, 'transfer_active') and self.xmodem_sayfasi.transfer_active:
                for byte in data:
                    if byte == 0x15:  # NAK - tekrar gönder
                        self.xmodem_sayfasi.add_to_terminal("NAK alındı - tekrar gönderiliyor", "rx")
                        self.xmodem_sayfasi.send_current_block_again()
                    elif byte == 0x06:  # ACK - sonraki blok
                        if self.xmodem_sayfasi.current_block_index < len(self.xmodem_sayfasi.current_blocks):
                            self.xmodem_sayfasi.send_next_block()
                        else:
                            # Transfer tamamlandı - EOT gönder
                            self.xmodem_sayfasi.add_to_terminal("Transfer tamamlanıyor...", "success")
                            self.xmodem_sayfasi.send_eot()
                    elif byte == 0x18:  # CAN - iptal
                        self.xmodem_sayfasi.add_to_terminal("Transfer iptal edildi (CAN alındı)", "error")
                        self.xmodem_sayfasi.transfer_active = False
                    else:
                        # Diğer karakterleri göster
                        if 32 <= byte <= 126:
                            self.xmodem_sayfasi.add_to_terminal(chr(byte), "rx")
                        else:
                            self.xmodem_sayfasi.add_to_terminal(f"\\x{byte:02X}", "rx")
            else:
                # Normal terminal modu - CR/LF düzeltmesi
                try:
                    # Önce bytes'ı string'e çevir
                    decoded_chars = []
                    for b in data:
                        if 32 <= b <= 126:  # Yazdırılabilir ASCII
                            decoded_chars.append(chr(b))
                        elif b == 10:  # LF (\n)
                            decoded_chars.append('\n')  
                        elif b == 13:  # CR (\r) - genellikle LF ile birlikte gelir
                            decoded_chars.append('\n')  # CR'ı da newline olarak işle
                        elif b == 9:   # TAB
                            decoded_chars.append('\t')
                        else:
                            decoded_chars.append(f'\\x{b:02X}')
                    
                    text_data = ''.join(decoded_chars)
                    
                    # CRLF'yi tek newline'a çevir
                    text_data = text_data.replace('\n\n', '\n')  # Ardışık \n\n'leri tek \n yap
                    
                except:
                    text_data = "."
                
                # Veri buffer'a ekle
                if not hasattr(self.xmodem_sayfasi, '_data_buffer'):
                    self.xmodem_sayfasi._data_buffer = ""
                
                self.xmodem_sayfasi._data_buffer += text_data
                
                # Tam satırları işle
                while '\n' in self.xmodem_sayfasi._data_buffer:
                    line, self.xmodem_sayfasi._data_buffer = self.xmodem_sayfasi._data_buffer.split('\n', 1)
                    if line.strip():  # Boş olmayan satırları göster
                        self.xmodem_sayfasi.add_to_terminal(line.strip(), "rx")
                
                # Eğer buffer çok uzunsa ve newline yoksa, zorla göster
                if len(self.xmodem_sayfasi._data_buffer) > 100:
                    if self.xmodem_sayfasi._data_buffer.strip():
                        self.xmodem_sayfasi.add_to_terminal(self.xmodem_sayfasi._data_buffer.strip(), "rx")
                    self.xmodem_sayfasi._data_buffer = ""
    
    def on_connection_changed(self, connected):
        """Bağlantı durumu değiştiğinde"""
        self.ana_sayfa.update_connection_status(connected)
        
        # Ana sayfadaki COM bilgilerini güncelle
        if connected:
            connection_info = self.serial_manager.get_connection_info()
            if connection_info:
                self.ana_sayfa.port_info_label.setText(f"Port: {connection_info['port']}")
                self.ana_sayfa.port_info_label.setStyleSheet("""
                    color: #00ff00;
                    font-size: 12px;
                    font-family: 'Courier New', monospace;
                """)
                self.ana_sayfa.baudrate_info_label.setText(f"Baudrate: {connection_info['baudrate']}")
                self.ana_sayfa.baudrate_info_label.setStyleSheet("""
                    color: #00ff00;
                    font-size: 12px;
                    font-family: 'Courier New', monospace;
                """)
                self.ana_sayfa.connect_btn.setEnabled(False)
                self.ana_sayfa.disconnect_btn.setEnabled(True)
        else:
            self.ana_sayfa.port_info_label.setText("Port: Bağlı değil")
            self.ana_sayfa.port_info_label.setStyleSheet("""
                color: #ff4444;
                font-size: 12px;
                font-family: 'Courier New', monospace;
            """)
            self.ana_sayfa.baudrate_info_label.setText("Baudrate: -")
            self.ana_sayfa.baudrate_info_label.setStyleSheet("""
                color: #888888;
                font-size: 12px;
                font-family: 'Courier New', monospace;
            """)
            self.ana_sayfa.connect_btn.setEnabled(True)
            self.ana_sayfa.disconnect_btn.setEnabled(False)
        
        # XMODEM sayfasındaysa terminal'e mesaj ekle
        if self.stacked_widget.currentWidget() == self.xmodem_sayfasi:
            if connected:
                self.xmodem_sayfasi.add_to_terminal("[CONNECT] Seri port bağlantısı kuruldu", "success")
            else:
                self.xmodem_sayfasi.add_to_terminal("[DISCONNECT] Seri port bağlantısı kesildi", "error")
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        # Pencere geometrisini kaydet
        geometry = self.geometry()
        config.set_window_geometry(
            geometry.x(), geometry.y(), 
            geometry.width(), geometry.height()
        )
        
        self.serial_manager.disconnect()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Uygulama stilini ayarla
    app.setStyle('Fusion')
    
    # Ana pencereyi oluştur ve göster
    window = MainApp()
    window.show()
    
    sys.exit(app.exec_())
