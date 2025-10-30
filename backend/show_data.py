from pymongo import MongoClient

# Direct MongoDB connection - Using 'smartcampus_db' database
client = MongoClient('mongodb://localhost:27017/')
db = client['smartcampus_db']  # The database where your data is stored

print("=" * 50)
print("📚 COURSES")
print("=" * 50)
for course in db.courses.find():
    print(f"- ID: {course['_id']}")
    print(f"  Title: {course.get('title')}")
    print(f"  Instructor: {course.get('instructor_id')}")
    print()

print("=" * 50)
print("🏆 CERTIFICATIONS")
print("=" * 50)
for cert in db.certifications.find():
    print(f"- ID: {cert['_id']}")
    print(f"  Title: {cert.get('title')}")
    print(f"  Course ID: {cert.get('course_id')}")
    print(f"  Total Steps: {cert.get('total_steps', 0)}")
    print()

print("=" * 50)
print("📝 CERTIFICATION STEPS")
print("=" * 50)
for step in db.certification_steps.find():
    print(f"- ID: {step['_id']}")
    print(f"  Title: {step.get('title')}")
    print(f"  Certification ID: {step.get('certification_id')}")
    print(f"  Type: {step.get('step_type')}")
    print()
