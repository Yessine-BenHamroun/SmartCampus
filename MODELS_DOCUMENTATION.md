# SmartCampus Models Documentation

## 📚 Complete Model Structure

### User Model (Enhanced with Role Enum)
**File**: `backend/users/models.py`

**Roles**:
- `ROLE_STUDENT` = 'student' (default)
- `ROLE_INSTRUCTOR` = 'instructor'
- `ROLE_ADMIN` = 'admin'

**Fields**:
- id, email, username, password
- first_name, last_name, phone
- **role** (enum: student/instructor/admin)
- is_active, is_verified
- profile_image, bio
- two_factor_enabled, two_factor_secret
- created_at, updated_at, last_login
- reset_password_token, reset_password_expires

---

## 🎓 Course-Related Models

### 1. Course
**File**: `backend/courses/models.py`
**Collection**: `courses`

Main structure for courses.

**Fields**:
- title, description, short_description
- instructor_id (ref to User)
- category, difficulty_level
- price, discount_price
- duration_hours
- thumbnail_image, preview_video
- syllabus, requirements, learning_outcomes
- language, enrolled_count
- rating, reviews_count
- is_published, is_featured

---

### 2. Module
**File**: `backend/courses/extended_models.py`
**Collection**: `modules`

Grouping of lessons within a course.

**Fields**:
- course_id (ref to Course)
- title, description
- order (sequence in course)
- duration_minutes
- is_published

---

### 3. Lesson
**File**: `backend/courses/extended_models.py`
**Collection**: `lessons`

Multimodal content (video, text, quiz, exercise, etc.)

**Fields**:
- module_id (ref to Module)
- course_id (ref to Course)
- title, description
- content_type (video/text/quiz/exercise/assignment/resource)
- content (JSON: video_url, text_content, etc.)
- order, duration_minutes
- is_free_preview, is_published
- resources (downloadable files)

---

### 4. Quiz
**File**: `backend/courses/extended_models.py`
**Collection**: `quizzes`

Assessment questionnaire.

**Fields**:
- lesson_id, course_id
- title, description
- questions (array of question objects)
- passing_score (percentage)
- time_limit_minutes (0 = no limit)
- max_attempts (0 = unlimited)
- shuffle_questions, show_correct_answers
- is_published

---

### 5. ExerciseTemplate
**File**: `backend/courses/extended_models.py`
**Collection**: `exercise_templates`

Pattern for automatic exercise generation.

**Fields**:
- course_id, lesson_id
- title, description
- template_type (code/math/text)
- difficulty (easy/medium/hard)
- template_data (JSON structure)
- variables (dynamic data)
- solution_template
- test_cases, hints, tags

---

### 6. GeneratedExercise
**File**: `backend/courses/extended_models.py`
**Collection**: `generated_exercises`

Unique instance of exercise for a student.

**Fields**:
- template_id (ref to ExerciseTemplate)
- student_id (ref to User)
- course_id
- title, description
- exercise_data (generated content)
- solution, test_cases
- hints_used
- status (not_started/in_progress/submitted/graded)
- score, max_score
- generated_at, submitted_at, graded_at

---

### 7. Submission
**File**: `backend/courses/extended_models.py`
**Collection**: `submissions`

Student's submitted work.

**Fields**:
- student_id, course_id, lesson_id
- exercise_id (quiz or generated exercise)
- submission_type (assignment/quiz/exercise)
- content (JSON), files (array)
- status (submitted/graded/returned)
- score, max_score
- feedback
- graded_by (instructor_id)
- submitted_at, graded_at

---

### 8. Discussion
**File**: `backend/courses/extended_models.py`
**Collection**: `discussions`

Thread for course/lesson discussions.

**Fields**:
- course_id, lesson_id (optional)
- author_id (User who started)
- title, content
- tags
- is_pinned, is_resolved
- views_count, comments_count

---

### 9. Comment
**File**: `backend/courses/extended_models.py`
**Collection**: `comments`

Message in a discussion thread.

**Fields**:
- discussion_id
- author_id
- content
- parent_comment_id (for nested replies)
- is_instructor, is_accepted_answer
- likes_count

---

### 10. Progress
**File**: `backend/courses/extended_models.py`
**Collection**: `progress`

Track student progress in courses.

**Fields**:
- student_id, course_id, lesson_id
- completed, completed_at
- time_spent_minutes
- last_position (video timestamp)
- notes
- bookmarked

---

### 11. Enrollment (Existing)
**File**: `backend/courses/models.py`
**Collection**: `enrollments`

Track student enrollments in courses.

---

### 12. Review (Existing)
**File**: `backend/courses/models.py`
**Collection**: `reviews`

Course reviews and ratings.

---

## 🎯 Next Steps

### 1. Update Navbar with New Sections

You mentioned adding these to the navbar. Here's what should be added:

**Already Exist**:
- ✅ Courses
- ✅ Instructors

**Need to Add**:
- 📚 **My Learning** (student dashboard)
  - My Courses (enrolled courses)
  - My Progress
  - My Submissions
  - My Discussions
  
- 🎓 **Teaching** (instructor dashboard - only for instructors)
  - My Created Courses
  - Student Submissions
  - Course Analytics
  
- 💬 **Discussions** (course forums)
  - All Discussions
  - My Discussions
  - Trending Topics
  
- 📊 **Progress** (learning analytics)
  - Learning Path
  - Certificates
  - Achievements

### 2. Create Views for New Features

I'll create views for these sections. Which ones would you like me to implement first?

**Priority 1 (Essential)**:
1. My Learning Dashboard
2. Course Detail with Modules/Lessons
3. Lesson Player
4. Quiz Taking
5. Discussion Forums

**Priority 2 (Important)**:
6. Exercise Generation
7. Submission Management
8. Progress Tracking
9. Instructor Dashboard

**Priority 3 (Nice to Have)**:
10. Analytics Dashboard
11. Certificate Generation
12. Advanced Features

### 3. API Endpoints Needed

For each model, we'll need CRUD endpoints:
- GET /api/courses/{id}/modules/
- GET /api/courses/{id}/lessons/
- POST /api/lessons/{id}/progress/
- GET /api/discussions/?course_id=X
- POST /api/discussions/{id}/comments/
- etc.

### 4. Frontend Templates Needed

New template pages:
- `my_learning.html` - Student dashboard
- `course_player.html` - Watch lessons
- `quiz_take.html` - Take quiz
- `discussions.html` - Forum list
- `discussion_detail.html` - Thread view
- `instructor_dashboard.html` - Teacher panel
- `submissions.html` - View submissions

---

## 🚀 Implementation Plan

**Phase 1: Student Learning Experience**
1. Course detail page with modules/lessons list
2. Lesson player (video/text/quiz)
3. Progress tracking
4. Quiz taking system

**Phase 2: Collaboration**
5. Discussion forums
6. Comments and replies
7. Q&A system

**Phase 3: Instructor Tools**
8. Course creation/management
9. Submission grading
10. Student progress monitoring

**Phase 4: Advanced Features**
11. Exercise generation AI
12. Analytics and reporting
13. Certificates and achievements

---

Would you like me to:
1. **Update the navbar** with the new menu items?
2. **Create views** for the student dashboard (My Learning)?
3. **Build the course player** for watching lessons?
4. **Set up discussion forums**?

Let me know which feature you'd like to implement first!
