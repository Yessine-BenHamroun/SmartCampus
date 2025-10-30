"""
Meeting Views - API for video conferencing system
Uses MongoDB for data storage
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from bson import ObjectId
from .models import Meeting, MeetingParticipant
from users.models import User


def serialize_meeting(meeting_doc):
    """Convert MongoDB meeting document to JSON-serializable dict"""
    if not meeting_doc:
        return None
    
    meeting_doc['id'] = str(meeting_doc['_id'])
    meeting_doc['instructor_id'] = str(meeting_doc['instructor_id'])
    
    # Convert datetime to ISO format
    for field in ['scheduled_date', 'started_at', 'ended_at', 'created_at', 'updated_at']:
        if field in meeting_doc and meeting_doc[field]:
            meeting_doc[field] = meeting_doc[field].isoformat()
    
    # Remove _id
    meeting_doc.pop('_id', None)
    
    return meeting_doc


def serialize_participant(participant_doc):
    """Convert MongoDB participant document to JSON-serializable dict"""
    if not participant_doc:
        return None
    
    participant_doc['id'] = str(participant_doc['_id'])
    participant_doc['meeting_id'] = str(participant_doc['meeting_id'])
    participant_doc['student_id'] = str(participant_doc['student_id'])
    
    # Convert datetime to ISO format
    for field in ['joined_at', 'left_at', 'created_at', 'updated_at']:
        if field in participant_doc and participant_doc[field]:
            participant_doc[field] = participant_doc[field].isoformat()
    
    # Remove _id
    participant_doc.pop('_id', None)
    
    return participant_doc


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def meeting_list(request):
    """
    GET: List all meetings for the instructor
    POST: Create a new meeting (instructors only)
    """
    user_id = request.user.get('_id')
    user_role = request.user.get('role', 'student')
    
    if request.method == 'GET':
        # Instructors see their own meetings
        if user_role == 'instructor':
            meetings = Meeting.find_by_instructor(user_id)
        else:
            # Students see their invitations
            participants = MeetingParticipant.find_by_student(user_id)
            meeting_ids = [p['meeting_id'] for p in participants]
            meetings = [Meeting.find_by_id(mid) for mid in meeting_ids]
            meetings = [m for m in meetings if m]  # Filter None values
        
        # Serialize meetings
        serialized = [serialize_meeting(m) for m in meetings]
        
        return Response({
            'success': True,
            'count': len(serialized),
            'meetings': serialized
        })
    
    elif request.method == 'POST':
        # Only instructors can create meetings
        if user_role != 'instructor':
            return Response({
                'success': False,
                'error': 'Only instructors can create meetings'
            }, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        
        # Validate required fields
        required_fields = ['title', 'scheduled_date', 'duration', 'student_ids']
        for field in required_fields:
            if field not in data:
                return Response({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate scheduled_date is in the future
        try:
            scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
            if scheduled_date <= datetime.utcnow():
                return Response({
                    'success': False,
                    'error': 'Scheduled date must be in the future'
                }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create meeting
        meeting_id = Meeting.create(
            title=data['title'],
            description=data.get('description', ''),
            instructor_id=user_id,
            instructor_email=request.user.get('email'),
            scheduled_date=scheduled_date,
            duration=int(data['duration'])
        )
        
        # Add participants
        student_ids = data.get('student_ids', [])
        for student_id in student_ids:
            # Get student info
            student = User.get_collection().find_one({'_id': ObjectId(student_id)})
            if student:
                MeetingParticipant.create(
                    meeting_id=meeting_id,
                    student_id=student_id,
                    student_email=student.get('email', '')
                )
        
        # Fetch and return created meeting
        meeting = Meeting.find_by_id(meeting_id)
        
        return Response({
            'success': True,
            'message': 'Meeting created successfully',
            'meeting': serialize_meeting(meeting)
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def meeting_detail(request, meeting_id):
    """
    GET: Get meeting details
    PUT: Update meeting (instructor only)
    DELETE: Cancel meeting (instructor only)
    """
    user_id = request.user.get('_id')
    user_role = request.user.get('role', 'student')
    
    # Get meeting
    meeting = Meeting.find_by_id(meeting_id)
    if not meeting:
        return Response({
            'success': False,
            'error': 'Meeting not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    is_instructor = str(meeting['instructor_id']) == str(user_id)
    
    # Check if student is invited
    if user_role == 'student':
        participants = MeetingParticipant.find_by_meeting(meeting_id)
        is_participant = any(str(p['student_id']) == str(user_id) for p in participants)
        
        if not is_participant:
            return Response({
                'success': False,
                'error': 'You are not invited to this meeting'
            }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        # Get participants
        participants = MeetingParticipant.find_by_meeting(meeting_id)
        
        return Response({
            'success': True,
            'meeting': serialize_meeting(meeting),
            'participants': [serialize_participant(p) for p in participants],
            'is_instructor': is_instructor
        })
    
    elif request.method == 'PUT':
        # Only instructor can update
        if not is_instructor:
            return Response({
                'success': False,
                'error': 'Only the instructor can update this meeting'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Cannot update if meeting has started
        if meeting['status'] != Meeting.STATUS_SCHEDULED:
            return Response({
                'success': False,
                'error': 'Cannot update a meeting that has already started or ended'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data
        update_data = {}
        
        # Update allowed fields
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'duration' in data:
            update_data['duration'] = int(data['duration'])
        if 'scheduled_date' in data:
            scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
            if scheduled_date <= datetime.utcnow():
                return Response({
                    'success': False,
                    'error': 'Scheduled date must be in the future'
                }, status=status.HTTP_400_BAD_REQUEST)
            update_data['scheduled_date'] = scheduled_date
        
        # Update meeting
        Meeting.update(meeting_id, **update_data)
        
        # Update participants if provided
        if 'student_ids' in data:
            # Remove old participants
            MeetingParticipant.get_collection().delete_many({'meeting_id': ObjectId(meeting_id)})
            
            # Add new participants
            for student_id in data['student_ids']:
                student = User.get_collection().find_one({'_id': ObjectId(student_id)})
                if student:
                    MeetingParticipant.create(
                        meeting_id=meeting_id,
                        student_id=student_id,
                        student_email=student.get('email', '')
                    )
        
        # Return updated meeting
        meeting = Meeting.find_by_id(meeting_id)
        return Response({
            'success': True,
            'message': 'Meeting updated successfully',
            'meeting': serialize_meeting(meeting)
        })
    
    elif request.method == 'DELETE':
        # Only instructor can delete
        if not is_instructor:
            return Response({
                'success': False,
                'error': 'Only the instructor can cancel this meeting'
            }, status=status.HTTP_403_FORBIDDEN)
        
        Meeting.delete(meeting_id)
        
        return Response({
            'success': True,
            'message': 'Meeting cancelled successfully'
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_start(request, meeting_id):
    """Start a meeting (instructor only)"""
    user_id = request.user.get('_id')
    
    meeting = Meeting.find_by_id(meeting_id)
    if not meeting:
        return Response({
            'success': False,
            'error': 'Meeting not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is instructor
    if str(meeting['instructor_id']) != str(user_id):
        return Response({
            'success': False,
            'error': 'Only the instructor can start this meeting'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check if meeting is scheduled
    if meeting['status'] != Meeting.STATUS_SCHEDULED:
        return Response({
            'success': False,
            'error': 'Meeting cannot be started'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Start meeting
    Meeting.start_meeting(meeting_id)
    
    meeting = Meeting.find_by_id(meeting_id)
    return Response({
        'success': True,
        'message': 'Meeting started successfully',
        'meeting': serialize_meeting(meeting)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_end(request, meeting_id):
    """End a meeting (instructor only)"""
    user_id = request.user.get('_id')
    
    meeting = Meeting.find_by_id(meeting_id)
    if not meeting:
        return Response({
            'success': False,
            'error': 'Meeting not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is instructor
    if str(meeting['instructor_id']) != str(user_id):
        return Response({
            'success': False,
            'error': 'Only the instructor can end this meeting'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check if meeting is ongoing
    if meeting['status'] != Meeting.STATUS_ONGOING:
        return Response({
            'success': False,
            'error': 'Meeting is not ongoing'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # End meeting
    Meeting.end_meeting(meeting_id)
    
    meeting = Meeting.find_by_id(meeting_id)
    return Response({
        'success': True,
        'message': 'Meeting ended successfully',
        'meeting': serialize_meeting(meeting)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_join(request, meeting_id):
    """Join a meeting (mark as attended)"""
    user_id = request.user.get('_id')
    user_role = request.user.get('role', 'student')
    
    meeting = Meeting.find_by_id(meeting_id)
    if not meeting:
        return Response({
            'success': False,
            'error': 'Meeting not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if meeting is ongoing
    if meeting['status'] != Meeting.STATUS_ONGOING:
        return Response({
            'success': False,
            'error': 'Meeting is not currently active'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user is invited (for students)
    if user_role == 'student':
        participants = MeetingParticipant.find_by_meeting(meeting_id)
        is_participant = any(str(p['student_id']) == str(user_id) for p in participants)
        
        if not is_participant:
            return Response({
                'success': False,
                'error': 'You are not invited to this meeting'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Mark as attended
        MeetingParticipant.mark_attended(meeting_id, user_id)
    
    return Response({
        'success': True,
        'message': 'Joined meeting successfully',
        'meeting_link': meeting['meeting_link']
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_leave(request, meeting_id):
    """Leave a meeting (record leave time)"""
    user_id = request.user.get('_id')
    
    meeting = Meeting.find_by_id(meeting_id)
    if not meeting:
        return Response({
            'success': False,
            'error': 'Meeting not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Mark as left
    MeetingParticipant.mark_left(meeting_id, user_id)
    
    # Calculate duration
    duration = MeetingParticipant.get_duration(meeting_id, user_id)
    
    return Response({
        'success': True,
        'message': 'Left meeting successfully',
        'duration': duration
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_respond(request, meeting_id):
    """Respond to meeting invitation (accept/decline)"""
    user_id = request.user.get('_id')
    action = request.data.get('action')  # 'accept' or 'decline'
    
    if action not in ['accept', 'decline']:
        return Response({
            'success': False,
            'error': 'Invalid action. Use "accept" or "decline"'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    meeting = Meeting.find_by_id(meeting_id)
    if not meeting:
        return Response({
            'success': False,
            'error': 'Meeting not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is invited
    participants = MeetingParticipant.find_by_meeting(meeting_id)
    is_participant = any(str(p['student_id']) == str(user_id) for p in participants)
    
    if not is_participant:
        return Response({
            'success': False,
            'error': 'You are not invited to this meeting'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Update status
    new_status = MeetingParticipant.STATUS_ACCEPTED if action == 'accept' else MeetingParticipant.STATUS_DECLINED
    MeetingParticipant.update_status(meeting_id, user_id, new_status)
    
    return Response({
        'success': True,
        'message': f'Meeting invitation {action}ed successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_meetings(request):
    """Get all meetings for a student (their invitations)"""
    user_id = request.user.get('_id')
    
    # Get all participations
    participants = MeetingParticipant.find_by_student(user_id)
    
    # Get meeting details for each
    meetings_data = []
    for participant in participants:
        meeting = Meeting.find_by_id(participant['meeting_id'])
        if meeting:
            meeting_data = serialize_meeting(meeting)
            meeting_data['participant_status'] = participant['status']
            meeting_data['joined_at'] = participant.get('joined_at')
            meeting_data['left_at'] = participant.get('left_at')
            meetings_data.append(meeting_data)
    
    return Response({
        'success': True,
        'count': len(meetings_data),
        'meetings': meetings_data
    })
