@echo off
echo ========================================
echo Computer Inspector - Fixed Build Script
echo ========================================
echo.

REM Check if Python is installed
echo [1/7] Checking Python installation...
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
echo [2/7] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

REM Test imports
echo.
echo [3/7] Testing application imports...
python test_imports.py
if errorlevel 1 (
    echo ❌ Error: Import test failed
    pause
    exit /b 1
)
echo ✅ Import test passed

REM Test application startup
echo.
echo [4/7] Testing application startup...
python -c "from ui.main_window import MainWindow; print('✅ Application startup test passed')"
if errorlevel 1 (
    echo ❌ Error: Application startup test failed
    pause
    exit /b 1
)
echo ✅ Application startup test passed

REM Install PyInstaller if not present
echo.
echo [5/7] Checking PyInstaller...
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

REM Clean previous builds
echo.
echo [6/7] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del *.spec

REM Build executable with fixed configuration
echo.
echo [7/7] Building executable with DLL fix...
echo Using compatible PyInstaller configuration...

REM Create a spec file for better control
echo Creating PyInstaller spec file...
pyinstaller --name "ComputerInspector" ^
    --onefile ^
    --windowed ^
    --clean ^
    --distpath "dist" ^
    --workpath "build" ^
    --add-data "assets;assets" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "psutil" ^
    --hidden-import "GPUtil" ^
    --hidden-import "screeninfo" ^
    --exclude-module "tkinter" ^
    --exclude-module "matplotlib" ^
    --exclude-module "numpy" ^
    --exclude-module "PIL" ^
    main.py

if errorlevel 1 (
    echo ❌ Error: Build failed
    echo Trying alternative build method...
    
    REM Alternative build method
    pyinstaller --onefile --windowed --name "ComputerInspector" ^
        --hidden-import "PyQt6" ^
        --hidden-import "psutil" ^
        --hidden-import "GPUtil" ^
        --hidden-import "screeninfo" ^
        main.py
    
    if errorlevel 1 (
        echo ❌ Error: Alternative build also failed
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
echo If you still get DLL errors, try running:
echo 1. python main.py (direct Python execution)
echo 2. Or use the launch.bat script
echo.
echo To run the application:
echo 1. Double-click dist\ComputerInspector.exe
echo 2. Or run: python main.py
echo 3. Or run: launch.bat
echo.
pause 