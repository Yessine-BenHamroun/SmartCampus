"""
Views for progress tracking and feedback management
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from courses.models_progress import StudentProgress, CourseReview, InstructorReview
from courses.serializers_progress import (
    StudentProgressSerializer, CourseReviewSerializer, InstructorReviewSerializer
)
from courses.models import Course
from courses.extended_models import Lesson, Quiz, Assignment
from users.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_progress(request, course_id):
    """
    Get student's progress for a specific course
    """
    try:
        student_id = str(request.user.id)
        
        # Get or create progress
        progress = StudentProgress.find_by_student_and_course(student_id, course_id)
        
        if not progress:
            return Response({
                'message': 'No progress found for this course',
                'progress': {
                    'completion_percentage': 0,
                    'lessons_completed': [],
                    'quizzes_completed': [],
                    'assignments_completed': []
                }
            })
        
        # Get course details for context
        course = Course.find_by_id(course_id)
        if not course:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'progress': progress.to_dict(),
            'course_title': course.title
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch progress',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_student_progress(request):
    """
    Get all progress for logged-in student across all courses
    """
    try:
        student_id = str(request.user.id)
        
        progress_list = StudentProgress.find_by_student(student_id)
        
        # Enrich with course details
        enriched_progress = []
        for progress in progress_list:
            course = Course.find_by_id(str(progress.course_id))
            if course:
                progress_dict = progress.to_dict()
                progress_dict['course_title'] = course.title
                progress_dict['course_thumbnail'] = course.thumbnail_url
                enriched_progress.append(progress_dict)
        
        return Response({
            'progress': enriched_progress,
            'total_courses': len(enriched_progress)
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch progress',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_lesson_progress(request, lesson_id):
    """
    Mark a lesson as completed
    """
    try:
        student_id = str(request.user.id)
        
        # Get lesson to find course_id
        lesson = Lesson.find_by_id(lesson_id)
        if not lesson:
            return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get course_id from lesson or from module
        if lesson.course_id:
            course_id = str(lesson.course_id)
        else:
            # Get course_id from module
            from courses.extended_models import Module
            module = Module.find_by_id(str(lesson.module_id))
            if not module:
                return Response({'error': 'Module not found'}, status=status.HTTP_404_NOT_FOUND)
            course_id = str(module.course_id)
        
        # Get or create progress
        progress = StudentProgress.find_by_student_and_course(student_id, course_id)
        if not progress:
            # Create new progress record
            from courses.extended_models import Enrollment
            enrollment = Enrollment.find_one(student_id, course_id)
            if not enrollment:
                return Response({'error': 'Not enrolled in this course'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            progress = StudentProgress.create(
                student_id=student_id,
                course_id=course_id,
                enrollment_id=str(enrollment._id)
            )
        
        # Mark lesson complete
        progress.mark_lesson_complete(lesson_id)
        
        # Update time spent if provided
        time_spent_minutes = request.data.get('time_spent_minutes', 0)
        if time_spent_minutes:
            current_time = getattr(progress, 'time_spent_minutes', 0) or 0
            progress.update(time_spent_minutes=current_time + time_spent_minutes)
        
        # Recalculate completion percentage
        from bson import ObjectId
        # Convert course_id to ObjectId for MongoDB query
        course_id_obj = ObjectId(course_id) if isinstance(course_id, str) else course_id
        
        total_lessons = Lesson.get_collection().count_documents({'course_id': course_id_obj})
        total_quizzes = Quiz.get_collection().count_documents({'course_id': course_id_obj})
        total_assignments = Assignment.get_collection().count_documents({'course_id': course_id_obj})
        
        progress.calculate_completion_percentage(total_lessons, total_quizzes, total_assignments)
        
        return Response({
            'message': 'Lesson marked as completed',
            'progress': progress.to_dict()
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Error in update_lesson_progress: {str(e)}")
        print(traceback.format_exc())
        return Response({
            'error': 'Failed to update progress',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_course_review(request, course_id):
    """
    Submit or update a course review
    Student can only review courses they're enrolled in
    """
    try:
        student_id = str(request.user.id)
        
        # Validate course exists
        course = Course.find_by_id(course_id)
        if not course:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if student is enrolled
        from courses.extended_models import Enrollment
        enrollment = Enrollment.find_one(student_id, course_id)
        if not enrollment:
            return Response({
                'error': 'You must be enrolled in this course to review it'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate data
        serializer = CourseReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if review already exists
        existing_review = CourseReview.find_by_student_and_course(student_id, course_id)
        
        if existing_review:
            # Update existing review
            existing_review.update(
                rating=serializer.validated_data['rating'],
                review_text=serializer.validated_data.get('review_text', ''),
                would_recommend=serializer.validated_data.get('would_recommend', True)
            )
            return Response({
                'message': 'Review updated successfully',
                'review': existing_review.to_dict()
            })
        else:
            # Create new review
            review = CourseReview.create(
                student_id=student_id,
                course_id=course_id,
                rating=serializer.validated_data['rating'],
                review_text=serializer.validated_data.get('review_text', ''),
                would_recommend=serializer.validated_data.get('would_recommend', True)
            )
            
            # Update course average rating
            rating_stats = CourseReview.get_course_average_rating(course_id)
            course.update(
                average_rating=rating_stats['average_rating'],
                total_reviews=rating_stats['total_reviews']
            )
            
            return Response({
                'message': 'Review submitted successfully',
                'review': review.to_dict()
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Failed to submit review',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_course_reviews(request, course_id):
    """
    Get all reviews for a course (public endpoint)
    """
    try:
        reviews = CourseReview.find_by_course(course_id)
        
        # Enrich with student names
        enriched_reviews = []
        for review in reviews:
            review_dict = review.to_dict()
            student = User.find_by_id(str(review.student_id))
            if student:
                review_dict['student_name'] = f"{student.first_name} {student.last_name}"
            enriched_reviews.append(review_dict)
        
        # Get rating statistics
        rating_stats = CourseReview.get_course_average_rating(course_id)
        
        return Response({
            'reviews': enriched_reviews,
            'statistics': rating_stats
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch reviews',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_instructor_review(request, instructor_id, course_id):
    """
    Submit or update an instructor review
    Student can only review instructors for courses they're enrolled in
    """
    try:
        student_id = str(request.user.id)
        
        # Validate instructor exists
        instructor = User.find_by_id(instructor_id)
        if not instructor or instructor.role != 'instructor':
            return Response({'error': 'Instructor not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate course exists and belongs to instructor
        course = Course.find_by_id(course_id)
        if not course:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if str(course.instructor_id) != instructor_id:
            return Response({
                'error': 'This instructor does not teach this course'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student is enrolled
        from courses.extended_models import Enrollment
        enrollment = Enrollment.find_one(student_id, course_id)
        if not enrollment:
            return Response({
                'error': 'You must be enrolled in this course to review the instructor'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate data
        serializer = InstructorReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if review already exists
        existing_review = InstructorReview.find_by_student_and_instructor(
            student_id, instructor_id, course_id
        )
        
        if existing_review:
            # Update existing review
            existing_review.update(
                rating=serializer.validated_data['rating'],
                review_text=serializer.validated_data.get('review_text', ''),
                teaching_quality=serializer.validated_data.get('teaching_quality', 0),
                communication=serializer.validated_data.get('communication', 0),
                course_content=serializer.validated_data.get('course_content', 0)
            )
            return Response({
                'message': 'Instructor review updated successfully',
                'review': existing_review.to_dict()
            })
        else:
            # Create new review
            review = InstructorReview.create(
                student_id=student_id,
                instructor_id=instructor_id,
                course_id=course_id,
                rating=serializer.validated_data['rating'],
                review_text=serializer.validated_data.get('review_text', ''),
                teaching_quality=serializer.validated_data.get('teaching_quality', 0),
                communication=serializer.validated_data.get('communication', 0),
                course_content=serializer.validated_data.get('course_content', 0)
            )
            
            return Response({
                'message': 'Instructor review submitted successfully',
                'review': review.to_dict()
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Failed to submit instructor review',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_instructor_reviews(request, instructor_id):
    """
    Get all reviews for an instructor (public endpoint)
    """
    try:
        reviews = InstructorReview.find_by_instructor(instructor_id)
        
        # Enrich with student and course names
        enriched_reviews = []
        for review in reviews:
            review_dict = review.to_dict()
            student = User.find_by_id(str(review.student_id))
            course = Course.find_by_id(str(review.course_id))
            if student:
                review_dict['student_name'] = f"{student.first_name} {student.last_name}"
            if course:
                review_dict['course_title'] = course.title
            enriched_reviews.append(review_dict)
        
        # Get rating statistics
        rating_stats = InstructorReview.get_instructor_average_rating(instructor_id)
        
        return Response({
            'reviews': enriched_reviews,
            'statistics': rating_stats
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to fetch instructor reviews',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
