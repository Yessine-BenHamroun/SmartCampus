"""
Blog serializers
"""
from rest_framework import serializers


class BlogPostSerializer(serializers.Serializer):
    """Blog post serializer"""
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(required=True, max_length=200)
    slug = serializers.SlugField(required=True, max_length=250)
    content = serializers.CharField(required=True)
    excerpt = serializers.CharField(required=False, allow_blank=True)
    author_id = serializers.CharField(read_only=True)
    category = serializers.ChoiceField(choices=[
        'Technology', 'Education', 'Career', 'Tips & Tricks',
        'News', 'Student Life', 'Industry Insights'
    ])
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
    featured_image = serializers.CharField(required=False, allow_blank=True)
    is_published = serializers.BooleanField(default=False)
    is_featured = serializers.BooleanField(default=False)
    views_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    published_at = serializers.CharField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class BlogCommentSerializer(serializers.Serializer):
    """Blog comment serializer"""
    id = serializers.CharField(read_only=True)
    post_id = serializers.CharField(required=True)
    user_id = serializers.CharField(read_only=True)
    content = serializers.CharField(required=True)
    parent_id = serializers.CharField(required=False, allow_null=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)
