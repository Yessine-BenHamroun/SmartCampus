# SmartCampus Quick Setup Script for Windows
# Run this script in PowerShell

Write-Host "SmartCampus Setup Script" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""

# Step 1: Create virtual environment
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists. Skipping..." -ForegroundColor Cyan
} else {
    python -m venv venv
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
}
Write-Host ""

# Step 2: Activate virtual environment
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Step 3: Install dependencies
Write-Host "Step 3: Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Step 4: Create .env file if it doesn't exist
Write-Host "Step 4: Setting up environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env file already exists. Skipping..." -ForegroundColor Cyan
} else {
    Copy-Item .env.example .env
    Write-Host ".env file created from .env.example" -ForegroundColor Green
    Write-Host "IMPORTANT: Edit .env file with your MongoDB connection details!" -ForegroundColor Red
}
Write-Host ""

# Step 5: Update templates
Write-Host "Step 5: Updating HTML templates..." -ForegroundColor Yellow
python update_templates.py
Write-Host ""

# Step 6: Collect static files
Write-Host "Step 6: Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput
Write-Host "Static files collected!" -ForegroundColor Green
Write-Host ""

# Step 7: Run migrations
Write-Host "Step 7: Running migrations..." -ForegroundColor Yellow
python manage.py migrate
Write-Host "Migrations completed!" -ForegroundColor Green
Write-Host ""

Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Make sure MongoDB is running (local or Atlas)" -ForegroundColor White
Write-Host "2. Edit .env file with your MongoDB credentials" -ForegroundColor White
Write-Host "3. Run: python manage.py runserver" -ForegroundColor White
Write-Host "4. Open: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "To create an admin user, run:" -ForegroundColor Yellow
Write-Host "python manage.py createsuperuser" -ForegroundColor White
Write-Host ""
