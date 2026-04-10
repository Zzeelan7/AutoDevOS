# Start AutoDevOS Backend and Frontend Servers
$ProjectRoot = "C:\Users\zzeel\OneDrive\Desktop\AutoDevOS"

Set-Location $ProjectRoot

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting AutoDevOS Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start FastAPI Backend (Port 8000)
Write-Host "[1/2] Starting FastAPI Backend on http://localhost:8000" -ForegroundColor Green
$BackendJob = Start-Process powershell -ArgumentList "-NoExit -Command `"Set-Location '$ProjectRoot'; & '.\.venv\Scripts\Activate.ps1'; python -m uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload`"" -PassThru -WindowStyle Normal

# Wait for backend to start
Start-Sleep -Seconds 3

# Start Next.js Frontend (Port 3000)
Write-Host "[2/2] Starting Next.js Frontend on http://localhost:3000" -ForegroundColor Green
$FrontendJob = Start-Process powershell -ArgumentList "-NoExit -Command `"Set-Location '$ProjectRoot\frontend'; npm run dev`"" -PassThru -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Both servers are starting..." -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
