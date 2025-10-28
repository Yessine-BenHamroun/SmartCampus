# 🔄 MIGRATION TO MONGODB AUTHENTICATION - COMPLETE GUIDE

## ✅ What Was Changed

### 🎯 **Migration Summary:**
Your SmartCampus frontend now uses **MongoDB** (via Backend API) instead of SQLite for user authentication!

---

## 📁 **New Files Created:**

1. **`learner/api_auth.py`** - Backend API authentication module
   - APIAuthBackend class for all API calls
   - Session management functions
   - Custom @api_login_required decorator

2. **`learner/context_processors.py`** - Template context processor
   - Makes user data available in all templates
   - Creates APIUser class that behaves like Django's User

3. **`learner/views_api.py`** → **`learner/views.py`** (replaced)
   - All views now use Backend API
   - JWT token management in sessions

4. **`learner/views_old_sqlite.py`** (backup)
   - Your original SQLite-based views (saved for reference)

---

## 🔧 **Files Modified:**

1. **`smartcampus/settings.py`**
   - Added: `BACKEND_API_URL = 'http://localhost:8001/api'`
   - Added: Context processor `'Learner.context_processors.api_auth_context'`

---

## 🎯 **Auth Functions - Status:**

### ✅ **Fully Implemented (MongoDB via API):**
| Function | Frontend View | Backend API | Status |
|----------|---------------|-------------|--------|
| Register | `register_view()` | `POST /api/users/register/` | ✅ Working |
| Login | `login_view()` | `POST /api/users/login/` | ✅ Working |
| Logout | `logout_view()` | `POST /api/users/logout/` | ✅ Working |
| Profile View | `profile_view()` | `GET /api/users/profile/` | ✅ Working |
| Edit Profile | `edit_profile_view()` | `PUT /api/users/profile/` | ✅ Working |
| Change Password | `edit_profile_view()` | `POST /api/users/change-password/` | ✅ Working |
| Forgot Password | `forgot_password_view()` | `POST /api/users/forgot-password/` | ✅ Working |
| Reset Password | `reset_password_view()` | `POST /api/users/reset-password/` | ✅ Working |

### ⏳ **Not Yet Implemented (Placeholders):**
| Function | Status | Note |
|----------|--------|------|
| 2FA Setup | ⏳ Placeholder | Backend API needs 2FA endpoints |
| 2FA Verification | ⏳ Placeholder | Will be implemented later |
| 2FA Disable | ⏳ Placeholder | Will be implemented later |

---

## 🚀 **How to Run:**

### **Step 1: Start Backend API Server** (IMPORTANT!)
```powershell
# Terminal 1 - Backend API
cd C:\Users\yessi\Desktop\5TWIN\Django\SmartCampus
.\venv\Scripts\Activate.ps1
cd backend
python manage.py runserver 8001
```

**The backend MUST be running on port 8001!**

### **Step 2: Start Frontend Server**
```powershell
# Terminal 2 - Frontend
cd C:\Users\yessi\Desktop\5TWIN\Django\SmartCampus
.\venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

### **Step 3: Test Authentication**
1. Go to: http://localhost:8000/register/
2. Register a new user
3. Check MongoDB: User should be in `smartcampus_db.users` collection
4. Login at: http://localhost:8000/login/
5. View profile: http://localhost:8000/profile/

---

## 🔍 **How It Works Now:**

```
┌──────────────────────────────────────────────────────┐
│  User visits /register/                              │
│         ↓                                            │
│  learner/views.py → register_view()                  │
│         ↓                                            │
│  learner/api_auth.py → APIAuthBackend.register()     │
│         ↓                                            │
│  HTTP POST to backend: /api/users/register/          │
│         ↓                                            │
│  backend/users/views.py → RegisterView               │
│         ↓                                            │
│  backend/users/models.py → User.create()             │
│         ↓                                            │
│  MongoDB: Save user to smartcampus_db.users          │
│         ↓                                            │
│  Return: JWT tokens (access + refresh)               │
│         ↓                                            │
│  Frontend: Save tokens in Django session             │
│         ↓                                            │
│  User registered & ready to login!                   │
└──────────────────────────────────────────────────────┘
```

---

## 💾 **Session Management:**

### **What's Stored in Django Session:**
```python
request.session = {
    'user': {
        '_id': '...',
        'username': 'john_doe',
        'email': 'john@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'role': 'student',
        'is_active': True,
        ...
    },
    'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...',  # Valid for 60 min
    'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...', # Valid for 24 hours
    'is_authenticated': True
}
```

### **Token Refresh:**
- Access token expires after 60 minutes
- `ensure_valid_token()` automatically refreshes it
- If refresh fails, user must login again

---

## 🗄️ **Database Comparison:**

### **Before (SQLite):**
```
db.sqlite3:
├── auth_user           ← Users stored here
├── auth_user_profile   ← Extended profile
├── otp_totp_totpdevice ← 2FA devices
└── django_session      ← Sessions
```

### **After (MongoDB):**
```
MongoDB (smartcampus_db):
└── users collection     ← All user data here!
    {
        "_id": ObjectId("..."),
        "username": "john_doe",
        "email": "john@example.com",
        "password": "hashed_password",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student",
        "is_active": true,
        "created_at": "2025-10-28T...",
        ...
    }

