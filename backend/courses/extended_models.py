"""
Extended Course-related models for MongoDB
Includes: Module, Lesson, Quiz, ExerciseTemplate, GeneratedExercise,
Submission, Discussion, Comment, Progress
"""
from datetime import datetime
from bson import ObjectId
from config.mongodb import get_collection


class Module:
    """Module model - Grouping of lessons within a course"""
    
    COLLECTION_NAME = 'modules'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.course_id = kwargs.get('course_id')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description', '')
        self.order = kwargs.get('order', 0)  # Order within course
        self.duration_minutes = kwargs.get('duration_minutes', 0)
        self.is_published = kwargs.get('is_published', False)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(Module.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create module"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_id(cls, module_id):
        """Find module by ID"""
        collection = cls.get_collection()
        if isinstance(module_id, str):
            module_id = ObjectId(module_id)
        module_data = collection.find_one({'_id': module_id})
        return cls(**module_data) if module_data else None
    
    @classmethod
    def find_by_course(cls, course_id):
        """Find modules by course"""
        collection = cls.get_collection()
        # Keep course_id as string since it's stored as string in the database
        if isinstance(course_id, ObjectId):
            course_id = str(course_id)
        modules_data = collection.find({'course_id': course_id}).sort('order', 1)
        return [cls(**module) for module in modules_data]
    
    def update(self, **kwargs):
        """Update module"""
        collection = self.get_collection()
        kwargs['updated_at'] = datetime.utcnow()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def delete(self):
        """Delete module"""
        collection = self.get_collection()
        collection.delete_one({'_id': self.id})
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'course_id': str(self.course_id),
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'duration_minutes': self.duration_minutes,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Lesson:
    """Lesson model - Multimodal content (video, text, quiz, etc.)"""
    
    COLLECTION_NAME = 'lessons'
    
    CONTENT_TYPES = ['video', 'text', 'quiz', 'exercise', 'assignment', 'resource']
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.module_id = kwargs.get('module_id')
        self.course_id = kwargs.get('course_id')  # For direct reference
        self.title = kwargs.get('title')
        self.description = kwargs.get('description', '')
        self.content_type = kwargs.get('content_type', 'text')
        self.content = kwargs.get('content', {})  # {video_url, text_content, etc.}
        self.order = kwargs.get('order', 0)
        self.duration_minutes = kwargs.get('duration_minutes', 0)
        self.is_free_preview = kwargs.get('is_free_preview', False)
        self.is_published = kwargs.get('is_published', False)
        self.resources = kwargs.get('resources', [])  # Downloadable files
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(Lesson.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create lesson"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_id(cls, lesson_id):
        """Find lesson by ID"""
        collection = cls.get_collection()
        if isinstance(lesson_id, str):
            lesson_id = ObjectId(lesson_id)
        lesson_data = collection.find_one({'_id': lesson_id})
        return cls(**lesson_data) if lesson_data else None
    
    @classmethod
    def find_by_module(cls, module_id):
        """Find lessons by module"""
        collection = cls.get_collection()
        # Keep module_id as string since it's stored as string in the database
        if isinstance(module_id, ObjectId):
            module_id = str(module_id)
        lessons_data = collection.find({'module_id': module_id}).sort('order', 1)
        return [cls(**lesson) for lesson in lessons_data]
    
    @classmethod
    def find_by_course(cls, course_id):
        """Find all lessons in a course"""
        collection = cls.get_collection()
        # Keep course_id as string since it's stored as string in the database
        if isinstance(course_id, ObjectId):
            course_id = str(course_id)
        lessons_data = collection.find({'course_id': course_id}).sort('order', 1)
        return [cls(**lesson) for lesson in lessons_data]
    
    def update(self, **kwargs):
        """Update lesson"""
        collection = self.get_collection()
        kwargs['updated_at'] = datetime.utcnow()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def delete(self):
        """Delete lesson"""
        collection = self.get_collection()
        collection.delete_one({'_id': self.id})
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'module_id': str(self.module_id) if self.module_id else None,
            'course_id': str(self.course_id) if self.course_id else None,
            'title': self.title,
            'description': self.description,
            'content_type': self.content_type,
            'content': self.content,
            'order': self.order,
            'duration_minutes': self.duration_minutes,
            'is_free_preview': self.is_free_preview,
            'is_published': self.is_published,
            'resources': self.resources,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Quiz:
    """Quiz model - Assessment questionnaire"""
    
    COLLECTION_NAME = 'quizzes'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.lesson_id = kwargs.get('lesson_id')
        self.course_id = kwargs.get('course_id')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description', '')
        self.questions = kwargs.get('questions', [])  # List of question objects
        self.passing_score = kwargs.get('passing_score', 70)  # Percentage
        self.time_limit_minutes = kwargs.get('time_limit_minutes', 0)  # 0 = no limit
        self.max_attempts = kwargs.get('max_attempts', 0)  # 0 = unlimited
        self.shuffle_questions = kwargs.get('shuffle_questions', False)
        self.show_correct_answers = kwargs.get('show_correct_answers', True)
        self.is_published = kwargs.get('is_published', False)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(Quiz.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create quiz"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_id(cls, quiz_id):
        """Find quiz by ID"""
        collection = cls.get_collection()
        if isinstance(quiz_id, str):
            quiz_id = ObjectId(quiz_id)
        quiz_data = collection.find_one({'_id': quiz_id})
        return cls(**quiz_data) if quiz_data else None
    
    @classmethod
    def find_by_lesson(cls, lesson_id):
        """Find quiz by lesson"""
        collection = cls.get_collection()
        if isinstance(lesson_id, str):
            lesson_id = ObjectId(lesson_id)
        quiz_data = collection.find_one({'lesson_id': lesson_id})
        return cls(**quiz_data) if quiz_data else None
    
    def update(self, **kwargs):
        """Update quiz"""
        collection = self.get_collection()
        kwargs['updated_at'] = datetime.utcnow()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def delete(self):
        """Delete quiz"""
        collection = self.get_collection()
        collection.delete_one({'_id': self.id})
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'lesson_id': str(self.lesson_id) if self.lesson_id else None,
            'course_id': str(self.course_id) if self.course_id else None,
            'title': self.title,
            'description': self.description,
            'questions': self.questions,
            'passing_score': self.passing_score,
            'time_limit_minutes': self.time_limit_minutes,
            'max_attempts': self.max_attempts,
            'shuffle_questions': self.shuffle_questions,
            'show_correct_answers': self.show_correct_answers,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ExerciseTemplate:
    """Exercise Template - Pattern for automatic exercise generation"""
    
    COLLECTION_NAME = 'exercise_templates'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.course_id = kwargs.get('course_id')
        self.lesson_id = kwargs.get('lesson_id')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description', '')
        self.template_type = kwargs.get('template_type', 'code')  # code, math, text, etc.
        self.difficulty = kwargs.get('difficulty', 'medium')
        self.template_data = kwargs.get('template_data', {})  # Template structure
        self.variables = kwargs.get('variables', [])  # Dynamic variables
        self.solution_template = kwargs.get('solution_template', '')
        self.test_cases = kwargs.get('test_cases', [])
        self.hints = kwargs.get('hints', [])
        self.tags = kwargs.get('tags', [])
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(ExerciseTemplate.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create exercise template"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_id(cls, template_id):
        """Find template by ID"""
        collection = cls.get_collection()
        if isinstance(template_id, str):
            template_id = ObjectId(template_id)
        template_data = collection.find_one({'_id': template_id})
        return cls(**template_data) if template_data else None
    
    @classmethod
    def find_by_lesson(cls, lesson_id):
        """Find templates by lesson"""
        collection = cls.get_collection()
        if isinstance(lesson_id, str):
            lesson_id = ObjectId(lesson_id)
        templates_data = collection.find({'lesson_id': lesson_id})
        return [cls(**template) for template in templates_data]
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'course_id': str(self.course_id) if self.course_id else None,
            'lesson_id': str(self.lesson_id) if self.lesson_id else None,
            'title': self.title,
            'description': self.description,
            'template_type': self.template_type,
            'difficulty': self.difficulty,
            'template_data': self.template_data,
            'variables': self.variables,
            'solution_template': self.solution_template,
            'test_cases': self.test_cases,
            'hints': self.hints,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class GeneratedExercise:
    """Generated Exercise - Unique instance of an exercise from template"""
    
    COLLECTION_NAME = 'generated_exercises'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.template_id = kwargs.get('template_id')
        self.student_id = kwargs.get('student_id')
        self.course_id = kwargs.get('course_id')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description', '')
        self.exercise_data = kwargs.get('exercise_data', {})  # Generated content
        self.solution = kwargs.get('solution', '')
        self.test_cases = kwargs.get('test_cases', [])
        self.hints_used = kwargs.get('hints_used', [])
        self.status = kwargs.get('status', 'not_started')  # not_started, in_progress, submitted, graded
        self.score = kwargs.get('score', 0)
        self.max_score = kwargs.get('max_score', 100)
        self.generated_at = kwargs.get('generated_at', datetime.utcnow())
        self.submitted_at = kwargs.get('submitted_at')
        self.graded_at = kwargs.get('graded_at')
    
    @staticmethod
    def get_collection():
        return get_collection(GeneratedExercise.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create generated exercise"""
        collection = cls.get_collection()
        kwargs['generated_at'] = datetime.utcnow()
        kwargs['status'] = 'not_started'
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_student(cls, student_id, course_id=None):
        """Find exercises by student"""
        collection = cls.get_collection()
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        query = {'student_id': student_id}
        if course_id:
            if isinstance(course_id, str):
                course_id = ObjectId(course_id)
            query['course_id'] = course_id
        exercises_data = collection.find(query).sort('generated_at', -1)
        return [cls(**exercise) for exercise in exercises_data]
    
    def update(self, **kwargs):
        """Update generated exercise"""
        collection = self.get_collection()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'template_id': str(self.template_id) if self.template_id else None,
            'student_id': str(self.student_id) if self.student_id else None,
            'course_id': str(self.course_id) if self.course_id else None,
            'title': self.title,
            'description': self.description,
            'exercise_data': self.exercise_data,
            'solution': self.solution,
            'test_cases': self.test_cases,
            'hints_used': self.hints_used,
            'status': self.status,
            'score': self.score,
            'max_score': self.max_score,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
        }


class Submission:
    """Submission - Student's submitted work"""
    
    COLLECTION_NAME = 'submissions'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.student_id = kwargs.get('student_id')
        self.course_id = kwargs.get('course_id')
        self.lesson_id = kwargs.get('lesson_id')
        self.exercise_id = kwargs.get('exercise_id')  # Can be quiz or generated exercise
        self.submission_type = kwargs.get('submission_type', 'assignment')  # assignment, quiz, exercise
        self.content = kwargs.get('content', {})  # Submitted content
        self.files = kwargs.get('files', [])  # Uploaded files
        self.status = kwargs.get('status', 'submitted')  # submitted, graded, returned
        self.score = kwargs.get('score', 0)
        self.max_score = kwargs.get('max_score', 100)
        self.feedback = kwargs.get('feedback', '')
        self.graded_by = kwargs.get('graded_by')  # Instructor ID
        self.submitted_at = kwargs.get('submitted_at', datetime.utcnow())
        self.graded_at = kwargs.get('graded_at')
    
    @staticmethod
    def get_collection():
        return get_collection(Submission.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create submission"""
        collection = cls.get_collection()
        kwargs['submitted_at'] = datetime.utcnow()
        kwargs['status'] = 'submitted'
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_student(cls, student_id, course_id=None):
        """Find submissions by student"""
        collection = cls.get_collection()
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        query = {'student_id': student_id}
        if course_id:
            if isinstance(course_id, str):
                course_id = ObjectId(course_id)
            query['course_id'] = course_id
        submissions_data = collection.find(query).sort('submitted_at', -1)
        return [cls(**submission) for submission in submissions_data]
    
    def update(self, **kwargs):
        """Update submission"""
        collection = self.get_collection()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'student_id': str(self.student_id) if self.student_id else None,
            'course_id': str(self.course_id) if self.course_id else None,
            'lesson_id': str(self.lesson_id) if self.lesson_id else None,
            'exercise_id': str(self.exercise_id) if self.exercise_id else None,
            'submission_type': self.submission_type,
            'content': self.content,
            'files': self.files,
            'status': self.status,
            'score': self.score,
            'max_score': self.max_score,
            'feedback': self.feedback,
            'graded_by': str(self.graded_by) if self.graded_by else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
        }


class Discussion:
    """Discussion - Thread for course/lesson discussions"""
    
    COLLECTION_NAME = 'discussions'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.course_id = kwargs.get('course_id')
        self.lesson_id = kwargs.get('lesson_id')  # Optional - can be course-wide
        self.author_id = kwargs.get('author_id')  # User who started discussion
        self.title = kwargs.get('title')
        self.content = kwargs.get('content', '')
        self.tags = kwargs.get('tags', [])
        self.is_pinned = kwargs.get('is_pinned', False)
        self.is_resolved = kwargs.get('is_resolved', False)
        self.views_count = kwargs.get('views_count', 0)
        self.comments_count = kwargs.get('comments_count', 0)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(Discussion.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create discussion"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        kwargs['views_count'] = 0
        kwargs['comments_count'] = 0
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_course(cls, course_id, lesson_id=None):
        """Find discussions by course"""
        collection = cls.get_collection()
        if isinstance(course_id, str):
            course_id = ObjectId(course_id)
        query = {'course_id': course_id}
        if lesson_id:
            if isinstance(lesson_id, str):
                lesson_id = ObjectId(lesson_id)
            query['lesson_id'] = lesson_id
        discussions_data = collection.find(query).sort('created_at', -1)
        return [cls(**discussion) for discussion in discussions_data]
    
    def update(self, **kwargs):
        """Update discussion"""
        collection = self.get_collection()
        kwargs['updated_at'] = datetime.utcnow()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def delete(self):
        """Delete discussion"""
        collection = self.get_collection()
        collection.delete_one({'_id': self.id})
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'course_id': str(self.course_id) if self.course_id else None,
            'lesson_id': str(self.lesson_id) if self.lesson_id else None,
            'author_id': str(self.author_id) if self.author_id else None,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'is_pinned': self.is_pinned,
            'is_resolved': self.is_resolved,
            'views_count': self.views_count,
            'comments_count': self.comments_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Comment:
    """Comment - Message in a discussion thread"""
    
    COLLECTION_NAME = 'comments'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.discussion_id = kwargs.get('discussion_id')
        self.author_id = kwargs.get('author_id')
        self.content = kwargs.get('content')
        self.parent_comment_id = kwargs.get('parent_comment_id')  # For nested replies
        self.is_instructor = kwargs.get('is_instructor', False)
        self.is_accepted_answer = kwargs.get('is_accepted_answer', False)
        self.likes_count = kwargs.get('likes_count', 0)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(Comment.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create comment"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        kwargs['likes_count'] = 0
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        
        # Increment comments count in discussion
        discussions_collection = get_collection('discussions')
        discussions_collection.update_one(
            {'_id': ObjectId(kwargs['discussion_id']) if isinstance(kwargs['discussion_id'], str) else kwargs['discussion_id']},
            {'$inc': {'comments_count': 1}}
        )
        
        return cls(**kwargs)
    
    @classmethod
    def find_by_discussion(cls, discussion_id):
        """Find comments by discussion"""
        collection = cls.get_collection()
        if isinstance(discussion_id, str):
            discussion_id = ObjectId(discussion_id)
        comments_data = collection.find({'discussion_id': discussion_id}).sort('created_at', 1)
        return [cls(**comment) for comment in comments_data]
    
    def update(self, **kwargs):
        """Update comment"""
        collection = self.get_collection()
        kwargs['updated_at'] = datetime.utcnow()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def delete(self):
        """Delete comment"""
        collection = self.get_collection()
        collection.delete_one({'_id': self.id})
        
        # Decrement comments count in discussion
        discussions_collection = get_collection('discussions')
        discussions_collection.update_one(
            {'_id': self.discussion_id},
            {'$inc': {'comments_count': -1}}
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'discussion_id': str(self.discussion_id) if self.discussion_id else None,
            'author_id': str(self.author_id) if self.author_id else None,
            'content': self.content,
            'parent_comment_id': str(self.parent_comment_id) if self.parent_comment_id else None,
            'is_instructor': self.is_instructor,
            'is_accepted_answer': self.is_accepted_answer,
            'likes_count': self.likes_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Progress:
    """Progress - Track student progress in courses"""
    
    COLLECTION_NAME = 'progress'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.student_id = kwargs.get('student_id')
        self.course_id = kwargs.get('course_id')
        self.lesson_id = kwargs.get('lesson_id')
        self.completed = kwargs.get('completed', False)
        self.completed_at = kwargs.get('completed_at')
        self.time_spent_minutes = kwargs.get('time_spent_minutes', 0)
        self.last_position = kwargs.get('last_position', 0)  # For video timestamp
        self.notes = kwargs.get('notes', '')
        self.bookmarked = kwargs.get('bookmarked', False)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(Progress.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create progress record"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_one(cls, student_id, lesson_id):
        """Find progress for a specific student and lesson"""
        collection = cls.get_collection()
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        if isinstance(lesson_id, str):
            lesson_id = ObjectId(lesson_id)
        progress_data = collection.find_one({
            'student_id': student_id,
            'lesson_id': lesson_id
        })
        return cls(**progress_data) if progress_data else None
    
    @classmethod
    def find_by_student_course(cls, student_id, course_id):
        """Find all progress for a student in a course"""
        collection = cls.get_collection()
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        if isinstance(course_id, str):
            course_id = ObjectId(course_id)
        progress_data = collection.find({
            'student_id': student_id,
            'course_id': course_id
        })
        return [cls(**progress) for progress in progress_data]
    
    def update(self, **kwargs):
        """Update progress"""
        collection = self.get_collection()
        kwargs['updated_at'] = datetime.utcnow()
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'student_id': str(self.student_id) if self.student_id else None,
            'course_id': str(self.course_id) if self.course_id else None,
            'lesson_id': str(self.lesson_id) if self.lesson_id else None,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_spent_minutes': self.time_spent_minutes,
            'last_position': self.last_position,
            'notes': self.notes,
            'bookmarked': self.bookmarked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
