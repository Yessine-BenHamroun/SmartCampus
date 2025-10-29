# Frontend Implementation - Quiz & Assignment System

## ✅ What Was Added

### Templates Created

1. **`Learner/templates/learner/create_quiz.html`**
   - Instructor interface to create quizzes for lessons
   - Features:
     - Add multiple MCQ questions with 4 options each
     - Mark correct answers
     - Set passing score, time limit, max attempts
     - Shuffle questions option
     - AI generation button (calls backend API)
     - Save as draft or publish
   - Dynamic question adding/removing with JavaScript

2. **`Learner/templates/learner/create_assignment.html`**
   - Instructor interface to create assignments for courses
   - Features:
     - Choose assignment type (Written/Coding/Mixed)
     - Add written questions (MCQ, True/False, Short Answer)
     - Add coding problems with test cases
     - Proctoring settings (copy/paste, window switching, warnings)
     - Time limits and passing scores
     - AI generation button
     - Save as draft or publish
   - Dynamic forms based on assignment type

3. **`Learner/templates/learner/take_quiz.html`**
   - Student interface to take quizzes
   - Features:
     - Display all questions
     - Radio button selection for answers
     - Timer (if time limit set)
     - Submit to backend API
     - Redirect to results page

4. **`Learner/templates/learner/take_assignment.html`**
   - Student interface to take assignments
   - Features:
     - Display questions or coding problem
     - Form submission
     - Proctoring tracking (frontend monitors violations)
     - Submit to backend API

### Views Added (Learner/views.py)

1. **`create_quiz_view(request, lesson_id)`**
   - URL: `/instructor/lesson/<lesson_id>/quiz/create/`
   - Fetches lesson details from backend API
   - Renders quiz creation form
   - Instructor only

2. **`take_quiz_view(request, quiz_id)`**
   - URL: `/quiz/<quiz_id>/take/`
   - Fetches quiz from backend API
   - Renders quiz taking interface
   - Student only

3. **`create_assignment_view(request, course_id)`**
   - URL: `/instructor/course/<course_id>/assignment/create/`
   - Fetches course details from backend API
   - Renders assignment creation form
   - Instructor only

4. **`take_assignment_view(request, assignment_id)`**
   - URL: `/assignment/<assignment_id>/take/`
   - Fetches assignment from backend API
   - Renders assignment taking interface
   - Student only

### URL Patterns Added (Learner/urls.py)

```python
# Quiz URLs
path('instructor/lesson/<str:lesson_id>/quiz/create/', views.create_quiz_view, name='create_quiz'),
path('quiz/<str:quiz_id>/take/', views.take_quiz_view, name='take_quiz'),

# Assignment URLs
path('instructor/course/<str:course_id>/assignment/create/', views.create_assignment_view, name='create_assignment'),
path('assignment/<str:assignment_id>/take/', views.take_assignment_view, name='take_assignment'),
```

---

## 🔗 How It Connects to Backend

### Flow Diagram

```
Frontend (Django Templates) → Backend API (DRF)
         ↓                           ↓
    User Actions              MongoDB Database
```

### Example: Creating a Quiz

1. **Instructor clicks "Create Quiz" button** (you need to add this button)
2. **Navigates to** `/instructor/lesson/{lesson_id}/quiz/create/`
3. **Django view** fetches lesson details from backend API
4. **Template renders** form with JavaScript
5. **Instructor fills form** and clicks "Create & Publish"
6. **JavaScript collects data** and sends POST to `/api/courses/instructor/lesson/{lesson_id}/quiz/create/`
7. **Backend API** validates and saves to MongoDB
8. **Success response** redirects to instructor courses page

### Example: Taking a Quiz

1. **Student clicks "Take Quiz" button** (you need to add this button)
2. **Navigates to** `/quiz/{quiz_id}/take/`
3. **Django view** fetches quiz from backend API
4. **Template renders** questions
5. **Student answers** and clicks "Submit"
6. **JavaScript collects answers** and sends POST to `/api/courses/quiz/{quiz_id}/submit/`
7. **Backend API** grades quiz automatically
8. **Success response** shows results with score and ranking

---

## 📝 What You Need to Add

### 1. Add Buttons in Instructor Course Management

In `instructor_courses.html` or `edit_course.html`, add buttons to create quizzes and assignments:

```html
<!-- After creating a lesson -->
<a href="{% url 'create_quiz' lesson_id=lesson.id %}" class="btn btn-primary btn-sm">
  <i class="bi bi-plus-circle"></i> Create Quiz
</a>

<!-- In course view -->
<a href="{% url 'create_assignment' course_id=course.id %}" class="btn btn-success btn-sm">
  <i class="bi bi-file-earmark-text"></i> Create Assignment
</a>
```

