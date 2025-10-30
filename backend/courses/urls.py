"""
Course app URL configuration
"""
from django.urls import path
from courses.views import (
    CourseListView,
    CourseDetailView,
    EnrollCourseView,
    MyEnrollmentsView,
    UpdateProgressView,
    CourseReviewsView,
    FeaturedCoursesView,
    InstructorCoursesView,
    CourseModulesView,
    ModuleLessonsView,
    LessonDetailView
)
from courses.views_instructor import (
    create_course,
    get_instructor_courses,
    manage_course,
    get_course_modules,
    create_module,
    manage_module,
    create_lesson,
    manage_lesson
)
from courses.views_quiz import (
    create_quiz,
    manage_quiz,
    get_lesson_quiz,
    check_lesson_quiz_availability,
    submit_quiz,
    get_quiz_attempts,
    get_my_quiz_attempts,
    get_course_quizzes
)
from courses.views_assignment import (
    create_assignment,
    manage_assignment,
    get_course_assignments,
    get_assignment_detail,
    submit_assignment,
    grade_assignment,
    get_assignment_submissions,
    get_my_assignment_submissions,
    get_submission_detail,
    validate_code_syntax
)
from courses.views_ai import (
    generate_quiz_ai,
    create_quiz_from_ai,
    generate_assignment_ai,
    create_assignment_from_ai
)
from courses.views_progress import (
    get_student_progress,
    get_all_student_progress,
    update_lesson_progress,
    get_course_status,
    submit_course_review,
    get_course_reviews,
    submit_instructor_review,
    get_instructor_reviews,
    submit_course_feedback,
    get_course_feedbacks
)

app_name = 'courses'

urlpatterns = [
    # Instructor Management URLs (MUST come before generic patterns)
    path('instructor/my-courses/', get_instructor_courses, name='get-instructor-courses'),
    path('instructor/create/', create_course, name='create-course'),
    path('instructor/course/<str:course_id>/modules/', get_course_modules, name='get-course-modules'),
    path('instructor/course/<str:course_id>/modules/create/', create_module, name='create-module'),
    path('instructor/course/<str:course_id>/', manage_course, name='manage-course'),
    path('instructor/module/<str:module_id>/lessons/', create_lesson, name='create-lesson'),
    path('instructor/module/<str:module_id>/', manage_module, name='manage-module'),
    path('instructor/lesson/<str:lesson_id>/', manage_lesson, name='manage-lesson'),
    
    # Quiz Management (Instructor)
    path('instructor/lesson/<str:lesson_id>/quiz/create/', create_quiz, name='create-quiz'),
    path('instructor/quiz/<str:quiz_id>/', manage_quiz, name='manage-quiz'),
    path('instructor/quiz/<str:quiz_id>/attempts/', get_quiz_attempts, name='get-quiz-attempts'),
    
    # Assignment Management (Instructor)
    path('instructor/course/<str:course_id>/assignment/create/', create_assignment, name='create-assignment'),
    path('instructor/assignment/<str:assignment_id>/', manage_assignment, name='manage-assignment'),
    path('instructor/assignment/<str:assignment_id>/submissions/', get_assignment_submissions, name='get-assignment-submissions'),
    path('instructor/submission/<str:submission_id>/grade/', grade_assignment, name='grade-assignment'),
    
    # AI Generation (Instructor)
    path('instructor/lesson/<str:lesson_id>/quiz/generate/', generate_quiz_ai, name='generate-quiz-ai'),
    path('instructor/lesson/<str:lesson_id>/quiz/create-from-ai/', create_quiz_from_ai, name='create-quiz-from-ai'),
    path('instructor/course/<str:course_id>/assignment/generate/', generate_assignment_ai, name='generate-assignment-ai'),
    path('instructor/course/<str:course_id>/assignment/create-from-ai/', create_assignment_from_ai, name='create-assignment-from-ai'),
    
    # Quiz (Student)
    path('lesson/<str:lesson_id>/quiz/', get_lesson_quiz, name='get-lesson-quiz'),
    path('lesson/<str:lesson_id>/quiz/check/', check_lesson_quiz_availability, name='check-lesson-quiz'),
    path('quiz/<str:quiz_id>/submit/', submit_quiz, name='submit-quiz'),
    path('quiz/<str:quiz_id>/my-attempts/', get_my_quiz_attempts, name='get-my-quiz-attempts'),
    path('course/<str:course_id>/quizzes/', get_course_quizzes, name='get-course-quizzes'),
    
    # Assignment (Student)
    path('course/<str:course_id>/assignments/', get_course_assignments, name='get-course-assignments'),
    path('assignment/<str:assignment_id>/', get_assignment_detail, name='get-assignment-detail'),
    path('assignment/<str:assignment_id>/submit/', submit_assignment, name='submit-assignment'),
    path('assignment/<str:assignment_id>/my-submissions/', get_my_assignment_submissions, name='get-my-assignment-submissions'),
    path('submission/<str:submission_id>/', get_submission_detail, name='get-submission-detail'),
    path('validate-code/', validate_code_syntax, name='validate-code-syntax'),
    
    # Course CRUD
    path('', CourseListView.as_view(), name='course-list'),
    path('featured/', FeaturedCoursesView.as_view(), name='featured-courses'),
    
    # Specific patterns MUST come before generic <str:course_id>
    path('my/enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),
    path('progress/my/', get_all_student_progress, name='my-progress'),
    path('module/<str:module_id>/lessons/', ModuleLessonsView.as_view(), name='module-lessons'),
    path('lesson/<str:lesson_id>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('lesson/<str:lesson_id>/complete/', update_lesson_progress, name='complete-lesson'),
    path('instructor/<str:instructor_id>/', InstructorCoursesView.as_view(), name='instructor-courses'),
    
    # Generic course patterns (MUST come after specific patterns)
    path('<str:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('<str:course_id>/modules/', CourseModulesView.as_view(), name='course-modules'),
    path('<str:course_id>/enroll/', EnrollCourseView.as_view(), name='enroll-course'),
    path('<str:course_id>/progress/', UpdateProgressView.as_view(), name='update-progress'),
    path('<str:course_id>/status/', get_course_status, name='course-status'),
    path('<str:course_id>/reviews/', CourseReviewsView.as_view(), name='course-reviews'),
    path('<str:course_id>/progress/details/', get_student_progress, name='course-progress'),
    
    # Course Reviews & Feedback
    path('<str:course_id>/review/submit/', submit_course_review, name='submit-course-review'),
    path('<str:course_id>/review/list/', get_course_reviews, name='get-course-reviews'),
    path('<str:course_id>/feedback/submit/', submit_course_feedback, name='submit-course-feedback'),
    path('<str:course_id>/feedbacks/', get_course_feedbacks, name='get-course-feedbacks'),
    
    # Instructor Reviews & Feedback
    path('instructor/<str:instructor_id>/course/<str:course_id>/review/', submit_instructor_review, name='submit-instructor-review'),
    path('instructor/<str:instructor_id>/reviews/', get_instructor_reviews, name='get-instructor-reviews'),
]
