from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['smartcampus_db']

# Get all modules
modules = list(db.modules.find())
print(f'Total modules in DB: {len(modules)}')
print()

for module in modules:
    print(f'Module: {module.get("title")}')
    print(f'  course_id: {module.get("course_id")} (type: {type(module.get("course_id"))})')
    print(f'  order: {module.get("order")}')
    print(f'  _id: {module.get("_id")}')
    print()

# Get a course ID to test
course = db.courses.find_one()
if course:
    course_id = str(course['_id'])
    print(f'\nLooking for modules with course_id = "{course_id}"')
    matching_modules = list(db.modules.find({'course_id': course_id}))
    print(f'Found {len(matching_modules)} modules')
