"""
User authentication views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import secrets

from users.models import User
from users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)


class RegisterView(APIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        print("\n" + "="*80)
        print("🟢 BACKEND API: Received registration request")
        print("="*80)
        print(f"📥 Request Data: {request.data}")
        
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            try:
                # Create user
                user_data = serializer.validated_data.copy()
                user_data.pop('confirm_password')
                
                print(f"📝 Creating user with data: {user_data}")
                user = User.create(**user_data)
                print(f"✅ User created successfully!")
                print(f"💾 MongoDB User ID: {user.id}")
                print(f"📧 Email: {user.email}")
                print(f"👤 Username: {user.username}")
                print(f"🗄️  Database: smartcampus_db")
                print(f"📊 Collection: users")
                
                # Generate JWT tokens
                refresh = RefreshToken()
                refresh['user_id'] = str(user.id)
                refresh['email'] = user.email
                
                print(f"🔑 JWT tokens generated")
                print("="*80 + "\n")
                
                return Response({
                    'message': 'User registered successfully',
                    'user': user.to_dict(),
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                print(f"❌ ERROR creating user: {str(e)}")
                print("="*80 + "\n")
                return Response({
                    'error': 'Registration failed',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"❌ Serializer validation FAILED: {serializer.errors}")
        print("="*80 + "\n")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        print("\n" + "="*80)
        print("🟢 BACKEND API: Received login request")
        print("="*80)
        print(f"📥 Request Data: {request.data}")
        
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            print(f"✅ Serializer validation passed")
            print(f"📧 Email: {email}")
            print(f"🔐 Password: {'*' * len(password)}")
            print(f"🔍 Searching for user in MongoDB...")
            
            # Find user
            user = User.find_by_email(email)
            
            if not user:
                print(f"❌ User NOT FOUND with email: {email}")
                print(f"💡 Make sure you're using the EMAIL address, not username")
                print("="*80 + "\n")
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            print(f"✅ User FOUND!")
            print(f"👤 Username: {user.username}")
            print(f"📧 Email: {user.email}")
            print(f"💾 User ID: {user.id}")
            print(f"🔐 Verifying password...")
            
            # Verify password
            if not User.verify_password(password, user.password):
                print(f"❌ Password verification FAILED!")
                print(f"💡 The password provided does not match the hashed password in database")
                print("="*80 + "\n")
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            print(f"✅ Password verified successfully!")
            
            # Check if user is active
            if not user.is_active:
                print(f"❌ User account is DEACTIVATED")
                print("="*80 + "\n")
                return Response({
                    'error': 'Account is deactivated'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Update last login
            print(f"✅ User is active!")
            print(f"🔄 Updating last login timestamp...")
            user.update(last_login=datetime.utcnow())
            
            # Generate JWT tokens
            print(f"🔑 Generating JWT tokens...")
            refresh = RefreshToken()
            refresh['user_email'] = user.email  # Use email as identifier
            refresh['user_id'] = str(user.id)  # Keep user_id as string for reference
            refresh['username'] = user.username
            
            print(f"✅ SUCCESS: Login completed!")
            print(f"🔑 Access Token: {str(refresh.access_token)[:50]}...")
            print("="*80 + "\n")
            
            return Response({
                'message': 'Login successful',
                'user': user.to_dict(),
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        print(f"❌ Serializer validation FAILED: {serializer.errors}")
        print("="*80 + "\n")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Logout failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(APIView):
    """Custom token refresh view for MongoDB users"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response({
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify and decode the refresh token
            token = RefreshToken(refresh_token)
            
            # Get user email from token
            user_email = token.get('user_email')
            
            if not user_email:
                return Response({
                    'error': 'Invalid token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Find user in MongoDB
            user = User.find_by_email(user_email)
            
            if not user or not user.is_active:
                return Response({
                    'error': 'User not found or inactive'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate new access token
            new_token = RefreshToken()
            new_token['user_email'] = user.email
            new_token['user_id'] = str(user.id)
            new_token['username'] = user.username
            
            return Response({
                'access': str(new_token.access_token),
                'refresh': str(new_token)  # Optional: return new refresh token too
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Token refresh failed',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


class ProfileView(APIView):
    """User profile endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user profile"""
        try:
            # request.user is now an AuthenticatedUser object
            user_id = request.user.id if hasattr(request.user, 'id') else request.user.get('user_id')
            user = User.find_by_id(user_id)
            
            if not user:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'user': user.to_dict()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to fetch profile',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update user profile"""
        try:
            print("\n" + "="*80)
            print("🟢 BACKEND API: Received profile update request")
            print("="*80)
            print(f"📥 Request Data: {request.data}")
            print(f"👤 Request User: {request.user}")
            
            # request.user is now an AuthenticatedUser object
            user_id = request.user.id if hasattr(request.user, 'id') else request.user.get('user_id')
            print(f"💾 User ID: {user_id}")
            
            user = User.find_by_id(user_id)
            
            if not user:
                print(f"❌ User NOT FOUND with ID: {user_id}")
                print("="*80 + "\n")
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            print(f"✅ User FOUND: {user.username}")
            
            serializer = UserProfileSerializer(data=request.data, partial=True)
            
            if serializer.is_valid():
                print(f"✅ Serializer validation passed")
                # Update allowed fields only
                allowed_fields = ['first_name', 'last_name', 'phone', 'profile_image', 'bio']
                update_data = {k: v for k, v in serializer.validated_data.items() if k in allowed_fields}
                
                print(f"📝 Updating fields: {update_data}")
                user.update(**update_data)
                
                print(f"✅ Profile updated successfully!")
                print("="*80 + "\n")
                
                return Response({
                    'message': 'Profile updated successfully',
                    'user': user.to_dict()
                }, status=status.HTTP_200_OK)
            
            print(f"❌ Serializer validation FAILED: {serializer.errors}")
            print("="*80 + "\n")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"❌ ERROR updating profile: {str(e)}")
            print("="*80 + "\n")
            return Response({
                'error': 'Failed to update profile',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    """Change password endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # request.user is now an AuthenticatedUser object
                user_id = request.user.id if hasattr(request.user, 'id') else request.user.get('user_id')
                user = User.find_by_id(user_id)
                
                if not user:
                    return Response({
                        'error': 'User not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Verify old password
                old_password = serializer.validated_data['old_password']
                if not User.verify_password(old_password, user.password):
                    return Response({
                        'error': 'Invalid old password'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update password
                new_password = serializer.validated_data['new_password']
                user.update(password=new_password)
                
                return Response({
                    'message': 'Password changed successfully'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': 'Password change failed',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    """Forgot password endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                email = serializer.validated_data['email']
                user = User.find_by_email(email)
                
                if not user:
                    # Don't reveal if email exists or not
                    return Response({
                        'message': 'If the email exists, a password reset link will be sent'
                    }, status=status.HTTP_200_OK)
                
                # Generate reset token
                reset_token = secrets.token_urlsafe(32)
                reset_expires = datetime.utcnow() + timedelta(hours=1)
                
                user.update(
                    reset_password_token=reset_token,
                    reset_password_expires=reset_expires
                )
                
                # Send email with reset link
                reset_url = f"http://localhost:8000/reset-password?token={reset_token}"
                
                send_mail(
                    subject='Password Reset Request',
                    message=f'Click the link below to reset your password:\n\n{reset_url}\n\nThis link will expire in 1 hour.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'Password reset link sent to your email'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': 'Failed to send reset email',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """Reset password endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                token = serializer.validated_data['token']
                new_password = serializer.validated_data['new_password']
                
                # Find user by token
                user = User.find_by_reset_token(token)
                
                if not user:
                    return Response({
                        'error': 'Invalid or expired reset token'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update password and clear reset token
                user.update(
                    password=new_password,
                    reset_password_token=None,
                    reset_password_expires=None
                )
                
                return Response({
                    'message': 'Password reset successful'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': 'Password reset failed',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
