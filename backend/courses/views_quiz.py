"""
Quiz views for instructors and students
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from bson import ObjectId

from courses.extended_models import Quiz, QuizAttempt, Lesson
from courses.serializers import QuizSerializer, QuizAttemptSerializer
from users.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz(request, lesson_id):
    """Create a quiz for a lesson (Instructor only)"""
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can create quizzes'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Verify lesson exists
    lesson = Lesson.find_by_id(lesson_id)
    if not lesson:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = QuizSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create quiz
    quiz_data = serializer.validated_data
    quiz_data['instructor_id'] = str(request.user.id)
    quiz_data['lesson_id'] = str(lesson_id)
    quiz_data['course_id'] = str(lesson.course_id)
    
    quiz = Quiz.create(**quiz_data)
    
    return Response(quiz.to_dict(), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_quiz(request, quiz_id):
    """Get, update, or delete a quiz (Instructor only)"""
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can manage quizzes'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    quiz = Quiz.find_by_id(quiz_id)
    if not quiz:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Verify instructor owns this quiz
    if str(quiz.instructor_id) != str(str(request.user.id)):
        return Response({'error': 'You do not have permission to manage this quiz'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        return Response(quiz.to_dict())
    
    elif request.method == 'PUT':
        serializer = QuizSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        quiz.update(**serializer.validated_data)
        return Response(quiz.to_dict())
    
    elif request.method == 'DELETE':
        quiz.delete()
        return Response({'message': 'Quiz deleted successfully'}, 
                       status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lesson_quiz(request, lesson_id):
    """Get quiz for a lesson (Student view - no correct answers)"""
    from bson import ObjectId
    from courses.models_progress import StudentProgress
    from courses.extended_models import Module
    
    lesson = Lesson.find_by_id(lesson_id)
    if not lesson:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
    
    quiz = Quiz.find_by_lesson(lesson_id)
    if not quiz:
        return Response({'error': 'No quiz found for this lesson'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    # Check if student is instructor
    user = User.find_by_id(str(request.user.id))
    is_instructor = user and user.role == 'instructor'
    
    # For students, check if they are enrolled in the course
    if not is_instructor:
        # Get course_id from lesson or module
        if lesson.course_id:
            course_id = str(lesson.course_id)
        else:
            module = Module.find_by_id(str(lesson.module_id))
            if not module:
                return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)
            course_id = str(module.course_id)
        
        # Check enrollment - allow quiz access if enrolled
        from courses.models import Enrollment
        enrollment = Enrollment.find_one(str(request.user.id), course_id)
        if not enrollment:
            return Response({'error': 'Not enrolled in this course'}, status=status.HTTP_403_FORBIDDEN)
        
        # Optional: Check if lesson is completed (commented out for now to allow testing)
        # progress = StudentProgress.find_by_student_and_course(str(request.user.id), course_id)
        # lesson_completed = False
        #
        # if progress and progress.lessons_completed:
        #     try:
        #         lesson_id_obj = ObjectId(lesson_id)
        #         lesson_completed = lesson_id_obj in progress.lessons_completed
        #     except Exception as e:
        #         print(f"Error converting lesson_id {lesson_id} to ObjectId: {e}")
        #         lesson_completed = str(lesson_id) in [str(lid) for lid in progress.lessons_completed]
        #
        # if not lesson_completed:
        #     return Response({
        #         'error': 'You must complete this lesson before taking the quiz',
        #         'lesson_id': lesson_id,
        #         'available': False
        #     }, status=status.HTTP_403_FORBIDDEN)
    
    # Don't show correct answers to students before attempt
    quiz_data = quiz.to_dict()
    if str(request.user.id) != quiz.instructor_id:
        for question in quiz_data.get('questions', []):
            question.pop('correct_answer', None)
    
    quiz_data['available'] = True
    return Response(quiz_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_lesson_quiz_availability(request, lesson_id):
    """Check if a quiz exists for a lesson (without gating - for immediate display after lesson completion)"""
    try:
        lesson = Lesson.find_by_id(lesson_id)
        if not lesson:
            return Response({
                'has_quiz': False,
                'quiz': None,
                'error': 'Lesson not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        quiz = Quiz.find_by_lesson(lesson_id)
        if not quiz:
            return Response({
                'has_quiz': False,
                'quiz': None
            }, status=status.HTTP_200_OK)
        
        # Return quiz info without gating (for checking availability right after lesson completion)
        quiz_data = quiz.to_dict()
        
        # Don't show correct answers to students
        user = User.find_by_id(str(request.user.id))
        is_instructor = user and user.role == 'instructor'
        
        if not is_instructor:
            for question in quiz_data.get('questions', []):
                question.pop('correct_answer', None)
        
        return Response({
            'has_quiz': True,
            'quiz': quiz_data,
            'available': True
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in check_lesson_quiz_availability: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'has_quiz': False,
            'quiz': None,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, quiz_id):
    """Submit a quiz attempt"""
    quiz = Quiz.find_by_id(quiz_id)
    if not quiz:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not quiz.is_published:
        return Response({'error': 'This quiz is not published yet'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Check max attempts
    if quiz.max_attempts > 0:
        previous_attempts = QuizAttempt.find_by_student_quiz(str(request.user.id), quiz_id)
        if len(previous_attempts) >= quiz.max_attempts:
            return Response({'error': f'Maximum attempts ({quiz.max_attempts}) reached'}, 
                           status=status.HTTP_400_BAD_REQUEST)
    
    serializer = QuizAttemptSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate score
    answers = serializer.validated_data['answers']
    score = 0
    max_score = 0
    
    for i, question in enumerate(quiz.questions):
        points = question.get('points', 1)
        max_score += points
        
        # Find student's answer for this question
        student_answer = next((a for a in answers if a['question_index'] == i), None)
        if student_answer:
            if student_answer['selected_answer'] == question['correct_answer']:
                score += points
    
    percentage = (score / max_score * 100) if max_score > 0 else 0
    passed = percentage >= quiz.passing_score
    
    # Create attempt record
    attempt_data = {
        'quiz_id': ObjectId(quiz_id),
        'student_id': ObjectId(str(request.user.id)),
        'course_id': ObjectId(quiz.course_id),
        'lesson_id': ObjectId(quiz.lesson_id),
        'answers': [dict(a) for a in answers],
        'score': score,
        'max_score': max_score,
        'percentage': round(percentage, 2),
        'passed': passed,
        'time_taken_minutes': serializer.validated_data['time_taken_minutes'],
        'completed_at': datetime.utcnow()
    }
    
    attempt = QuizAttempt.create(**attempt_data)
    
    # Get ranking
    all_attempts = QuizAttempt.find_by_quiz(quiz_id)
    completed_attempts = [a for a in all_attempts if a.completed_at]
    sorted_attempts = sorted(completed_attempts, key=lambda x: x.percentage, reverse=True)
    
    rank = next((i + 1 for i, a in enumerate(sorted_attempts) if str(a.id) == str(attempt.id)), None)
    
    result = attempt.to_dict()
    result['rank'] = rank
    result['total_attempts'] = len(completed_attempts)
    
    # Include correct answers if quiz allows
    if quiz.show_correct_answers:
        result['correct_answers'] = [
            {
                'question_index': i,
                'correct_answer': q['correct_answer'],
                'question_text': q['question_text']
            }
            for i, q in enumerate(quiz.questions)
        ]
    
    return Response(result, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_attempts(request, quiz_id):
    """Get all attempts for a quiz (Instructor only)"""
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can view all attempts'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    quiz = Quiz.find_by_id(quiz_id)
    if not quiz:
        return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if str(quiz.instructor_id) != str(str(request.user.id)):
        return Response({'error': 'You do not have permission to view these attempts'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    attempts = QuizAttempt.find_by_quiz(quiz_id)
    
    # Calculate statistics
    completed_attempts = [a for a in attempts if a.completed_at]
    if completed_attempts:
        avg_score = sum(a.percentage for a in completed_attempts) / len(completed_attempts)
        pass_rate = sum(1 for a in completed_attempts if a.passed) / len(completed_attempts) * 100
    else:
        avg_score = 0
        pass_rate = 0
    
    # Group by student
    student_attempts = {}
    for attempt in attempts:
        student_id = str(attempt.student_id)
        if student_id not in student_attempts:
            student = User.find_by_id(student_id)
            student_attempts[student_id] = {
                'student_id': student_id,
                'student_name': f"{student.first_name} {student.last_name}" if student else "Unknown",
                'attempts': [],
                'best_score': 0,
                'validated': False
            }
        
        attempt_dict = attempt.to_dict()
        student_attempts[student_id]['attempts'].append(attempt_dict)
        
        if attempt.percentage > student_attempts[student_id]['best_score']:
            student_attempts[student_id]['best_score'] = attempt.percentage
        
        if attempt.passed:
            student_attempts[student_id]['validated'] = True
    
    return Response({
        'quiz_id': quiz_id,
        'total_attempts': len(attempts),
        'unique_students': len(student_attempts),
        'average_score': round(avg_score, 2),
        'pass_rate': round(pass_rate, 2),
        'student_attempts': list(student_attempts.values())
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_quiz_attempts(request, quiz_id):
    """Get student's own attempts for a quiz"""
    attempts = QuizAttempt.find_by_student_quiz(str(request.user.id), quiz_id)
    
    return Response({
        'quiz_id': quiz_id,
        'attempts': [attempt.to_dict() for attempt in attempts],
        'total_attempts': len(attempts)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_quizzes(request, course_id):
    """Get all quizzes for a course"""
    quizzes = Quiz.find_by_course(course_id)
    
    # For students, hide correct answers
    user = User.find_by_id(str(request.user.id))
    is_instructor = user and user.role == 'instructor'
    
    quiz_list = []
    for quiz in quizzes:
        quiz_data = quiz.to_dict()
        if not is_instructor:
            for question in quiz_data.get('questions', []):
                question.pop('correct_answer', None)
        quiz_list.append(quiz_data)
    
    return Response({'quizzes': quiz_list})
