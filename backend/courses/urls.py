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
    InstructorCoursesView
)

app_name = 'courses'

urlpatterns = [
    # Course CRUD
    path('', CourseListView.as_view(), name='course-list'),
    path('featured/', FeaturedCoursesView.as_view(), name='featured-courses'),
    path('<str:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('instructor/<str:instructor_id>/', InstructorCoursesView.as_view(), name='instructor-courses'),
    
    # Enrollment
    path('<str:course_id>/enroll/', EnrollCourseView.as_view(), name='enroll-course'),
    path('my/enrollments/', MyEnrollmentsView.as_view(), name='my-enrollments'),
    path('<str:course_id>/progress/', UpdateProgressView.as_view(), name='update-progress'),
    
    # Reviews
    path('<str:course_id>/reviews/', CourseReviewsView.as_view(), name='course-reviews'),
]
