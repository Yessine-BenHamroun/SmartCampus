"""
User MongoDB Model
"""
from datetime import datetime
from bson import ObjectId
import bcrypt
from config.mongodb import get_collection


class User:
    """User model for MongoDB"""
    
    COLLECTION_NAME = 'users'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.email = kwargs.get('email')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.phone = kwargs.get('phone', '')
        self.role = kwargs.get('role', 'student')  # student, instructor, admin
        self.is_active = kwargs.get('is_active', True)
        self.is_verified = kwargs.get('is_verified', False)
        self.profile_image = kwargs.get('profile_image', '')
        self.bio = kwargs.get('bio', '')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.last_login = kwargs.get('last_login')
        self.reset_password_token = kwargs.get('reset_password_token')
        self.reset_password_expires = kwargs.get('reset_password_expires')
    
    @staticmethod
    def get_collection():
        """Get users collection"""
        return get_collection(User.COLLECTION_NAME)
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify password against hashed password"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @classmethod
    def create(cls, **kwargs):
        """Create a new user"""
        collection = cls.get_collection()
        
        # Hash password before saving
        if 'password' in kwargs:
            kwargs['password'] = cls.hash_password(kwargs['password'])
        
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        kwargs['is_active'] = kwargs.get('is_active', True)
        kwargs['is_verified'] = kwargs.get('is_verified', False)
        kwargs['role'] = kwargs.get('role', 'student')
        
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_data = collection.find_one({'_id': user_id})
        return cls(**user_data) if user_data else None
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        collection = cls.get_collection()
        user_data = collection.find_one({'email': email})
        return cls(**user_data) if user_data else None
    
    @classmethod
    def find_by_username(cls, username):
        """Find user by username"""
        collection = cls.get_collection()
        user_data = collection.find_one({'username': username})
        return cls(**user_data) if user_data else None
    
    @classmethod
    def find_by_reset_token(cls, token):
        """Find user by password reset token"""
        collection = cls.get_collection()
        user_data = collection.find_one({
            'reset_password_token': token,
            'reset_password_expires': {'$gt': datetime.utcnow()}
        })
        return cls(**user_data) if user_data else None
    
    def update(self, **kwargs):
        """Update user"""
        collection = self.get_collection()
        kwargs['updated_at'] = datetime.utcnow()
        
        # Hash password if it's being updated
        if 'password' in kwargs:
            kwargs['password'] = self.hash_password(kwargs['password'])
        
        collection.update_one(
            {'_id': self.id},
            {'$set': kwargs}
        )
        
        # Update current instance
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def delete(self):
        """Delete user"""
        collection = self.get_collection()
        collection.delete_one({'_id': self.id})
    
    def to_dict(self, include_password=False):
        """Convert user to dictionary"""
        user_dict = {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'profile_image': self.profile_image,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
        
        if include_password:
            user_dict['password'] = self.password
        
        return user_dict
