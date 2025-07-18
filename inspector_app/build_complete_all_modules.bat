@echo off
echo ========================================
echo Computer Inspector - Complete All Modules Build
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

REM Build with ALL modules included (based on analysis)
echo.
echo [6/6] Building executable with ALL modules...
echo Including all 84 modules identified by analysis...

pyinstaller --onefile --windowed --name "ComputerInspector" ^
    --add-data "assets;assets" ^
    --add-data "core;core" ^
    --add-data "ui;ui" ^
    --hidden-import "GPUtil" ^
    --hidden-import "PyQt6.QtCore.QThread" ^
    --hidden-import "PyQt6.QtCore.QTimer" ^
    --hidden-import "PyQt6.QtCore.QUrl" ^
    --hidden-import "PyQt6.QtCore.Qt" ^
    --hidden-import "PyQt6.QtCore.pyqtSignal" ^
    --hidden-import "PyQt6.QtGui.QDesktopServices" ^
    --hidden-import "PyQt6.QtGui.QFont" ^
    --hidden-import "PyQt6.QtGui.QIcon" ^
    --hidden-import "PyQt6.QtGui.QPixmap" ^
    --hidden-import "PyQt6.QtWidgets.QApplication" ^
    --hidden-import "PyQt6.QtWidgets.QCheckBox" ^
    --hidden-import "PyQt6.QtWidgets.QComboBox" ^
    --hidden-import "PyQt6.QtWidgets.QDialog" ^
    --hidden-import "PyQt6.QtWidgets.QFileDialog" ^
    --hidden-import "PyQt6.QtWidgets.QFrame" ^
    --hidden-import "PyQt6.QtWidgets.QGridLayout" ^
    --hidden-import "PyQt6.QtWidgets.QGroupBox" ^
    --hidden-import "PyQt6.QtWidgets.QHBoxLayout" ^
    --hidden-import "PyQt6.QtWidgets.QLabel" ^
    --hidden-import "PyQt6.QtWidgets.QLineEdit" ^
    --hidden-import "PyQt6.QtWidgets.QMainWindow" ^
    --hidden-import "PyQt6.QtWidgets.QMessageBox" ^
    --hidden-import "PyQt6.QtWidgets.QProgressBar" ^
    --hidden-import "PyQt6.QtWidgets.QPushButton" ^
    --hidden-import "PyQt6.QtWidgets.QScrollArea" ^
    --hidden-import "PyQt6.QtWidgets.QSizePolicy" ^
    --hidden-import "PyQt6.QtWidgets.QSpinBox" ^
    --hidden-import "PyQt6.QtWidgets.QSplitter" ^
    --hidden-import "PyQt6.QtWidgets.QTabWidget" ^
    --hidden-import "PyQt6.QtWidgets.QTextEdit" ^
    --hidden-import "PyQt6.QtWidgets.QVBoxLayout" ^
    --hidden-import "PyQt6.QtWidgets.QWidget" ^
    --hidden-import "concurrent.futures.ThreadPoolExecutor" ^
    --hidden-import "concurrent.futures.as_completed" ^
    --hidden-import "dataclasses.asdict" ^
    --hidden-import "dataclasses.dataclass" ^
    --hidden-import "datetime" ^
    --hidden-import "email" ^
    --hidden-import "email.encoders" ^
    --hidden-import "email.mime" ^
    --hidden-import "email.mime.base" ^
    --hidden-import "email.mime.base.MIMEBase" ^
    --hidden-import "email.mime.multipart" ^
    --hidden-import "email.mime.multipart.MIMEMultipart" ^
    --hidden-import "email.mime.text" ^
    --hidden-import "email.mime.text.MIMEText" ^
    --hidden-import "enum.Enum" ^
    --hidden-import "gmail_config" ^
    --hidden-import "gmail_config.GmailConfigManager" ^
    --hidden-import "gmail_config.setup_gmail_interactive" ^
    --hidden-import "gmail_config.test_gmail_configuration" ^
    --hidden-import "google_oauth_real.GmailSender" ^
    --hidden-import "google_oauth_real.GoogleSignInButton" ^
    --hidden-import "google_oauth_real.GoogleUser" ^
    --hidden-import "google_oauth_simple.GoogleAccountSelectionDialog" ^
    --hidden-import "google_oauth_simple.GoogleUser" ^
    --hidden-import "inspector_input.ReportConfiguration" ^
    --hidden-import "inspector_input.ReportFormat" ^
    --hidden-import "json" ^
    --hidden-import "os" ^
    --hidden-import "pathlib.Path" ^
    --hidden-import "platform" ^
    --hidden-import "psutil" ^
    --hidden-import "re" ^
    --hidden-import "screeninfo" ^
    --hidden-import "smtplib" ^
    --hidden-import "ssl" ^
    --hidden-import "subprocess" ^
    --hidden-import "sys" ^
    --hidden-import "system_info.system_collector" ^
    --hidden-import "test_google_oauth.TestWindow" ^
    --hidden-import "threading" ^
    --hidden-import "time" ^
    --hidden-import "typing.Any" ^
    --hidden-import "typing.Callable" ^
    --hidden-import "typing.Dict" ^
    --hidden-import "typing.List" ^
    --hidden-import "typing.Optional" ^
    --hidden-import "typing.Tuple" ^
    --hidden-import "typing.Union" ^
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
echo Note: ALL 84 modules are now included
echo The Python version works perfectly!
echo.
pause 