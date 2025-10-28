Write-Host "="*80 -ForegroundColor Cyan
Write-Host "🔄 RESTARTING SMARTCAMPUS SERVERS WITH DEBUG LOGGING" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan

Write-Host "`n📋 Instructions:" -ForegroundColor Yellow
Write-Host "1. Stop any running servers (Ctrl+C in their terminals)" -ForegroundColor White
Write-Host "2. This script will start both servers in separate windows" -ForegroundColor White
Write-Host "3. Watch the console logs to see where users are saved" -ForegroundColor White
Write-Host "`n"

# Start Backend Server
Write-Host "🟢 Starting Backend Server on port 8001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host '🟢 BACKEND SERVER (MongoDB API)' -ForegroundColor Green; .\venv\Scripts\python.exe manage.py runserver 8001"

Start-Sleep -Seconds 2

# Start Frontend Server  
Write-Host "🔵 Starting Frontend Server on port 8000..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host '🔵 FRONTEND SERVER (Django Templates)' -ForegroundColor Blue; .\venv\Scripts\python.exe manage.py runserver 8000"

Write-Host "`n✅ Both servers starting..." -ForegroundColor Green
Write-Host "`n📺 Watch the server terminals for detailed logs!" -ForegroundColor Yellow
Write-Host "`n🌐 Frontend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🌐 Backend:  http://localhost:8001/api" -ForegroundColor Cyan
Write-Host "`n🧪 Now try to register a user and watch the logs!" -ForegroundColor Magenta
Write-Host "="*80 -ForegroundColor Cyan
