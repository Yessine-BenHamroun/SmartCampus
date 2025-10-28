"""
Custom JWT Authentication Backend
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User


class AuthenticatedUser:
    """
    Simple user wrapper for DRF authentication
    Makes MongoDB User compatible with DRF's permission system
    """
    def __init__(self, user):
        self.user = user
        self.id = user.id
        self.email = user.email
        self.username = user.username
        self.role = user.role
        self.is_active = user.is_active
        self.is_authenticated = True
        self.is_anonymous = False
    
    def __str__(self):
        return f"AuthenticatedUser({self.username})"
    
    def __repr__(self):
        return self.__str__()


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
            
            # Return an AuthenticatedUser wrapper that's compatible with DRF
            return AuthenticatedUser(user)
            
        except Exception as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')
