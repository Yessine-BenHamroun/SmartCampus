"""
Certification Models for SmartCampus
MongoDB-based models for certifications, steps, progress tracking, and badges
"""
from datetime import datetime
from bson import ObjectId
from config.mongodb import get_database
import secrets
import string


class Certification:
    """Certification model for course certifications"""
    
    def __init__(self, course_id, instructor_id, title, description, 
                 badge_image=None, passing_score=70, _id=None, 
                 created_at=None, updated_at=None, is_active=True, total_steps=0):
        self.id = str(_id) if _id else str(ObjectId())
        self.course_id = course_id
        self.instructor_id = instructor_id
        self.title = title
        self.description = description
        self.badge_image = badge_image
        self.passing_score = passing_score
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.is_active = is_active
        self.total_steps = total_steps
    
    def to_dict(self):
        """Convert certification to dictionary"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'instructor_id': self.instructor_id,
            'title': self.title,
            'description': self.description,
            'badge_image': self.badge_image,
            'passing_score': self.passing_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'total_steps': self.total_steps
        }
    
    @staticmethod
    def create(course_id, instructor_id, title, description, **kwargs):
        """Create a new certification"""
        db = get_database()
        collection = db['certifications']
        
        certification_data = {
            '_id': ObjectId(),
            'course_id': course_id,
            'instructor_id': instructor_id,
            'title': title,
            'description': description,
            'badge_image': kwargs.get('badge_image'),
            'passing_score': kwargs.get('passing_score', 70),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': kwargs.get('is_active', True),
            'total_steps': 0
        }
        
        result = collection.insert_one(certification_data)
        certification_data['_id'] = result.inserted_id
        
        return Certification(**{k: v for k, v in certification_data.items()})
    
    @staticmethod
    def find_by_id(certification_id):
        """Find certification by ID"""
        db = get_database()
        collection = db['certifications']
        
        cert_data = collection.find_one({'_id': ObjectId(certification_id)})
        
        if cert_data:
            return Certification(**cert_data)
        return None
    
    @staticmethod
    def find_by_course(course_id):
        """Find all certifications for a course"""
        db = get_database()
        collection = db['certifications']
        
        certifications = collection.find({'course_id': course_id})
        
        return [Certification(**cert) for cert in certifications]
    
    @staticmethod
    def find_by_instructor(instructor_id):
        """Find all certifications created by an instructor"""
        db = get_database()
        collection = db['certifications']
        
        certifications = collection.find({'instructor_id': instructor_id})
        
        return [Certification(**cert) for cert in certifications]
    
    def update(self, **kwargs):
        """Update certification"""
        db = get_database()
        collection = db['certifications']
        
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        update_data['updated_at'] = datetime.utcnow()
        
        collection.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': update_data}
        )
        
        # Update instance attributes
        for key, value in update_data.items():
            setattr(self, key, value)
    
    def delete(self):
        """Delete certification"""
        db = get_database()
        collection = db['certifications']
        
        collection.delete_one({'_id': ObjectId(self.id)})


class CertificationStep:
    """Certification step model"""
    
    STEP_TYPES = ['video', 'reading', 'quiz', 'assignment', 'exam']
    
    def __init__(self, certification_id, step_number, step_type, title, 
                 description, content=None, duration_minutes=0, 
                 is_mandatory=True, passing_criteria=None, _id=None, 
                 created_at=None):
        self.id = str(_id) if _id else str(ObjectId())
        self.certification_id = certification_id
        self.step_number = step_number
        self.step_type = step_type
        self.title = title
        self.description = description
        self.content = content or {}
        self.duration_minutes = duration_minutes
        self.is_mandatory = is_mandatory
        self.passing_criteria = passing_criteria or {}
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert step to dictionary"""
        return {
            'id': self.id,
            'certification_id': self.certification_id,
            'step_number': self.step_number,
            'step_type': self.step_type,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'duration_minutes': self.duration_minutes,
            'is_mandatory': self.is_mandatory,
            'passing_criteria': self.passing_criteria,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def create(certification_id, step_number, step_type, title, description, **kwargs):
        """Create a new certification step"""
        db = get_database()
        collection = db['certification_steps']
        
        step_data = {
            '_id': ObjectId(),
            'certification_id': certification_id,
            'step_number': step_number,
            'step_type': step_type,
            'title': title,
            'description': description,
            'content': kwargs.get('content', {}),
            'duration_minutes': kwargs.get('duration_minutes', 0),
            'is_mandatory': kwargs.get('is_mandatory', True),
            'passing_criteria': kwargs.get('passing_criteria', {}),
            'created_at': datetime.utcnow()
        }
        
        result = collection.insert_one(step_data)
        step_data['_id'] = result.inserted_id
        
        # Update certification total steps
        cert_collection = db['certifications']
        cert_collection.update_one(
            {'_id': ObjectId(certification_id)},
            {'$inc': {'total_steps': 1}, '$set': {'updated_at': datetime.utcnow()}}
        )
        
        return CertificationStep(**step_data)
    
    @staticmethod
    def find_by_id(step_id):
        """Find step by ID"""
        db = get_database()
        collection = db['certification_steps']
        
        step_data = collection.find_one({'_id': ObjectId(step_id)})
        
        if step_data:
            return CertificationStep(**step_data)
        return None
    
    @staticmethod
    def find_by_certification(certification_id):
        """Find all steps for a certification"""
        db = get_database()
        collection = db['certification_steps']
        
        steps = collection.find({'certification_id': certification_id}).sort('step_number', 1)
        
        return [CertificationStep(**step) for step in steps]
    
    def update(self, **kwargs):
        """Update step"""
        db = get_database()
        collection = db['certification_steps']
        
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        collection.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': update_data}
        )
        
        # Update instance attributes
        for key, value in update_data.items():
            setattr(self, key, value)
    
    def delete(self):
        """Delete step"""
        db = get_database()
        collection = db['certification_steps']
        
        collection.delete_one({'_id': ObjectId(self.id)})
        
        # Update certification total steps
        cert_collection = db['certifications']
        cert_collection.update_one(
            {'_id': ObjectId(self.certification_id)},
            {'$inc': {'total_steps': -1}, '$set': {'updated_at': datetime.utcnow()}}
        )


