# Quick Reference Guide - Quiz & Assignment System

## For Your Validation Meeting

### Key Files Created/Modified

1. **Models**: `backend/courses/extended_models.py`
   - Enhanced `Quiz` model (lines 187-283)
   - New `QuizAttempt` model (lines 773-861)
   - New `Assignment` model (lines 864-955)
   - New `AssignmentSubmission` model (lines 958-1061)

2. **Serializers**: `backend/courses/serializers.py`
   - Added Quiz, QuizAttempt, Assignment, AssignmentSubmission serializers

3. **Views**:
   - `backend/courses/views_quiz.py` - Quiz CRUD and student operations
   - `backend/courses/views_assignment.py` - Assignment CRUD and grading
   - `backend/courses/views_ai.py` - AI generation endpoints

4. **Helpers**: `backend/courses/ai_helpers.py` - AI generation functions

5. **URLs**: `backend/courses/urls.py` - All new endpoints registered

---

## Quick Explanation Points

### Quiz System

**What it does**: After completing a lesson, students can take an MCQ quiz to test their knowledge.

**How it works**:
1. Instructor creates quiz with multiple choice questions
2. Each question has 4 options and one correct answer (stored as index 0-3)
3. Student submits answers
4. System compares student's answers with correct answers
5. Calculates score and percentage
6. Shows instant results with ranking

**Key Function** (`views_quiz.py` line 120):
```python
# Loop through questions and check answers
for i, question in enumerate(quiz.questions):
    if student_answer['selected_answer'] == question['correct_answer']:
        score += points
```

### Assignment System

**What it does**: After completing all course lessons, students take a comprehensive assignment.

**Types**:
- **Coding**: Write code with time limit, no copy/paste
- **Written**: MCQ, true/false, short answer questions
- **Mixed**: Both coding and written

**Proctoring Features**:
- Tracks copy/paste attempts
- Tracks window switches
- 3 warnings = automatic fail (score 0)

**Key Function** (`views_assignment.py` line 140):
```python
# Check warnings
if warnings_count >= assignment.max_warnings:
    # Invalidate submission with score 0
    submission_data['status'] = 'invalidated'
```

### AI Generation

**What it does**: Helps instructors create quizzes and assignments automatically.

**How it works**:
1. Instructor clicks "Generate with AI"
2. System analyzes lesson/course content
3. Generates questions
4. Instructor reviews and edits
5. Creates quiz/assignment

**Current Status**: Placeholder implementation ready for OpenAI integration

**Key Function** (`ai_helpers.py` line 10):
```python
def generate_quiz_questions(lesson_content, num_questions, difficulty):
    # In production: Call OpenAI API
    # Currently: Returns sample questions
```

### Grading Assistance

**What it does**: Helps instructor grade assignments by analyzing student's quiz performance.

**How it works**:
1. When student submits assignment, system checks their quiz scores
2. Calculates average quiz performance
3. Provides note to instructor: "Student averaged 85% on quizzes - work likely authentic"
4. Instructor uses this context when grading

**Key Function** (`views_assignment.py` line 164):
```python
# Get student's quiz scores
for quiz in quizzes:
    attempts = QuizAttempt.find_by_student_quiz(student_id, quiz_id)
    quiz_attempts.append(best_attempt.percentage)

avg_quiz_score = sum(quiz_attempts) / len(quiz_attempts)
```

### Statistics Dashboard

**What instructors see**:
- Average score across all students
- Pass rate percentage
- Number of attempts per student
- Who validated (passed) and who didn't
- AI recommendations for improvement

**Example Response**:
```json
{
  "average_score": 78.5,
  "pass_rate": 80.0,
  "student_attempts": [...],
  "ai_recommendations": [
    "Assignment difficulty appears appropriate",
    "Review student feedback to identify common challenges"
  ]
}
```

---

## API Endpoints Summary

### Instructor Endpoints

**Quizzes**:
- `POST /instructor/lesson/{id}/quiz/create/` - Create quiz
- `GET/PUT/DELETE /instructor/quiz/{id}/` - Manage quiz
- `GET /instructor/quiz/{id}/attempts/` - View all attempts
- `POST /instructor/lesson/{id}/quiz/generate/` - Generate with AI

**Assignments**:
- `POST /instructor/course/{id}/assignment/create/` - Create assignment
- `GET/PUT/DELETE /instructor/assignment/{id}/` - Manage assignment
- `GET /instructor/assignment/{id}/submissions/` - View submissions
- `POST /instructor/submission/{id}/grade/` - Grade submission
- `POST /instructor/course/{id}/assignment/generate/` - Generate with AI

### Student Endpoints

