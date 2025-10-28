"""
User app URL configuration
"""
from django.urls import path
from users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView
)
from users.views_2fa import (
    Setup2FAView,
    Verify2FASetupView,
    Verify2FALoginView,
    Disable2FAView,
    Check2FAStatusView
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    
    # Two-Factor Authentication (2FA)
    path('2fa/setup/', Setup2FAView.as_view(), name='setup-2fa'),
    path('2fa/verify-setup/', Verify2FASetupView.as_view(), name='verify-2fa-setup'),
    path('2fa/verify-login/', Verify2FALoginView.as_view(), name='verify-2fa-login'),
    path('2fa/disable/', Disable2FAView.as_view(), name='disable-2fa'),
    path('2fa/status/', Check2FAStatusView.as_view(), name='2fa-status'),
]
