"""
Test script to verify MongoDB authentication migration
Run this after starting both servers to test the new auth system
"""
import requests
import json

BACKEND_URL = 'http://localhost:8001/api'
FRONTEND_URL = 'http://localhost:8000'

def test_backend_api():
    """Test if backend API is running and responsive"""
    print("\n" + "="*80)
    print("🧪 TESTING BACKEND API")
    print("="*80)
    
    try:
        # Test registration
        print("\n1️⃣  Testing user registration...")
        test_user = {
            'username': 'testuser',
            'email': 'test@smartcampus.com',
            'password': 'Test123!@#',
            'confirm_password': 'Test123!@#',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = requests.post(f'{BACKEND_URL}/users/register/', json=test_user, timeout=5)
        
        if response.status_code == 201:
            print("   ✅ Registration successful!")
            data = response.json()
            tokens = data.get('tokens')
            print(f"   📧 Email: {test_user['email']}")
            print(f"   🔑 Access Token: {tokens['access'][:50]}...")
            print(f"   🔄 Refresh Token: {tokens['refresh'][:50]}...")
            return tokens
        elif response.status_code == 400:
            # User might already exist, try login
            print("   ⚠️  User might already exist, trying login...")
            return test_login(test_user['email'], test_user['password'])
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend API!")
        print("   💡 Make sure backend is running: cd backend && python manage.py runserver 8001")
        return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None


def test_login(email, password):
    """Test login"""
    print("\n2️⃣  Testing user login...")
    try:
        response = requests.post(
            f'{BACKEND_URL}/users/login/',
            json={'email': email, 'password': password},
            timeout=5
        )
        
        if response.status_code == 200:
            print("   ✅ Login successful!")
            data = response.json()
            tokens = data.get('tokens')
            user = data.get('user')
            print(f"   👤 Username: {user.get('username')}")
            print(f"   📧 Email: {user.get('email')}")
            print(f"   🔑 Access Token: {tokens['access'][:50]}...")
            return tokens
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None


def test_profile(access_token):
    """Test profile retrieval"""
    print("\n3️⃣  Testing profile retrieval...")
    try:
        response = requests.get(
            f'{BACKEND_URL}/users/profile/',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=5
        )
        
        if response.status_code == 200:
            print("   ✅ Profile retrieved successfully!")
            user = response.json().get('user')
            print(f"   👤 Username: {user.get('username')}")
            print(f"   📧 Email: {user.get('email')}")
            print(f"   📝 Role: {user.get('role')}")
            print(f"   ✅ Active: {user.get('is_active')}")
            return True
        else:
            print(f"   ❌ Profile retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def test_frontend():
    """Test if frontend is running"""
    print("\n" + "="*80)
    print("🌐 TESTING FRONTEND")
    print("="*80)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("\n✅ Frontend is running!")
            print(f"   🌐 URL: {FRONTEND_URL}")
            print(f"   📄 Homepage loaded successfully")
            return True
        else:
            print(f"\n⚠️  Frontend returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to frontend!")
        print("   💡 Make sure frontend is running: python manage.py runserver 8000")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def check_mongodb():
    """Check if MongoDB is accessible"""
    print("\n" + "="*80)
    print("🗄️  CHECKING MONGODB")
    print("="*80)
    
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
        client.server_info()
        print("\n✅ MongoDB is running!")
        
        # Check database
        db = client['smartcampus_db']
        users_count = db.users.count_documents({})
        print(f"   📊 Database: smartcampus_db")
        print(f"   👥 Users in database: {users_count}")
        
        return True
    except Exception as e:
        print("\n❌ MongoDB connection failed!")
        print(f"   Error: {str(e)}")
        print("   💡 Make sure MongoDB is running: net start MongoDB")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 SMARTCAMPUS MONGODB AUTHENTICATION TEST")
    print("="*80)
    
    # Check MongoDB first
    if not check_mongodb():
        print("\n⚠️  MongoDB must be running before proceeding!")
        return
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Test backend API
    tokens = test_backend_api()
    
    if tokens:
        access_token = tokens.get('access')
        test_profile(access_token)
    
    # Final summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    print(f"\n{'✅' if check_mongodb() else '❌'} MongoDB Connection")
    print(f"{'✅' if frontend_ok else '❌'} Frontend Server")
    print(f"{'✅' if tokens else '❌'} Backend API & Authentication")
    
    if all([check_mongodb(), frontend_ok, tokens]):
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        print("\n✅ Your SmartCampus is ready to use with MongoDB authentication!")
        print(f"\n🌐 Visit: {FRONTEND_URL}")
        print("   • Register a new account")
        print("   • Login with your credentials")
        print("   • View your profile")
        print("\n🔍 Check MongoDB to see your user data:")
        print("   use smartcampus_db")
        print("   db.users.find().pretty()")
    else:
        print("\n" + "="*80)
        print("⚠️  SOME TESTS FAILED")
        print("="*80)
        print("\n💡 Make sure both servers are running:")
        print(f"   Frontend: {FRONTEND_URL}")
        print(f"   Backend:  {BACKEND_URL}")
    
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    main()
