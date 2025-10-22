# 🗺️ SmartCampus API Map - Visual Guide

```
📍 BASE URL: http://localhost:8001/api

┌─────────────────────────────────────────────────────────┐
│                    🔐 AUTHENTICATION                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /users/register/          📝 Register new user  │
│  POST   /users/login/             🔓 Login user         │
│  POST   /users/logout/            🔒 Logout user        │
│  POST   /token/refresh/           🔄 Refresh token      │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                      👤 USER PROFILE                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /users/profile/           👁️  View profile      │
│  PUT    /users/profile/           ✏️  Update profile    │
│  POST   /users/change-password/   🔑 Change password    │
│  POST   /users/forgot-password/   💭 Request reset      │
│  POST   /users/reset-password/    🔓 Reset password     │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    📚 COURSES (Browse)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /courses/                 📋 List all courses   │
│         ?category=Web Development                        │
│         ?difficulty=Beginner                             │
│         ?featured=true                                   │
│         ?search=python                                   │
│         ?skip=0&limit=20                                 │
│                                                          │
│  GET    /courses/featured/        ⭐ Featured courses   │
│                                                          │
│  GET    /courses/{id}/            🔍 Course details     │
│                                                          │
│  GET    /courses/instructor/{id}/ 👨‍🏫 Instructor courses│
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              📚 COURSES (Instructor Actions) 🔒          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /courses/                 ➕ Create course      │
│  PUT    /courses/{id}/            ✏️  Update course     │
│  DELETE /courses/{id}/            🗑️  Delete course     │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               🎓 ENROLLMENTS (Student) 🔒                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /courses/{id}/enroll/     📝 Enroll in course  │
│  GET    /courses/my/enrollments/  📚 My enrollments    │
│  PUT    /courses/{id}/progress/   📊 Update progress   │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    ⭐ COURSE REVIEWS                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /courses/{id}/reviews/    👁️  View reviews     │
│  POST   /courses/{id}/reviews/ 🔒 💬 Add review        │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    📝 BLOG POSTS (Browse)                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /blog/                    📋 List all posts     │
│         ?category=Technology                             │
│         ?tag=python                                      │
│         ?featured=true                                   │
│         ?search=django                                   │
│         ?skip=0&limit=10                                 │
│                                                          │
│  GET    /blog/featured/           ⭐ Featured posts     │
│                                                          │
│  GET    /blog/{slug}/             🔍 Post details       │
│                                                          │
│  GET    /blog/author/{id}/        ✍️  Author's posts    │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              📝 BLOG POSTS (Author Actions) 🔒           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /blog/                    ➕ Create post        │
│  PUT    /blog/{slug}/             ✏️  Update post       │
│  DELETE /blog/{slug}/             🗑️  Delete post       │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   💬 BLOG COMMENTS 🔒                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /blog/{post_id}/comments/ 💬 Add comment       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Usage Flow Examples

### 👤 Student Journey

```
1. Register
   POST /api/users/register/
   
2. Login
   POST /api/users/login/
   → Get access token
   
3. Browse Courses
   GET /api/courses/
   GET /api/courses/featured/
   
4. View Course Details
   GET /api/courses/{id}/
   
5. Enroll in Course
   POST /api/courses/{id}/enroll/
   (with Bearer token)
   
6. Track Progress
   PUT /api/courses/{id}/progress/
   (with Bearer token)
   
7. Write Review
   POST /api/courses/{id}/reviews/
   (with Bearer token)
   
8. Read Blog
   GET /api/blog/
   GET /api/blog/{slug}/
   
9. Comment on Blog
   POST /api/blog/{post_id}/comments/
   (with Bearer token)
```

### 👨‍🏫 Instructor Journey

```
1. Register as Instructor
   POST /api/users/register/
   (role: "instructor")
   
2. Login
   POST /api/users/login/
   
3. Create Course
   POST /api/courses/
   (with Bearer token)
   
4. Update Course
   PUT /api/courses/{id}/
   (with Bearer token)
   
5. View My Courses
   GET /api/courses/instructor/{my_id}/
   
6. Write Blog Post
   POST /api/blog/
   (with Bearer token)
   
7. Manage Blog Posts
   PUT /api/blog/{slug}/
   DELETE /api/blog/{slug}/
   (with Bearer token)
```

## 🔐 Authentication Headers

For protected endpoints (marked with 🔒):

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

Get the token from:
- Registration response
- Login response
- Token refresh endpoint

## 📊 Response Format

### Success Response
```json
{
  "message": "Success message",
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error type",
  "detail": "Detailed error message"
}
```

## 🚦 HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | ✅ OK - Request successful |
| 201 | ✅ Created - Resource created |
| 400 | ❌ Bad Request - Invalid data |
| 401 | ❌ Unauthorized - No/invalid token |
| 403 | ❌ Forbidden - No permission |
| 404 | ❌ Not Found - Resource not found |
| 500 | ❌ Server Error - Internal error |

## 🎨 Frontend Integration Map

```
Frontend Template          →  Backend Endpoint
─────────────────────────────────────────────────
index.html                 →  GET /courses/featured/
                              GET /blog/featured/

courses.html               →  GET /courses/
                              GET /courses/?category=...

course-details.html        →  GET /courses/{id}/
                              POST /courses/{id}/enroll/
                              GET /courses/{id}/reviews/

instructors.html           →  GET /users/ (filter by role)
                              GET /courses/instructor/{id}/

instructor-profile.html    →  GET /users/{id}/profile/
                              GET /courses/instructor/{id}/

blog.html                  →  GET /blog/
                              GET /blog/?category=...

blog-details.html          →  GET /blog/{slug}/
                              POST /blog/{post_id}/comments/

enroll.html                →  POST /courses/{id}/enroll/

profile (student)          →  GET /users/profile/
                              GET /courses/my/enrollments/
                              PUT /users/profile/

dashboard (instructor)     →  GET /courses/instructor/{id}/
                              POST /courses/
                              POST /blog/
```

## 💡 Quick Tips

### Get All Courses
```
GET /api/courses/
```

### Search Courses
```
GET /api/courses/?search=python
```

### Filter by Category
```
GET /api/courses/?category=Web Development
```

### Get Featured Courses
```
GET /api/courses/featured/
```

### Get Course with Reviews
```
GET /api/courses/{course_id}/
```

### Enroll (Need Auth Token)
```
POST /api/courses/{course_id}/enroll/
Header: Authorization: Bearer {token}
```

### Get My Enrollments
```
GET /api/courses/my/enrollments/
Header: Authorization: Bearer {token}
```

### Create Blog Post (Instructor)
```
POST /api/blog/
Header: Authorization: Bearer {token}
Body: { title, slug, content, category, ... }
```

---

**Happy Coding! 🚀**
