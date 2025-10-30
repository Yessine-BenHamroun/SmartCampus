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
    import requests
    
    courses_list = []
    try:
        # Fetch published courses from backend API
        response = requests.get('http://localhost:8001/api/courses/')
        
        if response.status_code == 200:
            data = response.json()
            courses_list = data.get('courses', [])
    except Exception as e:
        print(f"Error fetching courses: {str(e)}")
    
    context = {
        'courses': courses_list,
        'total_count': len(courses_list)
    }
    
    return render(request, 'learner/courses.html', context)

def course_detail(request, course_id):
    """Course detail page view - shows course overview without content access"""
    import requests
    
    course = None
    modules = []
    is_enrolled = False
    
    try:
        # Fetch course details from backend API
        response = requests.get(f'http://localhost:8001/api/courses/{course_id}/')
        
        if response.status_code == 200:
            data = response.json()
            course = data.get('course')
            
            # Fetch course modules (curriculum overview only)
            modules_response = requests.get(f'http://localhost:8001/api/courses/{course_id}/modules/')
            if modules_response.status_code == 200:
                modules_data = modules_response.json()
                modules = modules_data.get('modules', [])
                
                # Fetch lessons for each module
                for module in modules:
                    module_id = module.get('id')
                    lessons_response = requests.get(f'http://localhost:8001/api/courses/module/{module_id}/lessons/')
                    if lessons_response.status_code == 200:
                        lessons_data = lessons_response.json()
                        module['lessons'] = lessons_data.get('lessons', [])
                    else:
                        module['lessons'] = []
            
            # Check if user is enrolled (if logged in)
            if api_is_authenticated(request):
                access_token = get_access_token(request)
                enrollment_response = requests.get(
                    f'http://localhost:8001/api/courses/{course_id}/enrollment/check/',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                if enrollment_response.status_code == 200:
                    enrollment_data = enrollment_response.json()
                    is_enrolled = enrollment_data.get('is_enrolled', False)
                    
    except Exception as e:
        print(f"Error fetching course details: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Get current user info
    current_user = get_current_user(request)
    is_logged_in = api_is_authenticated(request)
    
    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'current_user': current_user,
        'is_authenticated': is_logged_in
    }
    
    # Debug: Print session info
    if is_logged_in:
        print(f"✅ User is authenticated: {current_user.get('email') if current_user else 'Unknown'}")
        print(f"🔑 Access token in session: {bool(request.session.get('access_token'))}")
    else:
        print("❌ User is NOT authenticated")
    
    return render(request, 'learner/course_detail.html', context)

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


# Student Learning Views

@api_login_required
def my_learning_view(request):
    """Student dashboard - My enrolled courses"""
    import requests
    
    user = get_current_user(request)
    enrolled_courses = []
    completed_courses = 0
    in_progress_courses = 0
    certificates_earned = 0
    
    if user:
        try:
            # Fetch enrolled courses from backend API
            access_token = get_access_token(request)
            response = requests.get(
                'http://localhost:8001/api/courses/my/enrollments/',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                enrollments = data.get('enrollments', [])
                
                # Fetch course details for each enrollment
                for enrollment in enrollments:
                    course_id = enrollment.get('course_id')
                    course_response = requests.get(f'http://localhost:8001/api/courses/{course_id}/')
                    if course_response.status_code == 200:
                        course_data = course_response.json()
                        course = course_data.get('course')
                        if course:
                            course['progress'] = enrollment.get('progress', 0)
                            course['enrollment_date'] = enrollment.get('enrolled_at')
                            
                            # Fetch detailed progress info for richer dashboard data
                            progress_info = None
                            try:
                                progress_resp = requests.get(
                                    f'http://localhost:8001/api/courses/{course_id}/progress/details/',
                                    headers={'Authorization': f'Bearer {access_token}'}
                                )
                                if progress_resp.status_code == 200:
                                    progress_payload = progress_resp.json()
                                    progress_info = progress_payload.get('progress')
                            except Exception as progress_error:
                                print(f"Error fetching progress details for course {course_id}: {progress_error}")
                            
                            if progress_info:
                                course['progress_info'] = progress_info
                                completion_percentage = progress_info.get('completion_percentage', 0) or 0
                            else:
                                completion_percentage = course.get('progress', 0) or 0
                            
                            if enrollment.get('completed') or completion_percentage >= 100:
                                completed_courses += 1
                            elif completion_percentage > 0:
                                in_progress_courses += 1
                            
                            if enrollment.get('certificate_issued'):
                                certificates_earned += 1
                            
                            enrolled_courses.append(course)
                            
        except Exception as e:
            print(f"Error fetching enrollments: {str(e)}")
    
    context = {
        'page_title': 'My Learning Dashboard',
        'enrolled_courses': enrolled_courses,
        'completed_courses': completed_courses,
        'in_progress_courses': in_progress_courses,
        'certificates_earned': certificates_earned
    }
    
    return render(request, 'learner/my_learning.html', context)


@api_login_required
def my_progress_view(request):
    """Student progress tracking"""
    import requests

    access_token = get_access_token(request)
    progress_entries = []
    total_minutes = 0
    total_lessons = 0
    total_quizzes = 0
    total_assignments = 0
    average_percentage = 0

    try:
        response = requests.get(
            'http://localhost:8001/api/courses/progress/my/',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if response.status_code == 200:
            payload = response.json()
            api_entries = payload.get('progress', []) or []

            enriched_entries = []
            for entry in api_entries:
                lessons = entry.get('lessons_completed') or []
                quizzes = entry.get('quizzes_completed') or []
                assignments = entry.get('assignments_completed') or []

                minutes_raw = entry.get('time_spent_minutes', 0)
                try:
                    minutes = float(minutes_raw) if minutes_raw is not None else 0
                except (TypeError, ValueError):
                    minutes = 0

                completion_raw = entry.get('completion_percentage', 0)
                try:
                    completion = float(completion_raw) if completion_raw is not None else 0
                except (TypeError, ValueError):
                    completion = 0

                course_id = entry.get('course_id')
                if isinstance(course_id, dict) and course_id.get('$oid'):
                    course_id = course_id['$oid']

                course_title = 'Course'
                course_thumbnail = '/static/img/education/courses-3.webp'
                try:
                    if course_id:
                        course_resp = requests.get(
                            f'http://localhost:8001/api/courses/{course_id}/',
                            headers={'Authorization': f'Bearer {access_token}'}
                        )
                        if course_resp.status_code == 200:
                            course_payload = course_resp.json().get('course', {})
                            course_title = course_payload.get('title') or course_title
                            course_thumbnail = course_payload.get('thumbnail_url') or course_payload.get('thumbnail') or course_thumbnail
                except Exception as course_error:
                    print(f"Error fetching course {course_id} details: {course_error}")

                total_minutes += minutes
                total_lessons += len(lessons)
                total_quizzes += len(quizzes)
                total_assignments += len(assignments)
                average_percentage += completion

                enriched_entries.append({
                    **entry,
                    'course_id': course_id,
                    'course_title': course_title,
                    'course_thumbnail': course_thumbnail,
                    'lessons_completed_count': len(lessons),
                    'quizzes_completed_count': len(quizzes),
                    'assignments_completed_count': len(assignments),
                    'time_spent_minutes': minutes,
                    'completion_percentage': completion,
                    'lessons_completed': lessons,
                    'quizzes_completed': quizzes,
                    'assignments_completed': assignments
                })

            progress_entries = enriched_entries

            if progress_entries:
                average_percentage = round(average_percentage / len(progress_entries), 1)
    except Exception as e:
        print(f"Error fetching progress data: {str(e)}")

    total_hours = round(total_minutes / 60, 1) if total_minutes else 0

    context = {
        'page_title': 'My Progress',
        'progress_entries': progress_entries,
        'total_learning_hours': total_hours,
        'total_lessons_completed': total_lessons,
        'total_quizzes_passed': total_quizzes,
        'total_assignments_submitted': total_assignments,
        'average_completion_percentage': average_percentage
    }

    return render(request, 'learner/my_progress.html', context)


@api_login_required
def my_submissions_view(request):
    """Student submissions view"""
    user = get_current_user(request)
    
    # TODO: Fetch submissions from backend API
    context = {
        'page_title': 'My Submissions',
        'submissions': []  # Will be populated from API
    }
    
    return render(request, 'learner/my_submissions.html', context)


@api_login_required
def discussions_view(request):
    """Course discussions/forums"""
    user = get_current_user(request)
    
    # TODO: Fetch discussions from backend API
    context = {
        'page_title': 'Discussions',
        'discussions': []  # Will be populated from API
    }
    
    return render(request, 'learner/discussions.html', context)


# Instructor Views

@api_login_required
def instructor_dashboard_view(request):
    """Instructor dashboard - requires instructor or admin role"""
    user = get_current_user(request)
    
    # Check if user has instructor or admin role
    user_role = user.get('role', 'student')
    if user_role not in ['instructor', 'admin']:
        messages.error(request, 'Access denied. Instructor privileges required.')
        return redirect('index')
    
    # Fetch instructor's courses and statistics from backend API
    backend = APIAuthBackend()
    access_token = get_access_token(request)
    
    import requests
    courses = []
    stats = {
        'total_courses': 0,
        'published_courses': 0,
        'total_students': 0,
        'total_reviews': 0,
        'average_rating': 0.0
    }
    
    try:
        response = requests.get(
            'http://localhost:8001/api/courses/instructor/my-courses/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            courses = data.get('courses', [])
            
            # Calculate statistics
            stats['total_courses'] = len(courses)
            stats['published_courses'] = sum(1 for c in courses if c.get('published') or c.get('is_published'))
            stats['total_students'] = sum(c.get('enrollment_count', 0) for c in courses)
            stats['total_reviews'] = sum(c.get('review_count', 0) for c in courses)
            
            # Calculate average rating across all courses
            total_rating = sum(c.get('average_rating', 0) * c.get('review_count', 0) for c in courses)
            total_review_count = sum(c.get('review_count', 0) for c in courses)
            if total_review_count > 0:
                stats['average_rating'] = round(total_rating / total_review_count, 1)
        else:
            messages.error(request, 'Failed to load dashboard data')
    except Exception as e:
        messages.error(request, f'Error connecting to backend: {str(e)}')
    
    context = {
        'page_title': 'Teaching Dashboard',
        'stats': stats,
        'recent_courses': courses[:5]  # Show 5 most recent courses
    }
    
    return render(request, 'learner/instructor_dashboard.html', context)


@api_login_required
def instructor_courses_view(request):
    """Instructor's courses management"""
    user = get_current_user(request)
    
    # Check if user has instructor or admin role
    user_role = user.get('role', 'student')
    if user_role not in ['instructor', 'admin']:
        messages.error(request, 'Access denied. Instructor privileges required.')
        return redirect('index')
    
    # Fetch instructor's courses from backend API
    backend = APIAuthBackend()
    access_token = get_access_token(request)
    
    import requests
    try:
        response = requests.get(
            'http://localhost:8001/api/courses/instructor/my-courses/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            courses = data.get('courses', [])
        else:
            courses = []
            messages.error(request, 'Failed to load courses')
    except Exception as e:
        courses = []
        messages.error(request, f'Error connecting to backend: {str(e)}')
    
    context = {
        'page_title': 'My Courses',
        'courses': courses
    }
    
    return render(request, 'learner/instructor_courses.html', context)


@api_login_required
def instructor_submissions_view(request):
    """Submissions to grade (instructor view)"""
    user = get_current_user(request)
    
    # Check if user has instructor or admin role
    user_role = user.get('role', 'student')
    if user_role not in ['instructor', 'admin']:
        messages.error(request, 'Access denied. Instructor privileges required.')
        return redirect('index')
    
    # TODO: Fetch submissions from backend API
    context = {
        'page_title': 'Student Submissions',
        'submissions': []  # Will be populated from API
    }
    
    return render(request, 'learner/instructor_submissions.html', context)


@api_login_required
def course_analytics_view(request):
    """Course analytics for instructors"""
    user = get_current_user(request)
    
    # Check if user has instructor or admin role
    user_role = user.get('role', 'student')
    if user_role not in ['instructor', 'admin']:
        messages.error(request, 'Access denied. Instructor privileges required.')
        return redirect('index')
    
    # TODO: Fetch analytics from backend API
    context = {
        'page_title': 'Course Analytics',
        'analytics': {}  # Will be populated from API
    }
    
    return render(request, 'learner/course_analytics.html', context)


@api_login_required
def create_course_view(request):
    """Create a new course"""
    user = get_current_user(request)
    
    # Check if user has instructor or admin role
    user_role = user.get('role', 'student')
    if user_role not in ['instructor', 'admin']:
        messages.error(request, 'Access denied. Instructor privileges required.')
        return redirect('index')
    
    if request.method == 'POST':
        backend = APIAuthBackend()
        access_token = get_access_token(request)
        
        import requests
        try:
            # Prepare course data
            course_data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'category': request.POST.get('category', 'general'),
                'level': request.POST.get('level', 'beginner'),
                'price': request.POST.get('price', 0),
                'thumbnail': request.POST.get('thumbnail', ''),
                'preview_video': request.POST.get('preview_video', ''),
            }
            
            response = requests.post(
                'http://localhost:8001/api/courses/instructor/create/',
                json=course_data,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 201:
                data = response.json()
                messages.success(request, 'Course created successfully!')
                course_id = data['course']['id']
                return redirect('edit_course', course_id=course_id)
            else:
                error_data = response.json()
                messages.error(request, error_data.get('error', 'Failed to create course'))
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'page_title': 'Create New Course',
        'categories': ['general', 'programming', 'design', 'business', 'marketing', 'data-science'],
        'levels': ['beginner', 'intermediate', 'advanced']
    }
    
    return render(request, 'learner/create_course.html', context)


@api_login_required
def edit_course_view(request, course_id):
    """Edit an existing course"""
    user = get_current_user(request)
    
    # Check if user has instructor or admin role
    user_role = user.get('role', 'student')
    if user_role not in ['instructor', 'admin']:
        messages.error(request, 'Access denied. Instructor privileges required.')
        return redirect('index')
    
    backend = APIAuthBackend()
    access_token = get_access_token(request)
    
    import requests
    
    if request.method == 'POST':
        try:
            # Prepare update data
            update_data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'category': request.POST.get('category'),
                'level': request.POST.get('level'),
                'price': request.POST.get('price'),
                'thumbnail': request.POST.get('thumbnail', ''),
                'preview_video': request.POST.get('preview_video', ''),
            }
            
            if 'published' in request.POST:
                update_data['published'] = request.POST.get('published') == 'true'
            
            response = requests.put(
                f'http://localhost:8001/api/courses/instructor/course/{course_id}/',
                json=update_data,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 200:
                messages.success(request, 'Course updated successfully!')
            else:
                error_data = response.json()
                messages.error(request, error_data.get('error', 'Failed to update course'))
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Fetch course data
    try:
        response = requests.get(
            f'http://localhost:8001/api/courses/instructor/course/{course_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            course = data.get('course', {})
            
            # Fetch modules for this course
            modules_response = requests.get(
                f'http://localhost:8001/api/courses/instructor/course/{course_id}/modules/',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if modules_response.status_code == 200:
                modules_data = modules_response.json()
                course['modules'] = modules_data.get('modules', [])
            else:
                course['modules'] = []
        else:
            messages.error(request, 'Course not found')
            return redirect('instructor_courses')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('instructor_courses')
    
    context = {
        'page_title': 'Edit Course',
        'course': course,
        'categories': ['general', 'programming', 'design', 'business', 'marketing', 'data-science'],
        'levels': ['beginner', 'intermediate', 'advanced']
    }
    
    return render(request, 'learner/edit_course.html', context)


# Quiz Views

@api_login_required
def create_quiz_view(request, lesson_id):
    """Create quiz for a lesson (Instructor only)"""
    import requests
    
    # Get lesson and course details
    access_token = get_access_token(request)
    lesson = None
    course_id = None
    
    try:
        lesson_response = requests.get(
            f'http://localhost:8001/api/courses/lesson/{lesson_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if lesson_response.status_code == 200:
            lesson_data = lesson_response.json()
            lesson = lesson_data.get('lesson')
            course_id = lesson.get('course_id')
    except Exception as e:
        messages.error(request, f'Error fetching lesson: {str(e)}')
        return redirect('instructor_courses')
    
    context = {
        'lesson_id': lesson_id,
        'course_id': course_id,
        'lesson': lesson,
        'access_token': access_token
    }
    
    return render(request, 'learner/create_quiz.html', context)


@api_login_required
def take_quiz_view(request, quiz_id):
    """Take a quiz (Student)"""
    import requests
    import json
    
    access_token = get_access_token(request)
    quiz = None
    
    try:
        quiz_response = requests.get(
            f'http://localhost:8001/api/courses/quiz/{quiz_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if quiz_response.status_code == 200:
            quiz = quiz_response.json()
    except Exception as e:
        messages.error(request, f'Error fetching quiz: {str(e)}')
        return redirect('my_learning')
    
    context = {
        'quiz': quiz,
        'quiz_json': json.dumps(quiz)
    }
    
    return render(request, 'learner/take_quiz.html', context)


# Assignment Views

@api_login_required
def create_assignment_view(request, course_id):
    """Create assignment for a course (Instructor only)"""
    import requests
    
    # Get course details
    access_token = get_access_token(request)
    course = None
    
    try:
        course_response = requests.get(
            f'http://localhost:8001/api/courses/{course_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if course_response.status_code == 200:
            course_data = course_response.json()
            course = course_data.get('course')
    except Exception as e:
        messages.error(request, f'Error fetching course: {str(e)}')
        return redirect('instructor_courses')
    
    context = {
        'course_id': course_id,
        'course': course,
        'access_token': access_token
    }
    
    return render(request, 'learner/create_assignment.html', context)


@api_login_required
def take_assignment_view(request, assignment_id):
    """Take an assignment (Student)"""
    import requests
    import json
    
    access_token = get_access_token(request)
    assignment = None
    
    try:
        assignment_response = requests.get(
            f'http://localhost:8001/api/courses/assignment/{assignment_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if assignment_response.status_code == 200:
            assignment = assignment_response.json()
    except Exception as e:
        messages.error(request, f'Error fetching assignment: {str(e)}')
        return redirect('my_learning')
    
    context = {
        'assignment': assignment,
        'assignment_json': json.dumps(assignment)
    }
    
    return render(request, 'learner/take_assignment.html', context)


@api_login_required
def manage_quizzes_view(request):
    """Manage all quizzes (Instructor)"""
    return render(request, 'learner/manage_quizzes.html')


@api_login_required
def manage_assignments_view(request):
    """Manage all assignments (Instructor)"""
    return render(request, 'learner/manage_assignments.html')


@api_login_required
def grade_submission_view(request, submission_id):
    """Grade a student submission (Instructor)"""
    import requests
    import json
    
    access_token = get_access_token(request)
    submission = None
    
    try:
        submission_response = requests.get(
            f'http://localhost:8001/api/courses/submission/{submission_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if submission_response.status_code == 200:
            submission = submission_response.json()
    except Exception as e:
        messages.error(request, f'Error fetching submission: {str(e)}')
        return redirect('instructor_submissions')
    
    context = {
        'submission': submission,
        'submission_json': json.dumps(submission)
    }
    
    return render(request, 'learner/grade_submission.html', context)


@api_login_required
def my_progress_view(request):
    """View student's progress across all courses"""
    return render(request, 'learner/my_progress.html')


@api_login_required
def course_progress_view(request, course_id):
    """View detailed progress for a specific course"""
    import requests
    
    access_token = get_access_token(request)
    course = None
    
    try:
        course_response = requests.get(
            f'http://localhost:8001/api/courses/{course_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if course_response.status_code == 200:
            course = course_response.json()
    except Exception as e:
        messages.error(request, f'Error fetching course: {str(e)}')
    
    context = {
        'course': course,
        'course_id': course_id
    }
    
    return render(request, 'learner/course_progress.html', context)


@api_login_required
def submit_course_review_view(request, course_id):
    """Submit a review for a course"""
    import requests
    
    access_token = get_access_token(request)
    course = None
    
    try:
        course_response = requests.get(
            f'http://localhost:8001/api/courses/{course_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if course_response.status_code == 200:
            course = course_response.json()
    except Exception as e:
        messages.error(request, f'Error fetching course: {str(e)}')
    
    context = {
        'course': course,
        'course_id': course_id
    }
    
    return render(request, 'learner/submit_course_review.html', context)


@api_login_required
def submit_instructor_review_view(request, instructor_id, course_id):
    """Submit a review for an instructor"""
    import requests
    
    access_token = get_access_token(request)
    course = None
    instructor = None
    
    try:
        course_response = requests.get(
            f'http://localhost:8001/api/courses/{course_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if course_response.status_code == 200:
            course = course_response.json()
            
        # Get instructor info from users API
        instructor_response = requests.get(
            f'http://localhost:8001/api/users/{instructor_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if instructor_response.status_code == 200:
            instructor = instructor_response.json()
    except Exception as e:
        messages.error(request, f'Error fetching data: {str(e)}')
    
    context = {
        'course': course,
        'instructor': instructor,
        'course_id': course_id,
        'instructor_id': instructor_id
    }
    
    return render(request, 'learner/submit_instructor_review.html', context)


@api_login_required
def course_learning_view(request, course_id):
    """Main course learning page with lesson player and progress tracking"""
    import requests
    
    access_token = get_access_token(request)
    course = None
    modules = []
    current_lesson = None
    progress = None
    
    try:
        # Fetch course details
        course_response = requests.get(
            f'http://localhost:8001/api/courses/{course_id}/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if course_response.status_code == 200:
            course = course_response.json().get('course')
        
        # Fetch modules and lessons
        modules_response = requests.get(
            f'http://localhost:8001/api/courses/{course_id}/modules/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if modules_response.status_code == 200:
            modules = modules_response.json().get('modules', [])
            
            # Fetch lessons for each module
            for module in modules:
                lessons_response = requests.get(
                    f'http://localhost:8001/api/courses/module/{module["id"]}/lessons/',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                if lessons_response.status_code == 200:
                    module['lessons'] = lessons_response.json().get('lessons', [])
                else:
                    module['lessons'] = []
        
        # Fetch student progress
        progress_response = requests.get(
            f'http://localhost:8001/api/courses/{course_id}/progress/details/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if progress_response.status_code == 200:
            progress = progress_response.json().get('progress', {})
        
        # Determine current lesson (first incomplete lesson or first lesson)
        completed_lessons = progress.get('lessons_completed', []) if progress else []
        
        for module in modules:
            for lesson in module.get('lessons', []):
                if lesson['id'] not in completed_lessons:
                    current_lesson = lesson
                    break
            if current_lesson:
                break
        
        # If all lessons completed, show first lesson
        if not current_lesson and modules and modules[0].get('lessons'):
            current_lesson = modules[0]['lessons'][0]
            
    except Exception as e:
        messages.error(request, f'Error loading course: {str(e)}')
        print(f"Error in course_learning_view: {str(e)}")
        import traceback
        traceback.print_exc()
    
    context = {
        'course': course,
        'modules': modules,
        'current_lesson': current_lesson,
        'progress': progress,
        'course_id': course_id
    }
    
    return render(request, 'learner/course_learning.html', context)
