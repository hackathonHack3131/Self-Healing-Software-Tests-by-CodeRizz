# PowerShell script to run full SelfHeal 5-beat demonstration reliably

$ErrorActionPreference = "Stop"

# Determine python executable (prefer .venv)
$PythonExe = "python"
if (Test-Path ".\.venv\Scripts\python.exe") {
    $PythonExe = ".\.venv\Scripts\python.exe"
}

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   Starting SelfHeal Automated Demonstration Script (demo.ps1) " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# 1. Start demo shop in background
Write-Host "Starting target demo shop at http://127.0.0.1:5000..." -ForegroundColor Yellow
$ShopProcess = Start-Process -FilePath $PythonExe -ArgumentList "-m", "demo_app.app" -PassThru -NoNewWindow

$ExitCode = 0

try {
    # 2. Wait for /health with timeout
    $HealthUrl = "http://127.0.0.1:5000/health"
    $TimeoutSeconds = 15
    $StartTime = Get-Date
    $ServerReady = $false

    while (((Get-Date) - $StartTime).TotalSeconds -lt $TimeoutSeconds) {
        try {
            $Response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($Response.StatusCode -eq 200) {
                $ServerReady = $true
                break
            }
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }

    if (-not $ServerReady) {
        Write-Host "[ERROR] Target demo shop failed to become healthy within $TimeoutSeconds seconds." -ForegroundColor Red
        $ExitCode = 1
        exit $ExitCode
    }

    Write-Host "[OK] Target shop healthy at http://127.0.0.1:5000/health`n" -ForegroundColor Green

    # 3. Run full demo
    & $PythonExe cli.py demo
    $ExitCode = $LASTEXITCODE

} catch {
    Write-Host "[ERROR] Exception during demo execution: $_" -ForegroundColor Red
    $ExitCode = 1
} finally {
    # 4. Always stop the background demo shop process started by this script
    if ($ShopProcess -and -not $ShopProcess.HasExited) {
        Write-Host "`nStopping background demo shop (PID: $($ShopProcess.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $ShopProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "[OK] Target shop process stopped cleanly." -ForegroundColor Green
    }
}

exit $ExitCode
