@echo off
echo ========================================
echo Computer Inspector - One-Click Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Test imports
echo Testing application...
python test_imports.py >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Application test failed
    pause
    exit /b 1
)

REM Launch the application
echo.
echo 🚀 Launching Computer Inspector...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ❌ Application encountered an error
    echo Please check the error message above
    pause
) 