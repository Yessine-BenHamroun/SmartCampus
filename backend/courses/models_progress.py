"""
Progress tracking models for SmartCampus
Tracks student progress through courses, lessons, quizzes, and assignments
"""
from datetime import datetime
from bson import ObjectId
from config.mongodb import get_database

db = get_database()


class StudentProgress:
    """Track student progress in a course"""
    collection = db['student_progress']
    
    def __init__(self, student_id, course_id, enrollment_id, 
                 lessons_completed=None, quizzes_completed=None, 
                 assignments_completed=None, completion_percentage=0.0,
                 last_accessed=None, time_spent_minutes=0, 
                 created_at=None, updated_at=None, _id=None):
        self._id = _id
        self.student_id = ObjectId(student_id) if student_id else None
        self.course_id = ObjectId(course_id) if course_id else None
        self.enrollment_id = ObjectId(enrollment_id) if enrollment_id else None
        self.lessons_completed = lessons_completed or []  # List of lesson IDs
        self.quizzes_completed = quizzes_completed or []  # List of quiz IDs with scores
        self.assignments_completed = assignments_completed or []  # List of assignment IDs with scores
        self.completion_percentage = completion_percentage
        self.last_accessed = last_accessed or datetime.utcnow()
        self.time_spent_minutes = time_spent_minutes
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            '_id': str(self._id) if self._id else None,
            'student_id': str(self.student_id),
            'course_id': str(self.course_id),
            'enrollment_id': str(self.enrollment_id),
            'lessons_completed': [str(lid) for lid in self.lessons_completed],
            'quizzes_completed': self.quizzes_completed,
            'assignments_completed': self.assignments_completed,
            'completion_percentage': self.completion_percentage,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'time_spent_minutes': self.time_spent_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create(cls, **kwargs):
        """Create new progress record"""
        progress = cls(**kwargs)
        result = cls.collection.insert_one({
            'student_id': progress.student_id,
            'course_id': progress.course_id,
            'enrollment_id': progress.enrollment_id,
            'lessons_completed': progress.lessons_completed,
            'quizzes_completed': progress.quizzes_completed,
            'assignments_completed': progress.assignments_completed,
            'completion_percentage': progress.completion_percentage,
            'last_accessed': progress.last_accessed,
            'time_spent_minutes': progress.time_spent_minutes,
            'created_at': progress.created_at,
            'updated_at': progress.updated_at
        })
        progress._id = result.inserted_id
        return progress
    
    @classmethod
    def find_by_student_and_course(cls, student_id, course_id):
        """Find progress by student and course"""
        data = cls.collection.find_one({
            'student_id': ObjectId(student_id),
            'course_id': ObjectId(course_id)
        })
        return cls(**data) if data else None
    
    @classmethod
    def find_by_student(cls, student_id):
        """Get all progress records for a student"""
        cursor = cls.collection.find({'student_id': ObjectId(student_id)})
        return [cls(**data) for data in cursor]
    
    def update(self, **kwargs):
        """Update progress"""
        kwargs['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': self._id},
            {'$set': kwargs}
        )
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def mark_lesson_complete(self, lesson_id):
        """Mark a lesson as completed"""
        lesson_id_str = str(lesson_id)
        if lesson_id_str not in self.lessons_completed:
            self.lessons_completed.append(lesson_id_str)
            self.update(lessons_completed=self.lessons_completed)
    
    def mark_quiz_complete(self, quiz_id, score, passed):
        """Mark a quiz as completed with score"""
        quiz_entry = {
            'quiz_id': str(quiz_id),
            'score': score,
            'passed': passed,
            'completed_at': datetime.utcnow().isoformat()
        }
        # Update if exists, otherwise append
        found = False
        for i, q in enumerate(self.quizzes_completed):
            if q['quiz_id'] == str(quiz_id):
                self.quizzes_completed[i] = quiz_entry
                found = True
                break
        if not found:
            self.quizzes_completed.append(quiz_entry)
        self.update(quizzes_completed=self.quizzes_completed)
    
    def mark_assignment_complete(self, assignment_id, score, passed):
        """Mark an assignment as completed with score"""
        assignment_entry = {
            'assignment_id': str(assignment_id),
            'score': score,
            'passed': passed,
            'completed_at': datetime.utcnow().isoformat()
        }
        # Update if exists, otherwise append
        found = False
        for i, a in enumerate(self.assignments_completed):
            if a['assignment_id'] == str(assignment_id):
                self.assignments_completed[i] = assignment_entry
                found = True
                break
        if not found:
            self.assignments_completed.append(assignment_entry)
        self.update(assignments_completed=self.assignments_completed)
    
    def calculate_completion_percentage(self, total_lessons, total_quizzes, total_assignments):
        """Calculate overall completion percentage"""
        total_items = total_lessons + total_quizzes + total_assignments
        if total_items == 0:
            return 0.0
        
        completed_items = (
            len(self.lessons_completed) + 
            len(self.quizzes_completed) + 
            len(self.assignments_completed)
        )
        
        percentage = (completed_items / total_items) * 100
        self.update(completion_percentage=round(percentage, 2))
        return self.completion_percentage


