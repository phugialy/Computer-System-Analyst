@echo off
echo ========================================
echo Computer Inspector - Complete Build Script
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

REM Test application startup
echo.
echo [4/6] Testing application startup...
python -c "from ui.main_window import MainWindow; print('✅ Application startup test passed')"
if errorlevel 1 (
    echo ❌ Error: Application startup test failed
    pause
    exit /b 1
)
echo ✅ Application startup test passed

REM Install PyInstaller if not present
echo.
echo [5/6] Checking PyInstaller...
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

REM Build executable
echo.
echo [6/6] Building executable...
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo Building with PyInstaller...
pyinstaller --onefile --windowed --name "ComputerInspector" --icon "assets/icon.ico" main.py
if errorlevel 1 (
    echo ❌ Error: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Executable location: dist\ComputerInspector.exe
echo.
echo To run the application:
echo 1. Double-click dist\ComputerInspector.exe
echo 2. Or run: python main.py
echo.
pause 