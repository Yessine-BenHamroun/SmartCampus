# SmartCampus Backend - Complete API Documentation

## Base URL
```
http://localhost:8001/api
```

---

## 📚 Table of Contents
1. [Authentication](#authentication)
2. [Users](#users)
3. [Courses](#courses)
4. [Enrollments](#enrollments)
5. [Reviews](#reviews)
6. [Blog](#blog)
7. [Comments](#comments)

---

## 🔐 Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Get Access Token
See [Login](#post-apiuserslogin) endpoint to get tokens.

---

## 👤 Users

### POST `/api/users/register/`
Register a new user

**Request Body:**
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

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "...",
    "email": "student@example.com",
    "username": "johndoe",
    "role": "student"
  },
  "tokens": {
    "refresh": "...",
    "access": "..."
  }
}
```

### POST `/api/users/login/`
Login user

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "SecurePass123"
}
```

### GET `/api/users/profile/` 🔒
Get current user profile

### PUT `/api/users/profile/` 🔒
Update user profile

### POST `/api/users/change-password/` 🔒
Change password

### POST `/api/users/forgot-password/`
Request password reset

### POST `/api/users/reset-password/`
Reset password with token

---

## 📖 Courses

### GET `/api/courses/`
Get all courses

**Query Parameters:**
- `category` - Filter by category
- `difficulty` - Filter by difficulty level
- `featured` - Filter featured courses (true/false)
- `search` - Search in title/description
- `skip` - Pagination skip (default: 0)
- `limit` - Results per page (default: 20)

**Response:**
```json
{
  "count": 10,
  "courses": [
    {
      "id": "...",
      "title": "Web Development Bootcamp",
      "description": "Learn full-stack web development",
      "short_description": "Complete web dev course",
      "instructor": {
        "id": "...",
        "name": "Jane Doe",
        "profile_image": "..."
      },
      "category": "Web Development",
      "difficulty_level": "Beginner",
      "price": 99.99,
      "discount_price": 79.99,
      "duration_hours": 40,
      "thumbnail_image": "...",
      "enrolled_count": 150,
      "rating": 4.5,
      "reviews_count": 25,
      "is_published": true,
      "is_featured": true,
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

### POST `/api/courses/` 🔒
Create a new course (Instructor/Admin only)

**Request Body:**
```json
{
  "title": "Python Programming",
  "description": "Learn Python from scratch",
  "short_description": "Complete Python course",
  "instructor_id": "...",
  "category": "Programming",
  "difficulty_level": "Beginner",
  "price": 89.99,
  "discount_price": 69.99,
  "duration_hours": 30,
  "thumbnail_image": "...",
  "syllabus": [
    {
      "module": "Introduction",
      "lessons": ["What is Python", "Setup"]
    }
  ],
  "requirements": ["Basic computer skills"],
  "learning_outcomes": ["Master Python basics"],
  "language": "English",
  "is_published": true,
  "is_featured": false
}
```

### GET `/api/courses/featured/`
Get featured courses

**Query Parameters:**
- `limit` - Number of courses (default: 6)

### GET `/api/courses/<course_id>/`
Get course details

**Response:**
```json
{
  "course": {
    "id": "...",
    "title": "...",
    "description": "...",
    "instructor": {
      "id": "...",
      "name": "...",
      "email": "...",
      "bio": "...",
      "profile_image": "..."
    },
    "syllabus": [...],
    "requirements": [...],
    "learning_outcomes": [...],
    "reviews": [
      {
        "id": "...",
        "rating": 5,
        "comment": "Great course!",
        "created_at": "..."
      }
    ],
    ...
  }
}
```

### PUT `/api/courses/<course_id>/` 🔒
Update course (Course instructor only)

### DELETE `/api/courses/<course_id>/` 🔒
Delete course (Course instructor only)

### GET `/api/courses/instructor/<instructor_id>/`
Get all courses by an instructor

---

## 🎓 Enrollments

### POST `/api/courses/<course_id>/enroll/` 🔒
Enroll in a course

**Response:**
```json
{
  "message": "Successfully enrolled in course",
  "enrollment": {
    "id": "...",
    "student_id": "...",
    "course_id": "...",
    "enrolled_at": "2025-01-01T00:00:00",
    "progress": 0.0,
    "completed": false
  }
}
```

### GET `/api/courses/my/enrollments/` 🔒
Get all enrollments for logged-in student

**Response:**
```json
{
  "count": 5,
  "enrollments": [
    {
      "id": "...",
      "enrolled_at": "...",
      "progress": 45.5,
      "completed": false,
      "course": {
        "id": "...",
        "title": "...",
        "thumbnail_image": "...",
        ...
      }
    }
  ]
}
```

### PUT `/api/courses/<course_id>/progress/` 🔒
Update course progress

**Request Body:**
```json
{
  "progress": 75.5
}
```

---

## ⭐ Reviews

### GET `/api/courses/<course_id>/reviews/`
Get all reviews for a course

**Response:**
```json
{
  "count": 10,
  "reviews": [
    {
      "id": "...",
      "rating": 5,
      "comment": "Excellent course!",
      "student": {
        "id": "...",
        "name": "John Doe",
        "profile_image": "..."
      },
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

### POST `/api/courses/<course_id>/reviews/` 🔒
Create a review (Must be enrolled)

**Request Body:**
```json
{
  "course_id": "...",
  "rating": 5,
  "comment": "Great course, learned a lot!"
}
```

---

## 📝 Blog

### GET `/api/blog/`
Get all blog posts

**Query Parameters:**
- `category` - Filter by category
- `tag` - Filter by tag
- `featured` - Filter featured posts (true/false)
- `search` - Search in title/content
- `skip` - Pagination skip (default: 0)
- `limit` - Results per page (default: 10)

**Response:**
```json
{
  "count": 5,
  "posts": [
    {
      "id": "...",
      "title": "10 Tips for Learning Python",
      "slug": "10-tips-learning-python",
      "excerpt": "Quick tips to master Python faster",
      "author": {
        "id": "...",
        "name": "Jane Instructor",
        "profile_image": "..."
      },
      "category": "Technology",
      "tags": ["python", "programming", "tips"],
      "featured_image": "...",
      "views_count": 150,
      "likes_count": 25,
      "comments_count": 10,
      "published_at": "2025-01-01T00:00:00"
    }
  ]
}
```

### POST `/api/blog/` 🔒
Create a blog post (Instructor/Admin only)

**Request Body:**
```json
{
  "title": "Getting Started with Django",
  "slug": "getting-started-django",
  "content": "Full blog post content here...",
  "excerpt": "Short summary",
  "category": "Technology",
  "tags": ["django", "python", "web"],
  "featured_image": "...",
  "is_published": true,
  "is_featured": false
}
```

### GET `/api/blog/featured/`
Get featured blog posts

**Query Parameters:**
- `limit` - Number of posts (default: 3)

### GET `/api/blog/<slug>/`
Get blog post by slug

**Response:**
```json
{
  "post": {
    "id": "...",
    "title": "...",
    "slug": "...",
    "content": "Full content...",
    "author": {
      "id": "...",
      "name": "...",
      "email": "...",
      "bio": "...",
      "profile_image": "..."
    },
    "comments": [
      {
        "id": "...",
        "content": "Great post!",
        "user": {
          "name": "...",
          "profile_image": "..."
        },
        "created_at": "..."
      }
    ],
    ...
  }
}
```

### PUT `/api/blog/<slug>/` 🔒
Update blog post (Author only)

### DELETE `/api/blog/<slug>/` 🔒
Delete blog post (Author only)

### GET `/api/blog/author/<author_id>/`
Get all posts by an author

---

## 💬 Comments

### POST `/api/blog/<post_id>/comments/` 🔒
Add a comment to a blog post

**Request Body:**
```json
{
  "post_id": "...",
  "content": "Great article, very helpful!",
  "parent_id": null
}
```

**Response:**
```json
{
  "message": "Comment created successfully",
  "comment": {
    "id": "...",
    "post_id": "...",
    "user_id": "...",
    "content": "...",
    "created_at": "..."
  }
}
```

---

## 📊 Data Models

### User
```javascript
{
  _id: ObjectId,
  email: String (unique),
  username: String (unique),
  password: String (hashed),
  first_name: String,
  last_name: String,
  phone: String,
  role: String, // 'student', 'instructor', 'admin'
  is_active: Boolean,
  is_verified: Boolean,
  profile_image: String,
  bio: String,
  created_at: Date,
  updated_at: Date,
  last_login: Date
}
```

### Course
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  short_description: String,
  instructor_id: ObjectId (ref: User),
  category: String,
  difficulty_level: String,
  price: Number,
  discount_price: Number,
  duration_hours: Number,
  thumbnail_image: String,
  preview_video: String,
  syllabus: Array,
  requirements: Array,
  learning_outcomes: Array,
  language: String,
  enrolled_count: Number,
  rating: Number,
  reviews_count: Number,
  is_published: Boolean,
  is_featured: Boolean,
  created_at: Date,
  updated_at: Date
}
```

### Enrollment
```javascript
{
  _id: ObjectId,
  student_id: ObjectId (ref: User),
  course_id: ObjectId (ref: Course),
  enrolled_at: Date,
  progress: Number, // 0-100%
  completed: Boolean,
  completed_at: Date,
  last_accessed: Date,
  certificate_issued: Boolean
}
```

### Review
```javascript
{
  _id: ObjectId,
  course_id: ObjectId (ref: Course),
  student_id: ObjectId (ref: User),
  rating: Number, // 1-5
  comment: String,
  created_at: Date,
  updated_at: Date
}
```

### BlogPost
```javascript
{
  _id: ObjectId,
  title: String,
  slug: String (unique),
  content: String,
  excerpt: String,
  author_id: ObjectId (ref: User),
  category: String,
  tags: Array,
  featured_image: String,
  is_published: Boolean,
  is_featured: Boolean,
  views_count: Number,
  likes_count: Number,
  comments_count: Number,
  published_at: Date,
  created_at: Date,
  updated_at: Date
}
```

### BlogComment
```javascript
{
  _id: ObjectId,
  post_id: ObjectId (ref: BlogPost),
  user_id: ObjectId (ref: User),
  content: String,
  parent_id: ObjectId (ref: BlogComment), // for nested comments
  created_at: Date,
  updated_at: Date
}
```

---

## 🔒 Permission Levels

| Role | Permissions |
|------|-------------|
| **Student** | View courses, enroll, write reviews, comment on blogs |
| **Instructor** | All student permissions + Create/manage own courses, create blog posts |
| **Admin** | All permissions including user management |

---

## 🧪 Testing Examples

### Register and Login
```bash
# Register
curl -X POST http://localhost:8001/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"testuser","password":"Test123456","confirm_password":"Test123456","first_name":"Test","last_name":"User","role":"student"}'

# Login
curl -X POST http://localhost:8001/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123456"}'
```

### Get Courses
```bash
curl http://localhost:8001/api/courses/

# With filters
curl "http://localhost:8001/api/courses/?category=Web+Development&difficulty=Beginner"
```

### Enroll in Course (with auth)
```bash
curl -X POST http://localhost:8001/api/courses/<course_id>/enroll/ \
  -H "Authorization: Bearer <access_token>"
```

---

## 📌 Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

## 🚀 Next Features to Implement

- [ ] File upload for course materials
- [ ] Video streaming for course content
- [ ] Payment integration (Stripe/PayPal)
- [ ] Certificates generation
- [ ] Email notifications
- [ ] Real-time chat
- [ ] Forum discussions
- [ ] Assignments and quizzes
- [ ] Analytics dashboard
- [ ] Social sharing

---

🔒 = Requires Authentication