class StudentProgress:
    """Student progress tracking for certifications"""
    
    STATUSES = ['not_started', 'in_progress', 'completed', 'failed']
    
    def __init__(self, student_id, certification_id, course_id, 
                 current_step=0, completed_steps=None, step_scores=None,
                 exam_attempts=0, exam_score=0, status='not_started',
                 started_at=None, completed_at=None, badge_earned=False, _id=None):
        self.id = str(_id) if _id else str(ObjectId())
        self.student_id = student_id
        self.certification_id = certification_id
        self.course_id = course_id
        self.current_step = current_step
        self.completed_steps = completed_steps or []
        self.step_scores = step_scores or {}
        self.exam_attempts = exam_attempts
        self.exam_score = exam_score
        self.status = status
        self.started_at = started_at
        self.completed_at = completed_at
        self.badge_earned = badge_earned
    
    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'certification_id': self.certification_id,
            'course_id': self.course_id,
            'current_step': self.current_step,
            'completed_steps': self.completed_steps,
            'step_scores': self.step_scores,
            'exam_attempts': self.exam_attempts,
            'exam_score': self.exam_score,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'badge_earned': self.badge_earned
        }
    
    @staticmethod
    def create(student_id, certification_id, course_id):
        """Create new student progress"""
        db = get_database()
        collection = db['student_progress']
        
        progress_data = {
            '_id': ObjectId(),
            'student_id': student_id,
            'certification_id': certification_id,
            'course_id': course_id,
            'current_step': 0,
            'completed_steps': [],
            'step_scores': {},
            'exam_attempts': 0,
            'exam_score': 0,
            'status': 'in_progress',
            'started_at': datetime.utcnow(),
            'completed_at': None,
            'badge_earned': False
        }
        
        result = collection.insert_one(progress_data)
        progress_data['_id'] = result.inserted_id
        
        return StudentProgress(**progress_data)
    
    @staticmethod
    def find_by_student_and_certification(student_id, certification_id):
        """Find progress by student and certification"""
        db = get_database()
        collection = db['student_progress']
        
        progress_data = collection.find_one({
            'student_id': student_id,
            'certification_id': certification_id
        })
        
        if progress_data:
            return StudentProgress(**progress_data)
        return None
    
    @staticmethod
    def find_by_student(student_id):
        """Find all progress records for a student"""
        db = get_database()
        collection = db['student_progress']
        
        progress_records = collection.find({'student_id': student_id})
        
        return [StudentProgress(**record) for record in progress_records]
    
    @staticmethod
    def find_by_certification(certification_id):
        """Find all student progress for a certification"""
        db = get_database()
        collection = db['student_progress']
        
        progress_records = collection.find({'certification_id': certification_id})
        
        return [StudentProgress(**record) for record in progress_records]
    
    def update(self, **kwargs):
        """Update progress"""
        db = get_database()
        collection = db['student_progress']
        
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        collection.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': update_data}
        )
        
        # Update instance attributes
        for key, value in update_data.items():
            setattr(self, key, value)
    
    def complete_step(self, step_id, score=None):
        """Mark a step as completed"""
        if step_id not in self.completed_steps:
            self.completed_steps.append(step_id)
        
        if score is not None:
            self.step_scores[step_id] = score
        
        self.current_step += 1
        
        self.update(
            completed_steps=self.completed_steps,
            step_scores=self.step_scores,
            current_step=self.current_step
        )


