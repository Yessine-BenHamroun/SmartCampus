# SmartCampus Backend API

Django REST API backend for SmartCampus learning management system with MongoDB.

## Features

- ✅ User Authentication (Register, Login, Logout)
- ✅ JWT Token-based Authentication
- ✅ User Profile Management
- ✅ Password Change
- ✅ Forgot Password / Password Reset
- ✅ MongoDB Integration
- ✅ Role-based Access (Student, Instructor, Admin)
- ✅ CORS Support

## Tech Stack

- Django 4.2.7
- Django REST Framework
- MongoDB (PyMongo)
- JWT Authentication
- Bcrypt for password hashing

## Project Structure

```
backend/
├── config/                 # Django project settings
│   ├── settings.py        # Main settings
│   ├── urls.py            # Main URL routing
│   ├── mongodb.py         # MongoDB connection utilities
│   └── wsgi.py
├── users/                  # User management app
│   ├── models.py          # User MongoDB model
│   ├── serializers.py     # API serializers
│   ├── views.py           # API views
│   ├── urls.py            # User routes
│   └── authentication.py  # Custom JWT authentication
├── manage.py
├── requirements.txt
└── .env
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Update `.env` file with your MongoDB connection and settings:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=smartcampus_db

JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### 3. Start MongoDB

Make sure MongoDB is running on your system:

```bash
# Windows
mongod

# Linux/Mac
sudo systemctl start mongod
```

### 4. Run Django Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver 8001
```

The API will be available at: `http://localhost:8001`

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/register/` | Register new user | No |
| POST | `/api/users/login/` | Login user | No |
| POST | `/api/users/logout/` | Logout user | Yes |
| POST | `/api/token/refresh/` | Refresh JWT token | No |

### User Profile

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/profile/` | Get user profile | Yes |
| PUT | `/api/users/profile/` | Update user profile | Yes |

### Password Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/change-password/` | Change password | Yes |
| POST | `/api/users/forgot-password/` | Request password reset | No |
| POST | `/api/users/reset-password/` | Reset password with token | No |

## API Usage Examples

### Register a New User

```bash
curl -X POST http://localhost:8001/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "username": "johndoe",
    "password": "SecurePass123",
    "confirm_password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "student@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "is_active": true,
    "is_verified": false
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Login

```bash
curl -X POST http://localhost:8001/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "student@example.com",
    "username": "johndoe",
    "role": "student"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Get User Profile (Authenticated)

```bash
curl -X GET http://localhost:8001/api/users/profile/ \
  -H "Authorization: Bearer <access_token>"
```

### Update Profile (Authenticated)

```bash
curl -X PUT http://localhost:8001/api/users/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John Updated",
    "phone": "+1234567890",
    "bio": "Computer Science Student"
  }'
```

### Change Password (Authenticated)

```bash
curl -X POST http://localhost:8001/api/users/change-password/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123",
    "new_password": "NewSecurePass456",
    "confirm_password": "NewSecurePass456"
  }'
```

### Forgot Password

```bash
curl -X POST http://localhost:8001/api/users/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com"
  }'
```

### Reset Password

```bash
curl -X POST http://localhost:8001/api/users/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset_token_from_email",
    "new_password": "NewSecurePass789",
    "confirm_password": "NewSecurePass789"
  }'
```

## User Model Schema (MongoDB)

```javascript
{
  _id: ObjectId,
  email: String,
  username: String,
  password: String (hashed with bcrypt),
  first_name: String,
  last_name: String,
  phone: String,
  role: String (student/instructor/admin),
  is_active: Boolean,
  is_verified: Boolean,
  profile_image: String,
  bio: String,
  created_at: Date,
  updated_at: Date,
  last_login: Date,
  reset_password_token: String,
  reset_password_expires: Date
}
```

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

## Testing with Postman

1. Import the API endpoints into Postman
2. Register a user at `/api/users/register/`
3. Copy the `access` token from the response
4. Add it to Authorization header: `Bearer <access_token>`
5. Test protected endpoints

## Common Issues

### MongoDB Connection Error

Make sure MongoDB is running:
```bash
# Check if MongoDB is running
mongo --eval "db.adminCommand('ping')"
```

### Module Import Errors

Install all dependencies:
```bash
pip install -r requirements.txt
```

## Next Steps

- [ ] Add email verification
- [ ] Add refresh token blacklist
- [ ] Add rate limiting
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Add unit tests
- [ ] Add courses management
- [ ] Add enrollment system
- [ ] Add instructor features

## License

MIT
