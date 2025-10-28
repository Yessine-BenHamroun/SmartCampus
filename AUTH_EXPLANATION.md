# 🔐 SmartCampus Authentication Architecture

## 📊 Current Setup: TWO SEPARATE AUTH SYSTEMS

### 🎨 **FRONTEND Authentication (Currently Active)**

**Location:** `learner/views.py` + `learner/templates/`  
**Port:** 8000  
**Database:** SQLite (`db.sqlite3`)  
**Technology:** Django built-in auth + django-otp (2FA)

#### How It Works:

```
User → /register/ → learner/views.py → Django User Model → SQLite
                                                              ↓
User → /login/    → learner/views.py → authenticate()     → SQLite
                          ↓
                    Has 2FA enabled?
                          ↓
                    Yes → Send email code → verify_2fa_login
                    No  → login(request, user) → Session created
```

#### Database Tables (SQLite):
- `auth_user` - User accounts (Django's built-in)
- `auth_user_profile` - Extended user info
- `otp_totp_totpdevice` - 2FA devices
- `django_session` - User sessions

#### Features:
✅ Registration with email
✅ Login with username/password
✅ Two-Factor Authentication (2FA) via email
✅ Password reset via email
✅ Profile management
✅ Django sessions (cookie-based)
✅ Template-based (traditional web app)

#### Views (learner/views.py):
```python
register_view()         # Register user in SQLite
login_view()            # Login + 2FA check
logout_view()           # Logout from Django session
profile_view()          # Show user profile
edit_profile_view()     # Edit profile
setup_2fa()             # Enable 2FA
verify_2fa_login()      # Verify 2FA code
forgot_password()       # Send reset email
reset_password()        # Reset password with token
```

---

### 🔌 **BACKEND REST API Authentication (Separate, Unused)**

**Location:** `backend/users/` + `backend/config/`  
**Port:** 8001  
**Database:** MongoDB (`smartcampus_db`)  
**Technology:** Django REST Framework + JWT (simplejwt)

#### How It Works:

```
Client → POST /api/users/register/ → backend/users/views.py → MongoDB
                                            ↓
                                      Hash password (bcrypt)
                                            ↓
                                      Save to MongoDB
                                            ↓
                                      Return JWT tokens

Client → POST /api/users/login/ → backend/users/views.py → MongoDB
                                          ↓
                                    Verify password
                                          ↓
                                    Generate JWT tokens:
                                    - access_token (60 min)
                                    - refresh_token (24 hours)
                                          ↓
                                    Return tokens

Client → GET /api/courses/ → Headers: Authorization: Bearer <token>
                                          ↓
                                    Verify JWT token
                                          ↓
                                    Return course data
```

#### Database (MongoDB):
- `users` collection - User accounts
- `courses` collection - Courses data
- `enrollments` collection - Student enrollments
- `reviews` collection - Course reviews
- `blog_posts` collection - Blog posts
- `blog_comments` collection - Comments

#### Features:
✅ JWT-based authentication
✅ RESTful API endpoints
✅ Token refresh mechanism
✅ MongoDB for scalability
✅ CORS enabled
✅ Role-based access (student/instructor/admin)
✅ API for mobile/SPA apps

#### API Endpoints (backend/users/urls.py):
```python
POST   /api/users/register/         # Register (returns JWT)
POST   /api/users/login/            # Login (returns JWT)
POST   /api/users/logout/           # Blacklist refresh token
GET    /api/users/profile/          # Get profile (needs JWT)
PUT    /api/users/profile/          # Update profile (needs JWT)
POST   /api/users/change-password/  # Change password
POST   /api/users/forgot-password/  # Request reset
POST   /api/users/reset-password/   # Reset password
POST   /api/token/refresh/          # Refresh access token
```

---

## 🔄 **The Problem: They Don't Talk to Each Other!**

```
┌─────────────────────────┐         ┌─────────────────────────┐
│   FRONTEND (Port 8000)  │         │  BACKEND API (Port 8001)│
│                         │    ✗    │                         │
│   Users in SQLite       │ ─────── │   Users in MongoDB      │
│   Django Sessions       │  No     │   JWT Tokens            │
│   Template-based        │  Link   │   API-based             │
│                         │         │                         │
│   ✅ Currently Used     │         │   ❌ Currently Unused   │
└─────────────────────────┘         └─────────────────────────┘
```

**Current Issue:**
- You register/login on frontend → User saved in SQLite
- Backend API has its own users in MongoDB
- They are completely separate systems!
- Backend API endpoints exist but frontend doesn't use them

---

## 🎯 **Solutions:**

### **Option 1: Keep Frontend Auth Only** ⚡ (Simplest)

**What to do:** Nothing! It works as is.

**Pros:**
- Already working
- No changes needed
- Simple for web-only apps

**Cons:**
- SQLite not production-ready
- Can't support mobile apps
- Backend API is wasted code

**Best for:** Small projects, learning, quick MVPs

---

### **Option 2: Migrate Frontend to Use Backend API** 🚀 (Recommended)

**What to do:** Modify frontend views to call backend API

**Example Changes Needed:**

```python
# BEFORE (learner/views.py):
def login_view(request):
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)  # Django session
        
# AFTER (learner/views.py):
import requests

def login_view(request):
    # Call backend API
    response = requests.post('http://localhost:8001/api/users/login/', json={
        'username': username,
        'password': password
    })
    
    if response.status_code == 200:
        tokens = response.json()
        # Store JWT in session/cookies
        request.session['access_token'] = tokens['access']
        request.session['refresh_token'] = tokens['refresh']
```

**Pros:**
- One unified user database (MongoDB)
- Can add mobile app later
- Scalable architecture
- API ready for React/Vue frontend

**Cons:**
- Need to rewrite auth views
- More complex session handling
- Need to manage JWT tokens in templates

**Implementation Steps:**
1. Modify `learner/views.py` to call backend API
2. Store JWT tokens in sessions/cookies
3. Add middleware to inject tokens in API calls
4. Update templates to handle token-based auth
5. Migrate existing SQLite users to MongoDB (optional)

---

### **Option 3: Hybrid Approach** 🔀

**What to do:** Keep both, sync when needed

- Web templates use Django auth (SQLite)
- AJAX requests use backend API (MongoDB)
- Sync users between systems

**Best for:** Gradual migration

---

## 💡 **My Recommendation:**

### For Now (Learning Phase): **Option 1** ✅
- Keep current frontend auth
- It works perfectly for a web application
- Focus on building features

### For Production/Future: **Option 2** 🎯
- Migrate to backend API
- One source of truth (MongoDB)
- Ready for mobile/modern frontend

---

## 🛠️ **Quick Reference:**

### Currently Using (Frontend):
```bash
# Start frontend
python manage.py runserver 8000

# Users stored in: db.sqlite3
# Auth: Django sessions
# URLs: /login/, /register/, /profile/
```

### Available but Unused (Backend API):
```bash
# Start backend
cd backend
python manage.py runserver 8001

# Users stored in: MongoDB (smartcampus_db)
# Auth: JWT tokens
# URLs: /api/users/login/, /api/users/register/
```

---

## 🔍 **Test Both Systems:**

### Test Frontend Auth (Working):
1. Go to: http://localhost:8000/register/
2. Register a user
3. Check: SQLite database has new user
4. Login at: http://localhost:8000/login/

### Test Backend API (Separate):
1. Start backend: `cd backend && python manage.py runserver 8001`
2. Use Postman/curl:
   ```bash
   # Register
   curl -X POST http://localhost:8001/api/users/register/ \
     -H "Content-Type: application/json" \
     -d '{"username":"test","email":"test@test.com","password":"Test123!@#"}'
   
   # Login
   curl -X POST http://localhost:8001/api/users/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"Test123!@#"}'
   ```
3. Check: MongoDB has new user (different from SQLite!)

---

## ❓ **FAQ:**

**Q: Which one should I use?**  
A: Frontend auth is fine for web-only apps. Use backend API if you want mobile support or modern architecture.

**Q: Can I use both?**  
A: They're separate systems. You'd need to sync users between SQLite and MongoDB.

**Q: Why have both?**  
A: Backend was created for a complete REST API architecture, but frontend uses traditional Django auth for simplicity.

**Q: How do I connect them?**  
A: Rewrite frontend views to call backend API endpoints instead of using Django's built-in auth.

---

**Current Status:** Frontend auth (SQLite + Django) ✅ Working  
**Backend API:** Available but not connected to frontend  
**Next Steps:** Decide which approach fits your needs!
