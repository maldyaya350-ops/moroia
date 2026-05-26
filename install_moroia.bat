@echo off
:: فحص الصلاحيات للتأكد من تشغيله كمسؤول لتثبيت بايثون بدون مشاكل
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] Please run this script as Administrator!
    pause
    exit /b
)

echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] Python not found. Installing Python silently...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo [+] Python installed successfully!
)

echo [*] Installing MOROIA tool...
pip install moroia
echo [+] MOROIA is ready to use! Just type 'moroia'
pause