**Quizzes**:
- `GET /lesson/{id}/quiz/` - Get quiz
- `POST /quiz/{id}/submit/` - Submit answers
- `GET /quiz/{id}/my-attempts/` - View my attempts

**Assignments**:
- `GET /course/{id}/assignments/` - Get assignments
- `GET /assignment/{id}/` - Get assignment details
- `POST /assignment/{id}/submit/` - Submit assignment
- `GET /assignment/{id}/my-submissions/` - View my submissions

---

## Database Collections

- `quizzes` - Quiz definitions
- `quiz_attempts` - Student quiz attempts
- `assignments` - Assignment definitions
- `assignment_submissions` - Student submissions

All use MongoDB, automatically created on first insert.

---

## Code Structure Explanation

### Why separate view files?

- `views_quiz.py` - All quiz-related logic
- `views_assignment.py` - All assignment-related logic
- `views_ai.py` - All AI generation logic
- Keeps code organized and easy to maintain

### Why use MongoDB models?

- Flexible schema for questions (different types)
- Easy to store arrays (questions, answers, warnings)
- Fast queries for statistics
- Matches existing project structure

### Why AI helpers in separate file?

- Easy to swap placeholder with real AI service
- Testable independently
- Reusable across different features

---

## Common Questions & Answers

**Q: How does ranking work?**
A: Get all attempts, sort by percentage descending, find position of current attempt.

**Q: How are warnings tracked?**
A: Frontend detects violations (copy/paste, window switch), sends count with submission. Backend checks if count >= max_warnings.

**Q: Can students retake quizzes?**
A: Yes, if max_attempts = 0 (unlimited) or they haven't reached the limit.

**Q: How is AI assistance calculated?**
A: System gets student's average quiz score in the course, provides context to instructor.

**Q: What happens if student gets 3 warnings?**
A: Submission automatically invalidated with score 0, marked as "invalidated" status.

**Q: Can instructor edit AI-generated content?**
A: Yes, AI generates suggestions, instructor reviews and edits before creating.

**Q: How does automatic grading work for assignments?**
A: Only quizzes are auto-graded (MCQ). Assignments require manual instructor grading.

**Q: What's the difference between Quiz and Assignment?**
A: 
- Quiz: After each lesson, auto-graded, instant results
- Assignment: After whole course, manually graded, more comprehensive

---

## Testing Commands

### Create Quiz:
```bash
curl -X POST http://localhost:8000/api/courses/instructor/lesson/LESSON_ID/quiz/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Quiz",
    "questions": [
      {
        "question_text": "What is 2+2?",
        "options": ["2", "3", "4", "5"],
        "correct_answer": 2,
        "points": 1
      }
    ],
    "passing_score": 70
  }'
```

### Submit Quiz:
```bash
curl -X POST http://localhost:8000/api/courses/quiz/QUIZ_ID/submit/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_id": "QUIZ_ID",
    "course_id": "COURSE_ID",
    "lesson_id": "LESSON_ID",
    "answers": [
      {"question_index": 0, "selected_answer": 2}
    ],
    "time_taken_minutes": 5
  }'
```

---

## Key Points to Remember

1. ✅ Code is clean and well-commented
2. ✅ Each function has a clear purpose
3. ✅ Follows existing project patterns
4. ✅ All features requested are implemented
5. ✅ Security checks (permissions, ownership)
6. ✅ Statistics and analytics included
7. ✅ AI generation ready (placeholder)
8. ✅ Proctoring features (warnings system)
9. ✅ Comprehensive documentation
10. ✅ Easy to explain and demonstrate

---

## If Supervisor Asks About...

**"How does the ranking algorithm work?"**
→ Show `views_quiz.py` line 195-200, explain sorting by percentage

**"How do you prevent cheating?"**
→ Show warning system in `views_assignment.py` line 140-155

**"How does AI generation work?"**
→ Show `ai_helpers.py`, explain placeholder ready for OpenAI integration

**"How do you calculate statistics?"**
→ Show `views_assignment.py` line 280-295, explain aggregation logic

**"Why MongoDB instead of PostgreSQL?"**
→ Flexible schema for questions, matches existing project, easy array storage

**"Can you explain the data flow?"**
→ Student submits → Validation → Scoring → Storage → Statistics calculation

---

## Final Checklist

- ✅ Models created with all required fields
- ✅ Serializers for validation
- ✅ Views for all CRUD operations
- ✅ Permission checks on all endpoints
- ✅ Quiz auto-grading implemented
- ✅ Assignment manual grading with AI assistance
- ✅ Ranking system for quizzes
- ✅ Warning system for assignments
- ✅ Statistics dashboard
- ✅ AI generation endpoints
- ✅ URL patterns registered
- ✅ Documentation complete

**You're ready for validation! Good luck! 🚀**
