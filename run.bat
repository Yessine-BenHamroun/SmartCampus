@echo off
echo SmartCampus Quick Start
echo =======================
echo.

echo Starting Django development server...
echo.

cd /d "%~dp0"

if not exist "venv" (
    echo Virtual environment not found!
    echo Please run setup.ps1 first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Checking if MongoDB is accessible...
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/')); client.server_info(); print('MongoDB connection: OK')" 2>nul
if errorlevel 1 (
    echo WARNING: Cannot connect to MongoDB!
    echo Make sure MongoDB is running or check your .env file
    echo.
)

echo Starting server at http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver

pause
