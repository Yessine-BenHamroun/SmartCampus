"""
Frontend authentication module that communicates with Backend API
This replaces Django's built-in auth with MongoDB-based backend API
"""
import requests
from django.conf import settings
from datetime import datetime, timedelta
import json

# Backend API base URL
BACKEND_API_URL = getattr(settings, 'BACKEND_API_URL', 'http://localhost:8001/api')


class APIAuthBackend:
    """
    Custom authentication backend that uses the REST API
    """
    
    def __init__(self):
        self.api_url = BACKEND_API_URL
    
    def register(self, username, email, password, first_name='', last_name=''):
        """
        Register a new user via backend API
        Returns: (success, data/error_message, tokens)
        """
        try:
            print("\n" + "="*80)
            print("🔵 FRONTEND: Starting user registration")
            print("="*80)
            print(f"📧 Email: {email}")
            print(f"👤 Username: {username}")
            print(f"🌐 Backend API URL: {self.api_url}/users/register/")
            print(f"📤 Sending POST request...")
            
            response = requests.post(
                f'{self.api_url}/users/register/',
                json={
                    'username': username,
                    'email': email,
                    'password': password,
                    'confirm_password': password,
                    'first_name': first_name,
                    'last_name': last_name
                },
                timeout=10
            )
            
            print(f"📥 Response Status Code: {response.status_code}")
            print(f"📥 Response Body: {response.text[:500]}")
            
            if response.status_code == 201:
                data = response.json()
                print("✅ SUCCESS: User registered successfully!")
                print(f"💾 User ID: {data.get('user', {}).get('_id', 'N/A')}")
                print(f"📧 Email: {data.get('user', {}).get('email', 'N/A')}")
                print(f"🔑 Access Token: {data.get('tokens', {}).get('access', '')[:50]}...")
                print("="*80 + "\n")
                return True, data, data.get('tokens')
            else:
                error_data = response.json()
                error_msg = error_data.get('error', 'Registration failed')
                print(f"❌ FAILED: Registration failed with status {response.status_code}")
                print(f"❌ Error: {error_msg}")
                print("="*80 + "\n")
                if isinstance(error_data, dict):
                    # Collect all validation errors
                    errors = []
                    for field, messages in error_data.items():
                        if isinstance(messages, list):
                            errors.extend(messages)
                        else:
                            errors.append(str(messages))
                    error_msg = '; '.join(errors) if errors else error_msg
                return False, error_msg, None
                
        except requests.exceptions.ConnectionError:
            return False, 'Cannot connect to authentication server. Please try again later.', None
        except requests.exceptions.Timeout:
            return False, 'Authentication server timeout. Please try again.', None
        except Exception as e:
            return False, f'Registration error: {str(e)}', None
    
    def login(self, username=None, email=None, password=None):
        """
        Login user via backend API
        Returns: (success, user_data/error_message, tokens)
        """
        try:
            print("\n" + "="*80)
            print("🔵 FRONTEND: Starting user login")
            print("="*80)
            print(f"📥 Username provided: {username}")
            print(f"📥 Email provided: {email}")
            print(f"🔐 Password provided: {'*' * len(password) if password else 'None'}")
            
            # Backend uses email for login
            login_email = email if email else username
            
            # If username is provided but doesn't contain @, it's not an email
            if login_email and '@' not in login_email:
                print(f"⚠️  WARNING: Backend API requires EMAIL for login, but received username: {login_email}")
                print(f"❌ The backend does NOT support username-based login!")
                print("="*80 + "\n")
                return False, 'Please login with your email address, not username', None
            
            print(f"📧 Using email for login: {login_email}")
            print(f"🌐 Backend API URL: {self.api_url}/users/login/")
            print(f"📤 Sending POST request...")
            
            response = requests.post(
                f'{self.api_url}/users/login/',
                json={
                    'email': login_email,
                    'password': password
                },
                timeout=10
            )
            
            print(f"📥 Response Status Code: {response.status_code}")
            print(f"📥 Response Body: {response.text[:500]}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: User logged in successfully!")
                print(f"👤 Username: {data.get('user', {}).get('username', 'N/A')}")
                print(f"📧 Email: {data.get('user', {}).get('email', 'N/A')}")
                print(f"🔑 Access Token: {data.get('tokens', {}).get('access', '')[:50]}...")
                print("="*80 + "\n")
                return True, data.get('user'), data.get('tokens')
            else:
                error_data = response.json()
                error_msg = error_data.get('error', 'Invalid credentials')
                print(f"❌ FAILED: Login failed with status {response.status_code}")
                print(f"❌ Error: {error_msg}")
                print("="*80 + "\n")
                return False, error_msg, None
                
        except requests.exceptions.ConnectionError:
            return False, 'Cannot connect to authentication server. Please try again later.', None
        except requests.exceptions.Timeout:
            return False, 'Authentication server timeout. Please try again.', None
        except Exception as e:
            return False, f'Login error: {str(e)}', None
    
    def logout(self, refresh_token):
        """
        Logout user via backend API (blacklist refresh token)
        Returns: (success, message)
        """
        try:
            response = requests.post(
                f'{self.api_url}/users/logout/',
                json={'refresh_token': refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, 'Logout successful'
            else:
                # Even if API fails, we can still clear local session
                return True, 'Logged out locally'
                
        except Exception as e:
            # If API fails, still allow logout locally
            return True, 'Logged out locally'
    
    def get_profile(self, access_token):
        """
        Get user profile via backend API
        Returns: (success, user_data/error_message)
        """
        try:
            response = requests.get(
                f'{self.api_url}/users/profile/',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get('user')
            else:
                return False, 'Failed to fetch profile'
                
        except Exception as e:
            return False, f'Profile error: {str(e)}'
    
    def update_profile(self, access_token, **kwargs):
        """
        Update user profile via backend API
        Returns: (success, user_data/error_message)
        """
        try:
            response = requests.put(
                f'{self.api_url}/users/profile/',
                headers={'Authorization': f'Bearer {access_token}'},
                json=kwargs,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get('user')
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Failed to update profile')
                
        except Exception as e:
            return False, f'Update error: {str(e)}'
    
    def change_password(self, access_token, old_password, new_password):
        """
        Change password via backend API
        Returns: (success, message)
        """
        try:
            response = requests.post(
                f'{self.api_url}/users/change-password/',
                headers={'Authorization': f'Bearer {access_token}'},
                json={
                    'old_password': old_password,
                    'new_password': new_password,
                    'confirm_password': new_password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, 'Password changed successfully'
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Failed to change password')
                
        except Exception as e:
            return False, f'Password change error: {str(e)}'
    
    def forgot_password(self, email):
        """
        Request password reset via backend API
        Returns: (success, message)
        """
        try:
            response = requests.post(
                f'{self.api_url}/users/forgot-password/',
                json={'email': email},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get('message', 'Password reset link sent to your email')
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Failed to send reset email')
                
        except Exception as e:
            return False, f'Forgot password error: {str(e)}'
    
    def reset_password(self, token, new_password):
        """
        Reset password with token via backend API
        Returns: (success, message)
        """
        try:
            response = requests.post(
                f'{self.api_url}/users/reset-password/',
                json={
                    'token': token,
                    'new_password': new_password,
                    'confirm_password': new_password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, 'Password reset successful'
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Invalid or expired reset token')
                
        except Exception as e:
            return False, f'Password reset error: {str(e)}'
    
    def refresh_access_token(self, refresh_token):
        """
        Refresh access token using refresh token
        Returns: (success, new_access_token/error_message)
        """
        try:
            response = requests.post(
                f'{self.api_url}/token/refresh/',
                json={'refresh': refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get('access')
            else:
                return False, 'Failed to refresh token'
                
        except Exception as e:
            return False, f'Token refresh error: {str(e)}'
    
    # Two-Factor Authentication (2FA) methods
    
    def setup_2fa(self, access_token):
        """
        Setup 2FA - Generate secret and QR code
        Returns: (success, data/error_message)
        """
        try:
            response = requests.post(
                f'{self.api_url}/users/2fa/setup/',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Failed to setup 2FA')
                
        except Exception as e:
            return False, f'2FA setup error: {str(e)}'
    
    def verify_2fa_setup(self, access_token, secret, code):
        """
        Verify 2FA setup with code
        Returns: (success, message)
        """
        try:
            response = requests.post(
                f'{self.api_url}/users/2fa/verify-setup/',
                headers={'Authorization': f'Bearer {access_token}'},
                json={'secret': secret, 'code': code},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, 'Two-factor authentication enabled successfully'
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Invalid verification code')
                
        except Exception as e:
            return False, f'2FA verification error: {str(e)}'
    
    def disable_2fa(self, access_token, password):
        """
        Disable 2FA
        Returns: (success, message)
        """
        try:
            response = requests.post(
                f'{self.api_url}/users/2fa/disable/',
                headers={'Authorization': f'Bearer {access_token}'},
                json={'password': password},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, 'Two-factor authentication disabled successfully'
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Failed to disable 2FA')
                
        except Exception as e:
            return False, f'2FA disable error: {str(e)}'
    
    def check_2fa_status(self, access_token):
        """
        Check if 2FA is enabled
        Returns: (success, is_enabled/error_message)
        """
        try:
            response = requests.get(
                f'{self.api_url}/users/2fa/status/',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get('two_factor_enabled', False)
            else:
                return False, 'Failed to check 2FA status'
                
        except Exception as e:
            return False, f'2FA status check error: {str(e)}'


# Session helper functions

def save_user_session(request, user_data, tokens):
    """Save user data and tokens in session"""
    request.session['user'] = user_data
    request.session['access_token'] = tokens['access']
    request.session['refresh_token'] = tokens['refresh']
    request.session['is_authenticated'] = True
    request.session.modified = True


def clear_user_session(request):
    """Clear user session"""
    request.session.flush()


def get_current_user(request):
    """Get current authenticated user from session"""
    if request.session.get('is_authenticated'):
        return request.session.get('user')
    return None


def is_authenticated(request):
    """Check if user is authenticated"""
    return request.session.get('is_authenticated', False)


def get_access_token(request):
    """Get access token from session"""
    return request.session.get('access_token')


def get_refresh_token(request):
    """Get refresh token from session"""
    return request.session.get('refresh_token')


def ensure_valid_token(request):
    """
    Ensure access token is valid, refresh if needed
    Returns: (valid, access_token/error_message)
    """
    access_token = get_access_token(request)
    refresh_token = get_refresh_token(request)
    
    if not access_token or not refresh_token:
        return False, 'Not authenticated'
    
    # Try to refresh token
    backend = APIAuthBackend()
    success, new_access_token = backend.refresh_access_token(refresh_token)
    
    if success:
        request.session['access_token'] = new_access_token
        request.session.modified = True
        return True, new_access_token
    else:
        # Refresh failed, user needs to login again
        clear_user_session(request)
        return False, 'Session expired, please login again'


# Decorator for protecting views
def api_login_required(view_func):
    """
    Decorator to require API authentication
    Similar to @login_required but for API-based auth
    """
    def wrapper(request, *args, **kwargs):
        if not is_authenticated(request):
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.warning(request, 'Please login to access this page.')
            return redirect('login')
        
        # Ensure token is valid
        valid, result = ensure_valid_token(request)
        if not valid:
            from django.shortcuts import redirect
            from django.contrib import messages
            clear_user_session(request)
            messages.warning(request, result)
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
