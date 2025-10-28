"""
Script to check MongoDB users collection
This will show you exactly where your users are stored
"""
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')

print("\n" + "="*80)
print("🔍 CHECKING MONGODB DATABASES AND COLLECTIONS")
print("="*80)

# List all databases
print("\n📂 Available Databases:")
databases = client.list_database_names()
for db_name in databases:
    print(f"   - {db_name}")

# Check smartcampus_db specifically
print("\n" + "="*80)
print("🎯 SMARTCAMPUS_DB DATABASE")
print("="*80)

db = client['smartcampus_db']

# List all collections in smartcampus_db
print("\n📊 Collections in 'smartcampus_db':")
collections = db.list_collection_names()
if collections:
    for coll_name in collections:
        count = db[coll_name].count_documents({})
        print(f"   - {coll_name}: {count} documents")
else:
    print("   ⚠️  No collections found!")

# Check users collection
print("\n" + "="*80)
print("👥 USERS COLLECTION")
print("="*80)

users_collection = db['users']
user_count = users_collection.count_documents({})

print(f"\n📊 Total users in collection: {user_count}")

if user_count > 0:
    print("\n👤 Users found:")
    for user in users_collection.find():
        print(f"\n   📧 Email: {user.get('email')}")
        print(f"   👤 Username: {user.get('username')}")
        print(f"   💾 ID: {user.get('_id')}")
        print(f"   📅 Created: {user.get('created_at')}")
        print(f"   ✅ Active: {user.get('is_active')}")
        print(f"   🎓 Role: {user.get('role')}")
        print("   " + "-"*70)
else:
    print("\n⚠️  No users found in the collection!")
    print("\n🔍 Possible reasons:")
    print("   1. Users are in a different database")
    print("   2. Users are in a different collection name")
    print("   3. MongoDB connection string is different")

# Check ALL databases for 'users' collection
print("\n" + "="*80)
print("🔍 SEARCHING ALL DATABASES FOR 'users' COLLECTION")
print("="*80)

for db_name in databases:
    if db_name not in ['admin', 'config', 'local']:  # Skip system databases
        temp_db = client[db_name]
        if 'users' in temp_db.list_collection_names():
            count = temp_db['users'].count_documents({})
            print(f"\n✅ Found 'users' collection in '{db_name}' database")
            print(f"   📊 Documents: {count}")
            
            if count > 0:
                print(f"   👤 Sample user:")
                sample = temp_db['users'].find_one()
                print(f"      📧 Email: {sample.get('email')}")
                print(f"      👤 Username: {sample.get('username')}")

print("\n" + "="*80)
print("✅ SEARCH COMPLETE")
print("="*80 + "\n")

# MongoDB Compass connection string
print("🔗 MongoDB Compass Connection String:")
print("   mongodb://localhost:27017/")
print("\n📝 In MongoDB Compass:")
print("   1. Connect to: mongodb://localhost:27017/")
print("   2. Look for database: smartcampus_db")
print("   3. Look for collection: users")
print("   4. You should see 2 users there!")

client.close()
