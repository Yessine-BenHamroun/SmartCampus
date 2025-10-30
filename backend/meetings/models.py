"""
Meeting MongoDB Models
Gestion des réunions vidéo avec Jitsi Meet
"""
from datetime import datetime, timedelta
from bson import ObjectId
import uuid
from config.mongodb import get_collection


class Meeting:
    """Meeting model for MongoDB"""
    
    COLLECTION_NAME = 'meetings'
    
    # Status enum
    STATUS_SCHEDULED = 'scheduled'
    STATUS_ONGOING = 'ongoing'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUSES = [STATUS_SCHEDULED, STATUS_ONGOING, STATUS_COMPLETED, STATUS_CANCELLED]
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.meeting_id = kwargs.get('meeting_id', str(uuid.uuid4()))
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.instructor_id = kwargs.get('instructor_id')  # ObjectId of instructor
        self.instructor_email = kwargs.get('instructor_email', '')
        self.scheduled_date = kwargs.get('scheduled_date')
        self.duration = kwargs.get('duration', 60)  # minutes
        self.meeting_link = kwargs.get('meeting_link', f'https://meet.jit.si/SmartCampus-{self.meeting_id}')
        status = kwargs.get('status', self.STATUS_SCHEDULED)
        self.status = status if status in self.STATUSES else self.STATUS_SCHEDULED
        self.started_at = kwargs.get('started_at')
        self.ended_at = kwargs.get('ended_at')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        """Get meetings collection"""
        return get_collection(Meeting.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create a new meeting"""
        print("\n" + "="*80)
        print("🟡 MONGODB MODEL: Creating new meeting")
        print("="*80)
        
        collection = cls.get_collection()
        
        # Generate meeting_id if not provided
        if 'meeting_id' not in kwargs:
            kwargs['meeting_id'] = str(uuid.uuid4())
        
        # Generate meeting link
        kwargs['meeting_link'] = f"https://meet.jit.si/SmartCampus-{kwargs['meeting_id']}"
        
        # Set timestamps
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        kwargs['status'] = kwargs.get('status', cls.STATUS_SCHEDULED)
        
        # Convert instructor_id to ObjectId if string
        if 'instructor_id' in kwargs and isinstance(kwargs['instructor_id'], str):
            kwargs['instructor_id'] = ObjectId(kwargs['instructor_id'])
        
        # Convert scheduled_date to datetime if string
        if 'scheduled_date' in kwargs and isinstance(kwargs['scheduled_date'], str):
            kwargs['scheduled_date'] = datetime.fromisoformat(kwargs['scheduled_date'].replace('Z', '+00:00'))
        
        print(f"📝 Meeting data:")
        print(f"   Title: {kwargs.get('title')}")
        print(f"   Instructor ID: {kwargs.get('instructor_id')}")
        print(f"   Scheduled: {kwargs.get('scheduled_date')}")
        print(f"   Duration: {kwargs.get('duration')} minutes")
        print(f"   Meeting Link: {kwargs.get('meeting_link')}")
        
        result = collection.insert_one(kwargs)
        print(f"✅ Meeting created with ID: {result.inserted_id}")
        print("="*80)
        
        return result.inserted_id
    
    @classmethod
    def find_by_id(cls, meeting_id):
        """Find meeting by ID"""
        collection = cls.get_collection()
        if isinstance(meeting_id, str):
            meeting_id = ObjectId(meeting_id)
        return collection.find_one({'_id': meeting_id})
    
    @classmethod
    def find_by_instructor(cls, instructor_id):
        """Find all meetings by instructor"""
        collection = cls.get_collection()
        if isinstance(instructor_id, str):
            instructor_id = ObjectId(instructor_id)
        return list(collection.find({'instructor_id': instructor_id}).sort('scheduled_date', -1))
    
    @classmethod
    def update(cls, meeting_id, **kwargs):
        """Update meeting"""
        collection = cls.get_collection()
        if isinstance(meeting_id, str):
            meeting_id = ObjectId(meeting_id)
        
        kwargs['updated_at'] = datetime.utcnow()
        
        # Convert scheduled_date if provided
        if 'scheduled_date' in kwargs and isinstance(kwargs['scheduled_date'], str):
            kwargs['scheduled_date'] = datetime.fromisoformat(kwargs['scheduled_date'].replace('Z', '+00:00'))
        
        result = collection.update_one(
            {'_id': meeting_id},
            {'$set': kwargs}
        )
        return result.modified_count > 0
    
    @classmethod
    def delete(cls, meeting_id):
        """Delete meeting (soft delete by setting status to cancelled)"""
        return cls.update(meeting_id, status=cls.STATUS_CANCELLED)
    
    @classmethod
    def start_meeting(cls, meeting_id):
        """Start a meeting"""
        return cls.update(
            meeting_id,
            status=cls.STATUS_ONGOING,
            started_at=datetime.utcnow()
        )
    
    @classmethod
    def end_meeting(cls, meeting_id):
        """End a meeting"""
        return cls.update(
            meeting_id,
            status=cls.STATUS_COMPLETED,
            ended_at=datetime.utcnow()
        )


class MeetingParticipant:
    """Meeting participant model for MongoDB"""
    
    COLLECTION_NAME = 'meeting_participants'
    
    # Status enum
    STATUS_INVITED = 'invited'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    STATUS_ATTENDED = 'attended'
    STATUS_ABSENT = 'absent'
    STATUSES = [STATUS_INVITED, STATUS_ACCEPTED, STATUS_DECLINED, STATUS_ATTENDED, STATUS_ABSENT]
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.meeting_id = kwargs.get('meeting_id')  # ObjectId
        self.student_id = kwargs.get('student_id')  # ObjectId
        self.student_email = kwargs.get('student_email', '')
        status = kwargs.get('status', self.STATUS_INVITED)
        self.status = status if status in self.STATUSES else self.STATUS_INVITED
        self.joined_at = kwargs.get('joined_at')
        self.left_at = kwargs.get('left_at')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        """Get meeting participants collection"""
        return get_collection(MeetingParticipant.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Add a participant to a meeting"""
        collection = cls.get_collection()
        
        # Convert IDs to ObjectId if string
        if 'meeting_id' in kwargs and isinstance(kwargs['meeting_id'], str):
            kwargs['meeting_id'] = ObjectId(kwargs['meeting_id'])
        if 'student_id' in kwargs and isinstance(kwargs['student_id'], str):
            kwargs['student_id'] = ObjectId(kwargs['student_id'])
        
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        kwargs['status'] = kwargs.get('status', cls.STATUS_INVITED)
        
        # Check if already exists
        existing = collection.find_one({
            'meeting_id': kwargs['meeting_id'],
            'student_id': kwargs['student_id']
        })
        
        if existing:
            print(f"⚠️  Participant already exists for this meeting")
            return existing['_id']
        
        result = collection.insert_one(kwargs)
        print(f"✅ Participant added: {kwargs.get('student_email')}")
        return result.inserted_id
    
    @classmethod
    def find_by_meeting(cls, meeting_id):
        """Find all participants for a meeting"""
        collection = cls.get_collection()
        if isinstance(meeting_id, str):
            meeting_id = ObjectId(meeting_id)
        return list(collection.find({'meeting_id': meeting_id}))
    
    @classmethod
    def find_by_student(cls, student_id):
        """Find all meetings for a student"""
        collection = cls.get_collection()
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        return list(collection.find({'student_id': student_id}).sort('created_at', -1))
    
    @classmethod
    def update_status(cls, meeting_id, student_id, status, **kwargs):
        """Update participant status"""
        collection = cls.get_collection()
        
        if isinstance(meeting_id, str):
            meeting_id = ObjectId(meeting_id)
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        
        update_data = {'status': status, 'updated_at': datetime.utcnow()}
        update_data.update(kwargs)
        
        result = collection.update_one(
            {'meeting_id': meeting_id, 'student_id': student_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @classmethod
    def mark_attended(cls, meeting_id, student_id):
        """Mark participant as attended"""
        return cls.update_status(
            meeting_id,
            student_id,
            cls.STATUS_ATTENDED,
            joined_at=datetime.utcnow()
        )
    
    @classmethod
    def mark_left(cls, meeting_id, student_id):
        """Mark participant as left"""
        collection = cls.get_collection()
        
        if isinstance(meeting_id, str):
            meeting_id = ObjectId(meeting_id)
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        
        result = collection.update_one(
            {'meeting_id': meeting_id, 'student_id': student_id},
            {'$set': {'left_at': datetime.utcnow(), 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    @classmethod
    def get_duration(cls, meeting_id, student_id):
        """Calculate participant's duration in meeting"""
        collection = cls.get_collection()
        
        if isinstance(meeting_id, str):
            meeting_id = ObjectId(meeting_id)
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        
        participant = collection.find_one({
            'meeting_id': meeting_id,
            'student_id': student_id
        })
        
        if participant and participant.get('joined_at') and participant.get('left_at'):
            duration = participant['left_at'] - participant['joined_at']
            return int(duration.total_seconds() / 60)  # minutes
        
        return 0
