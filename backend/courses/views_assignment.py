"""
Assignment views for instructors and students
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from bson import ObjectId

from courses.extended_models import Assignment, AssignmentSubmission, QuizAttempt, Quiz
from courses.models import Course
from courses.serializers import AssignmentSerializer, AssignmentSubmissionSerializer, GradeAssignmentSerializer
from users.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_assignment(request, course_id):
    """Create an assignment for a course (Instructor only)"""
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
    
    serializer = AssignmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create assignment
    assignment_data = serializer.validated_data
    assignment_data['instructor_id'] = str(str(request.user.id))
    assignment_data['course_id'] = str(course_id)
    
    assignment = Assignment.create(**assignment_data)
    
    return Response(assignment.to_dict(), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_assignment(request, assignment_id):
    """Get, update, or delete an assignment (Instructor only)"""
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can manage assignments'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    assignment = Assignment.find_by_id(assignment_id)
    if not assignment:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Verify instructor owns this assignment
    if str(assignment.instructor_id) != str(str(request.user.id)):
        return Response({'error': 'You do not have permission to manage this assignment'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        return Response(assignment.to_dict())
    
    elif request.method == 'PUT':
        serializer = AssignmentSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        assignment.update(**serializer.validated_data)
        return Response(assignment.to_dict())
    
    elif request.method == 'DELETE':
        assignment.delete()
        return Response({'message': 'Assignment deleted successfully'}, 
                       status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_assignments(request, course_id):
    """Get all assignments for a course"""
    assignments = Assignment.find_by_course(course_id)
    
    # For students, only show published assignments
    user = User.find_by_id(str(request.user.id))
    is_instructor = user and user.role == 'instructor'
    
    if not is_instructor:
        assignments = [a for a in assignments if a.is_published]
    
    return Response({'assignments': [a.to_dict() for a in assignments]})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assignment_detail(request, assignment_id):
    """Get assignment details for student"""
    from bson import ObjectId
    from courses.models_progress import StudentProgress
    from courses.extended_models import Lesson, Module
    
    assignment = Assignment.find_by_id(assignment_id)
    if not assignment:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not assignment.is_published:
        user = User.find_by_id(str(request.user.id))
        if not user or user.role != 'instructor' or str(assignment.instructor_id) != str(str(request.user.id)):
            return Response({'error': 'This assignment is not published yet'}, 
                           status=status.HTTP_400_BAD_REQUEST)
    
    # Check if student is instructor
    user = User.find_by_id(str(request.user.id))
    is_instructor = user and user.role == 'instructor'
    
    assignment_data = assignment.to_dict()
    
    # For students, check if all lessons in the course are completed
    if not is_instructor:
        course_id = str(assignment.course_id)
        progress = StudentProgress.find_by_student_and_course(str(request.user.id), course_id)
        
        # Get all lessons in the course
        modules = Module.find_by_course(course_id)
        all_lessons = []
        for module in modules:
            lessons = Lesson.find_by_module(str(module.id))
            all_lessons.extend(lessons)
        
        # Check if all lessons are completed
        lessons_completed = progress.lessons_completed if progress else []
        all_lessons_completed = all(
            ObjectId(lesson.id) in lessons_completed for lesson in all_lessons
        ) if all_lessons else False
        
        if not all_lessons_completed:
            return Response({
                'error': 'You must complete all lessons in this course before accessing the assignment',
                'assignment_id': assignment_id,
                'available': False,
                'lessons_completed': len(lessons_completed),
                'total_lessons': len(all_lessons)
            }, status=status.HTTP_403_FORBIDDEN)
        
        assignment_data['available'] = True
    
    # Check student's previous attempts
    previous_submissions = AssignmentSubmission.find_by_student_assignment(str(request.user.id), assignment_id)
    assignment_data['attempts_count'] = len(previous_submissions)
    assignment_data['can_attempt'] = (
        assignment.max_attempts == 0 or 
        len(previous_submissions) < assignment.max_attempts
    )
    
    # Don't show correct answers for written assignments
    if assignment.assignment_type in ['written', 'mixed']:
        for question in assignment_data.get('questions', []):
            question.pop('correct_answer', None)
    
    return Response(assignment_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_assignment(request, assignment_id):
    """Submit an assignment"""
    assignment = Assignment.find_by_id(assignment_id)
    if not assignment:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not assignment.is_published:
        return Response({'error': 'This assignment is not published yet'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Check max attempts
    previous_submissions = AssignmentSubmission.find_by_student_assignment(str(request.user.id), assignment_id)
    if assignment.max_attempts > 0 and len(previous_submissions) >= assignment.max_attempts:
        return Response({'error': f'Maximum attempts ({assignment.max_attempts}) reached'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    serializer = AssignmentSubmissionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if warnings exceeded limit
    warnings_count = serializer.validated_data.get('warnings_count', 0)
    if warnings_count >= assignment.max_warnings:
        # Invalidate submission
        submission_data = {
            'assignment_id': ObjectId(assignment_id),
            'student_id': ObjectId(str(request.user.id)),
            'course_id': ObjectId(assignment.course_id),
            'warnings_count': warnings_count,
            'warning_details': serializer.validated_data.get('warning_details', []),
            'time_taken_minutes': serializer.validated_data['time_taken_minutes'],
            'status': 'invalidated',
            'score': 0,
            'max_score': 100,
            'percentage': 0,
            'passed': False,
            'submitted_at': datetime.utcnow()
        }
        submission = AssignmentSubmission.create(**submission_data)
        
        return Response({
            **submission.to_dict(),
            'message': f'Assignment invalidated due to {warnings_count} warnings'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create submission
    submission_data = {
        'assignment_id': ObjectId(assignment_id),
        'student_id': ObjectId(str(request.user.id)),
        'course_id': ObjectId(assignment.course_id),
        'answers': serializer.validated_data.get('answers', []),
        'code_solution': serializer.validated_data.get('code_solution', ''),
        'warnings_count': warnings_count,
        'warning_details': serializer.validated_data.get('warning_details', []),
        'time_taken_minutes': serializer.validated_data['time_taken_minutes'],
        'status': 'submitted',
        'max_score': 100,
        'submitted_at': datetime.utcnow()
    }
    
    # Calculate AI assistance note based on quiz performance
    quizzes = Quiz.find_by_course(assignment.course_id)
    quiz_attempts = []
    for quiz in quizzes:
        attempts = QuizAttempt.find_by_student_quiz(str(request.user.id), str(quiz.id))
        if attempts:
            best_attempt = max(attempts, key=lambda x: x.percentage)
            quiz_attempts.append(best_attempt.percentage)
    
    if quiz_attempts:
        avg_quiz_score = sum(quiz_attempts) / len(quiz_attempts)
        submission_data['ai_assistance_note'] = (
            f"Student's average quiz score: {avg_quiz_score:.1f}%. "
            f"Completed {len(quiz_attempts)} quizzes in this course. "
            f"{'Strong performance' if avg_quiz_score >= 80 else 'Moderate performance' if avg_quiz_score >= 60 else 'Needs improvement'} "
            "on lesson quizzes suggests this work is likely authentic."
        )
    else:
        submission_data['ai_assistance_note'] = "No quiz data available for comparison."
    
    submission = AssignmentSubmission.create(**submission_data)
    
    return Response(submission.to_dict(), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grade_assignment(request, submission_id):
    """Grade an assignment submission (Instructor only)"""
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can grade assignments'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    submission = AssignmentSubmission.find_by_id(submission_id)
    if not submission:
        return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)
    
    assignment = Assignment.find_by_id(str(submission.assignment_id))
    if not assignment:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Verify instructor owns this assignment
    if str(assignment.instructor_id) != str(str(request.user.id)):
        return Response({'error': 'You do not have permission to grade this submission'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    serializer = GradeAssignmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    score = serializer.validated_data['score']
    feedback = serializer.validated_data.get('feedback', '')
    
    # Calculate percentage and pass status
    percentage = (score / submission.max_score * 100) if submission.max_score > 0 else 0
    passed = percentage >= assignment.passing_score
    
    # Update submission
    submission.update(
        score=score,
        percentage=round(percentage, 2),
        passed=passed,
        feedback=feedback,
        status='graded',
        graded_by=ObjectId(str(request.user.id)),
        graded_at=datetime.utcnow()
    )
    
    return Response(submission.to_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assignment_submissions(request, assignment_id):
    """Get all submissions for an assignment (Instructor only)"""
    user = User.find_by_id(str(request.user.id))
    if not user or user.role != 'instructor':
        return Response({'error': 'Only instructors can view all submissions'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    assignment = Assignment.find_by_id(assignment_id)
    if not assignment:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if str(assignment.instructor_id) != str(str(request.user.id)):
        return Response({'error': 'You do not have permission to view these submissions'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    submissions = AssignmentSubmission.find_by_assignment(assignment_id)
    
    # Calculate statistics
    graded_submissions = [s for s in submissions if s.status == 'graded']
    if graded_submissions:
        avg_score = sum(s.percentage for s in graded_submissions) / len(graded_submissions)
        pass_rate = sum(1 for s in graded_submissions if s.passed) / len(graded_submissions) * 100
    else:
        avg_score = 0
        pass_rate = 0
    
    # Group by student
    student_submissions = {}
    for submission in submissions:
        student_id = str(submission.student_id)
        if student_id not in student_submissions:
            student = User.find_by_id(student_id)
            student_submissions[student_id] = {
                'student_id': student_id,
                'student_name': f"{student.first_name} {student.last_name}" if student else "Unknown",
                'submissions': [],
                'best_score': 0,
                'validated': False
            }
        
        submission_dict = submission.to_dict()
        student_submissions[student_id]['submissions'].append(submission_dict)
        
        if submission.status == 'graded':
            if submission.percentage > student_submissions[student_id]['best_score']:
                student_submissions[student_id]['best_score'] = submission.percentage
            
            if submission.passed:
                student_submissions[student_id]['validated'] = True
    
    # AI recommendations for assignment improvement
    ai_recommendations = []
    if graded_submissions:
        if avg_score < 50:
            ai_recommendations.append("Consider making the assignment easier or providing more guidance")
        elif avg_score > 90:
            ai_recommendations.append("Consider increasing difficulty to better challenge students")
        
        if pass_rate < 50:
            ai_recommendations.append("Low pass rate - review if requirements are clear")
        
        # Analyze common weak areas (placeholder for future implementation)
        ai_recommendations.append("Review student feedback to identify common challenges")
    
    return Response({
        'assignment_id': assignment_id,
        'total_submissions': len(submissions),
        'unique_students': len(student_submissions),
        'graded_count': len(graded_submissions),
        'pending_count': len([s for s in submissions if s.status == 'submitted']),
        'average_score': round(avg_score, 2),
        'pass_rate': round(pass_rate, 2),
        'student_submissions': list(student_submissions.values()),
        'ai_recommendations': ai_recommendations
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_assignment_submissions(request, assignment_id):
    """Get student's own submissions for an assignment"""
    submissions = AssignmentSubmission.find_by_student_assignment(str(request.user.id), assignment_id)
    
    return Response({
        'assignment_id': assignment_id,
        'submissions': [s.to_dict() for s in submissions],
        'total_submissions': len(submissions)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_submission_detail(request, submission_id):
    """Get submission details"""
    submission = AssignmentSubmission.find_by_id(submission_id)
    if not submission:
        return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permission
    user = User.find_by_id(str(request.user.id))
    is_owner = str(submission.student_id) == str(str(request.user.id))
    is_instructor = user and user.role == 'instructor'
    
    if not is_owner and not is_instructor:
        return Response({'error': 'You do not have permission to view this submission'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # If instructor, verify they own the assignment
    if is_instructor and not is_owner:
        assignment = Assignment.find_by_id(str(submission.assignment_id))
        if str(assignment.instructor_id) != str(str(request.user.id)):
            return Response({'error': 'You do not have permission to view this submission'}, 
                           status=status.HTTP_403_FORBIDDEN)
    
    return Response(submission.to_dict())


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_code_syntax(request):
    """Validate Python code syntax without executing it"""
    import ast
    
    code = request.data.get('code', '')
    
    if not code or not code.strip():
        return Response({
            'valid': False,
            'errors': ['Code cannot be empty'],
            'line_numbers': []
        })
    
    result = {
        'valid': True,
        'errors': [],
        'line_numbers': [],
        'warnings': []
    }
    
    try:
        # Parse the code using AST
        ast.parse(code)
        
        # Additional checks
        lines = code.split('\n')
        result['line_count'] = len([l for l in lines if l.strip()])
        result['has_comments'] = any('#' in line for line in lines)
        
    except SyntaxError as e:
        result['valid'] = False
        error_msg = f"Line {e.lineno}: {e.msg}"
        if e.text:
            error_msg += f" - '{e.text.strip()}'"
        result['errors'].append(error_msg)
        result['line_numbers'].append(e.lineno)
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Parsing error: {str(e)}")
    
    return Response(result)
