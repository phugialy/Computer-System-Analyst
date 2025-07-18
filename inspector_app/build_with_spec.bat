@echo off
echo ========================================
echo Computer Inspector - Spec File Build
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

REM Clean and build with spec file
echo.
echo [6/6] Building with spec file...
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo Building with ComputerInspector.spec...
pyinstaller ComputerInspector.spec

if errorlevel 1 (
    echo ❌ Error: Build failed with spec file
    echo Trying fallback method...
    
    REM Fallback: direct build with explicit includes
    pyinstaller --onefile --windowed --name "ComputerInspector" ^
        --add-data "assets;assets" ^
        --add-data "core;core" ^
        --add-data "ui;ui" ^
        --hidden-import "core.system_info" ^
        --hidden-import "core.test_launcher" ^
        --hidden-import "core.report_generator" ^
        --hidden-import "core.email_sender" ^
        --hidden-import "core.inspector_input" ^
        --hidden-import "ui.main_window" ^
        --hidden-import "ui.report_email_dialog" ^
        --hidden-import "gmail_config" ^
        --hidden-import "google_oauth_simple" ^
        main.py
    
    if errorlevel 1 (
        echo ❌ Error: Fallback build also failed
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 🎉 BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Executable location: dist\ComputerInspector.exe
echo.
echo To test the executable:
echo 1. Double-click dist\ComputerInspector.exe
echo 2. Or run from command line: dist\ComputerInspector.exe
echo.
echo If the executable still has issues, use:
echo 1. python main.py (direct Python execution)
echo 2. launch.bat (launcher script)
echo.
pause 