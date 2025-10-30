"""
URL configuration for certifications app
"""
from django.urls import path
from certifications.views import (
    # Instructor endpoints
    CertificationCreateView,
    CertificationUpdateView,
    CertificationDeleteView,
    CertificationStepCreateView,
    CertificationStepUpdateView,
    CertificationStepDeleteView,
    CertificationStudentsProgressView,
    
    # Student endpoints
    AvailableCertificationsView,
    CertificationEnrollView,
    CertificationStepsView,
    CompleteStepView,
    SubmitExamView,
    MyProgressView,
    MyBadgesView,
    
    # Public endpoints
    VerifyBadgeView,
    AIRecommendationsView,
    InstructorCertificationRecommendationsView
)

urlpatterns = [
    # Instructor endpoints (role: instructor only)
    path('create/', CertificationCreateView.as_view(), name='certification-create'),
    path('<str:certification_id>/update/', CertificationUpdateView.as_view(), name='certification-update'),
    path('<str:certification_id>/delete/', CertificationDeleteView.as_view(), name='certification-delete'),
    path('<str:certification_id>/steps/add/', CertificationStepCreateView.as_view(), name='certification-step-create'),
    path('steps/<str:step_id>/update/', CertificationStepUpdateView.as_view(), name='certification-step-update'),
    path('steps/<str:step_id>/delete/', CertificationStepDeleteView.as_view(), name='certification-step-delete'),
    path('<str:certification_id>/students/progress/', CertificationStudentsProgressView.as_view(), name='certification-students-progress'),
    path('instructor/recommendations/', InstructorCertificationRecommendationsView.as_view(), name='instructor-cert-recommendations'),
    
    # Student endpoints
    path('available/', AvailableCertificationsView.as_view(), name='certifications-available'),
    path('<str:certification_id>/enroll/', CertificationEnrollView.as_view(), name='certification-enroll'),
    path('<str:certification_id>/steps/', CertificationStepsView.as_view(), name='certification-steps'),
    path('steps/complete/', CompleteStepView.as_view(), name='step-complete'),
    path('<str:certification_id>/exam/submit/', SubmitExamView.as_view(), name='exam-submit'),
    path('my-progress/', MyProgressView.as_view(), name='my-progress'),
    path('my-badges/', MyBadgesView.as_view(), name='my-badges'),
    
    # Public endpoints
    path('verify/<str:verification_code>/', VerifyBadgeView.as_view(), name='verify-badge'),
    path('ai-recommendations/', AIRecommendationsView.as_view(), name='ai-recommendations'),
]
