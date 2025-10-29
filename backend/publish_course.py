from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['smartcampus_db']

# Get the first course
course = db.courses.find_one()

if course:
    # Update it to published
    result = db.courses.update_one(
        {'_id': course['_id']},
        {'$set': {'published': True}}
    )
    print(f"✅ Updated course '{course['title']}' to published")
    print(f"   Course ID: {course['_id']}")
else:
    print("❌ No courses found in database")
