Write-Host "Building Computer Inspector Application..." -ForegroundColor Green
Write-Host ""

# Check if PyInstaller is installed
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
        pip install pyinstaller
    }
} catch {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Build the application
Write-Host "Building application with PyInstaller..." -ForegroundColor Yellow
pyinstaller --onefile --windowed --manifest admin.manifest main.py

# Alternative: Use spec file
# pyinstaller inspector_app.spec

Write-Host ""
Write-Host "Build completed!" -ForegroundColor Green
Write-Host "Executable location: dist\ComputerInspector.exe" -ForegroundColor Cyan
Write-Host ""

# Check if build was successful
if (Test-Path "dist\ComputerInspector.exe") {
    Write-Host "✅ Build successful! Application is ready to use." -ForegroundColor Green
} else {
    Write-Host "❌ Build failed! Check the error messages above." -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to continue..." 