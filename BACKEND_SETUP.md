# SmartCampus Project Structure

## Overview

The project has been reorganized with separate **frontend** and **backend** structures:

```
SmartCampus/
├── backend/                    # Django REST API Backend
│   ├── config/                # Django project configuration
│   │   ├── settings.py       # Django settings with MongoDB
│   │   ├── urls.py           # Main URL routing
│   │   ├── mongodb.py        # MongoDB connection utilities
│   │   └── wsgi.py
│   ├── users/                 # User management app
│   │   ├── models.py         # User MongoDB model
│   │   ├── serializers.py    # API request/response serializers
│   │   ├── views.py          # API views (Register, Login, etc.)
│   │   ├── urls.py           # User app URL routing
│   │   └── authentication.py # Custom JWT authentication
│   ├── manage.py
│   ├── requirements.txt       # Backend dependencies
│   ├── .env                   # Environment variables
│   ├── README.md              # Backend documentation
│   └── test_setup.py          # Setup verification script
│
├── Learner/                    # Frontend Django app (existing)
├── smartcampus/                # Frontend project config (existing)
├── static/                     # Static files (CSS, JS, images)
├── manage.py                   # Frontend manage.py
└── requirements.txt            # Frontend requirements

```

## Backend Features Implemented

### ✅ User Management System

1. **User Authentication**
   - Register new users (students/instructors)
   - Login with JWT tokens
   - Logout with token blacklisting
   - Token refresh endpoint

2. **User Profile**
   - Get user profile
   - Update profile information
   - View user details

3. **Password Management**
   - Change password (for logged-in users)
   - Forgot password (send reset email)
   - Reset password with token

4. **Security Features**
   - Password hashing with bcrypt
   - JWT token authentication
   - CORS protection
   - Password strength validation
   - Role-based access control

## Backend API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/users/register/` | POST | Register new user | No |
| `/api/users/login/` | POST | Login user | No |
| `/api/users/logout/` | POST | Logout user | Yes |
| `/api/token/refresh/` | POST | Refresh JWT token | No |

### Profile Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/users/profile/` | GET | Get user profile | Yes |
| `/api/users/profile/` | PUT | Update profile | Yes |

### Password Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/users/change-password/` | POST | Change password | Yes |
| `/api/users/forgot-password/` | POST | Request reset | No |
| `/api/users/reset-password/` | POST | Reset with token | No |

## How to Run the Backend

### 1. Make Sure MongoDB is Running

```powershell
# Start MongoDB (if not running)
mongod
```

### 2. Navigate to Backend Directory

```powershell
cd backend
```

### 3. Install Dependencies (already done)

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment

Edit `backend/.env` file with your MongoDB URI:

```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=smartcampus_db
```

### 5. Run Migrations

```powershell
python manage.py migrate
```

### 6. Test the Setup

```powershell
python test_setup.py
```

### 7. Start the Backend Server

```powershell
python manage.py runserver 8001
```

Backend API will be available at: **http://localhost:8001**

## Testing the API

### Register a User (Example with PowerShell)

```powershell
$body = @{
    email = "student@example.com"
    username = "johndoe"
    password = "SecurePass123"
    confirm_password = "SecurePass123"
    first_name = "John"
    last_name = "Doe"
    role = "student"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/users/register/" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Login (Example)

```powershell
$loginBody = @{
    email = "student@example.com"
    password = "SecurePass123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8001/api/users/login/" `
    -Method POST `
    -Body $loginBody `
    -ContentType "application/json"

# Save the access token
$token = $response.tokens.access
```

### Get Profile (Authenticated Request)

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/users/profile/" `
    -Method GET `
    -Headers @{
        "Authorization" = "Bearer $token"
    }
```

## MongoDB User Schema

```javascript
{
  _id: ObjectId,
  email: String (unique, required),
  username: String (unique, required),
  password: String (hashed with bcrypt),
  first_name: String,
  last_name: String,
  phone: String,
  role: String (student/instructor/admin),
  is_active: Boolean (default: true),
  is_verified: Boolean (default: false),
  profile_image: String,
  bio: String,
  created_at: Date,
  updated_at: Date,
  last_login: Date,
  reset_password_token: String,
  reset_password_expires: Date
}
```

## Running Frontend and Backend Together

### Terminal 1: Backend API
```powershell
cd backend
python manage.py runserver 8001
```

### Terminal 2: Frontend
```powershell
python manage.py runserver 8000
```

- **Frontend**: http://localhost:8000 (Django templates)
- **Backend API**: http://localhost:8001 (REST API)

## Next Steps

Now that the user management backend is complete, you can:

1. ✅ Test all API endpoints with Postman or curl
2. ⏳ Connect frontend to backend API
3. ⏳ Add course management endpoints
4. ⏳ Add enrollment system
5. ⏳ Add instructor features
6. ⏳ Add admin dashboard
7. ⏳ Add file upload for profile images
8. ⏳ Add email verification
9. ⏳ Add social authentication
10. ⏳ Deploy to production

## Troubleshooting

### MongoDB Connection Error

```
pymongo.errors.ServerSelectionTimeoutError
```

**Solution**: Make sure MongoDB is running:
```powershell
mongod --dbpath C:\data\db
```

### Module Not Found Error

**Solution**: Install dependencies:
```powershell
cd backend
pip install -r requirements.txt
```

### Port Already in Use

**Solution**: Use a different port:
```powershell
python manage.py runserver 8002
```

## Important Notes

1. The **backend** runs on port **8001** (API only)
2. The **frontend** runs on port **8000** (Templates + Views)
3. MongoDB stores user data in `smartcampus_db` database
4. JWT tokens expire after 60 minutes (configurable in .env)
5. Refresh tokens expire after 24 hours
6. Password reset tokens expire after 1 hour

## Questions?

Check the `backend/README.md` for detailed API documentation and examples.
