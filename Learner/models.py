from django.db import models
from pymongo import MongoClient
from django.conf import settings

# MongoDB connection helper (global client cache)
_mongo_client = None

def get_db():
    """Get MongoDB database connection"""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.MONGODB_SETTINGS['host'])
    
    db_name = settings.MONGODB_SETTINGS['db_name']
    return _mongo_client[db_name]

# Example: Working with MongoDB collections
# You can use this in your views like:
# from learner.models import get_db
# db = get_db()
# courses = db.courses.find()

# For Django admin and authentication, standard Django models will work
# Example Django model (stored in SQLite):
class UserProfile(models.Model):
    """Example model for user profiles - stored in SQLite"""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"

# MongoDB collections are accessed directly through pymongo
# Example usage in views.py:
# from .models import get_db
# db = get_db()
# 
# # Insert a course
# db.courses.insert_one({
#     'title': 'Python Programming',
#     'description': 'Learn Python',
#     'instructor': 'John Doe',
#     'price': 99.99
# })
#
# # Query courses
# courses = list(db.courses.find())

