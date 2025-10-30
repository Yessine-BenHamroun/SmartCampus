"""
Context processors for making user data available in templates
"""
from .api_auth import get_current_user, is_authenticated


def api_auth_context(request):
    """
    Add API authentication context to all templates
    This replaces Django's default auth context
    """
    user = get_current_user(request) if is_authenticated(request) else None
    
    # Create a user object that behaves like Django's User
    class APIUser:
        def __init__(self, user_data):
            if user_data:
                # Extract ID - handle both 'id' and '_id' fields, dict and string formats
                raw_id = user_data.get('id') or user_data.get('_id')
                if isinstance(raw_id, dict):
                    self.id = raw_id.get('$oid')
                else:
                    self.id = raw_id
                
                self.username = user_data.get('username', '')
                self.email = user_data.get('email', '')
                self.first_name = user_data.get('first_name', '')
                self.last_name = user_data.get('last_name', '')
                self.is_authenticated = True
                self.is_active = user_data.get('is_active', True)
                self.role = user_data.get('role', 'student')
                self.profile_image = user_data.get('profile_image', '')
                self.bio = user_data.get('bio', '')
                self.phone = user_data.get('phone', '')
            else:
                self.is_authenticated = False
        
        def __bool__(self):
            return self.is_authenticated
        
        def __str__(self):
            return self.username if self.is_authenticated else 'AnonymousUser'
    
    return {
        'user': APIUser(user),
    }
