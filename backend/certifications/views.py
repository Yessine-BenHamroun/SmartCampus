"""
Certification Views
API endpoints for certification management
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime

from certifications.models import (
    Certification, CertificationStep, StudentProgress, EarnedBadge
)
from certifications.serializers import (
    CertificationSerializer, CertificationStepSerializer,
    StudentProgressSerializer, EarnedBadgeSerializer,
    StepCompletionSerializer, ExamSubmissionSerializer
)
from users.models import User


class IsInstructor(IsAuthenticated):
    """Permission class to check if user is an instructor"""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Get user email from JWT token
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else getattr(request.user, 'email', None)
        
        if not user_email:
            return False
        
        user = User.find_by_email(user_email)
        return user and user.role == 'instructor'


# ============= INSTRUCTOR ENDPOINTS =============

class CertificationCreateView(APIView):
    """Create a new certification (Instructor only)"""
    permission_classes = [IsInstructor]
    
    def post(self, request):
        """Create certification"""
        serializer = CertificationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Get instructor ID from token
            user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
            user = User.find_by_email(user_email)
            
            # Create certification
            certification = Certification.create(
                course_id=serializer.validated_data['course_id'],
                instructor_id=str(user.id),
                title=serializer.validated_data['title'],
                description=serializer.validated_data['description'],
                badge_image=serializer.validated_data.get('badge_image'),
                passing_score=serializer.validated_data.get('passing_score', 70),
                is_active=serializer.validated_data.get('is_active', True)
            )
            
            return Response({
                'message': 'Certification created successfully',
                'certification': certification.to_dict()
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CertificationUpdateView(APIView):
    """Update certification (Instructor only)"""
    permission_classes = [IsInstructor]
    
    def put(self, request, certification_id):
        """Update certification"""
        certification = Certification.find_by_id(certification_id)
        
        if not certification:
            return Response({
                'error': 'Certification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify instructor owns this certification
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        if str(certification.instructor_id) != str(user.id):
            return Response({
                'error': 'You do not have permission to update this certification'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CertificationSerializer(data=request.data, partial=True)
        
        if serializer.is_valid():
            certification.update(**serializer.validated_data)
            
            return Response({
                'message': 'Certification updated successfully',
                'certification': certification.to_dict()
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CertificationDeleteView(APIView):
    """Delete certification (Instructor only)"""
    permission_classes = [IsInstructor]
    
    def delete(self, request, certification_id):
        """Delete certification"""
        certification = Certification.find_by_id(certification_id)
        
        if not certification:
            return Response({
                'error': 'Certification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify instructor owns this certification
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        if str(certification.instructor_id) != str(user.id):
            return Response({
                'error': 'You do not have permission to delete this certification'
            }, status=status.HTTP_403_FORBIDDEN)
        
        certification.delete()
        
        return Response({
            'message': 'Certification deleted successfully'
        }, status=status.HTTP_200_OK)


class CertificationStepCreateView(APIView):
    """Add step to certification (Instructor only)"""
    permission_classes = [IsInstructor]
    
    def post(self, request, certification_id):
        """Add step to certification"""
        certification = Certification.find_by_id(certification_id)
        
        if not certification:
            return Response({
                'error': 'Certification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify instructor owns this certification
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        if str(certification.instructor_id) != str(user.id):
            return Response({
                'error': 'You do not have permission to add steps to this certification'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CertificationStepSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create step
            step = CertificationStep.create(
                certification_id=certification_id,
                step_number=serializer.validated_data['step_number'],
                step_type=serializer.validated_data['step_type'],
                title=serializer.validated_data['title'],
                description=serializer.validated_data['description'],
                content=serializer.validated_data.get('content', {}),
                duration_minutes=serializer.validated_data.get('duration_minutes', 0),
                is_mandatory=serializer.validated_data.get('is_mandatory', True),
                passing_criteria=serializer.validated_data.get('passing_criteria', {})
            )
            
            return Response({
                'message': 'Step added successfully',
                'step': step.to_dict()
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CertificationStepUpdateView(APIView):
    """Update certification step (Instructor only)"""
    permission_classes = [IsInstructor]
    
    def put(self, request, step_id):
        """Update step"""
        step = CertificationStep.find_by_id(step_id)
        
        if not step:
            return Response({
                'error': 'Step not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify instructor owns the certification
        certification = Certification.find_by_id(step.certification_id)
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        if str(certification.instructor_id) != str(user.id):
            return Response({
                'error': 'You do not have permission to update this step'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CertificationStepSerializer(data=request.data, partial=True)
        
        if serializer.is_valid():
            step.update(**serializer.validated_data)
            
            return Response({
                'message': 'Step updated successfully',
                'step': step.to_dict()
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CertificationStepDeleteView(APIView):
    """Delete certification step (Instructor only)"""
    permission_classes = [IsInstructor]
    
    def delete(self, request, step_id):
        """Delete step"""
        step = CertificationStep.find_by_id(step_id)
        
        if not step:
            return Response({
                'error': 'Step not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify instructor owns the certification
        certification = Certification.find_by_id(step.certification_id)
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        if str(certification.instructor_id) != str(user.id):
            return Response({
                'error': 'You do not have permission to delete this step'
            }, status=status.HTTP_403_FORBIDDEN)
        
        step.delete()
        
        return Response({
            'message': 'Step deleted successfully'
        }, status=status.HTTP_200_OK)


class CertificationStudentsProgressView(APIView):
    """View all student progress for a certification (Instructor only)"""
    permission_classes = [IsInstructor]
    
    def get(self, request, certification_id):
        """Get student progress"""
        certification = Certification.find_by_id(certification_id)
        
        if not certification:
            return Response({
                'error': 'Certification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify instructor owns this certification
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        if str(certification.instructor_id) != str(user.id):
            return Response({
                'error': 'You do not have permission to view this data'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all student progress
        progress_records = StudentProgress.find_by_certification(certification_id)
        
        return Response({
            'certification': certification.to_dict(),
            'student_progress': [record.to_dict() for record in progress_records]
        }, status=status.HTTP_200_OK)


# ============= STUDENT ENDPOINTS =============

class AvailableCertificationsView(APIView):
    """Get available certifications for enrolled courses (Student)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get available certifications"""
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        # TODO: Get enrolled courses for student
        # For now, return all active certifications
        # In production, filter by student's enrolled courses
        
        from config.mongodb import get_database
        db = get_database()
        certifications_data = db['certifications'].find({'is_active': True})
        
        certifications = [Certification(**cert).to_dict() for cert in certifications_data]
        
        return Response({
            'certifications': certifications
        }, status=status.HTTP_200_OK)


class CertificationEnrollView(APIView):
    """Enroll in a certification (Student)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, certification_id):
        """Enroll in certification"""
        certification = Certification.find_by_id(certification_id)
        
        if not certification:
            return Response({
                'error': 'Certification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        # Check if already enrolled
        existing_progress = StudentProgress.find_by_student_and_certification(
            str(user.id), certification_id
        )
        
        if existing_progress:
            return Response({
                'message': 'Already enrolled in this certification',
                'progress': existing_progress.to_dict()
            }, status=status.HTTP_200_OK)
        
        # Create progress record
        progress = StudentProgress.create(
            student_id=str(user.id),
            certification_id=certification_id,
            course_id=certification.course_id
        )
        
        return Response({
            'message': 'Successfully enrolled in certification',
            'progress': progress.to_dict()
        }, status=status.HTTP_201_CREATED)


class CertificationStepsView(APIView):
    """Get all steps for a certification (Student)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, certification_id):
        """Get certification steps"""
        certification = Certification.find_by_id(certification_id)
        
        if not certification:
            return Response({
                'error': 'Certification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        steps = CertificationStep.find_by_certification(certification_id)
        
        return Response({
            'certification': certification.to_dict(),
            'steps': [step.to_dict() for step in steps]
        }, status=status.HTTP_200_OK)


class CompleteStepView(APIView):
    """Mark a step as completed (Student)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Complete a step"""
        serializer = StepCompletionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        step_id = serializer.validated_data['step_id']
        score = serializer.validated_data.get('score')
        
        step = CertificationStep.find_by_id(step_id)
        
        if not step:
            return Response({
                'error': 'Step not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get student progress
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        progress = StudentProgress.find_by_student_and_certification(
            str(user.id), step.certification_id
        )
        
        if not progress:
            return Response({
                'error': 'Not enrolled in this certification'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Complete the step
        progress.complete_step(step_id, score)
        
        return Response({
            'message': 'Step completed successfully',
            'progress': progress.to_dict()
        }, status=status.HTTP_200_OK)


class SubmitExamView(APIView):
    """Submit exam and calculate score (Student)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, certification_id):
        """Submit exam"""
        serializer = ExamSubmissionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        certification = Certification.find_by_id(certification_id)
        
        if not certification:
            return Response({
                'error': 'Certification not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get student progress
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        progress = StudentProgress.find_by_student_and_certification(
            str(user.id), certification_id
        )
        
        if not progress:
            return Response({
                'error': 'Not enrolled in this certification'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get exam step (last step)
        steps = CertificationStep.find_by_certification(certification_id)
        exam_step = next((s for s in steps if s.step_type == 'exam'), None)
        
        if not exam_step:
            return Response({
                'error': 'No exam found for this certification'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate score (auto-grade MCQ/True-False)
        answers = serializer.validated_data['answers']
        exam_content = exam_step.content
        questions = exam_content.get('questions', [])
        
        correct_count = 0
        total_points = 0
        earned_points = 0
        
        for i, question in enumerate(questions):
            total_points += question.get('points', 1)
            student_answer = answers.get(str(i))
            correct_answer = question.get('correct_answer')
            
            if student_answer == correct_answer:
                correct_count += 1
                earned_points += question.get('points', 1)
        
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        
        # Update progress
        progress.exam_attempts += 1
        progress.exam_score = score
        
        # Check if passed
        if score >= certification.passing_score:
            progress.status = 'completed'
            progress.badge_earned = True
            progress.completed_at = datetime.utcnow()
            
            # Create earned badge
            badge = EarnedBadge.create(
                student_id=str(user.id),
                certification_id=certification_id,
                course_id=certification.course_id,
                final_score=score
            )
            
            # Send email notification
            try:
                send_mail(
                    subject=f'Congratulations! You earned: {certification.title}',
                    message=f'You have successfully completed {certification.title} with a score of {score:.2f}%.\n\nVerification Code: {badge.verification_code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Failed to send badge email: {e}")
            
            progress.update(
                exam_attempts=progress.exam_attempts,
                exam_score=score,
                status='completed',
                badge_earned=True,
                completed_at=progress.completed_at
            )
            
            return Response({
                'message': 'Congratulations! You passed the exam!',
                'score': score,
                'passed': True,
                'badge': badge.to_dict(),
                'progress': progress.to_dict()
            }, status=status.HTTP_200_OK)
        else:
            # Failed
            max_attempts = exam_content.get('max_attempts', 3)
            
            if progress.exam_attempts >= max_attempts:
                progress.status = 'failed'
            
            progress.update(
                exam_attempts=progress.exam_attempts,
                exam_score=score,
                status=progress.status
            )
            
            return Response({
                'message': 'Exam not passed. Please try again.',
                'score': score,
                'passed': False,
                'attempts_remaining': max(0, max_attempts - progress.exam_attempts),
                'progress': progress.to_dict()
            }, status=status.HTTP_200_OK)


class MyProgressView(APIView):
    """Get student's certification progress (Student)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get my progress"""
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        progress_records = StudentProgress.find_by_student(str(user.id))
        
        return Response({
            'progress': [record.to_dict() for record in progress_records]
        }, status=status.HTTP_200_OK)


class MyBadgesView(APIView):
    """Get student's earned badges (Student)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get my badges"""
        user_email = request.user.get('user_email') if isinstance(request.user, dict) else request.user.email
        user = User.find_by_email(user_email)
        
        badges = EarnedBadge.find_by_student(str(user.id))
        
        return Response({
            'badges': [badge.to_dict() for badge in badges]
        }, status=status.HTTP_200_OK)


# ============= PUBLIC ENDPOINTS =============

class VerifyBadgeView(APIView):
    """Verify a badge by verification code (Public)"""
    permission_classes = [AllowAny]
    
    def get(self, request, verification_code):
        """Verify badge"""
        badge = EarnedBadge.find_by_verification_code(verification_code)
        
        if not badge:
            return Response({
                'error': 'Invalid verification code',
                'valid': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get certification and student details
        certification = Certification.find_by_id(badge.certification_id)
        student = User.find_by_id(badge.student_id)
        
        return Response({
            'valid': True,
            'badge': badge.to_dict(),
            'certification': certification.to_dict() if certification else None,
            'student': {
                'name': f"{student.first_name} {student.last_name}" if student else 'Unknown',
                'email': student.email if student else None
            } if student else None
        }, status=status.HTTP_200_OK)
