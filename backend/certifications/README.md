# 🎓 SmartCampus Certification System

## Overview

A comprehensive certification system where instructors can create multi-step certifications with exams, and students earn badges upon completion.

## Features

### ✅ For Instructors

- Create and manage certifications for their courses
- Add multiple sequential steps (video, reading, quiz, assignment, exam)
- Configure passing scores and requirements
- Track student progress in real-time
- View completion analytics

### ✅ For Students

- Enroll in certifications for their courses
- Complete steps sequentially
- Take final exams with multiple attempts
- Earn verified badges upon passing
- Download shareable certificates
- Verify badge authenticity

## Database Schema (MongoDB)

### Collections

1. **certifications**

   - `_id`: ObjectId
   - `course_id`: string
   - `instructor_id`: string
   - `title`: string
   - `description`: string
   - `badge_image`: string (URL)
   - `passing_score`: number (default: 70)
   - `is_active`: boolean
   - `total_steps`: number
   - `created_at`: datetime
   - `updated_at`: datetime

2. **certification_steps**

   - `_id`: ObjectId
   - `certification_id`: string
   - `step_number`: number
   - `step_type`: enum ['video', 'reading', 'quiz', 'assignment', 'exam']
   - `title`: string
   - `description`: string
   - `content`: object (varies by type)
   - `duration_minutes`: number
   - `is_mandatory`: boolean
   - `passing_criteria`: object
   - `created_at`: datetime

3. **student_progress**

   - `_id`: ObjectId
   - `student_id`: string
   - `certification_id`: string
   - `course_id`: string
   - `current_step`: number
   - `completed_steps`: array of step IDs
   - `step_scores`: object {step_id: score}
   - `exam_attempts`: number
   - `exam_score`: number
   - `status`: enum ['not_started', 'in_progress', 'completed', 'failed']
   - `started_at`: datetime
   - `completed_at`: datetime
   - `badge_earned`: boolean

4. **earned_badges**
   - `_id`: ObjectId
   - `student_id`: string
   - `certification_id`: string
   - `course_id`: string
   - `final_score`: number
   - `verification_code`: string (unique)
   - `badge_url`: string
   - `earned_at`: datetime

## API Endpoints

### 🔐 Instructor Endpoints (Role: instructor)

#### Create Certification

```http
POST /api/certifications/create/
Authorization: Bearer {token}

{
  "course_id": "course123",
  "title": "Python Programming Mastery",
  "description": "Complete Python certification with practical projects",
  "badge_image": "https://example.com/badge.png",
  "passing_score": 75,
  "is_active": true
}
```

#### Update Certification

```http
PUT /api/certifications/{certification_id}/update/
Authorization: Bearer {token}

{
  "title": "Updated Title",
  "passing_score": 80
}
```

#### Delete Certification

```http
DELETE /api/certifications/{certification_id}/delete/
Authorization: Bearer {token}
```

#### Add Step

```http
POST /api/certifications/{certification_id}/steps/add/
Authorization: Bearer {token}

{
  "step_number": 1,
  "step_type": "video",
  "title": "Introduction to Python",
  "description": "Learn Python basics",
  "content": {
    "video_url": "https://youtube.com/...",
    "minimum_watch_time": 600
  },
  "duration_minutes": 30,
  "is_mandatory": true
}
```

#### Update Step

```http
PUT /api/certifications/steps/{step_id}/update/
Authorization: Bearer {token}

{
  "title": "Updated Step Title"
}
```

#### Delete Step

```http
DELETE /api/certifications/steps/{step_id}/delete/
Authorization: Bearer {token}
```

#### View Student Progress

```http
GET /api/certifications/{certification_id}/students/progress/
Authorization: Bearer {token}
```

---

### 👨‍🎓 Student Endpoints

#### Get Available Certifications

```http
GET /api/certifications/available/
Authorization: Bearer {token}
```

#### Enroll in Certification

