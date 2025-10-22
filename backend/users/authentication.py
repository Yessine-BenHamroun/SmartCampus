"""
Custom JWT Authentication Backend
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that works with MongoDB User model"""
    
    def get_user(self, validated_token):
        """Get user from MongoDB using the user_id in the token"""
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Token contained no recognizable user identification')
            
            user = User.find_by_id(user_id)
            
            if not user:
                raise AuthenticationFailed('User not found')
            
            if not user.is_active:
                raise AuthenticationFailed('User is inactive')
            
            # Return a dictionary with user info for request.user
            return {
                'user_id': str(user.id),
                'email': user.email,
                'username': user.username,
                'role': user.role,
            }
            
        except Exception as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')
