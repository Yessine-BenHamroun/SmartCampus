"""
Management command to initialize MongoDB collections for all course models
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING, TEXT
from pymongo.errors import CollectionInvalid


class Command(BaseCommand):
    help = 'Initialize MongoDB collections with indexes for course models'

    def handle(self, *args, **options):
        # Connect to MongoDB
        mongo_uri = settings.MONGODB_SETTINGS['host']
        db_name = settings.MONGODB_SETTINGS['db_name']
        
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        self.stdout.write(self.style.SUCCESS(f'\n🔗 Connected to MongoDB: {db_name}\n'))
        
        # Define collections with their indexes
        collections_config = {
            'courses': [
                IndexModel([('instructor_id', ASCENDING)]),
                IndexModel([('category', ASCENDING)]),
                IndexModel([('level', ASCENDING)]),
                IndexModel([('published', ASCENDING)]),
                IndexModel([('title', TEXT), ('description', TEXT)]),
                IndexModel([('created_at', DESCENDING)]),
            ],
            'enrollments': [
                IndexModel([('student_id', ASCENDING)]),
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('student_id', ASCENDING), ('course_id', ASCENDING)], unique=True),
                IndexModel([('enrolled_at', DESCENDING)]),
            ],
            'reviews': [
                IndexModel([('student_id', ASCENDING)]),
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('student_id', ASCENDING), ('course_id', ASCENDING)], unique=True),
                IndexModel([('rating', DESCENDING)]),
            ],
            'modules': [
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('course_id', ASCENDING), ('order', ASCENDING)]),
                IndexModel([('published', ASCENDING)]),
            ],
            'lessons': [
                IndexModel([('module_id', ASCENDING)]),
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('module_id', ASCENDING), ('order', ASCENDING)]),
                IndexModel([('lesson_type', ASCENDING)]),
                IndexModel([('published', ASCENDING)]),
            ],
            'quizzes': [
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('lesson_id', ASCENDING)]),
                IndexModel([('created_at', DESCENDING)]),
            ],
            'exercise_templates': [
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('lesson_id', ASCENDING)]),
                IndexModel([('difficulty', ASCENDING)]),
            ],
            'generated_exercises': [
                IndexModel([('template_id', ASCENDING)]),
                IndexModel([('student_id', ASCENDING)]),
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('student_id', ASCENDING), ('template_id', ASCENDING)]),
            ],
            'submissions': [
                IndexModel([('student_id', ASCENDING)]),
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('lesson_id', ASCENDING)]),
                IndexModel([('exercise_id', ASCENDING)]),
                IndexModel([('quiz_id', ASCENDING)]),
                IndexModel([('status', ASCENDING)]),
                IndexModel([('submitted_at', DESCENDING)]),
                IndexModel([('student_id', ASCENDING), ('status', ASCENDING)]),
            ],
            'discussions': [
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('lesson_id', ASCENDING)]),
                IndexModel([('author_id', ASCENDING)]),
                IndexModel([('created_at', DESCENDING)]),
                IndexModel([('is_pinned', ASCENDING), ('created_at', DESCENDING)]),
                IndexModel([('title', TEXT), ('content', TEXT)]),
            ],
            'comments': [
                IndexModel([('discussion_id', ASCENDING)]),
                IndexModel([('author_id', ASCENDING)]),
                IndexModel([('parent_comment_id', ASCENDING)]),
                IndexModel([('created_at', ASCENDING)]),
            ],
            'progress': [
                IndexModel([('student_id', ASCENDING)]),
                IndexModel([('course_id', ASCENDING)]),
                IndexModel([('lesson_id', ASCENDING)]),
                IndexModel([('student_id', ASCENDING), ('course_id', ASCENDING)]),
                IndexModel([('student_id', ASCENDING), ('lesson_id', ASCENDING)], unique=True),
                IndexModel([('last_accessed', DESCENDING)]),
            ],
        }
        
        # Create collections and indexes
        created_count = 0
        updated_count = 0
        
        for collection_name, indexes in collections_config.items():
            try:
                # Create collection if it doesn't exist
                if collection_name not in db.list_collection_names():
                    db.create_collection(collection_name)
                    self.stdout.write(self.style.SUCCESS(f'✅ Created collection: {collection_name}'))
                    created_count += 1
                else:
                    self.stdout.write(f'   Collection already exists: {collection_name}')
                
                # Create indexes
                collection = db[collection_name]
                if indexes:
                    collection.create_indexes(indexes)
                    self.stdout.write(self.style.WARNING(f'   📑 Created {len(indexes)} indexes for {collection_name}'))
                    updated_count += 1
                    
            except CollectionInvalid:
                self.stdout.write(self.style.WARNING(f'⚠️  Collection already exists: {collection_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error creating {collection_name}: {str(e)}'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n📊 Summary:'))
        self.stdout.write(self.style.SUCCESS(f'   • New collections created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'   • Collections with indexes: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'   • Total collections: {len(db.list_collection_names())}'))
        
        # List all collections
        self.stdout.write(self.style.SUCCESS(f'\n📚 All collections in database:'))
        for coll in sorted(db.list_collection_names()):
            count = db[coll].count_documents({})
            self.stdout.write(f'   • {coll}: {count} documents')
        
        self.stdout.write(self.style.SUCCESS(f'\n✨ MongoDB initialization complete!\n'))
        
        client.close()
