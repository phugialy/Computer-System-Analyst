@echo off
echo Starting Computer Inspector...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Launch the application
echo Launching Computer Inspector...
python main.py

if errorlevel 1 (
    echo.
    echo Application encountered an error.
    echo Please check the error message above.
    pause
) 