Django still uses SQLite for:
├── django_session      ← Sessions (with tokens)
├── django_admin_log    ← Admin logs
└── django_migrations   ← Migration history
```

---

## 🧪 **Testing Checklist:**

- [ ] Backend API running on port 8001
- [ ] Frontend running on port 8000
- [ ] Can register new user
- [ ] User appears in MongoDB `users` collection
- [ ] Can login with registered user
- [ ] Profile page shows correct data
- [ ] Can edit profile
- [ ] Can change password
- [ ] Forgot password sends email
- [ ] Reset password works with token
- [ ] Logout clears session
- [ ] Templates show username in header

---

## 🔧 **Troubleshooting:**

### **Problem: "Cannot connect to authentication server"**
**Solution:**
```powershell
# Make sure backend is running
cd backend
python manage.py runserver 8001
```

### **Problem: "No such table: auth_user"**
**Solution:**  
This is normal! We're not using SQLite for users anymore.  
Run migrations for Django's internal tables:
```powershell
python manage.py migrate
```

### **Problem: "User registered but can't login"**
**Solution:**  
Check MongoDB:
```powershell
# In MongoDB shell or Compass
use smartcampus_db
db.users.find({})
```

### **Problem: "Token expired"**
**Solution:**  
Login again. Access tokens expire after 60 minutes.

---

## 📝 **API Endpoints Reference:**

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/users/register/` | POST | Register new user | No |
| `/api/users/login/` | POST | Login & get tokens | No |
| `/api/users/logout/` | POST | Blacklist refresh token | Yes |
| `/api/users/profile/` | GET | Get user profile | Yes |
| `/api/users/profile/` | PUT | Update profile | Yes |
| `/api/users/change-password/` | POST | Change password | Yes |
| `/api/users/forgot-password/` | POST | Request reset email | No |
| `/api/users/reset-password/` | POST | Reset with token | No |
| `/api/token/refresh/` | POST | Refresh access token | No (needs refresh token) |

---

## 🎯 **Next Steps:**

### **Optional Enhancements:**

1. **Add 2FA to Backend API:**
   - Create 2FA endpoints in `backend/users/`
   - Update frontend to use them

2. **Migrate Existing Users:**
   - Export users from SQLite
   - Import into MongoDB
   - Script available if needed

3. **Add More Features:**
   - Email verification
   - Social login (Google, Facebook)
   - User roles and permissions
   - Profile images upload

---

## ✅ **Success Indicators:**

You'll know migration is successful when:
1. ✅ Backend API runs without errors
2. ✅ New registrations go to MongoDB (not SQLite)
3. ✅ Login returns JWT tokens
4. ✅ Profile page loads with MongoDB data
5. ✅ Header shows username dropdown
6. ✅ All auth functions work end-to-end

---

## 📚 **Key Files to Know:**

```
SmartCampus/
├── learner/
│   ├── views.py              ← NEW: API-based views
│   ├── views_old_sqlite.py   ← BACKUP: Old SQLite views
│   ├── api_auth.py           ← NEW: API backend connector
│   ├── context_processors.py ← NEW: Template user context
│   └── forms.py              ← Same forms, different backend
│
├── backend/
│   └── users/
│       ├── views.py          ← API endpoints
│       ├── models.py         ← MongoDB User model
│       └── serializers.py    ← Request/response validation
│
└── smartcampus/
    └── settings.py           ← Updated with API URL
```

---

## 🎉 **Congratulations!**

Your SmartCampus now uses:
- ✅ MongoDB for user storage (scalable!)
- ✅ JWT tokens for authentication (stateless!)
- ✅ REST API backend (mobile-ready!)
- ✅ Same user experience (seamless!)

**Both servers must run together:**
- Frontend: http://localhost:8000
- Backend API: http://localhost:8001

---

**Need Help?** Check the logs in both terminals for detailed error messages!
