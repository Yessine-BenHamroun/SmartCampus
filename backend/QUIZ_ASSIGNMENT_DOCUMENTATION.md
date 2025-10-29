# Quiz and Assignment System Documentation

## Overview

This document explains the Quiz and Assignment system implementation for SmartCampus. The system allows instructors to create assessments and assignments, with support for AI-generated content, automatic grading, and comprehensive analytics.

## Table of Contents

1. [Models](#models)
2. [API Endpoints](#api-endpoints)
3. [Features](#features)
4. [Workflows](#workflows)
5. [Code Explanation](#code-explanation)

---

## Models

### 1. Quiz Model

**Purpose**: Stores quiz information for lessons

**Location**: `courses/extended_models.py`

**Fields**:
- `lesson_id`: Reference to the lesson this quiz belongs to
- `course_id`: Reference to the course
- `instructor_id`: Reference to the instructor who created it
- `title`: Quiz title
- `description`: Quiz description
- `questions`: List of MCQ questions with options and correct answers
- `passing_score`: Minimum percentage to pass (default: 70%)
- `time_limit_minutes`: Time limit (0 = no limit)
- `max_attempts`: Maximum attempts allowed (0 = unlimited)
- `shuffle_questions`: Whether to randomize question order
- `show_correct_answers`: Show correct answers after submission
- `is_published`: Whether quiz is available to students
- `is_ai_generated`: Flag indicating AI-generated content

**Key Methods**:
- `create()`: Creates a new quiz
- `find_by_id()`: Finds quiz by ID
- `find_by_lesson()`: Gets quiz for a specific lesson
- `find_by_course()`: Gets all quizzes in a course
- `update()`: Updates quiz fields
- `delete()`: Removes quiz

### 2. QuizAttempt Model

**Purpose**: Tracks student attempts at quizzes

**Location**: `courses/extended_models.py`

**Fields**:
- `quiz_id`: Reference to the quiz
- `student_id`: Reference to the student
- `course_id`: Reference to the course
- `lesson_id`: Reference to the lesson
- `answers`: List of student's answers
- `score`: Points earned
- `max_score`: Total possible points
- `percentage`: Score as percentage
- `passed`: Whether student passed
- `time_taken_minutes`: Time spent on quiz
- `started_at`: When attempt started
- `completed_at`: When attempt was submitted

**Key Methods**:
- `create()`: Creates a new attempt
- `find_by_student_quiz()`: Gets all attempts by a student for a quiz
- `find_by_quiz()`: Gets all attempts for a quiz
- `update()`: Updates attempt data

### 3. Assignment Model

**Purpose**: Stores assignment information for courses

**Location**: `courses/extended_models.py`

**Fields**:
- `course_id`: Reference to the course
- `instructor_id`: Reference to the instructor
- `title`: Assignment title
- `description`: Assignment description
- `assignment_type`: Type (coding, written, mixed)
- `questions`: List of questions for written assignments
- `coding_problem`: Coding challenge details
- `time_limit_minutes`: Time limit
- `max_attempts`: Maximum attempts allowed
- `passing_score`: Minimum score to pass
- `allow_copy_paste`: Whether copy/paste is allowed
- `allow_window_switch`: Whether switching windows is allowed
- `max_warnings`: Maximum warnings before invalidation
- `is_published`: Whether assignment is available

**Key Methods**:
- `create()`: Creates a new assignment
- `find_by_id()`: Finds assignment by ID
- `find_by_course()`: Gets all assignments for a course
- `update()`: Updates assignment
- `delete()`: Removes assignment

### 4. AssignmentSubmission Model

**Purpose**: Tracks student assignment submissions

**Location**: `courses/extended_models.py`

**Fields**:
- `assignment_id`: Reference to the assignment
- `student_id`: Reference to the student
- `course_id`: Reference to the course
- `answers`: Student's answers
- `code_solution`: Code for coding assignments
- `warnings_count`: Number of warnings received
- `warning_details`: Details of each warning
- `time_taken_minutes`: Time spent
- `status`: Status (submitted, graded, invalidated)
- `score`: Points earned
- `max_score`: Total possible points
- `percentage`: Score as percentage
- `passed`: Whether student passed
- `feedback`: Instructor feedback
- `graded_by`: Instructor who graded it
- `ai_assistance_note`: AI recommendation for grading
- `started_at`: When submission started
- `submitted_at`: When submitted
- `graded_at`: When graded

**Key Methods**:
- `create()`: Creates a new submission
- `find_by_student_assignment()`: Gets student's submissions for an assignment
- `find_by_assignment()`: Gets all submissions for an assignment
- `update()`: Updates submission data

---

## API Endpoints

### Quiz Endpoints (Instructor)

#### 1. Create Quiz
```
POST /api/courses/instructor/lesson/{lesson_id}/quiz/create/
```
**Purpose**: Create a new quiz for a lesson

**Request Body**:
```json
{
  "title": "Lesson 1 Quiz",
  "description": "Test your knowledge",
  "questions": [
    {
      "question_text": "What is 2+2?",
      "options": ["3", "4", "5", "6"],
      "correct_answer": 1,
      "points": 1
    }
  ],
  "passing_score": 70,
  "time_limit_minutes": 30,
  "is_published": true
}
```

#### 2. Manage Quiz
```
GET/PUT/DELETE /api/courses/instructor/quiz/{quiz_id}/
```
**Purpose**: View, update, or delete a quiz

#### 3. Get Quiz Attempts
```
GET /api/courses/instructor/quiz/{quiz_id}/attempts/
```
**Purpose**: View all student attempts with statistics

**Response**:
```json
{
  "quiz_id": "...",
  "total_attempts": 25,
  "unique_students": 15,
  "average_score": 78.5,
  "pass_rate": 80.0,
  "student_attempts": [...]
}
```

#### 4. Generate Quiz with AI
```
POST /api/courses/instructor/lesson/{lesson_id}/quiz/generate/
```
**Purpose**: Generate quiz questions using AI

**Request Body**:
```json
{
  "num_questions": 5,
  "difficulty": "medium"
}
```

#### 5. Create Quiz from AI
```
POST /api/courses/instructor/lesson/{lesson_id}/quiz/create-from-ai/
```
**Purpose**: Create quiz from AI-generated questions

### Quiz Endpoints (Student)

#### 1. Get Lesson Quiz
```
GET /api/courses/lesson/{lesson_id}/quiz/
```
**Purpose**: Get quiz for a lesson (without correct answers)

#### 2. Submit Quiz
```
POST /api/courses/quiz/{quiz_id}/submit/
```
**Purpose**: Submit quiz answers

**Request Body**:
```json
{
  "quiz_id": "...",
  "course_id": "...",
  "lesson_id": "...",
  "answers": [
    {"question_index": 0, "selected_answer": 1},
    {"question_index": 1, "selected_answer": 2}
  ],
  "time_taken_minutes": 15
}
```

**Response**:
```json
{
  "id": "...",
  "score": 8,
  "max_score": 10,
  "percentage": 80.0,
  "passed": true,
  "rank": 3,
  "total_attempts": 20,
  "correct_answers": [...]
}
```

#### 3. Get My Quiz Attempts
```
GET /api/courses/quiz/{quiz_id}/my-attempts/
```
**Purpose**: View your own attempts for a quiz

#### 4. Get Course Quizzes
```
GET /api/courses/course/{course_id}/quizzes/
```
**Purpose**: Get all quizzes in a course

### Assignment Endpoints (Instructor)

#### 1. Create Assignment
```
POST /api/courses/instructor/course/{course_id}/assignment/create/
```
**Purpose**: Create a new assignment

**Request Body** (Written):
```json
{
  "title": "Course Final Assignment",
  "description": "Complete all questions",
  "assignment_type": "written",
  "questions": [
    {
      "question_text": "Explain the concept",
      "question_type": "short_answer",
      "points": 10
    }
  ],
  "time_limit_minutes": 60,
  "passing_score": 50,
  "allow_copy_paste": false,
  "allow_window_switch": false,
  "max_warnings": 3
}
```

**Request Body** (Coding):
```json
{
  "title": "Coding Challenge",
  "assignment_type": "coding",
  "coding_problem": {
    "description": "Write a function...",
    "starter_code": "def solve():\n    pass",
    "test_cases": [...]
  },
  "time_limit_minutes": 90
}
```

#### 2. Manage Assignment
```
GET/PUT/DELETE /api/courses/instructor/assignment/{assignment_id}/
```
**Purpose**: View, update, or delete an assignment

#### 3. Get Assignment Submissions
```
GET /api/courses/instructor/assignment/{assignment_id}/submissions/
```
**Purpose**: View all submissions with statistics and AI recommendations

**Response**:
```json
{
  "assignment_id": "...",
  "total_submissions": 30,
  "unique_students": 25,
  "graded_count": 20,
  "pending_count": 10,
  "average_score": 72.5,
  "pass_rate": 75.0,
  "student_submissions": [...],
  "ai_recommendations": [
    "Assignment difficulty appears appropriate",
    "Review student feedback to identify common challenges"
  ]
}
```

#### 4. Grade Assignment
```
POST /api/courses/instructor/submission/{submission_id}/grade/
```
**Purpose**: Grade a student's submission

**Request Body**:
```json
{
  "score": 85,
  "feedback": "Good work! Consider improving..."
}
```

#### 5. Generate Assignment with AI
```
POST /api/courses/instructor/course/{course_id}/assignment/generate/
```
**Purpose**: Generate assignment questions using AI

#### 6. Create Assignment from AI
```
POST /api/courses/instructor/course/{course_id}/assignment/create-from-ai/
```
**Purpose**: Create assignment from AI-generated content

### Assignment Endpoints (Student)

#### 1. Get Course Assignments
```
GET /api/courses/course/{course_id}/assignments/
```
**Purpose**: Get all published assignments for a course

#### 2. Get Assignment Detail
```
GET /api/courses/assignment/{assignment_id}/
```
**Purpose**: Get assignment details and check if you can attempt it

**Response**:
```json
{
  "id": "...",
  "title": "...",
  "description": "...",
  "time_limit_minutes": 60,
  "attempts_count": 1,
  "can_attempt": true,
  ...
}
```

#### 3. Submit Assignment
```
POST /api/courses/assignment/{assignment_id}/submit/
```
**Purpose**: Submit assignment answers

**Request Body**:
```json
{
  "assignment_id": "...",
  "course_id": "...",
  "answers": [...],
  "code_solution": "...",
  "warnings_count": 0,
  "warning_details": [],
  "time_taken_minutes": 45
}
```

**Note**: If `warnings_count >= max_warnings`, submission is invalidated with score 0

#### 4. Get My Submissions
```
GET /api/courses/assignment/{assignment_id}/my-submissions/
```
**Purpose**: View your submissions for an assignment

#### 5. Get Submission Detail
```
GET /api/courses/submission/{submission_id}/
```
**Purpose**: View details of a specific submission

---

## Features

### Quiz Features

1. **MCQ-Style Questions**: Multiple choice questions with single correct answer
2. **Automatic Grading**: Instant results after submission
3. **Ranking System**: Students ranked by performance
4. **Attempt Tracking**: Track number of attempts and best score
5. **Time Limits**: Optional time limits for quizzes
6. **Question Shuffling**: Randomize question order
7. **Show/Hide Answers**: Control whether correct answers are shown
8. **AI Generation**: Generate quiz questions from lesson content

### Assignment Features

1. **Multiple Types**: 
   - **Coding**: Programming challenges with test cases
   - **Written**: MCQ, true/false, short answer questions
   - **Mixed**: Combination of both

2. **Proctoring Features**:
   - Copy/paste detection
   - Window switch detection
   - Warning system (3 warnings = invalidation)
   - Time tracking

3. **Manual Grading**: Instructor grades submissions
4. **AI Assistance**: 
   - Suggests grading based on quiz performance
   - Provides recommendations for assignment improvement
   - Analyzes student consistency

5. **Statistics Dashboard**:
   - Average scores
   - Pass rates
   - Submission status tracking
   - Student performance comparison

---

## Workflows

### Quiz Workflow

#### Instructor Side:
1. Create lesson
2. Create quiz (manually or with AI)
   - If using AI: Generate → Review → Create
3. Publish quiz
4. Monitor attempts and statistics
5. View student rankings and performance

#### Student Side:
1. Complete lesson
2. "Test Your Knowledge" button becomes clickable
3. Take quiz
4. Receive instant results with ranking
5. View correct answers (if enabled)
6. See ranking among other students

### Assignment Workflow

#### Instructor Side:
1. Complete course creation
2. Create assignment (manually or with AI)
   - Choose type (coding/written/mixed)
   - Set time limits and rules
   - Configure proctoring settings
3. Publish assignment
4. Monitor submissions
5. Grade submissions with AI assistance
6. View statistics and AI recommendations

#### Student Side:
1. Complete all lessons in course
2. Assignment becomes available
3. Start assignment (timer begins)
4. Complete within time limit
5. System monitors for violations:
   - Copy/paste attempts
   - Window switches
   - 3 warnings = automatic fail
6. Submit assignment
7. Wait for instructor grading
8. View grade and feedback

---

## Code Explanation

### How Quiz Grading Works

**File**: `views_quiz.py` → `submit_quiz()`

```python
# 1. Get student's answers
answers = serializer.validated_data['answers']

# 2. Initialize scoring
score = 0
max_score = 0

# 3. Loop through each question
for i, question in enumerate(quiz.questions):
    points = question.get('points', 1)
    max_score += points
    
    # 4. Find student's answer for this question
    student_answer = next((a for a in answers if a['question_index'] == i), None)
    
    # 5. Check if answer is correct
    if student_answer:
        if student_answer['selected_answer'] == question['correct_answer']:
            score += points

# 6. Calculate percentage
percentage = (score / max_score * 100) if max_score > 0 else 0

# 7. Determine if passed
passed = percentage >= quiz.passing_score
```

**Explanation**:
- Each question has a `correct_answer` field (index of correct option)
- Student submits their `selected_answer` (index they chose)
- If indices match, student gets the points
- Percentage calculated from total points
- Pass/fail based on `passing_score` threshold

### How Ranking Works

**File**: `views_quiz.py` → `submit_quiz()`

```python
# 1. Get all attempts for this quiz
all_attempts = QuizAttempt.find_by_quiz(quiz_id)

# 2. Filter only completed attempts
completed_attempts = [a for a in all_attempts if a.completed_at]

# 3. Sort by percentage (highest first)
sorted_attempts = sorted(completed_attempts, key=lambda x: x.percentage, reverse=True)

# 4. Find current attempt's position
rank = next((i + 1 for i, a in enumerate(sorted_attempts) if str(a.id) == str(attempt.id)), None)
```

**Explanation**:
- Gets all completed attempts
- Sorts by percentage descending
- Finds position of current attempt in sorted list
- Position + 1 = rank (1st place, 2nd place, etc.)

### How Assignment Warnings Work

**File**: `views_assignment.py` → `submit_assignment()`

```python
# 1. Get warnings from submission
warnings_count = serializer.validated_data.get('warnings_count', 0)

# 2. Check against max warnings
if warnings_count >= assignment.max_warnings:
    # 3. Create invalidated submission
    submission_data = {
        'status': 'invalidated',
        'score': 0,
        'percentage': 0,
        'passed': False,
        'warnings_count': warnings_count,
        'warning_details': [...]
    }
    # 4. Return error response
    return Response({...}, status=400)
```

**Explanation**:
- Frontend tracks copy/paste and window switches
- Each violation increments `warnings_count`
- If count reaches `max_warnings` (default 3), submission is invalidated
- Student receives 0 score automatically
- Warning details stored for instructor review

### How AI Grading Assistance Works

**File**: `views_assignment.py` → `submit_assignment()`

```python
# 1. Get all quizzes in the course
quizzes = Quiz.find_by_course(assignment.course_id)

# 2. Get student's quiz attempts
quiz_attempts = []
for quiz in quizzes:
    attempts = QuizAttempt.find_by_student_quiz(request.user_id, str(quiz.id))
    if attempts:
        best_attempt = max(attempts, key=lambda x: x.percentage)
        quiz_attempts.append(best_attempt.percentage)

# 3. Calculate average quiz performance
if quiz_attempts:
    avg_quiz_score = sum(quiz_attempts) / len(quiz_attempts)
    
    # 4. Generate AI note
    submission_data['ai_assistance_note'] = (
        f"Student's average quiz score: {avg_quiz_score:.1f}%. "
        f"Completed {len(quiz_attempts)} quizzes. "
        f"{'Strong performance' if avg_quiz_score >= 80 else 'Needs improvement'}"
    )
```

**Explanation**:
- Analyzes student's quiz performance in the course
- Calculates average score across all quizzes
- Provides context to instructor for grading
- Helps detect if assignment work matches quiz performance
- Suggests if work is likely authentic

### How AI Question Generation Works

**File**: `ai_helpers.py` → `generate_quiz_questions()`

```python
def generate_quiz_questions(lesson_content, num_questions=5, difficulty='medium'):
    # 1. In production, this would call OpenAI API
    # 2. Pass lesson content to AI
    # 3. AI generates questions based on content
    # 4. Return formatted questions
    
    # Current implementation is placeholder
    # Returns sample questions for demonstration
    return sample_questions
```

**Explanation**:
- Currently uses placeholder implementation
- In production, would integrate with OpenAI or similar AI service
- AI would analyze lesson content and generate relevant questions
- Instructor can review and edit before creating quiz

---

## Database Collections

The system uses MongoDB with the following collections:

1. **quizzes**: Stores quiz definitions
2. **quiz_attempts**: Stores student quiz attempts
3. **assignments**: Stores assignment definitions
4. **assignment_submissions**: Stores student submissions

All collections are automatically created when first document is inserted.

---

## Security Considerations

1. **Permission Checks**: All endpoints verify user role (instructor/student)
2. **Ownership Verification**: Instructors can only manage their own content
3. **Published Status**: Students only see published content
4. **Attempt Limits**: Enforced at API level
5. **Warning System**: Prevents cheating on assignments
6. **Correct Answers**: Hidden from students until after submission

---

## Future Enhancements

1. **Real AI Integration**: Connect to OpenAI API for actual AI generation
2. **Code Execution**: Run and test coding assignment submissions
3. **Plagiarism Detection**: Compare submissions for similarity
4. **Advanced Analytics**: More detailed performance insights
5. **Peer Review**: Allow students to review each other's work
6. **Question Bank**: Reusable question library
7. **Adaptive Difficulty**: Adjust based on student performance

---

## Testing the System

### Test Quiz Creation:
```bash
curl -X POST http://localhost:8000/api/courses/instructor/lesson/{lesson_id}/quiz/create/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Test Quiz Submission:
```bash
curl -X POST http://localhost:8000/api/courses/quiz/{quiz_id}/submit/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Test Assignment Creation:
```bash
curl -X POST http://localhost:8000/api/courses/instructor/course/{course_id}/assignment/create/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Summary

This implementation provides a complete quiz and assignment system with:
- ✅ Quiz creation and management
- ✅ Automatic quiz grading
- ✅ Student ranking system
- ✅ Assignment creation (coding/written/mixed)
- ✅ Proctoring features (warnings for violations)
- ✅ Manual grading with AI assistance
- ✅ Comprehensive statistics and analytics
- ✅ AI generation support (placeholder ready for integration)
- ✅ Clean, maintainable code structure
- ✅ Proper permission handling
- ✅ MongoDB integration

The code is designed to be easy to understand and explain during validation, with clear function names, comments, and logical structure.
