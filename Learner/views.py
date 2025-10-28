from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .forms import RegisterForm, LoginForm
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import user_has_device
from django.http import HttpResponse
import qrcode
import io

# Create your views here.

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


# Authentication Views

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    
    return render(request, 'learner/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user has 2FA enabled
            if user_has_device(user):
                # Generate a random 6-digit code
                import random
                verification_code = str(random.randint(100000, 999999))
                
                # Store code in session with expiry
                import time
                request.session['2fa_code'] = verification_code
                request.session['2fa_user_id'] = user.id
                request.session['2fa_expires'] = time.time() + 300  # 5 minutes
                
                # Send code via email
                try:
                    send_mail(
                        'SmartCampus - Your 2FA Verification Code',
                        f'Hello {user.first_name or user.username},\n\n'
                        f'Your verification code is: {verification_code}\n\n'
                        f'This code will expire in 5 minutes.\n\n'
                        f'If you did not request this code, please ignore this email.\n\n'
                        f'Best regards,\n'
                        f'SmartCampus Team',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    
                    print(f"\n{'='*80}")
                    print(f"📧 2FA CODE SENT VIA EMAIL")
                    print(f"{'='*80}")
                    print(f"User: {user.username}")
                    print(f"Email: {user.email}")
                    print(f"🔐 VERIFICATION CODE: {verification_code}")
                    print(f"   (Valid for 5 minutes)")
                    print(f"{'='*80}\n")
                    
                    messages.success(request, f'A verification code has been sent to {user.email}')
                except Exception as e:
                    print(f"Error sending email: {e}")
                    messages.error(request, 'Error sending verification code. Please try again.')
                    return render(request, 'learner/login.html', {'form': LoginForm()})
                
                # Redirect to 2FA verification without logging in yet
                return redirect('verify_2fa_login')
            else:
                # No 2FA, login normally
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            form = LoginForm()
    else:
        form = LoginForm()
    
    return render(request, 'learner/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


@login_required
def profile_view(request):
    """User profile view"""
    # Check if user has 2FA enabled
    has_2fa = user_has_device(request.user)
    return render(request, 'learner/profile.html', {
        'user': request.user,
        'has_2fa': has_2fa
    })


@login_required
def edit_profile_view(request):
    """Edit user profile view"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # Update password if provided
        new_password = request.POST.get('new_password', '')
        if new_password:
            user.set_password(new_password)
            messages.success(request, 'Password updated successfully. Please login again.')
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'learner/edit_profile.html', {'user': request.user})


# Password Reset Views

def forgot_password_view(request):
    """Forgot password - request reset email"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )
            
            # Send email
            subject = 'Reset Your SmartCampus Password'
            message = render_to_string('learner/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=message,
            )
            
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
    
    return render(request, 'learner/forgot_password.html')


def reset_password_view(request, uidb64, token):
    """Reset password with token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful! You can now login with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        
        return render(request, 'learner/reset_password.html', {
            'validlink': True,
            'uidb64': uidb64,
            'token': token
        })
    else:
        return render(request, 'learner/reset_password.html', {'validlink': False})


# Two-Factor Authentication (2FA) Views

@login_required
def setup_2fa(request):
    """Setup 2FA for the user via email"""
    user = request.user
    
    # Check if user already has a confirmed device
    if TOTPDevice.objects.filter(user=user, confirmed=True).exists():
        messages.info(request, 'Two-factor authentication is already enabled for your account.')
        return redirect('profile')
    
    # Delete any old unconfirmed devices
    TOTPDevice.objects.filter(user=user, confirmed=False).delete()
    
    # Generate a random 6-digit verification code
    import random
    import time
    
    verification_code = str(random.randint(100000, 999999))
    
    # Store verification code in session
    request.session['2fa_setup_code'] = verification_code
    request.session['2fa_setup_expires'] = time.time() + 300  # 5 minutes
    request.session['2fa_setup_user_id'] = user.id
    
    # Send code via email
    try:
        send_mail(
            'SmartCampus - Enable Two-Factor Authentication',
            f'Hello {user.first_name or user.username},\n\n'
            f'You are enabling Two-Factor Authentication for your SmartCampus account.\n\n'
            f'Your verification code is: {verification_code}\n\n'
            f'This code will expire in 5 minutes.\n\n'
            f'If you did not request this, please ignore this email and ensure your account is secure.\n\n'
            f'Best regards,\n'
            f'SmartCampus Team',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        print(f"\n{'='*80}")
        print(f"� 2FA SETUP CODE SENT VIA EMAIL")
        print(f"{'='*80}")
        print(f"User: {user.username}")
        print(f"Email: {user.email}")
        print(f"🔐 SETUP VERIFICATION CODE: {verification_code}")
        print(f"   (Valid for 5 minutes)")
        print(f"{'='*80}\n")
        
        messages.success(request, f'A verification code has been sent to {user.email}')
    except Exception as e:
        print(f"Error sending email: {e}")
        messages.error(request, 'Error sending verification code. Please try again.')
        return redirect('profile')
    
    context = {
        'user_email': user.email
    }
    
    return render(request, 'learner/setup_2fa.html', context)


@login_required
def qr_code(request):
    """Generate QR code image for 2FA setup"""
    user = request.user
    
    # Get the unconfirmed device
    device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
    if not device:
        return HttpResponse("No device found", status=404)
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(device.config_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return HttpResponse(buf.getvalue(), content_type="image/png")


@login_required
def verify_2fa_setup(request):
    """Verify the setup code sent via email and enable 2FA"""
    if request.method != 'POST':
        return redirect('setup_2fa')
    
    import time
    
    user = request.user
    code = request.POST.get('token', '').strip()  # Keep 'token' field name for consistency
    
    # Get code from session
    stored_code = request.session.get('2fa_setup_code')
    code_expires = request.session.get('2fa_setup_expires')
    setup_user_id = request.session.get('2fa_setup_user_id')
    
    # Validate session data
    if not all([stored_code, code_expires, setup_user_id]):
        messages.error(request, 'Setup session expired. Please start the setup process again.')
        return redirect('setup_2fa')
    
    # Check if code expired
    if time.time() > code_expires:
        messages.error(request, 'Verification code has expired. Please start the setup process again.')
        # Clean up session
        request.session.pop('2fa_setup_code', None)
        request.session.pop('2fa_setup_expires', None)
        request.session.pop('2fa_setup_user_id', None)
        return redirect('setup_2fa')
    
    # Check if user matches
    if setup_user_id != user.id:
        messages.error(request, 'Invalid session. Please start the setup process again.')
        return redirect('setup_2fa')
    
    print(f"\n{'='*80}")
    print(f"🔐 2FA SETUP VERIFICATION ATTEMPT")
    print(f"{'='*80}")
    print(f"User: {user.username}")
    print(f"Entered code: {code}")
    print(f"Expected code: {stored_code}")
    print(f"Code expires at: {code_expires}")
    print(f"Current time: {time.time()}")
    
    # Verify the code
    if code == stored_code:
        print(f"✅ CODE MATCH - ENABLING 2FA")
        
        # Delete any old devices
        TOTPDevice.objects.filter(user=user).delete()
        
        # Create a confirmed TOTP device (we'll keep the device model but use email for login)
        device = TOTPDevice.objects.create(
            user=user,
            name='default',
            confirmed=True
        )
        
        # Clean up session
        request.session.pop('2fa_setup_code', None)
        request.session.pop('2fa_setup_expires', None)
        request.session.pop('2fa_setup_user_id', None)
        
        messages.success(request, '✅ Two-factor authentication has been successfully enabled!')
        print(f"✅ SUCCESS - 2FA enabled for {user.username}")
        print(f"{'='*80}\n")
        
        return redirect('profile')
    else:
        print(f"❌ CODE MISMATCH")
        print(f"{'='*80}\n")
        messages.error(request, '❌ Invalid verification code. Please try again.')
        return redirect('setup_2fa')


def verify_2fa_login(request):
    """Verify 2FA token sent via email"""
    import time
    
    # Check if there's a pending 2FA verification
    if '2fa_code' not in request.session or '2fa_user_id' not in request.session:
        messages.error(request, 'No pending verification. Please login again.')
        return redirect('login')
    
    # Check if code has expired
    if request.session.get('2fa_expires', 0) < time.time():
        messages.error(request, 'Verification code has expired. Please login again.')
        # Clean up session
        for key in ['2fa_code', '2fa_user_id', '2fa_expires']:
            if key in request.session:
                del request.session[key]
        return redirect('login')
    
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        stored_code = request.session.get('2fa_code')
        user_id = request.session.get('2fa_user_id')
        
        print(f"\n{'='*80}")
        print(f"🔐 2FA EMAIL VERIFICATION")
        print(f"{'='*80}")
        print(f"User ID: {user_id}")
        print(f"Code entered: {token}")
        print(f"Expected code: {stored_code}")
        
        if token == stored_code:
            # Get user and login
            try:
                user = User.objects.get(pk=user_id)
                login(request, user)
                
                # Clean up session
                for key in ['2fa_code', '2fa_user_id', '2fa_expires']:
                    if key in request.session:
                        del request.session[key]
                
                request.session['2fa_verified'] = True
                
                print(f"✅ 2FA Verification: SUCCESS")
                print(f"{'='*80}\n")
                
                messages.success(request, f'Welcome back, {user.username}! Two-factor authentication successful!')
                return redirect('index')
            except User.DoesNotExist:
                print(f"❌ 2FA Verification: User not found")
                print(f"{'='*80}\n")
                messages.error(request, 'User not found. Please login again.')
                return redirect('login')
        else:
            print(f"❌ 2FA Verification: FAILED - Code mismatch")
            print(f"{'='*80}\n")
            messages.error(request, 'Invalid verification code. Please try again.')
    else:
        # Display info when page loads
        user_id = request.session.get('2fa_user_id')
        stored_code = request.session.get('2fa_code')
        expires_at = request.session.get('2fa_expires', 0)
        remaining = int(expires_at - time.time())
        
        try:
            user = User.objects.get(pk=user_id)
            
            print(f"\n{'='*80}")
            print(f"� 2FA VERIFICATION PAGE LOADED")
            print(f"{'='*80}")
            print(f"User: {user.username}")
            print(f"Email: {user.email}")
            print(f"🔐 VERIFICATION CODE: {stored_code}")
            print(f"   (Expires in {remaining} seconds)")
            print(f"{'='*80}\n")
        except User.DoesNotExist:
            pass
    
    return render(request, 'learner/verify_2fa.html')


@login_required
def disable_2fa(request):
    """Disable 2FA for the user"""
    if request.method == 'POST':
        user = request.user
        
        # Delete all TOTP devices for the user
        TOTPDevice.objects.filter(user=user).delete()
        
        # Clear 2FA session
        if '2fa_verified' in request.session:
            del request.session['2fa_verified']
        
        messages.success(request, 'Two-factor authentication has been disabled.')
        return redirect('profile')
    
    return redirect('profile')
