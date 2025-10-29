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
    ModuleLessonsView
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
    
    # Course CRUD
    path('', CourseListView.as_view(), name='course-list'),
    path('featured/', FeaturedCoursesView.as_view(), name='featured-courses'),
    path('instructor/<str:instructor_id>/', InstructorCoursesView.as_view(), name='instructor-courses'),
    path('<str:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('<str:course_id>/modules/', CourseModulesView.as_view(), name='course-modules'),
    path('module/<str:module_id>/lessons/', ModuleLessonsView.as_view(), name='module-lessons'),
    
    # Enrollment
    path('<str:course_id>/enroll/', EnrollCourseView.as_view(), name='enroll-course'),
    path('my/enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),
    path('<str:course_id>/progress/', UpdateProgressView.as_view(), name='update-progress'),
    
    # Reviews
    path('<str:course_id>/reviews/', CourseReviewsView.as_view(), name='course-reviews'),
]
