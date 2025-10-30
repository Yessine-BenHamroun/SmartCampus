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
from courses.models import Course, Enrollment
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
def get_course_status(request, course_id):
    """
    Get course status with availability flags for quizzes and assignments
    Returns which lessons are completed and which quizzes/assignments are available
    """
    try:
        from bson import ObjectId
        student_id = str(request.user.id)
        
        # Get course
        course = Course.find_by_id(course_id)
        if not course:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get progress
        progress = StudentProgress.find_by_student_and_course(student_id, course_id)
        
        # Get all modules and lessons
        from courses.extended_models import Module, Lesson, Quiz, Assignment
        modules = Module.find_by_course(course_id)
        
        lessons_data = []
        for module in modules:
            lessons = Lesson.find_by_module(str(module.id))
            for lesson in lessons:
                lesson_id_str = str(lesson.id)
                is_completed = ObjectId(lesson.id) in (progress.lessons_completed if progress else [])
                
                # Get quiz for this lesson if it exists
                quiz = Quiz.find_by_lesson(lesson_id_str)
                can_take_quiz = is_completed and quiz is not None and quiz.is_published
                
                lessons_data.append({
                    'id': lesson_id_str,
                    'title': lesson.title,
                    'module_id': str(module.id),
                    'completed': is_completed,
                    'can_take_quiz': can_take_quiz,
                    'quiz_id': str(quiz.id) if quiz else None,
                    'duration_minutes': getattr(lesson, 'duration_minutes', 0)
                })
        
        # Check if all lessons are completed
        all_lessons_completed = all(l['completed'] for l in lessons_data) if lessons_data else False
        
        # Get assignments for this course
        assignments = Assignment.find_by_course(course_id)
        published_assignments = [a for a in assignments if a.is_published]
        
        # Assignment is available only if all lessons are completed
        can_take_assignment = all_lessons_completed and len(published_assignments) > 0
        
        return Response({
            'course_id': course_id,
            'course_title': course.title,
            'lessons': lessons_data,
            'course_completed': all_lessons_completed,
            'can_take_assignment': can_take_assignment,
            'assignments': [
                {
                    'id': str(a.id),
                    'title': a.title,
                    'available': can_take_assignment
                }
                for a in published_assignments
            ],
            'completion_percentage': progress.completion_percentage if progress else 0
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Error in get_course_status: {str(e)}")
        print(traceback.format_exc())
        return Response({
            'error': 'Failed to fetch course status',
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

        # Fetch all recorded progress entries for this student
        progress_records = StudentProgress.find_by_student(student_id)
        progress_map = {}
        for progress in progress_records:
            progress_dict = progress.to_dict()

            lessons_completed = progress_dict.get('lessons_completed') or []
            quizzes_completed = progress_dict.get('quizzes_completed') or []
            assignments_completed = progress_dict.get('assignments_completed') or []
            time_spent_minutes = progress_dict.get('time_spent_minutes') or 0
            completion_percentage = progress_dict.get('completion_percentage') or 0

            course_id = progress_dict.get('course_id')
            enrollment_id = progress_dict.get('enrollment_id')

            progress_map[course_id] = {
                'progress_id': progress_dict.get('_id'),
                'course_id': course_id,
                'enrollment_id': enrollment_id,
                'completion_percentage': float(completion_percentage or 0),
                'time_spent_minutes': int(time_spent_minutes or 0),
                'lessons_completed': lessons_completed,
                'quizzes_completed': quizzes_completed,
                'assignments_completed': assignments_completed,
                'last_accessed': progress_dict.get('last_accessed'),
            }

        # Fetch enrollments to ensure every course the student is taking appears
        enrollments = Enrollment.find_by_student(student_id)
        enriched_progress = []
        processed_course_ids = set()

        for enrollment in enrollments:
            course_id = str(enrollment.course_id)
            processed_course_ids.add(course_id)

            course = Course.find_by_id(course_id)
            course_title = course.title if course else 'Course'
            course_thumbnail = getattr(course, 'thumbnail_url', None) if course else None

            base_entry = progress_map.get(course_id, {
                'progress_id': None,
                'course_id': course_id,
                'enrollment_id': str(enrollment.id) if enrollment.id else None,
                'completion_percentage': 0.0,
                'time_spent_minutes': 0,
                'lessons_completed': [],
                'quizzes_completed': [],
                'assignments_completed': [],
                'last_accessed': None,
            })

            entry = {
                **base_entry,
                'course_title': course_title,
                'course_thumbnail': course_thumbnail,
                'enrolled_at': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
                'enrollment_progress': float(enrollment.progress or 0),
                'certificate_issued': bool(enrollment.certificate_issued),
            }

            entry['lessons_completed_count'] = len(entry['lessons_completed'] or [])
            entry['quizzes_completed_count'] = len(entry['quizzes_completed'] or [])
            entry['assignments_completed_count'] = len(entry['assignments_completed'] or [])
            entry['time_spent_hours'] = round(entry['time_spent_minutes'] / 60, 2) if entry['time_spent_minutes'] else 0

            enriched_progress.append(entry)

        # Include standalone progress entries that may not have an active enrollment (edge cases)
        for course_id, progress_entry in progress_map.items():
            if course_id in processed_course_ids:
                continue

            course = Course.find_by_id(course_id)
            course_title = course.title if course else 'Course'
            course_thumbnail = getattr(course, 'thumbnail_url', None) if course else None

            entry = {
                **progress_entry,
                'course_title': course_title,
                'course_thumbnail': course_thumbnail,
                'enrolled_at': None,
                'enrollment_progress': 0.0,
                'certificate_issued': False,
                'lessons_completed_count': len(progress_entry['lessons_completed'] or []),
                'quizzes_completed_count': len(progress_entry['quizzes_completed'] or []),
                'assignments_completed_count': len(progress_entry['assignments_completed'] or []),
                'time_spent_hours': round(progress_entry['time_spent_minutes'] / 60, 2) if progress_entry['time_spent_minutes'] else 0
            }
            enriched_progress.append(entry)

        total_minutes = sum(entry['time_spent_minutes'] for entry in enriched_progress)
        total_lessons = sum(entry['lessons_completed_count'] for entry in enriched_progress)
        total_quizzes = sum(entry['quizzes_completed_count'] for entry in enriched_progress)
        total_assignments = sum(entry['assignments_completed_count'] for entry in enriched_progress)
        average_completion = round(
            sum(entry['completion_percentage'] for entry in enriched_progress) / len(enriched_progress), 1
        ) if enriched_progress else 0.0

        return Response({
            'progress': enriched_progress,
            'total_courses': len(enriched_progress),
            'totals': {
                'time_spent_minutes': total_minutes,
                'time_spent_hours': round(total_minutes / 60, 2) if total_minutes else 0,
                'lessons_completed': total_lessons,
                'quizzes_completed': total_quizzes,
                'assignments_completed': total_assignments,
                'average_completion_percentage': average_completion,
            }
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
            enrollment = Enrollment.find_one(student_id, course_id)
            if not enrollment:
                return Response({'error': 'Not enrolled in this course'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            progress = StudentProgress.create(
                student_id=student_id,
                course_id=course_id,
                enrollment_id=str(enrollment.id)
            )
        
        # Mark lesson complete
        progress.mark_lesson_complete(lesson_id)
        
        # Update time spent if provided
        time_spent_minutes = request.data.get('time_spent_minutes', 0)
        if time_spent_minutes:
            current_time = getattr(progress, 'time_spent_minutes', 0) or 0
            progress.update(time_spent_minutes=current_time + time_spent_minutes)
        
        # Recalculate completion percentage - based only on lessons for simplicity
        from bson import ObjectId

        # Count total lessons in the course
        total_lessons = Lesson.get_collection().count_documents({'course_id': str(course_id)})
        
        # Calculate percentage based on lessons completed vs total lessons
        if total_lessons > 0:
            completed_percentage = (len(progress.lessons_completed) / total_lessons) * 100
            progress.update(completion_percentage=round(completed_percentage, 2))
        else:
            progress.update(completion_percentage=0.0)
        
        # Update enrollment progress to match StudentProgress
        enrollment = Enrollment.find_one(student_id, course_id)
        if enrollment:
            enrollment.update(progress=progress.completion_percentage)
        
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_course_feedback(request, course_id):
    """
    Submit feedback for a completed course
    """
    try:
        student_id = str(request.user.id)
        
        # Validate course exists
        course = Course.find_by_id(course_id)
        if not course:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if student completed the course
        progress = StudentProgress.find_by_student_and_course(student_id, course_id)
        if not progress or progress.completion_percentage < 100:
            return Response({'error': 'Course not completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if feedback already exists
        existing_feedback = CourseReview.find_by_student_and_course(student_id, course_id)
        if existing_feedback:
            return Response({'error': 'Feedback already submitted'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create feedback
        feedback = CourseReview.create(
            student_id=student_id,
            course_id=course_id,
            rating=request.data.get('rating', 5),
            review_text=request.data.get('comment', ''),
            would_recommend=request.data.get('recommend', True)
        )
        
        return Response({
            'message': 'Feedback submitted successfully',
            'feedback': feedback.to_dict()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Failed to submit feedback',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_feedbacks(request, course_id):
    """
    Get all feedbacks for a course (instructor only)
    """
    try:
        # Check if user is the course instructor
        course = Course.find_by_id(course_id)
        if not course or str(course.instructor_id) != str(request.user.id):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        feedbacks = CourseReview.find_by_course(course_id)
        feedbacks_data = [feedback.to_dict() for feedback in feedbacks]
        
        return Response({
            'feedbacks': feedbacks_data,
            'count': len(feedbacks_data)
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to load feedbacks',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_instructor_reviews(request, instructor_id):
    """
    Get all reviews for an instructor across all their courses
    """
    try:
        # Check if user is the instructor or an admin
        if str(request.user.id) != instructor_id and request.user.role != 'admin':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get all courses by this instructor
        courses = Course.find_by_instructor(instructor_id)
        course_ids = [str(course.id) for course in courses]
        
        # Get all reviews for these courses
        all_reviews = []
        for course_id in course_ids:
            reviews = CourseReview.find_by_course(course_id)
            for review in reviews:
                review_dict = review.to_dict()
                review_dict['course_title'] = next((c.title for c in courses if str(c.id) == course_id), 'Unknown Course')
                all_reviews.append(review_dict)
        
        # Get instructor review statistics
        total_reviews = len(all_reviews)
        average_rating = sum(r['rating'] for r in all_reviews) / total_reviews if total_reviews > 0 else 0
        
        return Response({
            'reviews': all_reviews,
            'statistics': {
                'total_reviews': total_reviews,
                'average_rating': round(average_rating, 1),
                'courses_count': len(courses)
            }
        })
        
    except Exception as e:
        return Response({
            'error': 'Failed to load instructor reviews',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
