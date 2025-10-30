"""
Serializers for Certification app
"""
from rest_framework import serializers


class CertificationSerializer(serializers.Serializer):
    """Serializer for Certification"""
    id = serializers.CharField(read_only=True)
    course_id = serializers.CharField(required=True)
    instructor_id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=True)
    badge_image = serializers.URLField(required=False, allow_null=True)
    passing_score = serializers.IntegerField(default=70, min_value=0, max_value=100)
    is_active = serializers.BooleanField(default=True)
    total_steps = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CertificationStepSerializer(serializers.Serializer):
    """Serializer for Certification Step"""
    id = serializers.CharField(read_only=True)
    certification_id = serializers.CharField(required=True)
    step_number = serializers.IntegerField(required=True, min_value=1)
    step_type = serializers.ChoiceField(
        choices=['video', 'reading', 'quiz', 'assignment', 'exam'],
        required=True
    )
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=True)
    content = serializers.JSONField(required=False, default=dict)
    duration_minutes = serializers.IntegerField(default=0, min_value=0)
    is_mandatory = serializers.BooleanField(default=True)
    passing_criteria = serializers.JSONField(required=False, default=dict)
    created_at = serializers.DateTimeField(read_only=True)
    
    def validate_step_type(self, value):
        """Validate step type"""
        allowed_types = ['video', 'reading', 'quiz', 'assignment', 'exam']
        if value not in allowed_types:
            raise serializers.ValidationError(f"Step type must be one of {allowed_types}")
        return value


class VideoStepContentSerializer(serializers.Serializer):
    """Serializer for video step content"""
    video_url = serializers.URLField(required=True)
    minimum_watch_time = serializers.IntegerField(default=0, min_value=0)
    transcript = serializers.CharField(required=False, allow_blank=True)


class ReadingStepContentSerializer(serializers.Serializer):
    """Serializer for reading step content"""
    content_text = serializers.CharField(required=False, allow_blank=True)
    pdf_url = serializers.URLField(required=False, allow_null=True)
    estimated_time = serializers.IntegerField(default=10, min_value=1)


class QuizQuestionSerializer(serializers.Serializer):
    """Serializer for quiz question"""
    question_text = serializers.CharField(required=True)
    question_type = serializers.ChoiceField(
        choices=['mcq', 'true_false', 'multiple_select'],
        default='mcq'
    )
    options = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        min_length=2
    )
    correct_answer = serializers.CharField(required=True)
    points = serializers.IntegerField(default=1, min_value=1)


class QuizStepContentSerializer(serializers.Serializer):
    """Serializer for quiz step content"""
    questions = QuizQuestionSerializer(many=True, required=True)
    time_limit_minutes = serializers.IntegerField(default=30, min_value=1)
    passing_score = serializers.IntegerField(default=70, min_value=0, max_value=100)
    allow_retakes = serializers.BooleanField(default=True)
    max_attempts = serializers.IntegerField(default=3, min_value=1)


class AssignmentStepContentSerializer(serializers.Serializer):
    """Serializer for assignment step content"""
    instructions = serializers.CharField(required=True)
    max_file_size_mb = serializers.IntegerField(default=10, min_value=1, max_value=100)
    allowed_file_types = serializers.ListField(
        child=serializers.CharField(),
        default=list
    )
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    grading_rubric = serializers.CharField(required=False, allow_blank=True)


class ExamStepContentSerializer(serializers.Serializer):
    """Serializer for exam step content"""
    questions = QuizQuestionSerializer(many=True, required=True)
    time_limit_minutes = serializers.IntegerField(required=True, min_value=30)
    passing_score = serializers.IntegerField(default=70, min_value=0, max_value=100)
    max_attempts = serializers.IntegerField(default=3, min_value=1)
    randomize_questions = serializers.BooleanField(default=True)
    show_results_immediately = serializers.BooleanField(default=False)


class StudentProgressSerializer(serializers.Serializer):
    """Serializer for Student Progress"""
    id = serializers.CharField(read_only=True)
    student_id = serializers.CharField(required=True)
    certification_id = serializers.CharField(required=True)
    course_id = serializers.CharField(required=True)
    current_step = serializers.IntegerField(default=0)
    completed_steps = serializers.ListField(child=serializers.CharField(), default=list)
    step_scores = serializers.JSONField(default=dict)
    exam_attempts = serializers.IntegerField(default=0)
    exam_score = serializers.FloatField(default=0)
    status = serializers.ChoiceField(
        choices=['not_started', 'in_progress', 'completed', 'failed'],
        default='not_started'
    )
    started_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    badge_earned = serializers.BooleanField(default=False)


class EarnedBadgeSerializer(serializers.Serializer):
    """Serializer for Earned Badge"""
    id = serializers.CharField(read_only=True)
    student_id = serializers.CharField(required=True)
    certification_id = serializers.CharField(required=True)
    course_id = serializers.CharField(required=True)
    final_score = serializers.FloatField(required=True)
    verification_code = serializers.CharField(read_only=True)
    badge_url = serializers.URLField(required=False, allow_null=True)
    earned_at = serializers.DateTimeField(read_only=True)


class StepCompletionSerializer(serializers.Serializer):
    """Serializer for completing a step"""
    step_id = serializers.CharField(required=True)
    score = serializers.FloatField(required=False, allow_null=True)
    submission_data = serializers.JSONField(required=False, default=dict)


class ExamSubmissionSerializer(serializers.Serializer):
    """Serializer for exam submission"""
    answers = serializers.JSONField(required=True)
    time_taken_minutes = serializers.IntegerField(required=True, min_value=0)
