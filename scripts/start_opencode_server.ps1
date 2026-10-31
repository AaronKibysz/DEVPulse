# Start a local OpenCode HTTP server for DevPulse.
# Run this in a separate terminal before using DevPulse.
$port = 49374
$password = $env:OPENCODE_SERVER_PASSWORD
if (-not $password -and (Test-Path "$HOME\.config\opencode\service.json")) {
    try {
        $data = Get-Content "$HOME\.config\opencode\service.json" | ConvertFrom-Json
        if ($data.password) { $password = $data.password }
    } catch {}
}
if ($password) { $env:OPENCODE_SERVER_PASSWORD = $password }
Write-Host "Starting OpenCode server on http://127.0.0.1:$port"
$process = Start-Process -FilePath "opencode" -ArgumentList "serve","--port",$port,"--hostname","127.0.0.1" -WindowStyle Hidden -PassThru
Write-Host "OpenCode server started (PID $($process.Id))."