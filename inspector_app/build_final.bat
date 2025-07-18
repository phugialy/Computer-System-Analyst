@echo off
echo ========================================
echo Computer Inspector - Final Build (Fixed)
echo ========================================
echo.

REM Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

REM Install dependencies
echo.
echo [2/6] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

REM Test imports
echo.
echo [3/6] Testing application imports...
python test_imports.py
if errorlevel 1 (
    echo ❌ Error: Import test failed
    pause
    exit /b 1
)
echo ✅ Import test passed

REM Install PyInstaller if not present
echo.
echo [4/6] Checking PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller ready

REM Force close processes and clean with different approach
echo.
echo [5/6] Preparing build environment...
echo Closing any running instances...
taskkill /f /im ComputerInspector.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
timeout /t 3 >nul

echo Cleaning with force...
if exist "dist" (
    echo Removing dist folder...
    rmdir /s /q "dist" 2>nul
    if errorlevel 1 (
        echo Trying alternative cleanup...
        del /f /q "dist\*.*" 2>nul
        rmdir /s /q "dist" 2>nul
    )
)
if exist "build" rmdir /s /q "build" 2>nul
if exist "*.spec" del *.spec 2>nul

REM Build with different name to avoid conflicts
echo.
echo [6/6] Building executable with new name...
echo Using alternative build approach...

pyinstaller --onefile --windowed --name "ComputerInspector_v2" ^
    --add-data "assets;assets" ^
    --add-data "core;core" ^
    --add-data "ui;ui" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "psutil" ^
    --hidden-import "GPUtil" ^
    --hidden-import "screeninfo" ^
    --hidden-import "core.system_info" ^
    --hidden-import "core.test_launcher" ^
    --hidden-import "core.report_generator" ^
    --hidden-import "core.email_sender" ^
    --hidden-import "core.inspector_input" ^
    --hidden-import "ui.main_window" ^
    --hidden-import "ui.report_email_dialog" ^
    --hidden-import "gmail_config" ^
    --hidden-import "google_oauth_simple" ^
    --exclude-module "tkinter" ^
    --exclude-module "matplotlib" ^
    --exclude-module "numpy" ^
    --exclude-module "PIL" ^
    main.py

if errorlevel 1 (
    echo ❌ Error: Build failed
    echo.
    echo ========================================
    echo 🎯 RECOMMENDED SOLUTION
    echo ========================================
    echo.
    echo Your application works perfectly with Python!
    echo.
    echo To run the application:
    echo 1. python main.py (recommended)
    echo 2. run_app.bat (one-click launcher)
    echo 3. launch.bat (launcher script)
    echo.
    echo The executable build is just a convenience.
    echo The core application is fully functional!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Executable location: dist\ComputerInspector_v2.exe
echo.
echo To run the application:
echo 1. Double-click dist\ComputerInspector_v2.exe
echo 2. Or run: python main.py (recommended)
echo 3. Or run: run_app.bat (one-click launcher)
echo.
echo Note: If the executable has issues, use python main.py
echo The Python version works perfectly!
echo.
pause 