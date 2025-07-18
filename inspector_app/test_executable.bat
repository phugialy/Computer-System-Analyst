@echo off
echo Testing Computer Inspector Executable
echo ====================================
echo.

REM Check if executable exists
if not exist "dist\ComputerInspector.exe" (
    echo ❌ Error: ComputerInspector.exe not found in dist folder
    echo Please run build_with_spec.bat first
    pause
    exit /b 1
)

echo ✅ Executable found: dist\ComputerInspector.exe
echo.

echo Testing executable...
echo Starting Computer Inspector...

REM Run the executable
start /wait dist\ComputerInspector.exe

if errorlevel 1 (
    echo.
    echo ❌ Executable failed to run properly
    echo.
    echo Troubleshooting options:
    echo 1. Try running as Administrator
    echo 2. Check if antivirus is blocking the executable
    echo 3. Use python main.py instead
    echo 4. Use launch.bat script
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ Executable ran successfully!
    echo The application should have opened in a new window.
    echo.
)

echo.
echo Alternative ways to run the application:
echo 1. python main.py (direct Python execution)
echo 2. launch.bat (launcher script)
echo 3. Double-click dist\ComputerInspector.exe
echo.
pause 