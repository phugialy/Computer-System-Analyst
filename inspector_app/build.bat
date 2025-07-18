@echo off
echo Building Computer Inspector Application...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build the application
echo Building application with PyInstaller...
pyinstaller --onefile --windowed --manifest admin.manifest main.py

REM Alternative: Use spec file
REM pyinstaller inspector_app.spec

echo.
echo Build completed!
echo Executable location: dist\ComputerInspector.exe
echo.
pause 