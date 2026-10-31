# Run DevPulse without showing a console window.
$env:PYTHONPATH = "src"
$pythonw = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $pythonw) {
    Write-Error "pythonw.exe was not found. Install Python or use python.exe."
    exit 1
}
Start-Process -FilePath $pythonw -ArgumentList "-m","devpulse.main" -WorkingDirectory "C:\Users\Aaron\Desktop\DEVPulse"