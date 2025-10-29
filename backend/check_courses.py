from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['smartcampus_db']

courses = list(db.courses.find())
print(f'Total courses in DB: {len(courses)}')
print()

for course in courses:
    print(f'Course: {course.get("title")}')
    print(f'  instructor_id: {course.get("instructor_id")}')
    print(f'  thumbnail_image: {course.get("thumbnail_image")}')
    print(f'  preview_video: {course.get("preview_video")}')
    print(f'  category: {course.get("category")}')
    print(f'  is_published: {course.get("is_published")}')
    print(f'  _id: {course.get("_id")}')
    print()
