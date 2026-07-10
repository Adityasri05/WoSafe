# WoSafe Startup Script for Local Development
Clear-Host
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "   🛡️  WoSafe — AI-Powered Women's Safety Intelligence Platform" -ForegroundColor Cyan
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Start backend FastAPI server in a new window
Write-Host "📡 [1/2] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd backend; `$env:PYTHONPATH='.'; .venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

# Wait a brief moment for the backend to start up
Start-Sleep -Seconds 2

# 2. Start Next.js frontend in the current console
Write-Host "💻 [2/2] Starting Next.js Frontend on http://127.0.0.1:3000..." -ForegroundColor Yellow
Write-Host "🚀 Project running successfully! Close the terminals to stop." -ForegroundColor Green
Write-Host ""
npm run dev
