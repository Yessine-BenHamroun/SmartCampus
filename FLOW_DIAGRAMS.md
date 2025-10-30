# Flow Diagrams - Enrollment & Gating System

## 1. Enrollment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENROLLMENT FLOW                              │
└─────────────────────────────────────────────────────────────────┘

Student Views Course
        │
        ▼
┌──────────────────────────────────┐
│ course_detail.html               │
│ - Shows course info              │
│ - "Start Learning" button        │
└──────────────────────────────────┘
        │
        ▼ (Click "Start Learning")
┌──────────────────────────────────┐
│ enrollInCourse() JS function     │
│ - Gets access token              │
│ - Calls enroll API               │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ POST /api/courses/{courseId}/enroll/                         │
│ Header: Authorization: Bearer {token}                        │
│ Port: 8001 ✅ (FIXED)                                        │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Backend: EnrollCourseView.post()                             │
│ - Verify user is authenticated                              │
│ - Check user is not instructor                              │
│ - Check course exists                                       │
│ - Check not already enrolled                                │
│ - Create Enrollment record                                  │
│ - Create StudentProgress record (0% completion)             │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Response: 201 Created                                        │
│ {                                                            │
│   "message": "Successfully enrolled in course",             │
│   "enrollment": {...}                                       │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────��────────────────────────────────────────���────┐
│ Frontend: Redirect to course_learning.html                   │
│ - Student can now access course content                      │
│ - Lessons are visible                                        │
│ - Quizzes/Assignments are LOCKED                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Quiz Gating Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUIZ GATING FLOW                              │
└─────────────────────────────────────────────────────────────────┘

SCENARIO A: BEFORE LESSON COMPLETION
═════════════════════════════════════

Student Views Lesson
        │
        ▼
┌──────────────────────────────────┐
│ course_learning.html             │
│ - Shows lesson content           │
│ - Quiz button (LOCKED/DISABLED)  │
└──────────────────────────────────┘
        │
        ▼ (Student tries to access quiz)
┌──────────────────────────────────────────────────────────────┐
│ GET /api/courses/lesson/{lessonId}/quiz/                     │
│ Header: Authorization: Bearer {token}                        │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Backend: get_lesson_quiz()                                   │
│ - Get lesson                                                 │
│ - Get quiz for lesson                                        │
│ - Check if user is instructor                               │
│ - If student:                                               │
│   - Get StudentProgress                                      │
│   - Check: ObjectId(lesson_id) in progress.lessons_completed│
│   - ❌ NOT FOUND                                             │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Response: 403 Forbidden                                      │
│ {                                                            │
│   "error": "You must complete this lesson before taking...", │
│   "lesson_id": "...",                                        │
│   "available": false                                         │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────��──────────────────┐
│ Frontend: Show message                                       │
│ "Complete this lesson to unlock the quiz"                   │
└──────────────────────────────────────────────────────────────┘


SCENARIO B: AFTER LESSON COMPLETION
════════════════════════════════════

Student Finishes Lesson
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ POST /api/courses/lesson/{lessonId}/complete/                │
│ Body: { "time_spent_minutes": 30 }                           │
│ Header: Authorization: Bearer {token}                        │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Backend: update_lesson_progress()                            │
│ - Get StudentProgress                                        │
│ - Call: progress.mark_lesson_complete(lesson_id)            │
│ - Add lesson_id to lessons_completed list                    │
│ - Recalculate completion_percentage                          │
│ - Save to database                                           │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Response: 200 OK                                             │
│ {                                                            │
│   "message": "Lesson marked as completed",                   │
│   "progress": {                                              │
│     "lessons_completed": ["lesson1", "lesson2"],             │
│     "completion_percentage": 50                              │
│   }                                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Frontend: Refresh course status                              │
│ GET /api/courses/{courseId}/status/                          │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Response: 200 OK                                             │
│ {                                                            │
│   "lessons": [                                               │
│     {                                                        │
│       "id": "lesson1",                                       │
│       "completed": true,                                     │
│       "can_take_quiz": true,  ✅ NOW TRUE!                   │
│       "quiz_id": "quiz1"                                     │
│     }                                                        │
│   ]                                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Frontend: Show quiz button (ENABLED)                         │
│ Student can now click "Take Quiz"                            │
└───────────────────────────────────────────────��──────────────┘
        │
        ▼ (Student clicks "Take Quiz")
┌──────────────────────────────────────────────────────────────┐
│ GET /api/courses/lesson/{lessonId}/quiz/                     │
│ Header: Authorization: Bearer {token}                        │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Backend: get_lesson_quiz()                                   │
│ - Get lesson                                                 │
│ - Get quiz for lesson                                        │
│ - Check if user is instructor                               │
│ - If student:                                               │
│   - Get StudentProgress                                      │
│   - Check: ObjectId(lesson_id) in progress.lessons_completed│
│   - ✅ FOUND!                                                │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Response: 200 OK                                             │
│ {                                                            │
│   "id": "quiz1",                                             │
│   "title": "Lesson 1 Quiz",                                  │
│   "questions": [...],                                        │
│   "available": true                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────���─────────────────────────────────────────────────┐
│ Frontend: Display quiz                                       │
│ Student can now take the quiz                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Assignment Gating Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                 ASSIGNMENT GATING FLOW                           │
└─────────────────────────────────────────────────────────────────┘

SCENARIO A: BEFORE ALL LESSONS COMPLETION
═══��═══════════════════════════════════════

Student Views Course (2/5 lessons completed)
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ course_learning.html                                         │
│ - Shows lessons (2 completed, 3 remaining)                   │
│ - Assignment button (LOCKED/DISABLED)                        │
│ - Progress: 40%                                              │
└──────────────────────────────────────────────────────────────┘
        │
        ▼ (Student tries to access assignment)
┌──────────────────────────────────────────────────────────────┐
│ GET /api/courses/assignment/{assignmentId}/                  │
│ Header: Authorization: Bearer {token}                        │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Backend: get_assignment_detail()                             │
│ - Get assignment                                             │
│ - Check if user is instructor                               │
│ - If student:                                               │
│   - Get StudentProgress                                      │
│   - Get all lessons in course (5 total)                      │
│   - Check: all lessons in progress.lessons_completed         │
│   - ❌ Only 2/5 found                                        │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Response: 403 Forbidden                                      │
│ {                                                            │
│   "error": "You must complete all lessons in this course...",│
│   "assignment_id": "...",                                    │
│   "available": false,                                        │
│   "lessons_completed": 2,                                    │
│   "total_lessons": 5                                         │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Frontend: Show message                                       │
│ "Complete all 5 lessons to unlock the assignment"            │
│ "Progress: 2/5 lessons completed"                            │
└──────────────────────────────────────────────────────────────┘


SCENARIO B: AFTER ALL LESSONS COMPLETION
═════════════════════════════════════════

Student Completes Last Lesson
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ POST /api/courses/lesson/{lessonId5}/complete/               │
│ Body: { "time_spent_minutes": 25 }                           │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────��─────────────────────────────────────────┐
│ Backend: update_lesson_progress()                            │
│ - Add lesson5 to lessons_completed                           │
│ - Recalculate: 5/5 lessons = 100% completion                 │
│ - Save to database                                           │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Response: 200 OK                                             │
│ {                                                            │
│   "progress": {                                              │
│     "lessons_completed": ["l1", "l2", "l3", "l4", "l5"],     │
│     "completion_percentage": 100                             │
│   }                                                          │
│ }                                                            │
└─────────────��────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Frontend: Refresh course status                              │
│ GET /api/courses/{courseId}/status/                          │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Response: 200 OK                                             │
│ {                                                            │
│   "course_completed": true,                                  │
│   "can_take_assignment": true,  ✅ NOW TRUE!                 │
│   "assignments": [                                           │
│     {                                                        │
│       "id": "assignment1",                                   │
│       "title": "Final Project",                              │
│       "available": true                                      │
│     }                                                        │
│   ]                                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Frontend: Show assignment button (ENABLED)                   │
│ Show congratulations message                                 │
│ "All lessons completed! Assignment is now available"         │
└───────────��──────────────────────────────────────────────────┘
        │
        ▼ (Student clicks "Take Assignment")
┌──────────────────────────────────────────────────────────────┐
│ GET /api/courses/assignment/{assignmentId}/                  │
│ Header: Authorization: Bearer {token}                        │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Backend: get_assignment_detail()                             │
│ - Get assignment                                             │
│ - Check if user is instructor                               │
│ - If student:                                               │
│   - Get StudentProgress                                      │
│   - Get all lessons in course (5 total)                      │
│   - Check: all lessons in progress.lessons_completed         │
│   - ✅ All 5/5 found!                                        │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Response: 200 OK                                             │
│ {                                                            │
│   "id": "assignment1",                                       │
│   "title": "Final Project",                                  │
│   "description": "...",                                      │
│   "questions": [...],                                        │
│   "available": true                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Frontend: Display assignment                                 │
│ Student can now submit the assignment                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Database State Changes

```
┌─────────────────────────────────────────────────────────────────┐
��              DATABASE STATE PROGRESSION                          │
└─────────────────────────────────────────────────────────────────┘

STEP 1: Student Enrolls
═══════════════════════

Enrollment Collection:
┌────────────────────────────────────────┐
│ {                                      │
│   _id: ObjectId(...),                  │
│   student_id: ObjectId(...),           │
│   course_id: ObjectId(...),            │
│   enrolled_at: 2024-01-15T10:00:00Z,   │
│   progress: 0,                         │
│   completed: false                     │
│ }                                      │
└────────────────────────────────────────┘

StudentProgress Collection:
┌────────────────────────────────────────┐
│ {                                      │
│   _id: ObjectId(...),                  │
│   student_id: ObjectId(...),           │
│   course_id: ObjectId(...),            │
│   lessons_completed: [],               │ ← Empty
│   quizzes_completed: [],               │ ← Empty
│   assignments_completed: [],           │ ← Empty
│   completion_percentage: 0,            │ ← 0%
│   time_spent_minutes: 0,               │
│   created_at: 2024-01-15T10:00:00Z     │
│ }                                      │
└────────────────────────────────────────┘


STEP 2: Student Completes Lesson 1
═══════════════════════════════════

StudentProgress Collection:
┌────────────────────────────────────────┐
│ {                                      │
│   _id: ObjectId(...),                  │
│   student_id: ObjectId(...),           │
│   course_id: ObjectId(...),            │
│   lessons_completed: [                 │
│     ObjectId("lesson1")                │ ← Added!
│   ],                                   │
│   quizzes_completed: [],               │
│   assignments_completed: [],           │
│   completion_percentage: 20,           │ ← 20% (1/5 lessons)
│   time_spent_minutes: 30,              │ ← Updated
│   updated_at: 2024-01-15T10:30:00Z     │
│ }                                      │
└────────────────────────────────────────┘

✅ Quiz 1 is now available
❌ Assignment still locked


STEP 3: Student Completes All Lessons
══════════════════════════════════════

StudentProgress Collection:
┌────────────────────────────────────────┐
│ {                                      │
│   _id: ObjectId(...),                  │
│   student_id: ObjectId(...),           │
│   course_id: ObjectId(...),            │
│   lessons_completed: [                 │
│     ObjectId("lesson1"),               │
│     ObjectId("lesson2"),               │
│     ObjectId("lesson3"),               │
│     ObjectId("lesson4"),               │
│     ObjectId("lesson5")                │ ← All added!
│   ],                                   │
│   quizzes_completed: [],               │
│   assignments_completed: [],           │
│   completion_percentage: 100,          │ ← 100% (5/5 lessons)
│   time_spent_minutes: 150,             │ ← Updated
│   updated_at: 2024-01-15T11:30:00Z     │
│ }                                      │
└────────────────────────────────────────┘

✅ All Quizzes are now available
✅ Assignment is now available


STEP 4: Student Completes Quiz 1
════════════════════════════════

StudentProgress Collection:
┌────────────────────────────────────────┐
│ {                                      │
│   _id: ObjectId(...),                  │
│   student_id: ObjectId(...),           │
│   course_id: ObjectId(...),            │
│   lessons_completed: [                 │
│     ObjectId("lesson1"),               │
│     ObjectId("lesson2"),               │
│     ObjectId("lesson3"),               │
│     ObjectId("lesson4"),               │
│     ObjectId("lesson5")                │
│   ],                                   │
│   quizzes_completed: [                 │
│     {                                  │
│       quiz_id: "quiz1",                │ ← Added!
│       score: 85,                       │
│       passed: true,                    │
│       completed_at: "2024-01-15T..."   │
│     }                                  │
│   ],                                   │
│   assignments_completed: [],           │
│   completion_percentage: 100,          │
│   updated_at: 2024-01-15T11:45:00Z     │
│ }                                      │
└────────────────────────────────────────┘


STEP 5: Student Submits Assignment
════════════════════════��══════════

StudentProgress Collection:
┌────────────────────────────────────────┐
│ {                                      │
│   _id: ObjectId(...),                  │
│   student_id: ObjectId(...),           │
│   course_id: ObjectId(...),            │
│   lessons_completed: [5 items],        │
│   quizzes_completed: [1 item],         │
│   assignments_completed: [             │
│     {                                  │
│       assignment_id: "assignment1",    │ ← Added!
│       score: 92,                       │
│       passed: true,                    │
│       completed_at: "2024-01-15T..."   │
│     }                                  │
│   ],                                   │
│   completion_percentage: 100,          │
│   updated_at: 2024-01-15T12:00:00Z     │
│ }                                      │
└────────────────────────────────────────┘

Enrollment Collection:
┌──────────────��─────────────────────────┐
│ {                                      │
│   _id: ObjectId(...),                  │
│   student_id: ObjectId(...),           │
│   course_id: ObjectId(...),            │
│   enrolled_at: 2024-01-15T10:00:00Z,   │
│   progress: 100,                       │ ← Updated to 100%
│   completed: true,                     │ ← Marked complete!
│   completed_at: 2024-01-15T12:00:00Z   │ ← Added!
│ }                                      │
└────────────────────────────────────────┘
```

---

## 5. API Response Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│              API RESPONSE TIMELINE                               │
└─────────────────────────────────────────────────────────────────┘

Time    Event                           API Call                Response
────    ─────                           ─────���──                ────────

10:00   Student enrolls                 POST /enroll/           201 Created
        StudentProgress created (0%)

10:05   Student views course            GET /status/            200 OK
        Lessons: all incomplete         can_take_quiz: false
        Assignments: locked             can_take_assignment: false

10:10   Student completes lesson 1      POST /lesson/1/complete/ 200 OK
        StudentProgress updated (20%)

10:11   Student checks status           GET /status/            200 OK
        Lesson 1: completed             can_take_quiz: true ✅
        Assignments: still locked       can_take_assignment: false

10:15   Student takes quiz 1            GET /lesson/1/quiz/     200 OK
        Quiz data returned              Quiz questions shown

10:20   Student submits quiz 1          POST /quiz/1/submit/    201 Created
        Quiz attempt recorded

10:25   Student completes lesson 2      POST /lesson/2/complete/ 200 OK
        StudentProgress updated (40%)

...     (Student completes lessons 3-5)

11:30   Student completes lesson 5      POST /lesson/5/complete/ 200 OK
        StudentProgress updated (100%)

11:31   Student checks status           GET /status/            200 OK
        All lessons: completed          can_take_quiz: true ✅
        Assignments: unlocked!          can_take_assignment: true ✅

11:35   Student accesses assignment     GET /assignment/1/      200 OK
        Assignment data returned        Assignment shown

11:45   Student submits assignment      POST /assignment/1/submit/ 201 Created
        Assignment submission recorded

12:00   Instructor grades assignment    POST /submission/1/grade/ 200 OK
        Enrollment marked complete      progress: 100%
```

---

## 6. Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  ERROR HANDLING FLOW                             │
└─────────────────────────────────────────────────────────────────┘

SCENARIO: Student tries to access quiz before lesson completion

Student Request
        │
        ▼
GET /api/courses/lesson/{lessonId}/quiz/
Authorization: Bearer {token}
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Backend Processing                                           │
│ 1. Authenticate user ✅                                      │
│ 2. Get lesson ✅                                             │
│ 3. Get quiz ✅                                               │
│ 4. Check if instructor ✅ (No, is student)                   │
│ 5. Get StudentProgress ✅                                    │
│ 6. Check lesson in completed list ❌ NOT FOUND               │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────��─────────────────────────────────────────┐
│ Error Response                                               │
│ Status: 403 Forbidden                                        │
│ {                                                            │
│   "error": "You must complete this lesson before...",        │
│   "lesson_id": "...",                                        │
│   "available": false                                         │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Frontend Handling                                            │
│ - Check response status (403)                                │
│ - Parse error message                                        │
│ - Show user-friendly message:                                │
│   "Complete this lesson to unlock the quiz"                  │
│ - Disable quiz button                                        │
│ - Show progress indicator                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Summary

These diagrams show:
1. **Enrollment Flow** - How students enroll and get access
2. **Quiz Gating** - How quizzes are locked/unlocked based on lesson completion
3. **Assignment Gating** - How assignments are locked/unlocked based on course completion
4. **Database Changes** - How StudentProgress evolves as student progresses
5. **API Timeline** - Sequence of API calls and responses
6. **Error Handling** - How errors are handled and communicated

All flows are now working correctly with the fixes applied!
