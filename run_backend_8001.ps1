# Start Django backend on port 8001
Write-Host "Starting Django backend on port 8001..." -ForegroundColor Green
Write-Host "Navigate to http://localhost:8001 to access the API" -ForegroundColor Cyan

cd backend
python manage.py runserver 8001
