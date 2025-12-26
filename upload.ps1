# CyberBrick V7RC Upload Script
# Uploads all project files to ESP32-C3 using mpremote

param(
    [string]$Port = "COM28",
    [switch]$Help
)

if ($Help) {
    Write-Host @"
CyberBrick V7RC Upload Script
==============================

Usage:
  .\upload.ps1 [-Port <COM_PORT>]

Parameters:
  -Port     Serial port (default: COM28)
  -Help     Show this help message

Examples:
  .\upload.ps1              # Upload to COM28
  .\upload.ps1 -Port COM3   # Upload to COM3

"@ -ForegroundColor Cyan
    exit 0
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CyberBrick V7RC Upload Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Port: $Port" -ForegroundColor Yellow
Write-Host ""

# Kill any Python processes that might be using the port
Write-Host "Checking for processes using $Port..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name python* -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "Terminating Python processes..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Upload boot.py
Write-Host "Uploading boot.py..." -ForegroundColor Cyan
mpremote connect $Port cp boot.py :boot.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ boot.py uploaded" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to upload boot.py" -ForegroundColor Red
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "  1. ESP32-C3 is connected to $Port" -ForegroundColor White
    Write-Host "  2. No other programs are using $Port" -ForegroundColor White
    Write-Host "  3. MicroPython firmware is installed" -ForegroundColor White
    exit 1
}

# Upload bbl_product.py
Write-Host ""
Write-Host "Uploading bbl_product.py..." -ForegroundColor Cyan
mpremote connect $Port cp bbl_product.py :bbl_product.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ bbl_product.py uploaded" -ForegroundColor Green
}

# Upload bbl library
Write-Host ""
Write-Host "Uploading bbl library..." -ForegroundColor Cyan
mpremote connect $Port cp -r bbl :
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ bbl library uploaded" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to upload bbl library" -ForegroundColor Red
    exit 1
}

# Upload app files
Write-Host ""
Write-Host "Uploading app files..." -ForegroundColor Cyan
mpremote connect $Port cp -r app :
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ app files uploaded" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to upload app files" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Upload complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resetting ESP32-C3..." -ForegroundColor Yellow
mpremote connect $Port reset
Write-Host "✓ Device reset" -ForegroundColor Green
Write-Host ""
Write-Host "Your CyberBrick V7RC is now ready to use!" -ForegroundColor Green
Write-Host "Connect to Wi-Fi: cyber_V7RC (password: 12341234)" -ForegroundColor Cyan
