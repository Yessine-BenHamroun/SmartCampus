"""
Course and related models for MongoDB
"""
from datetime import datetime
from bson import ObjectId
from config.mongodb import get_collection


class Course:
    """Course model"""
    
    COLLECTION_NAME = 'courses'
    
    DIFFICULTY_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    CATEGORIES = ['Web Development', 'Data Science', 'Mobile Development', 'Design', 
                  'Business', 'Marketing', 'IT & Software', 'Personal Development']
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description')
        self.short_description = kwargs.get('short_description', '')
        self.instructor_id = kwargs.get('instructor_id')  # Reference to User
        self.category = kwargs.get('category')
        # Support both 'level' (from DB) and 'difficulty_level' (legacy)
        self.difficulty_level = kwargs.get('level') or kwargs.get('difficulty_level', 'Beginner')
        self.level = self.difficulty_level  # Alias for consistency
        self.price = kwargs.get('price', 0.0)
        self.discount_price = kwargs.get('discount_price')
        self.duration_hours = kwargs.get('duration_hours', 0)
        # Support both 'thumbnail' (from DB) and 'thumbnail_image' (legacy)
        self.thumbnail = kwargs.get('thumbnail', '')
        self.thumbnail_image = self.thumbnail  # Alias for backward compatibility
        self.preview_video = kwargs.get('preview_video', '')
        self.syllabus = kwargs.get('syllabus', [])  # List of modules/lessons
        self.requirements = kwargs.get('requirements', [])
        self.learning_outcomes = kwargs.get('learning_outcomes', [])
        self.language = kwargs.get('language', 'English')
        self.enrolled_count = kwargs.get('enrolled_count', 0)
        self.rating = kwargs.get('rating', 0.0)
        self.reviews_count = kwargs.get('reviews_count', 0)
        # Support both 'published' (from DB) and 'is_published' (legacy)
        self.published = kwargs.get('published', False)
        self.is_published = self.published  # Alias for consistency
        self.is_featured = kwargs.get('is_featured', False)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(Course.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create a new course"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        kwargs['enrolled_count'] = 0
        kwargs['rating'] = 0.0
        kwargs['reviews_count'] = 0
        
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_id(cls, course_id):
        """Find course by ID"""
        collection = cls.get_collection()
        if isinstance(course_id, str):
            course_id = ObjectId(course_id)
        course_data = collection.find_one({'_id': course_id})
        return cls(**course_data) if course_data else None
    
    @classmethod
    def find_all(cls, filters=None, skip=0, limit=20):
        """Find all courses with filters"""
        collection = cls.get_collection()
        query = filters or {}
        courses_data = collection.find(query).skip(skip).limit(limit).sort('created_at', -1)
        return [cls(**course) for course in courses_data]
    
    @classmethod
    def find_by_instructor(cls, instructor_id):
        """Find courses by instructor"""
        collection = cls.get_collection()
        # Keep instructor_id as string since it's stored as string in the database
        instructor_id = str(instructor_id)
        courses_data = collection.find({'instructor_id': instructor_id})
        return [cls(**course) for course in courses_data]
    
    @classmethod
    def find_featured(cls, limit=6):
        """Find featured courses"""
        collection = cls.get_collection()
        courses_data = collection.find({'is_featured': True, 'is_published': True}).limit(limit)
        return [cls(**course) for course in courses_data]
    
    def update(self, **kwargs):
        """Update course"""
        collection = self.get_collection()
        kwargs['updated_at'] = datetime.utcnow()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def delete(self):
        """Delete course"""
        collection = self.get_collection()
        collection.delete_one({'_id': self.id})
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'short_description': self.short_description,
            'instructor_id': str(self.instructor_id) if self.instructor_id else None,
            'category': self.category,
            'difficulty_level': self.difficulty_level,
            'level': self.level,  # Include both field names
            'price': float(self.price),
            'discount_price': float(self.discount_price) if self.discount_price else None,
            'duration_hours': self.duration_hours,
            'thumbnail': self.thumbnail,  # Primary field name
            'thumbnail_image': self.thumbnail_image,  # Alias for compatibility
            'preview_video': self.preview_video,
            'syllabus': self.syllabus,
            'requirements': self.requirements,
            'learning_outcomes': self.learning_outcomes,
            'language': self.language,
            'enrolled_count': self.enrolled_count,
            'rating': float(self.rating),
            'reviews_count': self.reviews_count,
            'published': self.published,  # Primary field name
            'is_published': self.is_published,  # Alias for compatibility
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Enrollment:
    """Enrollment model - tracks student enrollments"""
    
    COLLECTION_NAME = 'enrollments'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.student_id = kwargs.get('student_id')
        self.course_id = kwargs.get('course_id')
        self.enrolled_at = kwargs.get('enrolled_at', datetime.utcnow())
        self.progress = kwargs.get('progress', 0.0)  # 0-100%
        self.completed = kwargs.get('completed', False)
        self.completed_at = kwargs.get('completed_at')
        self.last_accessed = kwargs.get('last_accessed')
        self.certificate_issued = kwargs.get('certificate_issued', False)
    
    @staticmethod
    def get_collection():
        return get_collection(Enrollment.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create enrollment"""
        collection = cls.get_collection()
        kwargs['enrolled_at'] = datetime.utcnow()
        kwargs['progress'] = 0.0
        kwargs['completed'] = False
        
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_student(cls, student_id):
        """Find enrollments by student"""
        collection = cls.get_collection()
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        enrollments_data = collection.find({'student_id': student_id})
        return [cls(**enrollment) for enrollment in enrollments_data]
    
    @classmethod
    def find_by_course(cls, course_id):
        """Find enrollments by course"""
        collection = cls.get_collection()
        if isinstance(course_id, str):
            course_id = ObjectId(course_id)
        enrollments_data = collection.find({'course_id': course_id})
        return [cls(**enrollment) for enrollment in enrollments_data]
    
    @classmethod
    def find_one(cls, student_id, course_id):
        """Check if student is enrolled in course"""
        collection = cls.get_collection()
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        if isinstance(course_id, str):
            course_id = ObjectId(course_id)
        enrollment_data = collection.find_one({
            'student_id': student_id,
            'course_id': course_id
        })
        return cls(**enrollment_data) if enrollment_data else None
    
    def update(self, **kwargs):
        """Update enrollment"""
        collection = self.get_collection()
        kwargs['last_accessed'] = datetime.utcnow()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'student_id': str(self.student_id),
            'course_id': str(self.course_id),
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'progress': float(self.progress),
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'certificate_issued': self.certificate_issued,
        }


class Review:
    """Course review model"""
    
    COLLECTION_NAME = 'reviews'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.course_id = kwargs.get('course_id')
        self.student_id = kwargs.get('student_id')
        self.rating = kwargs.get('rating', 5)  # 1-5
        self.comment = kwargs.get('comment', '')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(Review.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create review"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_course(cls, course_id):
        """Find reviews by course"""
        collection = cls.get_collection()
        if isinstance(course_id, str):
            course_id = ObjectId(course_id)
        reviews_data = collection.find({'course_id': course_id}).sort('created_at', -1)
        return [cls(**review) for review in reviews_data]
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'course_id': str(self.course_id),
            'student_id': str(self.student_id),
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
