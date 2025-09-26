import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal, QTimer


class SerialManager(QObject):
    """
    Seri port iletişimi için singleton manager sınıfı
    """
    _instance = None
    _initialized = False
    
    # Sinyaller
    data_received = pyqtSignal(bytes)
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SerialManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            super().__init__()
            self.serial_connection = None
            self.is_connected = False
            self.endianness = True  # True = MSB First (Big Endian), False = LSB First (Little Endian)
            
            # Veri okuma timer'ı
            self.read_timer = QTimer()
            self.read_timer.timeout.connect(self.read_serial_data)
            self.read_timer.setInterval(10)  # 10ms'de bir oku
            
            SerialManager._initialized = True
    
    @classmethod
    def get_instance(cls):
        """Singleton instance'ı döndür"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_available_ports(self):
        """Mevcut seri portları listele"""
        try:
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except Exception as e:
            self.error_occurred.emit(f"Port listesi alınamadı: {str(e)}")
            return []
    
    def connect(self, port, baudrate=115200, timeout=1):
        """
        Seri port bağlantısı kur
        
        Args:
            port (str): Port adı (örn: 'COM3', '/dev/ttyUSB0')
            baudrate (int): Baudrate değeri
            timeout (float): Timeout süresi (saniye)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if self.is_connected:
                self.disconnect()
            
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            self.is_connected = True
            self.connection_changed.emit(True)
            
            # Veri okuma timer'ını başlat
            self.read_timer.start()
            
            return True, f"{port} portuna başarıyla bağlandı"
            
        except serial.SerialException as e:
            self.is_connected = False
            self.connection_changed.emit(False)
            return False, f"Bağlantı hatası: {str(e)}"
        except Exception as e:
            self.is_connected = False
            self.connection_changed.emit(False)
            return False, f"Beklenmeyen hata: {str(e)}"
    
    def disconnect(self):
        """Seri port bağlantısını kes"""
        try:
            # Veri okuma timer'ını durdur
            self.read_timer.stop()
            
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            self.is_connected = False
            self.connection_changed.emit(False)
        except Exception as e:
            self.error_occurred.emit(f"Bağlantı kesme hatası: {str(e)}")
    
    def send_data(self, data):
        """
        Veri gönder
        
        Args:
            data (bytes): Gönderilecek veri
            
        Returns:
            bool: Gönderim başarılı mı
        """
        try:
            if not self.is_connected or not self.serial_connection:
                self.error_occurred.emit("Bağlantı yok")
                return False
            
            self.serial_connection.write(data)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Veri gönderme hatası: {str(e)}")
            return False
    
    def read_serial_data(self):
        """Timer ile sürekli veri okuma"""
        try:
            if not self.is_connected or not self.serial_connection:
                return
            
            # Mevcut veri var mı kontrol et
            if self.serial_connection.in_waiting > 0:
                data = self.serial_connection.read(self.serial_connection.in_waiting)
                if data:
                    self.data_received.emit(data)
                    
        except Exception as e:
            self.error_occurred.emit(f"Veri okuma hatası: {str(e)}")
    
    def read_data(self, size=1024):
        """
        Veri oku
        
        Args:
            size (int): Okunacak byte sayısı
            
        Returns:
            bytes: Okunan veri
        """
        try:
            if not self.is_connected or not self.serial_connection:
                return b''
            
            data = self.serial_connection.read(size)
            if data:
                self.data_received.emit(data)
            return data
            
        except Exception as e:
            self.error_occurred.emit(f"Veri okuma hatası: {str(e)}")
            return b''
    
    def set_endianness(self, msb_first=True):
        """
        Veri sıralamasını ayarla
        
        Args:
            msb_first (bool): True = MSB First (Big Endian), False = LSB First (Little Endian)
        """
        self.endianness = msb_first
    
    def get_connection_info(self):
        """Bağlantı bilgilerini döndür"""
        if self.is_connected and self.serial_connection:
            return {
                'port': self.serial_connection.port,
                'baudrate': self.serial_connection.baudrate,
                'is_open': self.serial_connection.is_open
            }
        return None
    
    def is_port_available(self, port):
        """Belirtilen portun kullanılabilir olup olmadığını kontrol et"""
        try:
            test_serial = serial.Serial(port, timeout=0.1)
            test_serial.close()
            return True
        except:
            return False
