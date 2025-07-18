@echo off
echo ========================================
echo Computer Inspector - Simple Build
echo ========================================
echo.

REM Kill any running instances
echo [1/4] Stopping any running instances...
taskkill /f /im ComputerInspector.exe 2>nul
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Clean previous builds
echo [2/4] Cleaning previous builds...
if exist "dist" (
    rmdir /s /q "dist" 2>nul
    if errorlevel 1 (
        echo Waiting for files to unlock...
        timeout /t 3 /nobreak >nul
        rmdir /s /q "dist" 2>nul
    )
)
if exist "build" rmdir /s /q "build" 2>nul
if exist "*.spec" del *.spec 2>nul

REM Install dependencies
echo [3/4] Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Build with minimal modules
echo [4/4] Building executable...
pyinstaller --onefile --windowed --name "ComputerInspector" ^
    --add-data "assets;assets" ^
    --add-data "core;core" ^
    --add-data "ui;ui" ^
    --hidden-import "email" ^
    --hidden-import "email.mime" ^
    --hidden-import "email.mime.text" ^
    --hidden-import "email.mime.multipart" ^
    --hidden-import "smtplib" ^
    --hidden-import "ssl" ^
    --hidden-import "GPUtil" ^
    --hidden-import "PyQt6" ^
    --hidden-import "psutil" ^
    --hidden-import "screeninfo" ^
    --collect-all "PyQt6" ^
    main.py

if errorlevel 1 (
    echo ❌ Build failed
    echo.
    echo 💡 Try running: python main.py (works perfectly!)
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 BUILD COMPLETED!
echo ========================================
echo.
echo Executable: dist\ComputerInspector.exe
echo.
echo 💡 If executable has issues, use: python main.py
echo.
pause 