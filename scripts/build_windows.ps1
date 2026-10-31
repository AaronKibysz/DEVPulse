# Build DevPulse for Windows with PyInstaller.
# Run from the repository root after installing dependencies.
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Error "PyInstaller is not installed. Run: pip install pyinstaller"
    exit 1
}
pyinstaller --clean --noconfirm devpulse.spec
if ($?) {
    Write-Host "Build completed. Output: dist\DevPulse"
}
