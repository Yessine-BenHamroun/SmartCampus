"""
Two-Factor Authentication (2FA) Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import pyotp
import qrcode
import io
import base64

from users.models import User


class Setup2FAView(APIView):
    """Setup 2FA - Generate secret and QR code"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Generate new 2FA secret and QR code"""
        try:
            print("\n" + "="*80)
            print("🔐 BACKEND API: Setting up 2FA")
            print("="*80)
            
            # Get user from request
            user_id = request.user.id if hasattr(request.user, 'id') else request.user.get('user_id')
            user = User.find_by_id(user_id)
            
            if not user:
                print("❌ User not found")
                print("="*80 + "\n")
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            print(f"👤 User: {user.username}")
            
            # Generate a new secret
            secret = pyotp.random_base32()
            print(f"🔑 Generated secret: {secret}")
            
            # Create provisioning URI for QR code
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user.email,
                issuer_name='SmartCampus'
            )
            print(f"📱 TOTP URI: {totp_uri}")
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            print("✅ QR code generated")
            print("="*80 + "\n")
            
            return Response({
                'secret': secret,
                'qr_code': qr_code_base64,  # Return just the base64 string, template will add data URI prefix
                'manual_entry_key': secret
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print("="*80 + "\n")
            return Response({
                'error': 'Failed to setup 2FA',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Verify2FASetupView(APIView):
    """Verify 2FA setup with TOTP code"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Verify TOTP code and enable 2FA"""
        try:
            print("\n" + "="*80)
            print("🔐 BACKEND API: Verifying 2FA setup")
            print("="*80)
            
            # Get user from request
            user_id = request.user.id if hasattr(request.user, 'id') else request.user.get('user_id')
            user = User.find_by_id(user_id)
            
            if not user:
                print("❌ User not found")
                print("="*80 + "\n")
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            secret = request.data.get('secret')
            code = request.data.get('code')
            
            print(f"👤 User: {user.username}")
            print(f"🔑 Secret: {secret}")
            print(f"🔢 Code: {code}")
            
            if not secret or not code:
                print("❌ Missing secret or code")
                print("="*80 + "\n")
                return Response({
                    'error': 'Secret and code are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify the TOTP code
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(code, valid_window=1)
            
            if is_valid:
                print("✅ Code verified!")
                # Save the secret and enable 2FA
                user.update(
                    two_factor_secret=secret,
                    two_factor_enabled=True
                )
                print("✅ 2FA enabled for user")
                print("="*80 + "\n")
                
                return Response({
                    'message': 'Two-factor authentication enabled successfully'
                }, status=status.HTTP_200_OK)
            else:
                print("❌ Invalid code")
                print("="*80 + "\n")
                return Response({
                    'error': 'Invalid verification code'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print("="*80 + "\n")
            return Response({
                'error': 'Failed to verify 2FA',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Verify2FALoginView(APIView):
    """Verify 2FA code during login"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Verify TOTP code during login"""
        try:
            print("\n" + "="*80)
            print("🔐 BACKEND API: Verifying 2FA login")
            print("="*80)
            
            # Get user from request
            user_id = request.user.id if hasattr(request.user, 'id') else request.user.get('user_id')
            user = User.find_by_id(user_id)
            
            if not user:
                print("❌ User not found")
                print("="*80 + "\n")
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if not user.two_factor_enabled:
                print("❌ 2FA not enabled for this user")
                print("="*80 + "\n")
                return Response({
                    'error': '2FA is not enabled for this account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            code = request.data.get('code')
            print(f"👤 User: {user.username}")
            print(f"🔢 Code: {code}")
            
            if not code:
                print("❌ Missing code")
                print("="*80 + "\n")
                return Response({
                    'error': 'Verification code is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify the TOTP code
            totp = pyotp.TOTP(user.two_factor_secret)
            is_valid = totp.verify(code, valid_window=1)
            
            if is_valid:
                print("✅ Code verified!")
                print("="*80 + "\n")
                return Response({
                    'message': '2FA verification successful'
                }, status=status.HTTP_200_OK)
            else:
                print("❌ Invalid code")
                print("="*80 + "\n")
                return Response({
                    'error': 'Invalid verification code'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print("="*80 + "\n")
            return Response({
                'error': 'Failed to verify 2FA',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Disable2FAView(APIView):
    """Disable 2FA for user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Disable 2FA"""
        try:
            print("\n" + "="*80)
            print("🔐 BACKEND API: Disabling 2FA")
            print("="*80)
            
            # Get user from request
            user_id = request.user.id if hasattr(request.user, 'id') else request.user.get('user_id')
            user = User.find_by_id(user_id)
            
            if not user:
                print("❌ User not found")
                print("="*80 + "\n")
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            print(f"👤 User: {user.username}")
            
            # Verify password for security
            password = request.data.get('password')
            if not password:
                print("❌ Password required")
                print("="*80 + "\n")
                return Response({
                    'error': 'Password is required to disable 2FA'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not User.verify_password(password, user.password):
                print("❌ Invalid password")
                print("="*80 + "\n")
                return Response({
                    'error': 'Invalid password'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Disable 2FA
            user.update(
                two_factor_enabled=False,
                two_factor_secret=''
            )
            
            print("✅ 2FA disabled")
            print("="*80 + "\n")
            
            return Response({
                'message': 'Two-factor authentication disabled successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print("="*80 + "\n")
            return Response({
                'error': 'Failed to disable 2FA',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Check2FAStatusView(APIView):
    """Check if user has 2FA enabled"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check 2FA status"""
        try:
            # Get user from request
            user_id = request.user.id if hasattr(request.user, 'id') else request.user.get('user_id')
            user = User.find_by_id(user_id)
            
            if not user:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'two_factor_enabled': user.two_factor_enabled
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to check 2FA status',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
