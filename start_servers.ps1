# SmartCampus - Start Both Servers
# This script starts both frontend and backend servers

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host "  🚀 SmartCampus - Starting Frontend & Backend Servers" -ForegroundColor Cyan
Write-Host "==============================================================================`n" -ForegroundColor Cyan

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

Write-Host "`n🔧 Checking MongoDB connection..." -ForegroundColor Green
Write-Host "   (Make sure MongoDB is running on localhost:27017)`n" -ForegroundColor Yellow

# Start backend in new window
Write-Host "🔌 Starting Backend API Server (Port 8001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; cd backend; python manage.py runserver 8001"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Write-Host "🌐 Starting Frontend Server (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python manage.py runserver 8000"

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host "  ✅ Both servers are starting!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "`n📌 Access your application at:" -ForegroundColor White
Write-Host "   🌐 Frontend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "   🔌 Backend:   http://localhost:8001" -ForegroundColor Cyan
Write-Host "`n📝 Note: Both servers MUST be running for authentication to work!" -ForegroundColor Yellow
Write-Host "`n⏹️  To stop servers: Close the PowerShell windows or press Ctrl+C`n" -ForegroundColor White

# Keep this window open
Read-Host "Press Enter to exit this window (servers will keep running)"
