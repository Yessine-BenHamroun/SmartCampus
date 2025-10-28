"""
Views using Backend API for authentication (MongoDB)
This replaces the old SQLite-based authentication
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .api_auth import (
    APIAuthBackend,
    save_user_session,
    clear_user_session,
    get_current_user,
    is_authenticated as api_is_authenticated,
    get_access_token,
    api_login_required
)
from .forms import RegisterForm, LoginForm
import time


# Page Views (no auth required)

def index(request):
    """Home page view"""
    return render(request, 'learner/index.html')

def about(request):
    """About page view"""
    return render(request, 'learner/about.html')

def courses(request):
    """Courses listing page view"""
    return render(request, 'learner/courses.html')

def course_details(request):
    """Course details page view"""
    return render(request, 'learner/course-details.html')

def instructors(request):
    """Instructors listing page view"""
    return render(request, 'learner/instructors.html')

def instructor_profile(request):
    """Instructor profile page view"""
    return render(request, 'learner/instructor-profile.html')

def blog(request):
    """Blog listing page view"""
    return render(request, 'learner/blog.html')

def blog_details(request):
    """Blog details page view"""
    return render(request, 'learner/blog-details.html')

def contact(request):
    """Contact page view"""
    return render(request, 'learner/contact.html')

def events(request):
    """Events page view"""
    return render(request, 'learner/events.html')

def enroll(request):
    """Enrollment page view"""
    return render(request, 'learner/enroll.html')

def pricing(request):
    """Pricing page view"""
    return render(request, 'learner/pricing.html')

def privacy(request):
    """Privacy policy page view"""
    return render(request, 'learner/privacy.html')

def terms(request):
    """Terms and conditions page view"""
    return render(request, 'learner/terms.html')

def starter_page(request):
    """Starter page view"""
    return render(request, 'learner/starter-page.html')

def error_404(request, exception=None):
    """Custom 404 error page view"""
    return render(request, 'learner/404.html', status=404)


# Authentication Views (using Backend API)

def register_view(request):
    """User registration view - calls backend API"""
    if api_is_authenticated(request):
        return redirect('index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            backend = APIAuthBackend()
            
            # Call backend API to register
            success, result, tokens = backend.register(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', '')
            )
            
            if success:
                username = form.cleaned_data.get('username')
                messages.success(request, f'Account created for {username}! You can now log in.')
                return redirect('login')
            else:
                messages.error(request, result)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    
    return render(request, 'learner/register.html', {'form': form})


def login_view(request):
    """User login view - calls backend API"""
    if api_is_authenticated(request):
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            backend = APIAuthBackend()
            
            # Backend API only accepts email for login
            success, result, tokens = backend.login(
                email=email,
                password=password
            )
            
            if success:
                # Save user data and tokens in session
                save_user_session(request, result, tokens)
                
                username = result.get('username', 'User')
                messages.success(request, f'Welcome back, {username}!')
                
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                messages.error(request, result)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'learner/login.html', {'form': form})


def logout_view(request):
    """User logout view - calls backend API"""
    if api_is_authenticated(request):
        backend = APIAuthBackend()
        refresh_token = request.session.get('refresh_token')
        
        if refresh_token:
            backend.logout(refresh_token)
    
    clear_user_session(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


@api_login_required
def profile_view(request):
    """User profile view"""
    user = get_current_user(request)
    
    # Check 2FA status from backend
    backend = APIAuthBackend()
    access_token = get_access_token(request)
    success, has_2fa = backend.check_2fa_status(access_token)
    
    if not success:
        has_2fa = False  # Default to False if check fails
    
    return render(request, 'learner/profile.html', {
        'has_2fa': has_2fa
    })


@api_login_required
def edit_profile_view(request):
    """Edit user profile view - calls backend API"""
    if request.method == 'POST':
        backend = APIAuthBackend()
        access_token = get_access_token(request)
        
        # Prepare update data
        update_data = {}
        if request.POST.get('first_name'):
            update_data['first_name'] = request.POST.get('first_name')
        if request.POST.get('last_name'):
            update_data['last_name'] = request.POST.get('last_name')
        if request.POST.get('phone'):
            update_data['phone'] = request.POST.get('phone')
        if request.POST.get('bio'):
            update_data['bio'] = request.POST.get('bio')
        
        # Check if password change is requested
        new_password = request.POST.get('new_password', '').strip()
        old_password = request.POST.get('old_password', '').strip()
        
        if new_password and old_password:
            # Change password first
            success, msg = backend.change_password(access_token, old_password, new_password)
            if success:
                messages.success(request, 'Password updated successfully. Please login again.')
                clear_user_session(request)
                return redirect('login')
            else:
                messages.error(request, msg)
                return redirect('edit_profile')
        
        # Update profile
        if update_data:
            success, result = backend.update_profile(access_token, **update_data)
            if success:
                # Update session data
                request.session['user'] = result
                request.session.modified = True
                messages.success(request, 'Profile updated successfully!')
            else:
                messages.error(request, result)
        
        return redirect('profile')
    
    user = get_current_user(request)
    return render(request, 'learner/edit_profile.html')


# Password Reset Views

def forgot_password_view(request):
    """Forgot password - request reset email via backend API"""
    if request.method == 'POST':
        email = request.POST.get('email')
        backend = APIAuthBackend()
        
        success, message = backend.forgot_password(email)
        
        if success:
            messages.success(request, message)
            return redirect('login')
        else:
            messages.error(request, message)
    
    return render(request, 'learner/forgot_password.html')


def reset_password_view(request):
    """Reset password with token via backend API"""
    token = request.GET.get('token')
    
    if not token:
        messages.error(request, 'Invalid reset link.')
        return redirect('login')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'learner/reset_password.html', {
                'validlink': True,
                'token': token
            })
        
        backend = APIAuthBackend()
        success, message = backend.reset_password(token, new_password)
        
        if success:
            messages.success(request, 'Password reset successful! You can now login with your new password.')
            return redirect('login')
        else:
            messages.error(request, message)
            return render(request, 'learner/reset_password.html', {
                'validlink': False
            })
    
    return render(request, 'learner/reset_password.html', {
        'validlink': True,
        'token': token
    })


# 2FA Views - Full Implementation

@api_login_required
def setup_2fa(request):
    """Setup 2FA - Generate QR code"""
    backend = APIAuthBackend()
    access_token = get_access_token(request)
    
    # Get QR code and secret from backend
    success, result = backend.setup_2fa(access_token)
    
    if success:
        # Store secret temporarily in session for verification
        request.session['temp_2fa_secret'] = result.get('secret')
        request.session.modified = True
        
        return render(request, 'learner/setup_2fa.html', {
            'qr_code': result.get('qr_code'),
            'secret': result.get('manual_entry_key')
        })
    else:
        messages.error(request, result)
        return redirect('profile')


@api_login_required
def verify_2fa_setup(request):
    """Verify 2FA setup with code"""
    if request.method == 'POST':
        code = request.POST.get('code')
        secret = request.session.get('temp_2fa_secret')
        
        if not secret:
            messages.error(request, 'Setup session expired. Please start again.')
            return redirect('setup_2fa')
        
        backend = APIAuthBackend()
        access_token = get_access_token(request)
        
        success, message = backend.verify_2fa_setup(access_token, secret, code)
        
        if success:
            # Clear temporary secret
            request.session.pop('temp_2fa_secret', None)
            request.session.modified = True
            messages.success(request, '✅ Two-factor authentication enabled successfully!')
            return redirect('profile')
        else:
            messages.error(request, message)
            return redirect('setup_2fa')
    
    return redirect('setup_2fa')


def verify_2fa_login(request):
    """Verify 2FA during login - placeholder for now"""
    # TODO: Implement 2FA verification during login flow
    messages.info(request, '2FA verification during login will be enhanced soon.')
    return redirect('login')


@api_login_required
def disable_2fa(request):
    """Disable 2FA"""
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if not password:
            messages.error(request, 'Password is required to disable 2FA.')
            return redirect('profile')
        
        backend = APIAuthBackend()
        access_token = get_access_token(request)
        
        success, message = backend.disable_2fa(access_token, password)
        
        if success:
            messages.success(request, '🔓 ' + message)
        else:
            messages.error(request, message)
        
        return redirect('profile')
    
    return redirect('profile')
