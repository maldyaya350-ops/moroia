@echo off
:: =================================================================
::       MOROIA SYSTEM LAUNCHER & AUTO-ELEVATOR v1.9.1
:: =================================================================
title Moroia Premium Launcher v1.9.1
color 0B

:: 1️⃣ خطوة الحماية: التأكد من تشغيل الملف كمسؤول (Run as Administrator)
echo [*] Checking System Privileges...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [+] Administrator privileges confirmed. Proceeding...
    goto :launch
) else (
    echo [!] WARNING: Administrator privileges required for Deep Fix & Cleaning.
    echo [*] Attempting to elevate permissions automatically...
    goto :elevate
)

:elevate
    :: عمل سكربت VBS مؤقت لإجبار الويندوز على إظهار نافذة الـ UAC للمسؤول
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "cmd.exe", "/c """"%~s0""""", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:launch
cls
echo =================================================================
echo       __  __  ____  _____   ____  _____  _      /\   
echo      ^|  \/  ^|/ __ \^|  __ \ / __ \^|_   _^|^| ^|    /  \  
echo      ^| \  / ^| ^|  ^| ^| ^|__) ^| ^|  ^| ^| ^| ^|  ^| ^|   /    \ 
echo      ^| ^|\/^| ^| ^|  ^| ^|  _  /^| ^|  ^| ^| ^| ^|  ^| ^|  /  /\  \ 
echo      ^| ^|  ^| ^| ^|__^| ^| ^| \ \^| ^|__^| ^|_^| ^|_ ^| ^|_/ ____  \ 
echo      ^|_^|  ^|_^\____/^|_^|  ^\_\____/^|_____^|^|_/_/    \_\ 
echo                  PREMIUM ENGINE LAUNCHER v1.9.1
echo =================================================================
echo [*] Initializing Moroia core library components...

:: 2️⃣ التأكد من إن مكتبة moroia ومكتباتها الفرعية متثبتة ومحدثة لآخر إصدار
python -c "import moroia" >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [!] Moroia v1.9.1 is not detected or needs global mapping.
    echo [*] Running automated installation via PIP...
    pip install moroia --upgrade --force-reinstall
)

:: 3️⃣ تشغيل الوحش فوراً
echo [+] Core environment is ready. Launching diagnostic telemetry...
echo -----------------------------------------------------------------
moroia

:: منع إغلاق الشاشة بعد انتهاء الفحص عشان المستخدم يشوف التقارير براحته
echo.
echo [*] Session finished. Press any key to exit Moroia Launcher.
pause >nul
