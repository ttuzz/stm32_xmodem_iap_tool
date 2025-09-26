import os
import json
from pathlib import Path


class ConfigManager:
    """Uygulama ayarlarını yöneten sınıf"""
    
    def __init__(self):
        self.config_file = Path.home() / ".xmodem_gui_config.json"
        self.config = self.load_config()
    
    def load_config(self):
        """Konfigürasyon dosyasını yükle"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Varsayılan konfigürasyon
        return {
            "last_file_path": "",
            "last_port": "",
            "last_baudrate": "115200",
            "last_endianness": 0,  # 0 = MSB First, 1 = LSB First
            "last_connection": {
                "port": "",
                "baudrate": "115200"
            },
            "window_geometry": {
                "x": 100,
                "y": 100,
                "width": 900,
                "height": 700
            }
        }
    
    def save_config(self):
        """Konfigürasyonu kaydet"""
        try:
            # Gizli dosya oluştur
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Konfigürasyon kaydedilemedi: {e}")
    
    def get_last_file_path(self):
        """Son kullanılan dosya yolunu al"""
        return self.config.get("last_file_path", "")
    
    def set_last_file_path(self, file_path):
        """Son kullanılan dosya yolunu kaydet"""
        self.config["last_file_path"] = file_path
        self.save_config()
    
    def get_last_port(self):
        """Son kullanılan port'u al"""
        return self.config.get("last_port", "")
    
    def set_last_port(self, port):
        """Son kullanılan port'u kaydet"""
        self.config["last_port"] = port
        self.save_config()
    
    def get_last_baudrate(self):
        """Son kullanılan baudrate'i al"""
        return self.config.get("last_baudrate", "115200")
    
    def set_last_baudrate(self, baudrate):
        """Son kullanılan baudrate'i kaydet"""
        self.config["last_baudrate"] = baudrate
        self.save_config()
    
    def get_last_endianness(self):
        """Son kullanılan endianness'i al"""
        return self.config.get("last_endianness", 0)
    
    def set_last_endianness(self, endianness):
        """Son kullanılan endianness'i kaydet"""
        self.config["last_endianness"] = endianness
        self.save_config()
    
    def get_window_geometry(self):
        """Pencere geometrisini al"""
        return self.config.get("window_geometry", {
            "x": 100, "y": 100, "width": 900, "height": 700
        })
    
    def set_window_geometry(self, x, y, width, height):
        """Pencere geometrisini kaydet"""
        self.config["window_geometry"] = {
            "x": x, "y": y, "width": width, "height": height
        }
        self.save_config()
    
    def get_last_connection(self):
        """Son bağlantı bilgilerini al"""
        return self.config.get("last_connection", {"port": "", "baudrate": "115200"})
    
    def set_last_connection(self, port, baudrate):
        """Son bağlantı bilgilerini kaydet"""
        self.config["last_connection"] = {
            "port": port,
            "baudrate": str(baudrate)
        }
        self.save_config()
    
    def clear_config(self):
        """Konfigürasyonu temizle"""
        self.config = {
            "last_file_path": "",
            "last_port": "",
            "last_baudrate": "115200",
            "last_endianness": 0,
            "window_geometry": {
                "x": 100, "y": 100, "width": 900, "height": 700
            }
        }
        self.save_config()


# Global config instance
config = ConfigManager()
