from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QFrame, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from serialiletisim import SerialManager
from config import config

class ComAyarlariSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.serial_manager = SerialManager.get_instance()
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
        
        # Başlık
        baslik = QLabel("COM PORT AYARLARI")
        baslik.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        
        ust_bar_layout.addWidget(geri_buton)
        ust_bar_layout.addWidget(baslik, alignment=Qt.AlignCenter)
        ust_bar_layout.addStretch()
        
        layout.addWidget(ust_bar)
        
        # Ana içerik
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background-color: #1a1a1a;
            color: white;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Port seçimi
        port_frame = QFrame()
        port_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 0.6);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        port_layout = QHBoxLayout(port_frame)
        
        port_label = QLabel("Port:")
        port_label.setStyleSheet("font-size: 16px;")
        self.port_selector = QComboBox()
        self.port_selector.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 5px;
                min-height: 30px;
                min-width: 150px;
            }
        """)
        
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setFixedSize(40, 30)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #00ffff;
                color: black;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #33ffff;
            }
        """)
        
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_selector)
        port_layout.addWidget(self.refresh_button)
        
        # Baudrate seçimi
        baud_frame = QFrame()
        baud_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 0.6);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        baud_layout = QHBoxLayout(baud_frame)
        
        baud_label = QLabel("Baudrate:")
        baud_label.setStyleSheet("font-size: 16px;")
        self.baudrate_selector = QComboBox()
        self.baudrate_selector.addItems([
            "110", "300", "600", "1200", "2400", "4800", "9600", "14400", 
            "19200", "38400", "57600", "115200", "230400", "460800", "921600"
        ])
        # Son kullanılan baudrate'i yükle
        last_baudrate = config.get_last_baudrate()
        self.baudrate_selector.setCurrentText(last_baudrate)
        self.baudrate_selector.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 5px;
                min-height: 30px;
                min-width: 150px;
            }
        """)
        
        baud_layout.addWidget(baud_label)
        baud_layout.addWidget(self.baudrate_selector)
        
        # Veri sıralaması seçimi
        endian_frame = QFrame()
        endian_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 0.6);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        endian_layout = QHBoxLayout(endian_frame)
        
        endian_label = QLabel("Veri Sıralaması:")
        endian_label.setStyleSheet("font-size: 16px;")
        self.endian_selector = QComboBox()
        self.endian_selector.addItems(["MSB First (Big Endian)", "LSB First (Little Endian)"])
        # Son kullanılan endianness'i yükle
        last_endianness = config.get_last_endianness()
        self.endian_selector.setCurrentIndex(last_endianness)
        self.endian_selector.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 5px;
                min-height: 30px;
                min-width: 150px;
            }
        """)
        
        endian_layout.addWidget(endian_label)
        endian_layout.addWidget(self.endian_selector)
        
        # Bağlantı butonları
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 0.6);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        
        self.connect_button = QPushButton("Bağlan")
        self.disconnect_button = QPushButton("Bağlantıyı Kes")
        self.disconnect_button.setEnabled(False)
        
        button_style = """
            QPushButton {
                background-color: #00ffff;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #33ffff;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #cccccc;
            }
        """
        
        self.connect_button.setStyleSheet(button_style)
        self.disconnect_button.setStyleSheet(button_style)
        
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        
        # Durum etiketi
        self.status_label = QLabel("Durum: Bağlı değil")
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            padding: 10px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Ana layout'a ekle
        content_layout.addWidget(port_frame)
        content_layout.addWidget(baud_frame)
        content_layout.addWidget(endian_frame)
        content_layout.addWidget(button_frame)
        content_layout.addWidget(self.status_label)
        content_layout.addStretch()
        
        layout.addWidget(content_widget)
        self.setLayout(layout)
        
        # Buton bağlantıları
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.start_connection)
        self.disconnect_button.clicked.connect(self.stop_connection)
        self.endian_selector.currentIndexChanged.connect(self.update_endianness)
        
        self.refresh_ports()
        
    def refresh_ports(self):
        """Mevcut seri portları yenile"""
        self.port_selector.clear()
        ports = self.serial_manager.get_available_ports()
        self.port_selector.addItems(ports)
        if not ports:
            self.status_label.setText("Durum: Hiçbir port bulunamadı")
        else:
            self.status_label.setText("Durum: Portlar güncellendi")
            
    def start_connection(self):
        """Seri port bağlantısını başlat"""
        port = self.port_selector.currentText()
        baudrate = int(self.baudrate_selector.currentText())
        
        success, message = self.serial_manager.connect(port, baudrate)
        if success:
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.status_label.setText(f"Durum: {message}")
            
            # Başarılı bağlantıda ayarları kaydet
            config.set_last_port(port)
            config.set_last_baudrate(str(baudrate))
        else:
            QMessageBox.warning(self, "Bağlantı Hatası", message)
            
    def stop_connection(self):
        """Seri port bağlantısını durdur"""
        self.serial_manager.disconnect()
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.status_label.setText("Durum: Bağlantı kesildi")
        
    def update_endianness(self, index):
        """Veri sıralamasını güncelle"""
        self.serial_manager.set_endianness(index == 0)  # 0 = MSB First
        # Endianness ayarını kaydet
        config.set_last_endianness(index) 