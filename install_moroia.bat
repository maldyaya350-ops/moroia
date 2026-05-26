@echo off
echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] Python not found. Installing Python silently...
    :: تحميل بايثون مصغر وثيق ومباشر
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe
    :: تثبيت بايثون في الخلفية مع تفعيل الـ PATH تلقائياً
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo [+] Python installed successfully!
)

echo [*] Installing MOROIA tool...
pip install moroia
echo [+] MOROIA is ready to use! Just type 'moroia'
pause