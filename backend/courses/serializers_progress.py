"""
Serializers for progress tracking and feedback
"""
from rest_framework import serializers


class StudentProgressSerializer(serializers.Serializer):
    """Serializer for student progress"""
    _id = serializers.CharField(read_only=True)
    student_id = serializers.CharField()
    course_id = serializers.CharField()
    enrollment_id = serializers.CharField()
    lessons_completed = serializers.ListField(child=serializers.CharField(), required=False)
    quizzes_completed = serializers.ListField(required=False)
    assignments_completed = serializers.ListField(required=False)
    completion_percentage = serializers.FloatField(read_only=True)
    last_accessed = serializers.DateTimeField(read_only=True)
    time_spent_minutes = serializers.IntegerField(default=0)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CourseReviewSerializer(serializers.Serializer):
    """Serializer for course reviews"""
    _id = serializers.CharField(read_only=True)
    student_id = serializers.CharField(read_only=True)
    course_id = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review_text = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    would_recommend = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars")
        return value
    
    def validate_review_text(self, value):
        """Validate review text"""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Review must be at least 10 characters long")
        return value.strip()


class InstructorReviewSerializer(serializers.Serializer):
    """Serializer for instructor reviews"""
    _id = serializers.CharField(read_only=True)
    student_id = serializers.CharField(read_only=True)
    instructor_id = serializers.CharField()
    course_id = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review_text = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    teaching_quality = serializers.IntegerField(min_value=1, max_value=5, required=False)
    communication = serializers.IntegerField(min_value=1, max_value=5, required=False)
    course_content = serializers.IntegerField(min_value=1, max_value=5, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def validate_rating(self, value):
        """Validate overall rating"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars")
        return value
    
    def validate_teaching_quality(self, value):
        """Validate teaching quality rating"""
        if value and (value < 1 or value > 5):
            raise serializers.ValidationError("Teaching quality rating must be between 1 and 5")
        return value
    
    def validate_communication(self, value):
        """Validate communication rating"""
        if value and (value < 1 or value > 5):
            raise serializers.ValidationError("Communication rating must be between 1 and 5")
        return value
    
    def validate_course_content(self, value):
        """Validate course content rating"""
        if value and (value < 1 or value > 5):
            raise serializers.ValidationError("Course content rating must be between 1 and 5")
        return value
    
    def validate_review_text(self, value):
        """Validate review text"""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Review must be at least 10 characters long")
        return value.strip()