```http
POST /api/certifications/{certification_id}/enroll/
Authorization: Bearer {token}
```

#### Get Certification Steps

```http
GET /api/certifications/{certification_id}/steps/
Authorization: Bearer {token}
```

#### Complete a Step

```http
POST /api/certifications/steps/complete/
Authorization: Bearer {token}

{
  "step_id": "step123",
  "score": 85.5,
  "submission_data": {
    "answers": {...}
  }
}
```

#### Submit Exam

```http
POST /api/certifications/{certification_id}/exam/submit/
Authorization: Bearer {token}

{
  "answers": {
    "0": "option_a",
    "1": "option_c",
    "2": "option_b"
  },
  "time_taken_minutes": 45
}
```

#### Get My Progress

```http
GET /api/certifications/my-progress/
Authorization: Bearer {token}
```

#### Get My Badges

```http
GET /api/certifications/my-badges/
Authorization: Bearer {token}
```

---

### 🌐 Public Endpoints

#### Verify Badge

```http
GET /api/certifications/verify/{verification_code}/
```

Response:

```json
{
  "valid": true,
  "badge": {
    "id": "badge123",
    "student_id": "student456",
    "certification_id": "cert789",
    "final_score": 92.5,
    "verification_code": "ABC123XYZ789",
    "earned_at": "2025-10-29T22:00:00Z"
  },
  "certification": {
    "title": "Python Programming Mastery",
    "description": "..."
  },
  "student": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

## Step Types & Content Schemas

### 1. Video Step

```json
{
  "step_type": "video",
  "content": {
    "video_url": "https://youtube.com/watch?v=...",
    "minimum_watch_time": 600,
    "transcript": "Optional transcript text"
  }
}
```

### 2. Reading Step

```json
{
  "step_type": "reading",
  "content": {
    "content_text": "Markdown or HTML content",
    "pdf_url": "https://example.com/reading.pdf",
    "estimated_time": 15
  }
}
```

### 3. Quiz Step

```json
{
  "step_type": "quiz",
  "content": {
    "questions": [
      {
        "question_text": "What is Python?",
        "question_type": "mcq",
        "options": ["A language", "A snake", "A framework"],
        "correct_answer": "A language",
        "points": 1
      }
    ],
    "time_limit_minutes": 30,
    "passing_score": 70,
    "allow_retakes": true,
    "max_attempts": 3
  }
}
```

### 4. Assignment Step

```json
{
  "step_type": "assignment",
  "content": {
    "instructions": "Create a Python script that...",
    "max_file_size_mb": 10,
    "allowed_file_types": [".py", ".zip"],
    "due_date": "2025-11-30T23:59:59Z",
    "grading_rubric": "Grading criteria..."
  }
}
```

### 5. Exam Step (Final)

```json
{
  "step_type": "exam",
  "content": {
    "questions": [...],
    "time_limit_minutes": 90,
    "passing_score": 75,
    "max_attempts": 3,
    "randomize_questions": true,
    "show_results_immediately": false
  }
}
```

## Business Rules

### Certification Creation

- Only instructors can create certifications
- Minimum 1 step required before exam
- Final exam is mandatory
- All steps must be sequential

### Student Progression

- Must complete steps in order
- Cannot skip steps
- Must pass quiz/exam steps to proceed
- Assignments require grading before proceeding
- Final exam unlocks after all steps completed

### Badge Earning

- Complete all steps
- Pass final exam with minimum score
- Unique verification code generated
- Email notification sent
- Badge is downloadable

### Retry Logic

- Quiz steps: unlimited retries (configurable)
- Exam: limited retries (default 3)
- After max retries: status = 'failed'

## Example Usage Flow

### Instructor Creates Certification

```python
# 1. Create certification
POST /api/certifications/create/
{
  "course_id": "python101",
  "title": "Python Basics Certificate",
  "description": "Learn Python fundamentals",
  "passing_score": 70
}

