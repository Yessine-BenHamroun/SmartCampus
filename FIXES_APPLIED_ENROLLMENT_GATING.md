# Fixes Applied: Enrollment & Gating System

## Overview
This document outlines all fixes applied to resolve the enrollment connection error and implement proper gating for quizzes and assignments based on course progress.

---

## Issue 1: ERR_CONNECTION_REFUSED on Enrollment

### Problem
Frontend was calling `http://localhost:8001/api/courses/{courseId}/enroll/` but the backend was not running on port 8001, causing:
```
POST http://localhost:8001/api/courses/6901007…/enroll/ net::ERR_CONNECTION_REFUSED
```

### Solution
Created a PowerShell script to start the Django backend on port 8001:

**File:** `run_backend_8001.ps1`
```powershell
# Start Django backend on port 8001
Write-Host "Starting Django backend on port 8001..." -ForegroundColor Green
Write-Host "Navigate to http://localhost:8001 to access the API" -ForegroundColor Cyan

cd backend
python manage.py runserver 8001
```

### How to Use
1. Open PowerShell in the project root
2. Run: `.\run_backend_8001.ps1`
3. The backend will start on `http://localhost:8001`
4. All frontend API calls to `http://localhost:8001` will now work

---

## Issue 2: Quizzes & Assignments Not Gated by Progress

### Problem
- Quizzes were accessible even if the student hadn't completed the lesson
- Assignments were accessible even if the student hadn't completed all lessons
- No visibility control based on course progress

### Solution

#### A. Added Progress Status Endpoint

**File:** `backend/courses/views_progress.py`

New endpoint: `GET /api/courses/<course_id>/status/`

Returns:
```json
{
  "course_id": "...",
  "course_title": "...",
  "lessons": [
    {
      "id": "...",
      "title": "...",
      "completed": true/false,
      "can_take_quiz": true/false,
      "quiz_id": "..." or null,
      "duration_minutes": 0
    }
  ],
  "course_completed": true/false,
  "can_take_assignment": true/false,
  "assignments": [
    {
      "id": "...",
      "title": "...",
      "available": true/false
    }
  ],
  "completion_percentage": 0-100
}
```

**Route:** Added to `backend/courses/urls.py`
```python
path('<str:course_id>/status/', get_course_status, name='course-status'),
```

#### B. Quiz Gating Logic

**File:** `backend/courses/views_quiz.py`

Modified `get_lesson_quiz()` to:
1. Check if the student is an instructor (instructors bypass gating)
2. For students: verify the lesson is marked as completed in StudentProgress
3. Return 403 Forbidden if lesson is not completed
4. Include `available: true` flag in response if accessible

```python
# For students, check if lesson is completed
if not is_instructor:
    progress = StudentProgress.find_by_student_and_course(student_id, course_id)
    lesson_completed = ObjectId(lesson_id) in (progress.lessons_completed if progress else [])
    
    if not lesson_completed:
        return Response({
            'error': 'You must complete this lesson before taking the quiz',
            'lesson_id': lesson_id,
            'available': False
        }, status=status.HTTP_403_FORBIDDEN)
```

#### C. Assignment Gating Logic

**File:** `backend/courses/views_assignment.py`

Modified `get_assignment_detail()` to:
1. Check if the student is an instructor (instructors bypass gating)
2. For students: retrieve all lessons in the course
3. Verify ALL lessons are marked as completed in StudentProgress
4. Return 403 Forbidden if any lesson is incomplete
5. Include `available: true` flag in response if accessible

```python
# For students, check if all lessons in the course are completed
if not is_instructor:
    course_id = str(assignment.course_id)
    progress = StudentProgress.find_by_student_and_course(student_id, course_id)
    
    # Get all lessons in the course
    modules = Module.find_by_course(course_id)
    all_lessons = []
    for module in modules:
        lessons = Lesson.find_by_module(str(module.id))
        all_lessons.extend(lessons)
    
    # Check if all lessons are completed
    lessons_completed = progress.lessons_completed if progress else []
    all_lessons_completed = all(
        ObjectId(lesson.id) in lessons_completed for lesson in all_lessons
    ) if all_lessons else False
    
    if not all_lessons_completed:
        return Response({
            'error': 'You must complete all lessons in this course before accessing the assignment',
            'assignment_id': assignment_id,
            'available': False,
            'lessons_completed': len(lessons_completed),
            'total_lessons': len(all_lessons)
        }, status=status.HTTP_403_FORBIDDEN)
```

---

## Frontend Integration

### How to Use the New Endpoints

#### 1. Get Course Status (Quizzes & Assignments Availability)

