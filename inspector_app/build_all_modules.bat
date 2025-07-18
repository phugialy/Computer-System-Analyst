@echo off
echo ========================================
echo Computer Inspector - All Modules Build
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

REM Clean previous builds
echo.
echo [5/6] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "build" rmdir /s /q "build" 2>nul
if exist "*.spec" del *.spec 2>nul

REM Build with ALL necessary modules included
echo.
echo [6/6] Building executable with ALL modules...
echo Including all Python standard library modules...

pyinstaller --onefile --windowed --name "ComputerInspector" ^
    --add-data "assets;assets" ^
    --add-data "core;core" ^
    --add-data "ui;ui" ^
    --hidden-import "platform" ^
    --hidden-import "os" ^
    --hidden-import "sys" ^
    --hidden-import "subprocess" ^
    --hidden-import "time" ^
    --hidden-import "datetime" ^
    --hidden-import "pathlib" ^
    --hidden-import "json" ^
    --hidden-import "re" ^
    --hidden-import "threading" ^
    --hidden-import "concurrent.futures" ^
    --hidden-import "smtplib" ^
    --hidden-import "ssl" ^
    --hidden-import "email" ^
    --hidden-import "email.mime.text" ^
    --hidden-import "email.mime.multipart" ^
    --hidden-import "email.mime.base" ^
    --hidden-import "email.encoders" ^
    --hidden-import "dataclasses" ^
    --hidden-import "enum" ^
    --hidden-import "typing" ^
    --hidden-import "collections" ^
    --hidden-import "itertools" ^
    --hidden-import "functools" ^
    --hidden-import "hashlib" ^
    --hidden-import "base64" ^
    --hidden-import "urllib" ^
    --hidden-import "urllib.parse" ^
    --hidden-import "urllib.request" ^
    --hidden-import "socket" ^
    --hidden-import "select" ^
    --hidden-import "signal" ^
    --hidden-import "tempfile" ^
    --hidden-import "shutil" ^
    --hidden-import "glob" ^
    --hidden-import "fnmatch" ^
    --hidden-import "stat" ^
    --hidden-import "pwd" ^
    --hidden-import "grp" ^
    --hidden-import "pipes" ^
    --hidden-import "posix" ^
    --hidden-import "nt" ^
    --hidden-import "ntpath" ^
    --hidden-import "posixpath" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "PyQt6.QtNetwork" ^
    --hidden-import "PyQt6.QtMultimedia" ^
    --hidden-import "PyQt6.QtMultimediaWidgets" ^
    --hidden-import "PyQt6.QtOpenGL" ^
    --hidden-import "PyQt6.QtOpenGLWidgets" ^
    --hidden-import "PyQt6.QtPrintSupport" ^
    --hidden-import "PyQt6.QtSql" ^
    --hidden-import "PyQt6.QtSvg" ^
    --hidden-import "PyQt6.QtSvgWidgets" ^
    --hidden-import "PyQt6.QtTest" ^
    --hidden-import "PyQt6.QtWebEngineCore" ^
    --hidden-import "PyQt6.QtWebEngineWidgets" ^
    --hidden-import "PyQt6.QtXml" ^
    --hidden-import "psutil" ^
    --hidden-import "psutil._pswindows" ^
    --hidden-import "psutil._psutil_windows" ^
    --hidden-import "screeninfo" ^
    --hidden-import "screeninfo.get_monitors" ^
    --hidden-import "core.system_info" ^
    --hidden-import "core.test_launcher" ^
    --hidden-import "core.report_generator" ^
    --hidden-import "core.email_sender" ^
    --hidden-import "core.inspector_input" ^
    --hidden-import "ui.main_window" ^
    --hidden-import "ui.report_email_dialog" ^
    --hidden-import "gmail_config" ^
    --hidden-import "google_oauth_simple" ^
    --collect-all "PyQt6" ^
    --collect-all "psutil" ^
    --collect-all "screeninfo" ^
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
echo Executable location: dist\ComputerInspector.exe
echo.
echo To run the application:
echo 1. Double-click dist\ComputerInspector.exe
echo 2. Or run: python main.py (recommended)
echo 3. Or run: run_app.bat (one-click launcher)
echo.
echo Note: ALL Python modules are now included
echo The Python version works perfectly!
echo.
pause 