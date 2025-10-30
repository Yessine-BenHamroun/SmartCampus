"""
Course API views for managing courses, enrollments, and reviews.
This module provides API endpoints for course CRUD operations, 
student enrollments, progress tracking, and course reviews.
"""
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from bson import ObjectId

from courses.models import Course, Enrollment, Review
from courses.serializers import (
    CourseSerializer,
    EnrollmentSerializer,
    ReviewSerializer,
    UpdateProgressSerializer
)
from users.models import User


class CourseListView(APIView):
    """List all courses or create a new course"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all courses with optional filters"""
        try:
            # Get query parameters
            category = request.query_params.get('category')
            difficulty = request.query_params.get('difficulty')
            is_featured = request.query_params.get('featured')
            search = request.query_params.get('search')
            skip = int(request.query_params.get('skip', 0))
            limit = int(request.query_params.get('limit', 20))
            
            # Build filters
            filters = {'is_published': True}
            if category:
                filters['category'] = category
            if difficulty:
                filters['difficulty_level'] = difficulty
            if is_featured:
                filters['is_featured'] = is_featured.lower() == 'true'
            if search:
                filters['$or'] = [
                    {'title': {'$regex': search, '$options': 'i'}},
                    {'description': {'$regex': search, '$options': 'i'}}
                ]
            
            courses = Course.find_all(filters, skip, limit)
            
            # Get instructor details for each course
            courses_data = []
            for course in courses:
                course_dict = course.to_dict()
                if course.instructor_id:
                    instructor = User.find_by_id(course.instructor_id)
                    if instructor:
                        course_dict['instructor'] = {
                            'id': str(instructor.id),
                            'name': f"{instructor.first_name} {instructor.last_name}",
                            'email': instructor.email,
                            'profile_image': instructor.profile_image
                        }
                courses_data.append(course_dict)
            
            return Response({
                'count': len(courses_data),
                'courses': courses_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch courses',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create a new course (instructor only)"""
        try:
            # Check if user is instructor
            user_id = request.user.get('user_id')
            user = User.find_by_id(user_id)
            
            if not user or user.role not in ['instructor', 'admin']:
                return Response({
                    'error': 'Only instructors can create courses'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = CourseSerializer(data=request.data)
            
            if serializer.is_valid():
                course_data = serializer.validated_data.copy()
                course_data['instructor_id'] = ObjectId(user_id)
                
                course = Course.create(**course_data)
                
                return Response({
                    'message': 'Course created successfully',
                    'course': course.to_dict()
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to create course',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseDetailView(APIView):
    """Get, update, or delete a specific course"""
    permission_classes = [AllowAny]
    
    def get(self, request, course_id):
        """Get course details"""
        try:
            course = Course.find_by_id(course_id)
            
            if not course:
                return Response({
                    'error': 'Course not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            course_dict = course.to_dict()
            
            # Get instructor details
            if course.instructor_id:
                instructor = User.find_by_id(course.instructor_id)
                if instructor:
                    course_dict['instructor'] = {
                        'id': str(instructor.id),
                        'name': f"{instructor.first_name} {instructor.last_name}",
                        'email': instructor.email,
                        'bio': instructor.bio,
                        'profile_image': instructor.profile_image
                    }
            
            # Get reviews
            reviews = Review.find_by_course(course_id)
            course_dict['reviews'] = [review.to_dict() for review in reviews]
            
            return Response({
                'course': course_dict
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch course',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, course_id):
        """Update course (instructor only)"""
        try:
            course = Course.find_by_id(course_id)
            
            if not course:
                return Response({
                    'error': 'Course not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user is the course instructor
            user_id = request.user.get('user_id')
            if str(course.instructor_id) != user_id:
                return Response({
                    'error': 'Only course instructor can update this course'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = CourseSerializer(data=request.data, partial=True)
            
            if serializer.is_valid():
                course.update(**serializer.validated_data)
                
                return Response({
                    'message': 'Course updated successfully',
                    'course': course.to_dict()
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to update course',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, course_id):
        """Delete course (instructor only)"""
        try:
            course = Course.find_by_id(course_id)
            
            if not course:
                return Response({
                    'error': 'Course not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user is the course instructor
            user_id = request.user.get('user_id')
            if str(course.instructor_id) != user_id:
                return Response({
                    'error': 'Only course instructor can delete this course'
                }, status=status.HTTP_403_FORBIDDEN)
            
            course.delete()
            
            return Response({
                'message': 'Course deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to delete course',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EnrollCourseView(APIView):
    """Enroll in a course"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id):
        """Enroll student in course"""
        try:
            student_id = request.user.get('user_id')
            
            # Check if course exists
            course = Course.find_by_id(course_id)
            if not course:
                return Response({
                    'error': 'Course not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if already enrolled
            existing = Enrollment.find_one(student_id, course_id)
            if existing:
                return Response({
                    'error': 'Already enrolled in this course'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create enrollment
            enrollment = Enrollment.create(
                student_id=ObjectId(student_id),
                course_id=ObjectId(course_id)
            )
            
            # Update course enrolled count
            course.update(enrolled_count=course.enrolled_count + 1)
            
            return Response({
                'message': 'Successfully enrolled in course',
                'enrollment': enrollment.to_dict()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Failed to enroll',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyEnrollmentsView(APIView):
    """Get student's enrollments"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all enrollments for logged-in student"""
        try:
            student_id = request.user.get('user_id')
            enrollments = Enrollment.find_by_student(student_id)
            
            enrollments_data = []
            for enrollment in enrollments:
                enrollment_dict = enrollment.to_dict()
                
                # Get course details
                course = Course.find_by_id(enrollment.course_id)
                if course:
                    enrollment_dict['course'] = course.to_dict()
                
                enrollments_data.append(enrollment_dict)
            
            return Response({
                'count': len(enrollments_data),
                'enrollments': enrollments_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch enrollments',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateProgressView(APIView):
    """Update course progress"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request, course_id):
        """Update progress for a course"""
        try:
            student_id = request.user.get('user_id')
            
            enrollment = Enrollment.find_one(student_id, course_id)
            if not enrollment:
                return Response({
                    'error': 'Not enrolled in this course'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = UpdateProgressSerializer(data=request.data)
            
            if serializer.is_valid():
                progress = serializer.validated_data['progress']
                
                update_data = {'progress': progress}
                if progress >= 100:
                    update_data['completed'] = True
                    update_data['completed_at'] = datetime.utcnow()
                
                enrollment.update(**update_data)
                
                return Response({
                    'message': 'Progress updated successfully',
                    'enrollment': enrollment.to_dict()
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to update progress',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseReviewsView(APIView):
    """Get or create course reviews"""
    permission_classes = [AllowAny]
    
    def get(self, request, course_id):
        """Get all reviews for a course"""
        try:
            reviews = Review.find_by_course(course_id)
            
            reviews_data = []
            for review in reviews:
                review_dict = review.to_dict()
                
                # Get student details
                student = User.find_by_id(review.student_id)
                if student:
                    review_dict['student'] = {
                        'id': str(student.id),
                        'name': f"{student.first_name} {student.last_name}",
                        'profile_image': student.profile_image
                    }
                
                reviews_data.append(review_dict)
            
            return Response({
                'count': len(reviews_data),
                'reviews': reviews_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch reviews',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, course_id):
        """Create a review for a course"""
        try:
            student_id = request.user.get('user_id')
            
            # Check if enrolled
            enrollment = Enrollment.find_one(student_id, course_id)
            if not enrollment:
                return Response({
                    'error': 'Must be enrolled to review this course'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = ReviewSerializer(data=request.data)
            
            if serializer.is_valid():
                review_data = serializer.validated_data.copy()
                review_data['student_id'] = ObjectId(student_id)
                review_data['course_id'] = ObjectId(course_id)
                
                review = Review.create(**review_data)
                
                # Update course rating
                all_reviews = Review.find_by_course(course_id)
                avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
                
                course = Course.find_by_id(course_id)
                course.update(
                    rating=avg_rating,
                    reviews_count=len(all_reviews)
                )
                
                return Response({
                    'message': 'Review created successfully',
                    'review': review.to_dict()
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to create review',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FeaturedCoursesView(APIView):
    """Get featured courses"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get featured courses"""
        try:
            limit = int(request.query_params.get('limit', 6))
            courses = Course.find_featured(limit)
            
            courses_data = []
            for course in courses:
                course_dict = course.to_dict()
                
                # Get instructor details
                if course.instructor_id:
                    instructor = User.find_by_id(course.instructor_id)
                    if instructor:
                        course_dict['instructor'] = {
                            'id': str(instructor.id),
                            'name': f"{instructor.first_name} {instructor.last_name}",
                            'profile_image': instructor.profile_image
                        }
                
                courses_data.append(course_dict)
            
            return Response({
                'count': len(courses_data),
                'courses': courses_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch featured courses',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InstructorCoursesView(APIView):
    """Get courses by instructor"""
    permission_classes = [AllowAny]
    
    def get(self, request, instructor_id):
        """Get all courses by an instructor"""
        try:
            courses = Course.find_by_instructor(instructor_id)
            
            courses_data = [course.to_dict() for course in courses if course.is_published]
            
            return Response({
                'count': len(courses_data),
                'courses': courses_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch instructor courses',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
