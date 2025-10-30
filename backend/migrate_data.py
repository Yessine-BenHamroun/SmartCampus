"""
Migrate data from smartcampus_db to smartcampus database
"""
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Source and destination databases
source_db = client['smartcampus_db']
dest_db = client['smartcampus']

print("=" * 60)
print("🔄 MIGRATING DATA FROM smartcampus_db TO smartcampus")
print("=" * 60)

# Collections to migrate
collections_to_migrate = ['courses', 'certifications', 'certification_steps']

for collection_name in collections_to_migrate:
    source_collection = source_db[collection_name]
    dest_collection = dest_db[collection_name]
    
    # Get all documents from source
    documents = list(source_collection.find())
    
    if documents:
        print(f"\n📦 Migrating {collection_name}...")
        print(f"   Found {len(documents)} documents")
        
        # Clear existing data in destination (optional - comment out if you want to keep existing)
        dest_collection.delete_many({})
        print(f"   Cleared existing data in destination")
        
        # Insert documents into destination
        dest_collection.insert_many(documents)
        print(f"   ✅ Migrated {len(documents)} documents to smartcampus.{collection_name}")
    else:
        print(f"\n⚠️  No documents found in {collection_name}")

print("\n" + "=" * 60)
print("✅ MIGRATION COMPLETE!")
print("=" * 60)

# Verify migration
print("\n📊 Verification:")
for collection_name in collections_to_migrate:
    count = dest_db[collection_name].count_documents({})
    print(f"   smartcampus.{collection_name}: {count} documents")

print("\n✨ You can now view all data in MongoDB Compass under 'smartcampus' database!")
