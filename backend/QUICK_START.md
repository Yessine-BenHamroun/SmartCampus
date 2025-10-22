# SmartCampus Backend Quick Start Guide

## Prerequisites Checklist

- [ ] Python installed
- [ ] MongoDB installed and running
- [ ] Virtual environment activated

## Step 1: Check MongoDB

```powershell
# Check if MongoDB is running
mongo --eval "db.adminCommand('ping')"

# If not running, start it:
mongod
```

## Step 2: Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

## Step 3: Configure Environment

Make sure `backend/.env` is configured:
- MONGO_URI should point to your MongoDB
- Default: `mongodb://localhost:27017/`

## Step 4: Run Django Migrations

```powershell
python manage.py migrate
```

## Step 5: Test the Setup

```powershell
python test_setup.py
```

You should see:
```
✅ MongoDB connection successful!
✅ User model tests passed!
🎉 All tests passed! Backend is ready.
```

## Step 6: Start the Backend Server

```powershell
python manage.py runserver 8001
```

Backend API is now running at: **http://localhost:8001**

## Step 7: Test the API

### Using PowerShell:

```powershell
# Register a user
$body = '{"email":"test@test.com","username":"testuser","password":"Test123456","confirm_password":"Test123456","first_name":"Test","last_name":"User","role":"student"}'

Invoke-WebRequest -Uri "http://localhost:8001/api/users/register/" -Method POST -Body $body -ContentType "application/json"
```

### Using Python:

```python
import requests

# Register
response = requests.post('http://localhost:8001/api/users/register/', json={
    'email': 'test@test.com',
    'username': 'testuser',
    'password': 'Test123456',
    'confirm_password': 'Test123456',
    'first_name': 'Test',
    'last_name': 'User',
    'role': 'student'
})

print(response.json())
```

## Available Endpoints

Once the server is running, you can access:

- **Register**: POST `http://localhost:8001/api/users/register/`
- **Login**: POST `http://localhost:8001/api/users/login/`
- **Profile**: GET `http://localhost:8001/api/users/profile/` (requires auth)
- **Change Password**: POST `http://localhost:8001/api/users/change-password/` (requires auth)
- **Forgot Password**: POST `http://localhost:8001/api/users/forgot-password/`
- **Reset Password**: POST `http://localhost:8001/api/users/reset-password/`

## Common Issues

### Issue: "No module named 'rest_framework'"
**Solution**: Install dependencies
```powershell
pip install -r requirements.txt
```

### Issue: "Connection refused" when connecting to MongoDB
**Solution**: Start MongoDB
```powershell
mongod
```

### Issue: Port 8001 already in use
**Solution**: Use a different port
```powershell
python manage.py runserver 8002
```

## Running Both Frontend and Backend

### Terminal 1 (Backend):
```powershell
cd backend
python manage.py runserver 8001
```

### Terminal 2 (Frontend):
```powershell
cd ..
python manage.py runserver 8000
```

- Frontend: http://localhost:8000
- Backend API: http://localhost:8001

## Next: Testing with Postman

1. Download Postman: https://www.postman.com/downloads/
2. Create a new request
3. Set method to POST
4. URL: `http://localhost:8001/api/users/register/`
5. Body → raw → JSON:
```json
{
  "email": "student@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "confirm_password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```
6. Click Send

You should get a response with user data and JWT tokens!

## Success!

If everything is working, you should see:
- ✅ Backend server running on port 8001
- ✅ MongoDB connected
- ✅ Can register new users
- ✅ Can login and get JWT tokens

## Need Help?

Check the detailed documentation in:
- `backend/README.md` - Full API documentation
- `BACKEND_SETUP.md` - Complete setup guide