class CourseReview:
    """Student reviews and ratings for courses"""
    collection = db['course_reviews']
    
    def __init__(self, student_id, course_id, rating, review_text="",
                 would_recommend=True, created_at=None, updated_at=None, _id=None):
        self._id = _id
        self.student_id = ObjectId(student_id) if student_id else None
        self.course_id = ObjectId(course_id) if course_id else None
        self.rating = rating  # 1-5 stars
        self.review_text = review_text
        self.would_recommend = would_recommend
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            '_id': str(self._id) if self._id else None,
            'student_id': str(self.student_id),
            'course_id': str(self.course_id),
            'rating': self.rating,
            'review_text': self.review_text,
            'would_recommend': self.would_recommend,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create(cls, **kwargs):
        """Create new review"""
        review = cls(**kwargs)
        result = cls.collection.insert_one({
            'student_id': review.student_id,
            'course_id': review.course_id,
            'rating': review.rating,
            'review_text': review.review_text,
            'would_recommend': review.would_recommend,
            'created_at': review.created_at,
            'updated_at': review.updated_at
        })
        review._id = result.inserted_id
        return review
    
    @classmethod
    def find_by_course(cls, course_id):
        """Get all reviews for a course"""
        cursor = cls.collection.find({'course_id': ObjectId(course_id)})
        return [cls(**data) for data in cursor]
    
    @classmethod
    def find_by_student_and_course(cls, student_id, course_id):
        """Check if student already reviewed this course"""
        data = cls.collection.find_one({
            'student_id': ObjectId(student_id),
            'course_id': ObjectId(course_id)
        })
        return cls(**data) if data else None
    
    @classmethod
    def get_course_average_rating(cls, course_id):
        """Calculate average rating for a course"""
        pipeline = [
            {'$match': {'course_id': ObjectId(course_id)}},
            {'$group': {
                '_id': '$course_id',
                'average_rating': {'$avg': '$rating'},
                'total_reviews': {'$sum': 1}
            }}
        ]
        result = list(cls.collection.aggregate(pipeline))
        if result:
            return {
                'average_rating': round(result[0]['average_rating'], 2),
                'total_reviews': result[0]['total_reviews']
            }
        return {'average_rating': 0, 'total_reviews': 0}
    
    def update(self, **kwargs):
        """Update review"""
        kwargs['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': self._id},
            {'$set': kwargs}
        )
        for key, value in kwargs.items():
            setattr(self, key, value)


class InstructorReview:
    """Student reviews and ratings for instructors"""
    collection = db['instructor_reviews']
    
    def __init__(self, student_id, instructor_id, course_id, rating,
                 review_text="", teaching_quality=0, communication=0,
                 course_content=0, created_at=None, updated_at=None, _id=None):
        self._id = _id
        self.student_id = ObjectId(student_id) if student_id else None
        self.instructor_id = ObjectId(instructor_id) if instructor_id else None
        self.course_id = ObjectId(course_id) if course_id else None
        self.rating = rating  # Overall 1-5 stars
        self.review_text = review_text
        # Detailed ratings
        self.teaching_quality = teaching_quality  # 1-5
        self.communication = communication  # 1-5
        self.course_content = course_content  # 1-5
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            '_id': str(self._id) if self._id else None,
            'student_id': str(self.student_id),
            'instructor_id': str(self.instructor_id),
            'course_id': str(self.course_id),
            'rating': self.rating,
            'review_text': self.review_text,
            'teaching_quality': self.teaching_quality,
            'communication': self.communication,
            'course_content': self.course_content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create(cls, **kwargs):
        """Create new instructor review"""
        review = cls(**kwargs)
        result = cls.collection.insert_one({
            'student_id': review.student_id,
            'instructor_id': review.instructor_id,
            'course_id': review.course_id,
            'rating': review.rating,
            'review_text': review.review_text,
            'teaching_quality': review.teaching_quality,
            'communication': review.communication,
            'course_content': review.course_content,
            'created_at': review.created_at,
            'updated_at': review.updated_at
        })
        review._id = result.inserted_id
        return review
    
    @classmethod
    def find_by_instructor(cls, instructor_id):
        """Get all reviews for an instructor"""
        cursor = cls.collection.find({'instructor_id': ObjectId(instructor_id)})
        return [cls(**data) for data in cursor]
    
    @classmethod
    def find_by_student_and_instructor(cls, student_id, instructor_id, course_id):
        """Check if student already reviewed this instructor for this course"""
        data = cls.collection.find_one({
            'student_id': ObjectId(student_id),
            'instructor_id': ObjectId(instructor_id),
            'course_id': ObjectId(course_id)
        })
        return cls(**data) if data else None
    
    @classmethod
    def get_instructor_average_rating(cls, instructor_id):
        """Calculate average rating for an instructor"""
        pipeline = [
            {'$match': {'instructor_id': ObjectId(instructor_id)}},
            {'$group': {
                '_id': '$instructor_id',
                'average_rating': {'$avg': '$rating'},
                'average_teaching_quality': {'$avg': '$teaching_quality'},
                'average_communication': {'$avg': '$communication'},
                'average_course_content': {'$avg': '$course_content'},
                'total_reviews': {'$sum': 1}
            }}
        ]
        result = list(cls.collection.aggregate(pipeline))
        if result:
            return {
                'average_rating': round(result[0]['average_rating'], 2),
                'average_teaching_quality': round(result[0]['average_teaching_quality'], 2),
                'average_communication': round(result[0]['average_communication'], 2),
                'average_course_content': round(result[0]['average_course_content'], 2),
                'total_reviews': result[0]['total_reviews']
            }
        return {
            'average_rating': 0,
            'average_teaching_quality': 0,
            'average_communication': 0,
            'average_course_content': 0,
            'total_reviews': 0
        }
    
    def update(self, **kwargs):
        """Update review"""
        kwargs['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': self._id},
            {'$set': kwargs}
        )
        for key, value in kwargs.items():
            setattr(self, key, value)
