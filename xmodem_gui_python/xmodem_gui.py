import sys
import os
import binascii
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QTextEdit, QMessageBox
)

BLOCK_SIZE = 128
PADDING_BYTE = 0x1A  # CTRL+Z


def split_and_pad(data: bytes, block_size=BLOCK_SIZE, pad_byte=PADDING_BYTE):
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


def compute_crc32_stream(blocks):
    crc = 0
    for b in blocks:
        crc = binascii.crc32(b, crc)
    return crc & 0xFFFFFFFF


def crc32b_style(data: bytes):
    """
    C-style CRC32 implementation equivalent to:
    uint32_t crc32b(uint32_t *start_addr, size_t total_bytes)
    """
    total_bytes = len(data)
    crc = 0xFFFFFFFF
    
    # word_count = (total_bytes + 3) / 4  # 4 byte'ı word'e yuvarla
    word_count = (total_bytes + 3) // 4
    
    for i in range(word_count):
        # 4 byte'lık word oluştur
        word_start = i * 4
        word_bytes = data[word_start:word_start + 4]
        
        # Eksik byte'ları 0 ile doldur
        while len(word_bytes) < 4:
            word_bytes += b'\x00'
        
        # word'ü MSB-first byte'lara ayır
        word = (word_bytes[0] << 24) | (word_bytes[1] << 16) | (word_bytes[2] << 8) | word_bytes[3]
        
        bytes_array = [
            (word >> 24) & 0xFF,  # MSB
            (word >> 16) & 0xFF,
            (word >> 8) & 0xFF,
            word & 0xFF           # LSB
        ]
        
        # Eğer son word dolu değilse, fazladan byte'ları toplam byte sayısına göre atla
        limit = 4
        if i == word_count - 1 and (total_bytes % 4 != 0):
            limit = total_bytes % 4
        
        for j in range(limit):
            crc ^= (bytes_array[j] << 24)  # MSB-first
            for k in range(8):
                msb = crc >> 31
                crc = (crc << 1) & 0xFFFFFFFF
                crc ^= (0 - msb) & 0x04C11DB7
    
    return crc  # output tamamlayıcı yapılmadı (PC ile uyumlu)


class XmodemGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XMODEM Padded CRC32 Hesaplayıcı")
        self.setGeometry(200, 200, 600, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Bir dosya seçin...")
        layout.addWidget(self.label)

        self.select_btn = QPushButton("Dosya Seç")
        self.select_btn.clicked.connect(self.select_file)
        layout.addWidget(self.select_btn)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "All Files (*)")
        if not path:
            return

        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okunamadı:\n{e}")
            return

        orig_len = len(data)
        blocks = split_and_pad(data)
        padded_len = len(blocks) * BLOCK_SIZE

        overall_crc32 = compute_crc32_stream(blocks)
        crc_orig = binascii.crc32(data) & 0xFFFFFFFF
        
        # C-style CRC32 hesapla (padded data için)
        padded_data = b''.join(blocks)
        crc32b_padded = crc32b_style(padded_data)
        crc32b_orig = crc32b_style(data)

        filename = os.path.basename(path)
        packet_count = len(blocks)

        out_lines = []
        out_lines.append(f"Dosya: {filename}")
        out_lines.append(f"Boyut: {orig_len} byte, Paket sayısı: {packet_count}")
        out_lines.append(f"CRC32: 0x{overall_crc32:08X}")
        out_lines.append("")
        out_lines.append("=== Detaylar ===")
        out_lines.append(f"Padded boyut: {padded_len} byte")
        out_lines.append(f"Python CRC32 (orijinal): 0x{crc_orig:08X}")
        out_lines.append(f"C-style CRC32B (padded): 0x{crc32b_padded:08X}")
        out_lines.append(f"C-style CRC32B (orijinal): 0x{crc32b_orig:08X}")

        self.result_box.setText("\n".join(out_lines))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = XmodemGui()
    win.show()
    sys.exit(app.exec_())
