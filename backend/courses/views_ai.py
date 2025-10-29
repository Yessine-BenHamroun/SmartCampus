"""
AI generation views for quizzes and assignments
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from courses.extended_models import Lesson, Quiz, Assignment
from courses.models import Course
from courses.ai_helpers import generate_quiz_questions, generate_assignment_questions
from users.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quiz_ai(request, lesson_id):
    """
    Generate quiz questions using AI based on lesson content
    Instructor only
    """
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can generate quizzes'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Verify lesson exists
    lesson = Lesson.find_by_id(lesson_id)
    if not lesson:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get parameters from request
    num_questions = request.data.get('num_questions', 5)
    difficulty = request.data.get('difficulty', 'medium')
    
    # Prepare lesson content for AI
    # Extract all relevant content from the lesson
    content_text = ""
    
    # Get content based on lesson type
    if hasattr(lesson, 'content') and lesson.content:
        if isinstance(lesson.content, dict):
            # If content is a dictionary, extract text fields
            if 'text_content' in lesson.content:
                content_text = lesson.content.get('text_content', '')
            elif 'video_url' in lesson.content:
                content_text = f"Video lesson: {lesson.content.get('video_url', '')}"
            else:
                content_text = str(lesson.content)
        else:
            content_text = str(lesson.content)
    
    lesson_content = {
        'title': lesson.title,
        'description': lesson.description or '',
        'content': content_text,
        'content_type': getattr(lesson, 'content_type', 'text'),
        'duration': getattr(lesson, 'duration_minutes', 0)
    }
    
    # Generate questions using AI helper
    questions = generate_quiz_questions(lesson_content, num_questions, difficulty)
    
    # Return generated questions (instructor can review before creating quiz)
    return Response({
        'lesson_id': lesson_id,
        'generated_questions': questions,
        'message': 'Review and edit questions before creating the quiz'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz_from_ai(request, lesson_id):
    """
    Create a quiz from AI-generated questions
    Instructor only
    """
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can create quizzes'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Verify lesson exists
    lesson = Lesson.find_by_id(lesson_id)
    if not lesson:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get quiz data from request
    title = request.data.get('title', f'Quiz: {lesson.title}')
    description = request.data.get('description', '')
    questions = request.data.get('questions', [])
    passing_score = request.data.get('passing_score', 70)
    time_limit_minutes = request.data.get('time_limit_minutes', 0)
    
    if not questions:
        return Response({'error': 'No questions provided'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Create quiz
    quiz_data = {
        'lesson_id': str(lesson_id),
        'course_id': str(lesson.course_id),
        'instructor_id': str(str(request.user.id)),
        'title': title,
        'description': description,
        'questions': questions,
        'passing_score': passing_score,
        'time_limit_minutes': time_limit_minutes,
        'is_ai_generated': True,
        'is_published': False  # Instructor must publish manually
    }
    
    quiz = Quiz.create(**quiz_data)
    
    return Response({
        **quiz.to_dict(),
        'message': 'AI-generated quiz created successfully. Review and publish when ready.'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_assignment_ai(request, course_id):
    """
    Generate assignment questions using AI based on course content
    Instructor only
    """
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can generate assignments'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Verify course exists and instructor owns it
    course = Course.find_by_id(course_id)
    if not course:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if str(course.instructor_id) != str(str(request.user.id)):
        return Response({'error': 'You do not have permission to create assignments for this course'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Get parameters from request
    assignment_type = request.data.get('assignment_type', 'written')
    num_questions = request.data.get('num_questions', 5)
    
    # Prepare course content for AI
    course_content = {
        'title': course.title,
        'description': course.description,
        'category': course.category,
        'difficulty_level': course.difficulty_level
    }
    
    # Generate questions using AI helper
    generated_content = generate_assignment_questions(course_content, assignment_type, num_questions)
    
    # Return generated content (instructor can review before creating assignment)
    return Response({
        'course_id': course_id,
        'assignment_type': assignment_type,
        'generated_content': generated_content,
        'message': 'Review and edit content before creating the assignment'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_assignment_from_ai(request, course_id):
    """
    Create an assignment from AI-generated content
    Instructor only
    """
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can create assignments'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Verify course exists and instructor owns it
    course = Course.find_by_id(course_id)
    if not course:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if str(course.instructor_id) != str(str(request.user.id)):
        return Response({'error': 'You do not have permission to create assignments for this course'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Get assignment data from request
    title = request.data.get('title', f'Assignment: {course.title}')
    description = request.data.get('description', '')
    assignment_type = request.data.get('assignment_type', 'written')
    questions = request.data.get('questions', [])
    coding_problem = request.data.get('coding_problem', {})
    time_limit_minutes = request.data.get('time_limit_minutes', 60)
    passing_score = request.data.get('passing_score', 50)
    
    # Validate content based on type
    if assignment_type == 'coding' and not coding_problem:
        return Response({'error': 'Coding problem required for coding assignments'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    if assignment_type in ['written', 'mixed'] and not questions:
        return Response({'error': 'Questions required for written assignments'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Create assignment
    assignment_data = {
        'course_id': str(course_id),
        'instructor_id': str(str(request.user.id)),
        'title': title,
        'description': description,
        'assignment_type': assignment_type,
        'questions': questions,
        'coding_problem': coding_problem,
        'time_limit_minutes': time_limit_minutes,
        'passing_score': passing_score,
        'is_published': False  # Instructor must publish manually
    }
    
    assignment = Assignment.create(**assignment_data)
    
    return Response({
        **assignment.to_dict(),
        'message': 'AI-generated assignment created successfully. Review and publish when ready.'
    }, status=status.HTTP_201_CREATED)