### 2. Add Buttons in Student Course View

In `course_detail.html` or lesson view, add buttons for students:

```html
<!-- If lesson has a quiz -->
{% if lesson.has_quiz %}
<a href="{% url 'take_quiz' quiz_id=lesson.quiz_id %}" class="btn btn-primary">
  <i class="bi bi-pencil-square"></i> Take Quiz
</a>
{% endif %}

<!-- If course has assignments -->
{% for assignment in course.assignments %}
<a href="{% url 'take_assignment' assignment_id=assignment.id %}" class="btn btn-success">
  <i class="bi bi-file-earmark-code"></i> Take Assignment
</a>
{% endfor %}
```

### 3. Update Instructor Dashboard

Show quiz and assignment statistics:

```html
<div class="stats-card">
  <h4>Quizzes Created</h4>
  <p class="stat-number">{{ total_quizzes }}</p>
</div>

<div class="stats-card">
  <h4>Assignments Created</h4>
  <p class="stat-number">{{ total_assignments }}</p>
</div>
```

### 4. Update Student Dashboard

Show quiz results and assignment submissions:

```html
<div class="quiz-results">
  <h4>Recent Quiz Results</h4>
  {% for attempt in recent_quiz_attempts %}
  <div class="result-item">
    <span>{{ attempt.quiz_title }}</span>
    <span class="badge bg-{{ attempt.passed|yesno:'success,danger' }}">
      {{ attempt.percentage }}%
    </span>
  </div>
  {% endfor %}
</div>
```

---

## 🎨 Styling Notes

The templates use:
- **Bootstrap 5** classes (already in your project)
- **Bootstrap Icons** (bi-*)
- Custom CSS classes that match your existing design:
  - `.course-form-card`
  - `.form-section`
  - `.question-card`
  - `.form-actions`

All styling is consistent with your existing `create_course.html` template.

---

## 🔧 JavaScript Functionality

### Quiz Creation (`create_quiz.html`)
- **Dynamic question adding**: Click "Add Question" to add more questions
- **Question removal**: Click trash icon to remove questions
- **AI Generation**: Calls `/api/courses/instructor/lesson/{id}/quiz/generate/`
- **Form submission**: Collects all data and POSTs to backend API

### Assignment Creation (`create_assignment.html`)
- **Type switching**: Shows/hides sections based on assignment type
- **Dynamic test cases**: Add/remove test cases for coding problems
- **AI Generation**: Calls `/api/courses/instructor/course/{id}/assignment/generate/`
- **Form submission**: Handles different assignment types

### Quiz Taking (`take_quiz.html`)
- **Timer**: Countdown timer if time limit is set
- **Auto-submit**: Automatically submits when time runs out
- **Answer validation**: Ensures all questions are answered
- **API submission**: POSTs answers to backend for grading

### Assignment Taking (`take_assignment.html`)
- **Proctoring**: Monitors copy/paste and window switching
- **Warning tracking**: Counts violations
- **Timer**: Countdown for time limit
- **API submission**: POSTs submission to backend

---

## 🚀 Testing the Frontend

### Test Quiz Creation:
1. Login as instructor
2. Go to your courses
3. Edit a course, view modules/lessons
4. Click "Create Quiz" button (you need to add this)
5. Or manually navigate to: `/instructor/lesson/{lesson_id}/quiz/create/`
6. Fill the form and submit

### Test Quiz Taking:
1. Login as student
2. Enroll in a course
3. Navigate to lesson with quiz
4. Click "Take Quiz" button (you need to add this)
5. Or manually navigate to: `/quiz/{quiz_id}/take/`
6. Answer questions and submit

### Test Assignment Creation:
1. Login as instructor
2. Go to your courses
3. Click "Create Assignment" button (you need to add this)
4. Or manually navigate to: `/instructor/course/{course_id}/assignment/create/`
5. Fill the form and submit

### Test Assignment Taking:
1. Login as student
2. Enroll in a course
3. Navigate to assignments section
4. Click "Take Assignment" button (you need to add this)
5. Or manually navigate to: `/assignment/{assignment_id}/take/`
6. Complete and submit

---

## ✅ Summary

**What's Complete:**
- ✅ 4 new HTML templates with full functionality
- ✅ 4 new Django views to render templates
- ✅ 4 new URL patterns
- ✅ JavaScript for dynamic forms and API calls
- ✅ Consistent styling with existing project
- ✅ Full integration with backend APIs

**What You Need to Do:**
1. Add "Create Quiz" and "Create Assignment" buttons in instructor interface
2. Add "Take Quiz" and "Take Assignment" buttons in student interface
3. Update dashboards to show quiz/assignment statistics
4. Test all flows end-to-end

**The frontend is ready to use! Just add the navigation buttons and you're good to go!** 🎉
