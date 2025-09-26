@echo off
echo XMODEM Seri Port Uygulamasi baslatiliyor...
echo.

REM Python'un yuklu olup olmadigini kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python yuklu degil!
    echo Lutfen Python'u yukleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Gerekli paketleri yukle
echo Gerekli paketler kontrol ediliyor...
pip install -r requirements.txt

REM Uygulamayi baslat
echo.
echo Uygulama baslatiliyor...
python run_app.py

pause
