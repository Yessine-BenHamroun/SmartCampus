from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
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
]