class EarnedBadge:
    """Earned badge model"""
    
    def __init__(self, student_id, certification_id, course_id, 
                 final_score, verification_code=None, badge_url=None,
                 earned_at=None, _id=None):
        self.id = str(_id) if _id else str(ObjectId())
        self.student_id = student_id
        self.certification_id = certification_id
        self.course_id = course_id
        self.final_score = final_score
        self.verification_code = verification_code or self._generate_verification_code()
        self.badge_url = badge_url
        self.earned_at = earned_at or datetime.utcnow()
    
    @staticmethod
    def _generate_verification_code():
        """Generate unique verification code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(12))
    
    def to_dict(self):
        """Convert badge to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'certification_id': self.certification_id,
            'course_id': self.course_id,
            'final_score': self.final_score,
            'verification_code': self.verification_code,
            'badge_url': self.badge_url,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None
        }
    
    @staticmethod
    def create(student_id, certification_id, course_id, final_score, **kwargs):
        """Create a new earned badge"""
        db = get_database()
        collection = db['earned_badges']
        
        badge_data = {
            '_id': ObjectId(),
            'student_id': student_id,
            'certification_id': certification_id,
            'course_id': course_id,
            'final_score': final_score,
            'verification_code': EarnedBadge._generate_verification_code(),
            'badge_url': kwargs.get('badge_url'),
            'earned_at': datetime.utcnow()
        }
        
        result = collection.insert_one(badge_data)
        badge_data['_id'] = result.inserted_id
        
        return EarnedBadge(**badge_data)
    
    @staticmethod
    def find_by_verification_code(code):
        """Find badge by verification code"""
        db = get_database()
        collection = db['earned_badges']
        
        badge_data = collection.find_one({'verification_code': code})
        
        if badge_data:
            return EarnedBadge(**badge_data)
        return None
    
    @staticmethod
    def find_by_student(student_id):
        """Find all badges earned by a student"""
        db = get_database()
        collection = db['earned_badges']
        
        badges = collection.find({'student_id': student_id})
        
        return [EarnedBadge(**badge) for badge in badges]