```javascript
async function getCourseStatus(courseId) {
  const response = await fetch(`http://localhost:8001/api/courses/${courseId}/status/`, {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer ' + accessToken,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  
  // data.lessons[i].can_take_quiz - true if quiz is available
  // data.can_take_assignment - true if assignment is available
  // data.lessons[i].completed - true if lesson is completed
  
  return data;
}
```

#### 2. Mark Lesson Complete

```javascript
async function completeLesson(lessonId, timeSpentMinutes = 0) {
  const response = await fetch(`http://localhost:8001/api/courses/lesson/${lessonId}/complete/`, {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + accessToken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      time_spent_minutes: timeSpentMinutes
    })
  });
  
  return await response.json();
}
```

#### 3. Access Quiz (After Lesson Completion)

```javascript
async function getQuiz(lessonId) {
  const response = await fetch(`http://localhost:8001/api/courses/lesson/${lessonId}/quiz/`, {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer ' + accessToken,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.status === 403) {
    const error = await response.json();
    console.log('Quiz not available:', error.error);
    return null;
  }
  
  return await response.json();
}
```

#### 4. Access Assignment (After All Lessons Completion)

```javascript
async function getAssignment(assignmentId) {
  const response = await fetch(`http://localhost:8001/api/courses/assignment/${assignmentId}/`, {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer ' + accessToken,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.status === 403) {
    const error = await response.json();
    console.log('Assignment not available:', error.error);
    console.log(`Lessons completed: ${error.lessons_completed}/${error.total_lessons}`);
    return null;
  }
  
  return await response.json();
}
```

---

## Files Modified

1. **backend/courses/views_progress.py**
   - Added `get_course_status()` endpoint
   - Returns lesson completion status and quiz/assignment availability

2. **backend/courses/views_quiz.py**
   - Modified `get_lesson_quiz()` to gate access based on lesson completion
   - Added availability flag to response

3. **backend/courses/views_assignment.py**
   - Modified `get_assignment_detail()` to gate access based on all lessons completion
   - Added availability flag and progress info to response

4. **backend/courses/urls.py**
   - Added import for `get_course_status`
   - Added route: `path('<str:course_id>/status/', get_course_status, name='course-status')`

5. **run_backend_8001.ps1** (NEW)
   - PowerShell script to start backend on port 8001

---

## Testing Checklist

- [ ] Backend starts on port 8001 without errors
- [ ] Enrollment works: `POST /api/courses/{courseId}/enroll/` returns 201
- [ ] Course status endpoint works: `GET /api/courses/{courseId}/status/` returns lesson data
- [ ] Quiz is blocked before lesson completion: `GET /api/courses/lesson/{lessonId}/quiz/` returns 403
- [ ] Quiz is accessible after lesson completion: returns 200 with quiz data
- [ ] Assignment is blocked before all lessons completion: `GET /api/courses/assignment/{assignmentId}/` returns 403
- [ ] Assignment is accessible after all lessons completion: returns 200 with assignment data
- [ ] Lesson completion updates progress: `POST /api/courses/lesson/{lessonId}/complete/` updates StudentProgress
- [ ] Progress percentage increases as lessons are completed

---

## Architecture

### Progress Tracking Flow

```
Student enrolls in course
    ↓
StudentProgress record created (0% completion)
    ↓
Student completes lesson
    ↓
POST /api/courses/lesson/{lessonId}/complete/
    ↓
StudentProgress.mark_lesson_complete(lesson_id)
    ↓
Completion percentage recalculated
    ↓
GET /api/courses/{courseId}/status/
    ↓
Returns: lessons[i].can_take_quiz = true (if lesson completed)
    ↓
Student can now access quiz
    ↓
After all lessons completed:
    ↓
Returns: can_take_assignment = true
    ���
Student can now access assignment
```

### Gating Logic

**Quiz Availability:**
- Instructor: Always accessible
- Student: Only if `ObjectId(lesson_id) in StudentProgress.lessons_completed`

**Assignment Availability:**
- Instructor: Always accessible
- Student: Only if ALL lessons in course are in `StudentProgress.lessons_completed`

---

## Error Responses

### Quiz Not Available
```json
{
  "error": "You must complete this lesson before taking the quiz",
  "lesson_id": "...",
  "available": false
}
```
Status: 403 Forbidden

### Assignment Not Available
```json
{
  "error": "You must complete all lessons in this course before accessing the assignment",
  "assignment_id": "...",
  "available": false,
  "lessons_completed": 2,
  "total_lessons": 5
}
```
Status: 403 Forbidden

---

## Next Steps

1. Update frontend templates to:
   - Call `/api/courses/{courseId}/status/` on page load
   - Show "Complete lesson to unlock quiz" if `can_take_quiz` is false
   - Show "Complete all lessons to unlock assignment" if `can_take_assignment` is false
   - Refresh status after lesson completion

2. Add UI indicators:
   - Locked icon on unavailable quizzes/assignments
   - Progress bar showing lessons completed
   - Unlock notifications when quiz/assignment becomes available

3. Consider adding:
   - Email notifications when assignment becomes available
   - Prerequisite lesson requirements (not just completion)
   - Time-based availability (e.g., assignment available after X days)
