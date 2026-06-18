param(
    [switch]$NoConfirm
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $scriptDir "qr_generator.py"

if (-not (Test-Path $scriptPath)) {
    Write-Host "Error: qr_generator.py not found in $scriptDir" -ForegroundColor Red
    exit 1
}

Write-Host "=== QR Generator Builder ===" -ForegroundColor Cyan
Write-Host "Source: $scriptPath" -ForegroundColor Gray
Write-Host ""

# Check if pyinstaller is available
$pyinstaller = Get-Command "pyinstaller" -ErrorAction SilentlyContinue
if (-not $pyinstaller) {
    Write-Host "PyInstaller not found." -ForegroundColor Yellow
    $install = if ($NoConfirm) { $true } else {
        $r = Read-Host "Install PyInstaller? (y/N)"
        $r -eq "y"
    }
    if ($install) {
        pip install pyinstaller cryptography
    } else {
        exit 1
    }
}

Write-Host "Building executable..." -ForegroundColor Yellow
pyinstaller --onefile --windowed --name "QR_Generator" --noconfirm $scriptPath

if ($LASTEXITCODE -eq 0) {
    $exePath = Join-Path $scriptDir "dist\QR_Generator.exe"
    if (Test-Path $exePath) {
        Write-Host ""
        Write-Host "Build successful!" -ForegroundColor Green
        Write-Host "Executable: $exePath" -ForegroundColor Cyan

        # Clean up build artifacts
        $buildDir = Join-Path $scriptDir "build"
        $specFile = Join-Path $scriptDir "QR_Generator.spec"
        if (Test-Path $buildDir) { Remove-Item -Recurse -Force $buildDir }
        if (Test-Path $specFile) { Remove-Item -Force $specFile }
        Write-Host "Build artifacts cleaned up." -ForegroundColor Gray
    }
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
