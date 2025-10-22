"""
Test script to verify MongoDB connection and User model
"""
import os
import sys
import django

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.mongodb import get_database, get_collection
from users.models import User


def test_mongodb_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB connection...")
    try:
        db = get_database()
        # Ping the database
        db.command('ping')
        print("✅ MongoDB connection successful!")
        print(f"✅ Connected to database: {db.name}")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False


def test_user_model():
    """Test User model operations"""
    print("\nTesting User model...")
    try:
        # Create a test user
        test_email = "test@example.com"
        
        # Clean up if exists
        existing_user = User.find_by_email(test_email)
        if existing_user:
            existing_user.delete()
            print("Cleaned up existing test user")
        
        # Create new user
        user = User.create(
            email=test_email,
            username="testuser",
            password="TestPass123",
            first_name="Test",
            last_name="User",
            role="student"
        )
        print(f"✅ User created: {user.email}")
        
        # Find user by email
        found_user = User.find_by_email(test_email)
        print(f"✅ User found by email: {found_user.username}")
        
        # Find user by ID
        found_by_id = User.find_by_id(user.id)
        print(f"✅ User found by ID: {found_by_id.email}")
        
        # Update user
        user.update(first_name="Updated")
        print(f"✅ User updated: {user.first_name}")
        
        # Verify password
        is_valid = User.verify_password("TestPass123", user.password)
        print(f"✅ Password verification: {is_valid}")
        
        # Convert to dict
        user_dict = user.to_dict()
        print(f"✅ User to dict: {user_dict['email']}")
        
        # Clean up
        user.delete()
        print("✅ User deleted successfully")
        
        return True
    except Exception as e:
        print(f"❌ User model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_users_collection():
    """Test users collection"""
    print("\nTesting users collection...")
    try:
        collection = get_collection('users')
        count = collection.count_documents({})
        print(f"✅ Users collection has {count} documents")
        return True
    except Exception as e:
        print(f"❌ Collection test failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("SmartCampus Backend Tests")
    print("=" * 50)
    
    # Run tests
    mongo_ok = test_mongodb_connection()
    if mongo_ok:
        users_ok = test_users_collection()
        model_ok = test_user_model()
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print("=" * 50)
        print(f"MongoDB Connection: {'✅ PASS' if mongo_ok else '❌ FAIL'}")
        print(f"Users Collection: {'✅ PASS' if users_ok else '❌ FAIL'}")
        print(f"User Model: {'✅ PASS' if model_ok else '❌ FAIL'}")
        
        if mongo_ok and users_ok and model_ok:
            print("\n🎉 All tests passed! Backend is ready.")
        else:
            print("\n⚠️ Some tests failed. Please check the errors above.")
    else:
        print("\n❌ Cannot proceed without MongoDB connection.")
        print("Make sure MongoDB is running on mongodb://localhost:27017/")
