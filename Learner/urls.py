from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('courses/<str:course_id>/', views.course_detail, name='course_detail'),
    path('course-details/', views.course_details, name='course_details'),
    path('instructors/', views.instructors, name='instructors'),
    path('instructor-profile/', views.instructor_profile, name='instructor_profile'),
    path('blog/', views.blog, name='blog'),
    path('blog-details/', views.blog_details, name='blog_details'),
    path('contact/', views.contact, name='contact'),
    path('events/', views.events, name='events'),
    path('enroll/', views.enroll, name='enroll'),
    path('pricing/', views.pricing, name='pricing'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('starter-page/', views.starter_page, name='starter_page'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Password Reset URLs
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    
    # Two-Factor Authentication URLs
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('verify-2fa-setup/', views.verify_2fa_setup, name='verify_2fa_setup'),
    path('verify-2fa-login/', views.verify_2fa_login, name='verify_2fa_login'),
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
    
    # Student Learning URLs
    path('my-learning/', views.my_learning_view, name='my_learning'),
    path('my-progress/', views.my_progress_view, name='my_progress'),
    path('my-submissions/', views.my_submissions_view, name='my_submissions'),
    path('discussions/', views.discussions_view, name='discussions'),
    
    # Instructor URLs
    path('instructor/dashboard/', views.instructor_dashboard_view, name='instructor_dashboard'),
    path('instructor/courses/', views.instructor_courses_view, name='instructor_courses'),
    path('instructor/courses/create/', views.create_course_view, name='create_course'),
    path('instructor/courses/<str:course_id>/edit/', views.edit_course_view, name='edit_course'),
    path('instructor/submissions/', views.instructor_submissions_view, name='instructor_submissions'),
    path('instructor/analytics/', views.course_analytics_view, name='course_analytics'),
    
    # Quiz URLs
    path('instructor/lesson/<str:lesson_id>/quiz/create/', views.create_quiz_view, name='create_quiz'),
    path('quiz/<str:quiz_id>/take/', views.take_quiz_view, name='take_quiz'),
    
    # Assignment URLs
    path('instructor/course/<str:course_id>/assignment/create/', views.create_assignment_view, name='create_assignment'),
    path('assignment/<str:assignment_id>/take/', views.take_assignment_view, name='take_assignment'),
    
    # Management URLs
    path('instructor/manage-quizzes/', views.manage_quizzes_view, name='manage_quizzes'),
    path('instructor/manage-assignments/', views.manage_assignments_view, name='manage_assignments'),
    path('instructor/submission/<str:submission_id>/grade/', views.grade_submission_view, name='grade_submission'),
    
    # Certification URLs
    path('instructor/course/<str:course_id>/certifications/create/', views.create_certification_view, name='create_certification'),
    path('instructor/certification/<str:certification_id>/steps/', views.manage_certification_steps_view, name='manage_certification_steps'),
    path('instructor/certification/<str:certification_id>/steps/add/', views.add_certification_step_view, name='add_certification_step'),
    path('instructor/certification/step/<str:step_id>/delete/', views.delete_certification_step_view, name='delete_certification_step'),
    path('my-badges/', views.my_badges_view, name='my_badges'),
]