# 2. Add video step
POST /api/certifications/{cert_id}/steps/add/
{
  "step_number": 1,
  "step_type": "video",
  "title": "Python Introduction",
  "content": {
    "video_url": "...",
    "minimum_watch_time": 600
  }
}

# 3. Add quiz step
POST /api/certifications/{cert_id}/steps/add/
{
  "step_number": 2,
  "step_type": "quiz",
  "title": "Python Basics Quiz",
  "content": {
    "questions": [...],
    "passing_score": 70
  }
}

# 4. Add final exam
POST /api/certifications/{cert_id}/steps/add/
{
  "step_number": 3,
  "step_type": "exam",
  "title": "Final Exam",
  "content": {
    "questions": [...],
    "passing_score": 75,
    "max_attempts": 3
  }
}
```

### Student Completes Certification

```python
# 1. Enroll
POST /api/certifications/{cert_id}/enroll/

# 2. View steps
GET /api/certifications/{cert_id}/steps/

# 3. Complete video step
POST /api/certifications/steps/complete/
{
  "step_id": "step1"
}

# 4. Complete quiz step
POST /api/certifications/steps/complete/
{
  "step_id": "step2",
  "score": 85
}

# 5. Submit exam
POST /api/certifications/{cert_id}/exam/submit/
{
  "answers": {...},
  "time_taken_minutes": 60
}

# Response if passed:
{
  "message": "Congratulations! You passed the exam!",
  "score": 82.5,
  "passed": true,
  "badge": {
    "verification_code": "ABC123XYZ789",
    ...
  }
}
```

## Installation

### 1. Add to Django settings

```python
INSTALLED_APPS = [
    ...
    'certifications',
]
```

### 2. Add to URLs

```python
urlpatterns = [
    ...
    path('api/certifications/', include('certifications.urls')),
]
```

### 3. Create MongoDB Indexes

```javascript
// In MongoDB shell
db.certifications.createIndex({ course_id: 1 });
db.certifications.createIndex({ instructor_id: 1 });
db.certification_steps.createIndex({ certification_id: 1, step_number: 1 });
db.student_progress.createIndex({ student_id: 1 });
db.student_progress.createIndex({ certification_id: 1 });
db.student_progress.createIndex({ status: 1 });
db.earned_badges.createIndex({ student_id: 1 });
db.earned_badges.createIndex({ verification_code: 1 }, { unique: true });
```

### 4. Restart Backend Server

```bash
python manage.py runserver 8001
```

## Testing

### Test Certification Creation

```bash
curl -X POST http://localhost:8001/api/certifications/create/ \
  -H "Authorization: Bearer {instructor_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "test_course",
    "title": "Test Certification",
    "description": "Test description",
    "passing_score": 70
  }'
```

### Test Badge Verification

```bash
curl http://localhost:8001/api/certifications/verify/ABC123XYZ789/
```

## Email Notifications

The system sends email notifications for:

- ✅ Badge earned (includes verification code)
- 📧 Exam passed
- 📧 Exam failed (with retry info)

Configure email settings in `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=SmartCampus <your-email@gmail.com>
```

## Security Features

- ✅ Role-based access control (instructor/student)
- ✅ JWT authentication required
- ✅ Ownership verification for instructor actions
- ✅ Unique verification codes for badges
- ✅ Exam anti-cheating (time limits, attempt tracking)

## Next Steps (Future Enhancements)

- [ ] Badge PDF certificate generation
- [ ] Certificate templates
- [ ] Leaderboards
- [ ] LinkedIn badge sharing
- [ ] Certificate expiry/recertification
- [ ] Batch badge generation
- [ ] Advanced analytics dashboard
- [ ] Assignment file upload/grading
- [ ] Tab switching detection for exams
- [ ] Question randomization

## Support

For issues or questions, contact the SmartCampus development team.

---

**Created:** October 29, 2025  
**Version:** 1.0.0  
**Author:** SmartCampus Team
