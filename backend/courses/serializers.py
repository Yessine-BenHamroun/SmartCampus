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
