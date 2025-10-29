"""
Course serializers
"""
from rest_framework import serializers


class CourseSerializer(serializers.Serializer):
    """Course serializer"""
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=True)
    short_description = serializers.CharField(required=False, allow_blank=True)
    instructor_id = serializers.CharField(required=True)
    category = serializers.ChoiceField(choices=[
        'Web Development', 'Data Science', 'Mobile Development', 'Design',
        'Business', 'Marketing', 'IT & Software', 'Personal Development'
    ])
    difficulty_level = serializers.ChoiceField(
        choices=['Beginner', 'Intermediate', 'Advanced', 'Expert'],
        default='Beginner'
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    duration_hours = serializers.IntegerField(default=0)
    thumbnail_image = serializers.CharField(required=False, allow_blank=True)
    preview_video = serializers.CharField(required=False, allow_blank=True)
    syllabus = serializers.ListField(required=False, default=list)
    requirements = serializers.ListField(required=False, default=list)
    learning_outcomes = serializers.ListField(required=False, default=list)
    language = serializers.CharField(default='English')
    is_published = serializers.BooleanField(default=False)
    is_featured = serializers.BooleanField(default=False)
    enrolled_count = serializers.IntegerField(read_only=True)
    rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class EnrollmentSerializer(serializers.Serializer):
    """Enrollment serializer"""
    id = serializers.CharField(read_only=True)
    student_id = serializers.CharField(read_only=True)
    course_id = serializers.CharField(required=True)
    enrolled_at = serializers.CharField(read_only=True)
    progress = serializers.FloatField(read_only=True)
    completed = serializers.BooleanField(read_only=True)
    completed_at = serializers.CharField(read_only=True)
    last_accessed = serializers.CharField(read_only=True)
    certificate_issued = serializers.BooleanField(read_only=True)


class ReviewSerializer(serializers.Serializer):
    """Review serializer"""
    id = serializers.CharField(read_only=True)
    course_id = serializers.CharField(required=True)
    student_id = serializers.CharField(read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5, required=True)
    comment = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class UpdateProgressSerializer(serializers.Serializer):
    """Update course progress"""
    progress = serializers.FloatField(min_value=0.0, max_value=100.0, required=True)


class QuizQuestionSerializer(serializers.Serializer):
    """Quiz question serializer"""
    question_text = serializers.CharField(required=True)
    options = serializers.ListField(child=serializers.CharField(), required=True)
    correct_answer = serializers.IntegerField(required=True)  # Index of correct option
    points = serializers.IntegerField(default=1)


class QuizSerializer(serializers.Serializer):
    """Quiz serializer"""
    id = serializers.CharField(read_only=True)
    lesson_id = serializers.CharField(required=True)
    course_id = serializers.CharField(required=True)
    instructor_id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    questions = QuizQuestionSerializer(many=True, required=True)
    passing_score = serializers.IntegerField(default=70)
    time_limit_minutes = serializers.IntegerField(default=0)
    max_attempts = serializers.IntegerField(default=0)
    shuffle_questions = serializers.BooleanField(default=False)
    show_correct_answers = serializers.BooleanField(default=True)
    is_published = serializers.BooleanField(default=False)
    is_ai_generated = serializers.BooleanField(default=False)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class QuizAttemptAnswerSerializer(serializers.Serializer):
    """Quiz attempt answer serializer"""
    question_index = serializers.IntegerField(required=True)
    selected_answer = serializers.IntegerField(required=True)


class QuizAttemptSerializer(serializers.Serializer):
    """Quiz attempt serializer"""
    id = serializers.CharField(read_only=True)
    quiz_id = serializers.CharField(required=True)
    student_id = serializers.CharField(read_only=True)
    course_id = serializers.CharField(required=True)
    lesson_id = serializers.CharField(required=True)
    answers = QuizAttemptAnswerSerializer(many=True, required=True)
    score = serializers.IntegerField(read_only=True)
    max_score = serializers.IntegerField(read_only=True)
    percentage = serializers.FloatField(read_only=True)
    passed = serializers.BooleanField(read_only=True)
    time_taken_minutes = serializers.IntegerField(required=True)
    started_at = serializers.CharField(read_only=True)
    completed_at = serializers.CharField(read_only=True)


class AssignmentQuestionSerializer(serializers.Serializer):
    """Assignment question serializer"""
    question_text = serializers.CharField(required=True)
    question_type = serializers.ChoiceField(choices=['mcq', 'true_false', 'short_answer'])
    options = serializers.ListField(child=serializers.CharField(), required=False)
    correct_answer = serializers.CharField(required=False)
    points = serializers.IntegerField(default=1)


class AssignmentSerializer(serializers.Serializer):
    """Assignment serializer"""
    id = serializers.CharField(read_only=True)
    course_id = serializers.CharField(required=True)
    instructor_id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    assignment_type = serializers.ChoiceField(choices=['coding', 'written', 'mixed'], default='written')
    questions = AssignmentQuestionSerializer(many=True, required=False)
    coding_problem = serializers.DictField(required=False)
    time_limit_minutes = serializers.IntegerField(default=60)
    max_attempts = serializers.IntegerField(default=1)
    passing_score = serializers.IntegerField(default=50)
    allow_copy_paste = serializers.BooleanField(default=False)
    allow_window_switch = serializers.BooleanField(default=False)
    max_warnings = serializers.IntegerField(default=3)
    is_published = serializers.BooleanField(default=False)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class AssignmentSubmissionSerializer(serializers.Serializer):
    """Assignment submission serializer"""
    id = serializers.CharField(read_only=True)
    assignment_id = serializers.CharField(required=True)
    student_id = serializers.CharField(read_only=True)
    course_id = serializers.CharField(required=True)
    answers = serializers.ListField(required=False)
    code_solution = serializers.CharField(required=False, allow_blank=True)
    warnings_count = serializers.IntegerField(default=0)
    warning_details = serializers.ListField(required=False)
    time_taken_minutes = serializers.IntegerField(required=True)
    status = serializers.CharField(read_only=True)
    score = serializers.IntegerField(read_only=True)
    max_score = serializers.IntegerField(read_only=True)
    percentage = serializers.FloatField(read_only=True)
    passed = serializers.BooleanField(read_only=True)
    feedback = serializers.CharField(read_only=True)
    graded_by = serializers.CharField(read_only=True)
    ai_assistance_note = serializers.CharField(read_only=True)
    started_at = serializers.CharField(read_only=True)
    submitted_at = serializers.CharField(read_only=True)
    graded_at = serializers.CharField(read_only=True)


class GradeAssignmentSerializer(serializers.Serializer):
    """Grade assignment submission"""
    score = serializers.IntegerField(required=True, min_value=0)
    feedback = serializers.CharField(required=False, allow_blank=True)
